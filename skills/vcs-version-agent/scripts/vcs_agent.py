#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GabeBrain VCS Agent - Controlador e Gerenciador de Versões de Projetos
---------------------------------------------------------------------
Inspeciona o estado dos projetos entre o ambiente local (GabeBrain) e o GitHub.
- `status`/`check` atualizam referências remotas quando online, sem alterar a árvore de trabalho.
- Pull, merge, commit e push só são executados pelo comando explícito `sync`.
- Alterações não commitadas exigem `--commit-dirty` e um único `--repo` informado.
- Detecta branches da Arena.ai; a verificação no boot e pré-prompt é sem escrita.
"""

import os
import sys
import json
import socket
import logging
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# Configurar UTF-8 seguro no console do Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# User-specific state belongs in OS config/state directories, never in a repository.
def _default_config_dir() -> Path:
    """Preserve the existing per-user Gemini config location without hard-coded usernames."""
    return Path.home() / ".gemini" / "config"


def _default_log_dir() -> Path:
    """Preserve the existing per-user log location without hard-coded usernames."""
    return Path.home() / ".gemini" / "antigravity" / "logs"


def _ensure_private_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    if os.name != "nt":
        path.chmod(0o700)
    return path


CONFIG_DIR = Path(os.environ.get("GABEBRAIN_CONFIG_DIR") or _default_config_dir()).expanduser()
PROJECTS_CONFIG_FILE = CONFIG_DIR / "vcs_projects.json"
STATE_LEDGER_FILE = CONFIG_DIR / "vcs_state.json"
LOG_DIR = Path(os.environ.get("GABEBRAIN_LOG_DIR") or _default_log_dir()).expanduser()
LOG_FILE = LOG_DIR / "vcs_sync.log"

home = Path.home()
DEFAULT_SEARCH_PATHS = [
    home / ".gemini" / "antigravity" / "scratch",
    home / "Meu Drive" / "Github - projetos",
    home / "Documents" / "GitHub",
]

logger = logging.getLogger("vcs_agent")


def configure_logging() -> None:
    """Initialize private file logging only when the CLI actually runs."""
    _ensure_private_dir(LOG_DIR)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8"), logging.StreamHandler(sys.stdout)],
    )
    if os.name != "nt" and LOG_FILE.exists():
        LOG_FILE.chmod(0o600)


def is_online(host: str = "github.com", port: int = 443, timeout: float = 3.0) -> bool:
    """Verifica se há conectividade de rede com o GitHub."""
    try:
        socket.setdefaulttimeout(timeout)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
        return True
    except (socket.timeout, socket.error, OSError):
        return False


def run_git(cmd: List[str], cwd: Path, timeout: int = 30) -> Tuple[int, str, str]:
    """Executa um comando git capturando saída e código de retorno."""
    try:
        proc = subprocess.run(
            ["git"] + cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace"
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", f"Timeout ({timeout}s) executando git {' '.join(cmd)}"
    except Exception as e:
        return -1, "", str(e)


def load_config() -> Dict[str, Any]:
    """Carrega ou inicializa a configuração de projetos monitorados."""
    if PROJECTS_CONFIG_FILE.exists():
        try:
            with open(PROJECTS_CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Erro ao ler {PROJECTS_CONFIG_FILE}: {e}. Criando nova.")

    default_config = {
        "version": "1.0.0",
        "search_paths": [str(p) for p in DEFAULT_SEARCH_PATHS],
        "track_arena_branches": True,
        "auto_merge_arena": False,
        "arena_merge_reviewed": False,
        "notify_on_sync": True,
        "projects": [
            {
                "name": "licenciamentoambiental",
                "path": str(DEFAULT_SEARCH_PATHS[0] / "licenciamentoambiental"),
                "repo": "gabrielhklaser/licenciamentoambiental",
                "default_branch": "main",
            },
            {
                "name": "agentearena",
                "path": str(DEFAULT_SEARCH_PATHS[0] / "agentearena"),
                "repo": "gabrielhklaser/agentearena",
                "default_branch": "main",
            },
            {
                "name": "gabriel_agent_skills",
                "path": str(DEFAULT_SEARCH_PATHS[0] / "gabriel_agent_skills"),
                "repo": "gabrielhklaser/agent-skills",
                "default_branch": "main",
            },
            {
                "name": "outorgasys",
                "path": str(DEFAULT_SEARCH_PATHS[1] / "outorgasys"),
                "repo": "gabrielhklaser/outorgasys",
                "default_branch": "main",
            },
            {
                "name": "partiturabatera.github.io",
                "path": str(DEFAULT_SEARCH_PATHS[2] / "partiturabatera.github.io"),
                "repo": "gabrielhklaser/partiturabatera.github.io",
                "default_branch": "main",
            }
        ]
    }
    save_config(default_config)
    return default_config


def save_config(config: Dict[str, Any]):
    """Salva a configuração de projetos."""
    _ensure_private_dir(CONFIG_DIR)
    with open(PROJECTS_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    if os.name != "nt":
        PROJECTS_CONFIG_FILE.chmod(0o600)


def load_state() -> Dict[str, Any]:
    """Carrega o livro de registros de estado e histórico de sincronizações."""
    if STATE_LEDGER_FILE.exists():
        try:
            with open(STATE_LEDGER_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"last_run": None, "projects": {}}


def save_state(state: Dict[str, Any]):
    """Salva o livro de registros de estado."""
    _ensure_private_dir(CONFIG_DIR)
    with open(STATE_LEDGER_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    if os.name != "nt":
        STATE_LEDGER_FILE.chmod(0o600)


def scan_and_register_projects() -> List[str]:
    """Escaneia os diretórios padrão do GabeBrain e cadastra novos repositórios Git encontrados."""
    config = load_config()
    existing_paths = {os.path.normpath(p["path"]).lower() for p in config.get("projects", [])}
    new_found = []

    for search_root_str in config.get("search_paths", []):
        search_root = Path(search_root_str)
        if not search_root.exists():
            continue

        # Procura até 2 níveis de profundidade
        try:
            for item in search_root.iterdir():
                if item.is_dir() and (item / ".git").exists():
                    norm_path = os.path.normpath(str(item)).lower()
                    if norm_path not in existing_paths:
                        # Extrai informações do repositório
                        _, remote_url, _ = run_git(["config", "--get", "remote.origin.url"], item)
                        _, branch, _ = run_git(["branch", "--show-current"], item)
                        repo_name = item.name
                        
                        proj_entry = {
                            "name": repo_name,
                            "path": str(item),
                            "repo": remote_url or f"gabrielhklaser/{repo_name}",
                            "default_branch": branch or "main",
                        }
                        config.setdefault("projects", []).append(proj_entry)
                        existing_paths.add(norm_path)
                        new_found.append(f"{repo_name} ({item})")
                        logger.info(f"Novo projeto Git registrado automaticamente: {repo_name} em {item}")
        except Exception as e:
            logger.error(f"Erro ao escanear {search_root}: {e}")

    if new_found:
        save_config(config)
    return new_found


def inspect_arena_branches(repo_path: Path) -> Dict[str, Any]:
    """
    Inspeciona branches criadas pelo Arena.ai web (origin/arena/*).
    Detecta se há novas alterações ou commits do bot/web aguardando integração.
    """
    code, out, _ = run_git(["branch", "-r", "--list", "origin/arena/*"], repo_path)
    if code != 0 or not out:
        return {"has_arena_branches": False, "latest_arena_branch": None, "unmerged_commits": []}

    arena_branches = [line.strip().replace("origin/", "") for line in out.splitlines() if line.strip()]
    if not arena_branches:
        return {"has_arena_branches": False, "latest_arena_branch": None, "unmerged_commits": []}

    # Ordena branches pelo commit mais recente
    branches_info = []
    for br in arena_branches:
        # Obter data e autor do último commit dessa branch remota
        c_code, c_out, _ = run_git(["log", "-n", "1", "--format=%ct|%h|%an|%s", f"origin/{br}"], repo_path)
        if c_code == 0 and c_out:
            parts = c_out.split("|", 3)
            if len(parts) == 4:
                timestamp, sha, author, msg = parts
                branches_info.append({
                    "branch": br,
                    "timestamp": int(timestamp),
                    "sha": sha,
                    "author": author,
                    "message": msg
                })

    if not branches_info:
        return {"has_arena_branches": True, "latest_arena_branch": arena_branches[-1], "unmerged_commits": []}

    branches_info.sort(key=lambda x: x["timestamp"], reverse=True)
    latest_arena = branches_info[0]

    # Verificar se os commits dessa branch já estão contidos no HEAD atual
    code_diff, diff_out, _ = run_git(["rev-list", f"HEAD..origin/{latest_arena['branch']}", "--oneline"], repo_path)
    unmerged = diff_out.splitlines() if (code_diff == 0 and diff_out) else []

    return {
        "has_arena_branches": True,
        "latest_arena_branch": latest_arena["branch"],
        "latest_commit": latest_arena,
        "unmerged_commits": unmerged,
        "is_ahead_of_local": len(unmerged) > 0
    }


def analyze_project(proj: Dict[str, Any], online: bool) -> Dict[str, Any]:
    """Analisa o estado atual de um projeto Git."""
    repo_path = Path(proj["path"])
    info = {
        "name": proj["name"],
        "path": str(repo_path),
        "exists": repo_path.exists() and (repo_path / ".git").exists(),
        "online": online,
        "branch": "",
        "dirty": False,
        "dirty_files_count": 0,
        "ahead": 0,
        "behind": 0,
        "tracking_remote": None,
        "arena": {},
        "status_summary": "",
        "action_required": "none"
    }

    if not info["exists"]:
        info["status_summary"] = "Diretório ou .git não encontrado"
        info["action_required"] = "clone_or_fix"
        return info

    # Branch atual
    _, branch, _ = run_git(["branch", "--show-current"], repo_path)
    info["branch"] = branch or "HEAD destacada"

    # Status de alterações locais
    _, status_out, _ = run_git(["status", "--porcelain"], repo_path)
    dirty_lines = [l for l in status_out.splitlines() if l.strip()]
    info["dirty"] = len(dirty_lines) > 0
    info["dirty_files_count"] = len(dirty_lines)

    # Remote tracking
    _, remote_url, _ = run_git(["config", "--get", "remote.origin.url"], repo_path)
    info["tracking_remote"] = remote_url

    if online and remote_url:
        # Fetch com timeout seguro
        run_git(["fetch", "--all", "--prune", "--tags"], repo_path, timeout=25)

        # Ahead / Behind em relação ao upstream
        code_u, u_branch, _ = run_git(["rev-parse", "--abbrev-ref", "@{u}"], repo_path)
        if code_u == 0 and u_branch:
            _, ahead_str, _ = run_git(["rev-list", "--count", "@{u}..HEAD"], repo_path)
            _, behind_str, _ = run_git(["rev-list", "--count", "HEAD..@{u}"], repo_path)
            info["ahead"] = int(ahead_str) if ahead_str.isdigit() else 0
            info["behind"] = int(behind_str) if behind_str.isdigit() else 0
        else:
            # Caso não tenha upstream configurado, verifica contra origin/<branch>
            _, behind_str, _ = run_git(["rev-list", "--count", f"HEAD..origin/{branch}"], repo_path)
            _, ahead_str, _ = run_git(["rev-list", "--count", f"origin/{branch}..HEAD"], repo_path)
            info["ahead"] = int(ahead_str) if ahead_str.isdigit() else 0
            info["behind"] = int(behind_str) if behind_str.isdigit() else 0

        # Análise específica de Arena.ai
        arena_info = inspect_arena_branches(repo_path)
        info["arena"] = arena_info

    # Determina ação requerida
    if info["dirty"]:
        info["action_required"] = "commit_needed"
    elif online and (info["behind"] > 0 or info.get("arena", {}).get("is_ahead_of_local")):
        info["action_required"] = "pull_needed"
    elif online and info["ahead"] > 0:
        info["action_required"] = "push_needed"
    else:
        info["action_required"] = "in_sync"

    return info


def sync_project(
    proj: Dict[str, Any],
    online: bool,
    auto_merge_arena: bool = False,
    commit_dirty: bool = False,
) -> Dict[str, Any]:
    """Sincroniza um projeto; alterações não commitadas só entram com opt-in explícito."""
    repo_path = Path(proj["path"])
    result = {
        "name": proj["name"],
        "success": True,
        "skipped": False,
        "online": online,
        "actions": [],
        "errors": []
    }

    if not (repo_path.exists() and (repo_path / ".git").exists()):
        result["success"] = False
        result["errors"].append(f"Caminho não é um repositório git válido: {repo_path}")
        return result

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. TRATAMENTO DE ARQUIVOS MODIFICADOS LOCALMENTE (ONLINE E OFFLINE)
    _, status_out, _ = run_git(["status", "--porcelain"], repo_path)
    dirty_lines = [l for l in status_out.splitlines() if l.strip()]

    if dirty_lines and not commit_dirty:
        result["skipped"] = True
        result["actions"].append(
            f"Ignorado: há {len(dirty_lines)} arquivo(s) localmente modificados; "
            "nada foi staged, commitado ou enviado. Revise `git status` e execute "
            "`sync --repo <nome> --commit-dirty` somente se desejar incluir essas alterações."
        )
        return result

    if dirty_lines:
        prefix = "chore(offline-sync)" if not online else "chore(manual-sync)"
        msg = f"{prefix}: snapshot local ({len(dirty_lines)} arquivos) [{now_str}]"
        
        # Stage all files only after the explicit --commit-dirty opt-in.
        add_code, _, add_err = run_git(["add", "-A"], repo_path)
        if add_code != 0:
            result["success"] = False
            result["errors"].append(f"Falha ao executar git add: {add_err}")
            return result

        commit_code, commit_out, commit_err = run_git(["commit", "-m", msg], repo_path)
        if commit_code == 0:
            result["actions"].append(f"Commit local realizado: {msg}")
            logger.info(f"[{proj['name']}] {msg}")
        else:
            result["errors"].append(f"Falha no commit: {commit_err}")

    # SE ESTIVER OFFLINE, O CICLO SE ENCERRA AQUI COM SUCESSO E ESTADO PRESERVADO
    if not online:
        result["actions"].append("Modo Offline: Alterações salvas em commit local. Aguardando conexão para push.")
        return result

    # 2. MODO ONLINE: SINCRONIZAÇÃO BIDIRECIONAL COM GITHUB
    # Fetch de todas as branches e tags
    f_code, _, f_err = run_git(["fetch", "--all", "--prune", "--tags"], repo_path, timeout=30)
    if f_code != 0:
        result["success"] = False
        result["errors"].append(f"Falha no git fetch: {f_err}")
        return result

    # Branch atual
    _, current_branch, _ = run_git(["branch", "--show-current"], repo_path)
    current_branch = current_branch or "main"

    # 3. VERIFICAÇÃO E INTEGRAÇÃO DE ARENA.AI
    arena_data = inspect_arena_branches(repo_path)
    if arena_data.get("has_arena_branches") and arena_data.get("is_ahead_of_local"):
        latest_br = arena_data["latest_arena_branch"]
        unmerged_cnt = len(arena_data["unmerged_commits"])
        logger.info(f"[{proj['name']}] Detectados {unmerged_cnt} commits na branch Arena.ai 'origin/{latest_br}'!")

        if auto_merge_arena:
            # Tenta merge defensivo da branch Arena na branch atual
            merge_code, merge_out, merge_err = run_git(
                ["merge", f"origin/{latest_br}", "-m", f"chore(arena-sync): integra atualizações da Arena.ai ({latest_br}) [{now_str}]"],
                repo_path
            )
            if merge_code == 0:
                result["actions"].append(f"Arena.ai: Integrados {unmerged_cnt} commits de 'origin/{latest_br}'.")
                logger.info(f"[{proj['name']}] Merge de origin/{latest_br} concluído com sucesso!")
            else:
                # Se der conflito no merge da arena, aborta merge para não quebrar a árvore
                run_git(["merge", "--abort"], repo_path)
                result["errors"].append(f"Conflito ao integrar branch Arena 'origin/{latest_br}'. Requer verificação manual.")
                logger.warning(f"[{proj['name']}] Conflito ao mesclar origin/{latest_br}. Merge abortado por segurança.")

    # 4. PULL / REBASE DO TRACKING BRANCH ATUAL
    # Verifica commits atrás do upstream
    code_u, u_branch, _ = run_git(["rev-parse", "--abbrev-ref", "@{u}"], repo_path)
    target_upstream = u_branch if (code_u == 0 and u_branch) else f"origin/{current_branch}"

    _, behind_cnt_str, _ = run_git(["rev-list", "--count", f"HEAD..{target_upstream}"], repo_path)
    behind_cnt = int(behind_cnt_str) if behind_cnt_str.isdigit() else 0

    if behind_cnt > 0:
        logger.info(f"[{proj['name']}] Puxando {behind_cnt} commits remotos de {target_upstream}...")
        pull_code, pull_out, pull_err = run_git(["pull", "--rebase", "origin", current_branch], repo_path, timeout=30)
        if pull_code == 0:
            result["actions"].append(f"Pull: {behind_cnt} commits atualizados com sucesso de {target_upstream}.")
        else:
            # Se der conflito no rebase, cria branch de segurança antes de abortar
            backup_branch = f"backup/conflict-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            run_git(["branch", backup_branch], repo_path)
            run_git(["rebase", "--abort"], repo_path)
            result["success"] = False
            result["errors"].append(f"Conflito durante pull --rebase. Criada branch de backup '{backup_branch}'. Rebase abortado.")
            logger.error(f"[{proj['name']}] Conflito no rebase! Backup salvo em {backup_branch}.")

    # 5. PUSH PARA GITHUB
    _, ahead_cnt_str, _ = run_git(["rev-list", "--count", f"{target_upstream}..HEAD"], repo_path)
    ahead_cnt = int(ahead_cnt_str) if ahead_cnt_str.isdigit() else 0

    if ahead_cnt > 0:
        logger.info(f"[{proj['name']}] Enviando {ahead_cnt} commits locais para GitHub (origin {current_branch})...")
        push_code, push_out, push_err = run_git(["push", "origin", current_branch], repo_path, timeout=40)
        if push_code == 0:
            result["actions"].append(f"Push: {ahead_cnt} commits enviados ao GitHub com sucesso.")
            logger.info(f"[{proj['name']}] Push realizado com sucesso!")
        else:
            result["success"] = False
            result["errors"].append(f"Falha ao enviar commits para o GitHub: {push_err}")
            logger.error(f"[{proj['name']}] Falha no git push: {push_err}")
    elif not dirty_lines and behind_cnt == 0 and not result["actions"]:
        result["actions"].append("Repositório já está 100% atualizado e em sincronia.")

    return result


def send_windows_notification(title: str, message: str):
    """Envia uma notificação visual sem interpolar dados em código PowerShell."""
    try:
        ps_script = """
        [System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms') | Out-Null
        $notify = New-Object System.Windows.Forms.NotifyIcon
        $notify.Icon = [System.Drawing.SystemIcons]::Information
        $notify.BalloonTipTitle = [Environment]::GetEnvironmentVariable('GABEBRAIN_NOTIFY_TITLE')
        $notify.BalloonTipText = [Environment]::GetEnvironmentVariable('GABEBRAIN_NOTIFY_MESSAGE')
        $notify.BalloonTipIcon = [System.Windows.Forms.ToolTipIcon]::Info
        $notify.Visible = $True
        $notify.ShowBalloonTip(4000)
        Start-Sleep -Seconds 1
        $notify.Dispose()
        """
        env = os.environ.copy()
        env["GABEBRAIN_NOTIFY_TITLE"] = title
        env["GABEBRAIN_NOTIFY_MESSAGE"] = message
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_script],
            capture_output=True,
            timeout=10,
            env=env,
            check=False,
        )
    except Exception as e:
        logger.debug(f"Notificação visual do Windows ignorada: {e}")


def cmd_status(args):
    """Exibe o status completo dos projetos já cadastrados, sem registrar outros."""
    config = load_config()
    online = is_online()
    mode_str = "[ONLINE] Conectado ao GitHub" if online else "[OFFLINE] Modo Local Seguro"
    
    print("\n" + "="*80)
    print(f" GABEBRAIN VCS AGENT - PAINEL DE CONTROLE DE VERSOES | {mode_str}")
    print("="*80)

    projects = config.get("projects", [])
    if not projects:
        print("Nenhum projeto registrado ainda.")
        return

    for proj in projects:
        info = analyze_project(proj, online)
        status_tag = "[EM SINCRONIA]" if info["action_required"] == "in_sync" else f"[{info['action_required'].upper()}]"
        
        print(f"\n* PROJETO: {info['name']} {status_tag}")
        print(f"   - Caminho:  {info['path']}")
        print(f"   - Branch:   {info['branch']} (Ahead: +{info['ahead']} | Behind: -{info['behind']})")
        print(f"   - Estado:   {'Modificações locais pendentes (' + str(info['dirty_files_count']) + ' arquivos)' if info['dirty'] else 'Diretório de trabalho limpo'}")
        
        arena = info.get("arena", {})
        if arena.get("has_arena_branches"):
            latest = arena.get("latest_arena_branch", "N/A")
            unmerged = len(arena.get("unmerged_commits", []))
            arena_flag = f"[AVISO] {unmerged} commits pendentes de origin/{latest}" if unmerged > 0 else f"[OK] Atualizado com origin/{latest}"
            print(f"   - Arena.ai: {arena_flag}")

        print(f"   - Ação:     {info['action_required'].upper()}")

    print("\n" + "="*80 + "\n")


def _project_matches(proj: Dict[str, Any], target: str) -> bool:
    """Match only an exact project name or exact expanded filesystem path."""
    target = str(target).strip()
    if not target:
        return False
    if str(proj.get("name", "")).casefold() == target.casefold():
        return True
    project_path = proj.get("path")
    if not project_path:
        return False
    try:
        return Path(project_path).expanduser().resolve() == Path(target).expanduser().resolve()
    except (OSError, RuntimeError, TypeError):
        return False


def cmd_sync(args):
    """Sincroniza somente os projetos já cadastrados na configuração local."""
    config = load_config()
    force_offline = getattr(args, "force_offline", False)
    target_repo = getattr(args, "repo", None)
    commit_dirty = bool(getattr(args, "commit_dirty", False))
    projects = config.get("projects", [])
    if target_repo:
        projects = [p for p in projects if _project_matches(p, target_repo)]
    if commit_dirty and len(projects) != 1:
        raise SystemExit("[ERRO] --commit-dirty exige identificar exatamente um projeto com --repo.")

    online = False if force_offline else is_online()
    print(f"\n[GABEBRAIN VCS] Iniciando sincronização... [{'ONLINE' if online else 'OFFLINE'}]")
    synced_count = 0
    total_actions = []

    for proj in projects:
        res = sync_project(
            proj,
            online,
            auto_merge_arena=bool(config.get("auto_merge_arena", False) and config.get("arena_merge_reviewed", False)),
            commit_dirty=commit_dirty,
        )
        status_tag = "PULADO" if res.get("skipped") else ("OK" if res["success"] else "ERRO")
        print(f"\n[{status_tag}] {proj['name']}:")
        for a in res["actions"]:
            print(f"  ✓ {a}")
            total_actions.append(f"{proj['name']}: {a}")
        for err in res["errors"]:
            print(f"  ✗ {err}")
        if res["success"] and not res.get("skipped"):
            synced_count += 1

    # Atualiza livro de registros de estado
    state = load_state()
    state["last_run"] = datetime.now().isoformat()
    state["last_mode"] = "online" if online else "offline"
    save_state(state)

    print(f"\n[GABEBRAIN VCS] Finalizado: {synced_count}/{len(projects)} projetos sincronizados com sucesso.\n")

    if config.get("notify_on_sync", True) and getattr(args, "notify", False):
        mode_txt = "GitHub Online" if online else "Offline (Snapshot Local)"
        send_windows_notification(
            "GabeBrain VCS Sincronizado",
            f"{synced_count} projetos atualizados ({mode_txt}). Paridade garantida!"
        )


def cmd_check(args):
    """Verifica o estado sem alterar a árvore de trabalho ou enviar commits; pode fazer fetch."""
    config = load_config()
    online = is_online(timeout=2.0)
    target_repo = getattr(args, "repo", None)
    projects = config.get("projects", [])
    if target_repo:
        projects = [p for p in projects if _project_matches(p, target_repo)]

    needs_sync = False
    reasons = []

    for proj in projects:
        info = analyze_project(proj, online)
        if info["dirty"]:
            needs_sync = True
            reasons.append(f"{proj['name']} tem alterações locais não commitadas.")
        if online and info["behind"] > 0:
            needs_sync = True
            reasons.append(f"{proj['name']} tem {info['behind']} novos commits no GitHub.")
        if online and info.get("arena", {}).get("is_ahead_of_local"):
            needs_sync = True
            reasons.append(f"{proj['name']} tem novas versões criadas na Arena.ai web.")

    if needs_sync:
        print("[ALERTA VCS] Divergências detectadas antes de iniciar o prompt:")
        for reason in reasons:
            print(f"  -> {reason}")
        print("[ALERTA VCS] Nenhuma alteração foi aplicada automaticamente. Revise o estado e execute `sync` manualmente se desejar.")
        print("[ALERTA VCS] Para incluir arquivos não commitados, revise `git status` e informe `--commit-dirty` junto com `--repo`.")
    else:
        print("[OK VCS] Projetos cadastrados sem divergências detectadas. Nenhuma alteração foi aplicada.")


def cmd_startup(args):
    """Verifica repositórios no logon; não altera a árvore de trabalho nem envia commits."""
    logger.info("=== GABEBRAIN STARTUP VCS CHECK INICIADO ===")
    args.repo = None
    cmd_check(args)
    logger.info("=== GABEBRAIN STARTUP VCS CHECK CONCLUÍDO ===")


def cmd_add(args):
    """Adiciona manualmente um diretório de projeto à lista monitorada."""
    path = Path(args.path).resolve()
    if not (path.exists() and (path / ".git").exists()):
        print(f"Erro: {path} não é um repositório git válido.")
        sys.exit(1)

    config = load_config()
    name = args.name or path.name
    _, remote_url, _ = run_git(["config", "--get", "remote.origin.url"], path)
    _, branch, _ = run_git(["branch", "--show-current"], path)

    # Remover duplicatas antigas
    config["projects"] = [p for p in config.get("projects", []) if os.path.normpath(p["path"]).lower() != os.path.normpath(str(path)).lower()]

    new_proj = {
        "name": name,
        "path": str(path),
        "repo": remote_url or f"gabrielhklaser/{name}",
        "default_branch": branch or "main",
    }
    config["projects"].append(new_proj)
    save_config(config)
    print(f"Projeto '{name}' cadastrado com sucesso em: {path}")


def main():
    parser = argparse.ArgumentParser(description="GabeBrain VCS Agent - Controle de Versões")
    subparsers = parser.add_subparsers(dest="command", help="Comando a executar")

    # status
    subparsers.add_parser("status", help="Exibe o status de versões de todos os projetos")

    # sync
    sync_parser = subparsers.add_parser("sync", help="Sincroniza projetos; alterações não commitadas são ignoradas por padrão")
    sync_parser.add_argument("--repo", help="Nome exato ou caminho do repositório específico")
    sync_parser.add_argument("--force-offline", action="store_true", help="Força modo offline")
    sync_parser.add_argument("--notify", action="store_true", help="Dispara notificação visual no Windows")
    sync_parser.add_argument(
        "--commit-dirty",
        action="store_true",
        help="Inclui arquivos não commitados; exige --repo e revisão prévia de git status",
    )

    # check
    check_parser = subparsers.add_parser("check", help="Verifica divergências sem sincronizar automaticamente")
    check_parser.add_argument("--repo", help="Nome exato ou caminho do repositório a verificar")

    # startup
    subparsers.add_parser("startup", help="Verificação sem escrita executada no logon")

    # add
    add_parser = subparsers.add_parser("add", help="Adiciona um repositório git")
    add_parser.add_argument("path", help="Caminho do repositório local")
    add_parser.add_argument("--name", help="Nome amigável do projeto")

    # scan
    subparsers.add_parser("scan", help="Escaneia diretórios e adiciona projetos git automaticamente")

    args = parser.parse_args()
    if args.command == "sync" and args.commit_dirty and not args.repo:
        parser.error("--commit-dirty exige --repo para limitar o escopo a um único projeto")
    if not args.command:
        parser.print_help()
        sys.exit(0)

    configure_logging()

    if args.command == "status":
        cmd_status(args)
    elif args.command == "sync":
        cmd_sync(args)
    elif args.command == "check":
        cmd_check(args)
    elif args.command == "startup":
        cmd_startup(args)
    elif args.command == "add":
        cmd_add(args)
    elif args.command == "scan":
        new_projects = scan_and_register_projects()
        print(f"Escaneamento concluído. {len(new_projects)} novos projetos registrados.")
        cmd_status(args)


if __name__ == "__main__":
    main()
