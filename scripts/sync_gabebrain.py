# -*- coding: utf-8 -*-
"""
sync_gabebrain.py - mantem as copias de skills e Master Skills do GabeBrain em paridade.

Fonte da verdade:
  skills/         deste repositorio   -> deploy para os agentes
  master-skills/  <-> vault "📚 Biblioteca de Agentes" (o vault e onde se edita; o repo versiona)

Destinos das skills (so atualiza as skills que o destino ja tem, exceto o
deploy principal, que recebe todas):
  ~/.gemini/config/skills                   (Antigravity - recebe todas)
  <vault>/.claude/skills                    (Claude Code, projeto do vault)
  <vault>/.agents/skills                    (Codex / agentes genericos)
  ~/.claude/skills                          (Claude Code, global)

Tambem regenera as notas de leitura em <vault>/20-Skills (geradas: nao editar).

Nunca copia segredos (.env, perfis de navegador) para o vault, que sincroniza
com o Google Drive.

Uso:
  python scripts/sync_gabebrain.py            # mostra o que faria
  python scripts/sync_gabebrain.py --apply    # aplica
"""
import argparse
import os
import re
import shutil
import sys
from datetime import date
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = Path(__file__).resolve().parent.parent
REPO_SKILLS = REPO / "skills"
REPO_MASTERS = REPO / "master-skills"
HOME = Path.home()
VAULT = Path(os.environ.get(
    "GABEBRAIN_VAULT", r"C:\GabeBrain\GabeBrain"))
DEPLOY_MAIN = HOME / ".gemini" / "config" / "skills"
DEPLOY_MIRRORS = [VAULT / ".claude" / "skills", VAULT / ".agents" / "skills",
                  HOME / ".claude" / "skills"]
VAULT_MASTERS = VAULT / "📚 Biblioteca de Agentes"
SKILL_NOTES = VAULT / "20-Skills"

IGNORE = shutil.ignore_patterns(
    "__pycache__", "*.pyc", ".env", "*.log", "*.lock", "vcs_state.json",
    "*user_data*", "*user-data*", "browser_data", ".session_data")

DOMAINS = {
    "arena-ai-controller": "dominio/engenharia-software",
    "vcs-version-agent": "dominio/engenharia-software",
    "prompt-router-coordinator": "dominio/engenharia-software",
    "superpowers-coding-agent": "dominio/engenharia-software",
    "ecc-harness-optimizer": "dominio/engenharia-software",
    "skillspector-auditor": "dominio/engenharia-software",
    "github-research": "dominio/engenharia-software",
    "sprout-cli": "dominio/engenharia-software",
    "desktop-screenshot": "dominio/engenharia-software",
    "biblioteca-pesquisavel": "dominio/geociencias",
    "biblioteca-triagem": "dominio/geociencias",
    "biblioteca-mapa-documento": "dominio/geociencias",
    "gis-multicamadas": "dominio/geociencias",
    "flow-report": "dominio/geociencias",
    "hydro-context": "dominio/geociencias",
    "environmentalist-analyst": "dominio/geociencias",
    "run-tests": "dominio/engenharia-software",
    "canva-image-agent": "dominio/design",
    "web-asset-generator": "dominio/design",
    "ui-ux-pro-max": "dominio/design",
    "deep-research": "dominio/pesquisa-web",
    "research": "dominio/pesquisa-web",
    "research-add-fields": "dominio/pesquisa-web",
    "research-add-items": "dominio/pesquisa-web",
    "research-deep": "dominio/pesquisa-web",
    "research-report": "dominio/pesquisa-web",
    "context7-cli": "dominio/engenharia-software",
    "context7-mcp": "dominio/engenharia-software",
    "find-docs": "dominio/engenharia-software",
    "ponytail": "dominio/engenharia-software",
    "ponytail-review": "dominio/engenharia-software",
    "ponytail-audit": "dominio/engenharia-software",
    "ponytail-debt": "dominio/engenharia-software",
    "ponytail-gain": "dominio/engenharia-software",
    "ponytail-help": "dominio/engenharia-software",
    "caveman": "dominio/engenharia-software",
    "caveman-commit": "dominio/engenharia-software",
    "caveman-compress": "dominio/engenharia-software",
    "watch": "dominio/pesquisa-web",
    "impeccable": "dominio/design",
    "graphify": "dominio/engenharia-software",
}


def tracked_files(root: Path) -> dict:
    """relpath -> conteudo com EOL normalizado, sem o que IGNORE descarta."""
    out = {}
    for p in root.rglob("*"):
        rel = p.relative_to(root)
        if any(IGNORE("", [part]) for part in rel.parts) or not p.is_file():
            continue
        out[rel] = p.read_bytes().replace(b"\r\n", b"\n")
    return out


def dir_differs(a: Path, b: Path) -> bool:
    # git autocrlf muda o EOL no checkout; so conteudo real conta.
    # Arquivo so no destino tambem conta: e copia velha que ficaria para tras.
    return not b.exists() or tracked_files(a) != tracked_files(b)


def newer_in_dst(src: Path, dst: Path) -> list:
    """Arquivos que alguem editou direto no destino depois do repo."""
    a, b = tracked_files(src), tracked_files(dst)
    return [str(rel) for rel, data in b.items()
            if a.get(rel) != data
            and (not (src / rel).exists()
                 or (dst / rel).stat().st_mtime > (src / rel).stat().st_mtime + 2)]


def deploy_skill(src: Path, dst: Path, apply: bool) -> bool:
    if not dir_differs(src, dst):
        return False
    edited = newer_in_dst(src, dst) if dst.exists() else []
    if edited:
        print(f"  CONFLITO {src.name} em {dst.parent}: editado no destino depois do repo "
              f"({', '.join(edited[:3])}). Leve a mudança para o repo; nada sobrescrito.")
        return False
    print(f"  skill  {src.name} -> {dst.parent}")
    if not apply:
        return True
    shutil.copytree(src, dst, ignore=IGNORE, dirs_exist_ok=True)
    # Remove do destino o que saiu do repo, mas preserva o que o repo ignora
    # de proposito (.env, perfis de navegador, logs): isso e estado local.
    for p in sorted(dst.rglob("*"), reverse=True):
        rel = p.relative_to(dst)
        if (src / rel).exists() or any(IGNORE(str(p.parent), [p.name])):
            continue
        if any(IGNORE(str(a.parent), [a.name]) for a in rel.parents if str(a) != "."):
            continue
        if p.is_file():
            p.unlink()
        elif p.is_dir() and not any(p.iterdir()):
            p.rmdir()
    return True


def purge_secrets(root: Path, apply: bool):
    for p in root.rglob(".env"):
        print(f"  SEGREDO removido do vault: {p}")
        if apply:
            p.unlink()


def sync_skills(apply: bool):
    print("== skills")
    skills = sorted(p for p in REPO_SKILLS.iterdir() if (p / "SKILL.md").exists())
    for s in skills:
        deploy_skill(s, DEPLOY_MAIN / s.name, apply)
    for mirror in DEPLOY_MIRRORS:
        if not mirror.exists():
            continue
        for s in skills:
            if (mirror / s.name).exists():
                deploy_skill(s, mirror / s.name, apply)
        purge_secrets(mirror, apply)
    orphans = [p.name for p in DEPLOY_MAIN.iterdir()
               if p.is_dir() and not (REPO_SKILLS / p.name).exists()]
    if orphans:
        print(f"  AVISO: skills no deploy fora do repo (versione-as): {orphans}")
    return skills


def sync_masters(apply: bool):
    """Vault -> repo (o vault e onde se edita); master nova no repo -> vault.
    Subagentes em 'Subagente_*.md' sincronizam com 'agents/*.md'."""
    print("== master-skills & subagentes")
    def same(a: Path, b: Path) -> bool:
        # git autocrlf reescreve EOL no checkout: compara so o conteudo
        return a.read_bytes().replace(b"\r\n", b"\n") == b.read_bytes().replace(b"\r\n", b"\n")

    repo_agents = REPO / "agents"
    for v in sorted(VAULT_MASTERS.glob("*.md")):
        if v.name.startswith("Subagente_"):
            agent_file = v.name.replace("Subagente_", "")
            r = repo_agents / agent_file
            if not r.exists() or not same(v, r):
                print(f"  vault -> repo (subagente) {v.name} -> agents/{agent_file}")
                if apply:
                    shutil.copy2(v, r)
        else:
            r = REPO_MASTERS / v.name
            if not r.exists() or not same(v, r):
                print(f"  vault -> repo {v.name}")
                if apply:
                    shutil.copy2(v, r)
    for r in sorted(REPO_MASTERS.glob("*.md")):
        if not (VAULT_MASTERS / r.name).exists():
            print(f"  AVISO: so no repo (copie para o vault ou remova): {r.name}")
    for a in sorted(repo_agents.glob("*.md")):
        v_sub = VAULT_MASTERS / f"Subagente_{a.name}"
        if not v_sub.exists() and not a.name.endswith("-agent.md"):
            print(f"  AVISO subagente so no repo (copie para o vault): {a.name}")


def front_desc(text: str) -> str:
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return ""
    fm = m.group(1)
    d = re.search(r"^description:\s*(>-?|\|)?\s*(.*?)(?=^\w[\w-]*:|\Z)", fm, re.M | re.S)
    if not d:
        return ""
    return " ".join(line.strip() for line in d.group(2).splitlines()).strip().strip('"')


def strip_front(text: str) -> str:
    return re.sub(r"^---\s*\n.*?\n---\s*\n", "", text, count=1, flags=re.DOTALL)


def build_notes(skills, apply: bool):
    # print("== 20-Skills (notas geradas)")
    today = date.today().isoformat()
    rows = []
    wanted = set()
    for s in skills:
        text = (s / "SKILL.md").read_text(encoding="utf-8", errors="replace")
        desc = front_desc(text) or "(sem description no frontmatter)"
        domain = DOMAINS.get(s.name, "dominio/computacao")
        body = strip_front(text).strip()
        note = "\n".join([
            "---",
            "tipo: skill",
            f"skill_id: {s.name}",
            "gerado_por: gabebrain-skills/scripts/sync_gabebrain.py",
            f"data_atualizacao: {today}",
            "tags:",
            "  - skill",
            "  - tipo/skill",
            f"  - {domain}",
            "---",
            f"# Skill: `{s.name}`",
            "",
            "> [!info] Nota gerada — não edite aqui",
            f"> Fonte: repositório `gabebrain-skills/skills/{s.name}/SKILL.md`. "
            "Edite lá e rode `python scripts/sync_gabebrain.py --apply`.",
            "",
            f"**Descrição:** {desc}",
            "",
            "---",
            "",
            body,
            "",
            "---",
            "[[00 - Índice de Skills|⬅ Catálogo de Skills]] · [[MOC - GabeBrain|🏠 MOC]]",
            "",
        ])
        name = f"Skill_{s.name}.md"
        wanted.add(name)
        target = SKILL_NOTES / name
        if not target.exists() or target.read_text(encoding="utf-8", errors="replace") != note:
            print(f"  nota  {name}")
            if apply:
                target.write_text(note, encoding="utf-8", newline="\n")
        short = desc if len(desc) <= 160 else desc[:157].rsplit(" ", 1)[0] + "…"
        rows.append(f"| [[Skill_{s.name}\\|{s.name}]] | `#{domain}` | {short.replace('|', '/')} |")

    for old in SKILL_NOTES.glob("Skill_*.md"):
        if old.name not in wanted:
            print(f"  AVISO: nota sem skill correspondente: {old.name}")

    index = "\n".join([
        "---",
        "tipo: indice",
        "gerado_por: gabebrain-skills/scripts/sync_gabebrain.py",
        f"data_atualizacao: {today}",
        "tags:",
        "  - indice",
        "  - skills",
        "  - tipo/indice",
        "---",
        "# ⚡ Catálogo de Skills Executáveis (GabeBrain)",
        "",
        f"{len(skills)} skills. Fonte da verdade: repositório "
        "[gabebrain-skills](https://github.com/gabrielhklaser/gabebrain-skills) → "
        "deploy em `~/.gemini/config/skills` (Antigravity), `.claude/skills` e "
        "`.agents/skills` do vault. Notas geradas — edite o `SKILL.md` no repo e rode "
        "`python scripts/sync_gabebrain.py --apply`.",
        "",
        "| Skill | Domínio | Descrição |",
        "|:---|:---|:---|",
        *rows,
        "",
        "---",
        "[[MOC - GabeBrain|🏠 MOC Central]] · "
        "[[00 - Índice da Biblioteca de Agentes|🤖 Biblioteca de Agentes]]",
        "",
    ])
    target = SKILL_NOTES / "00 - Índice de Skills.md"
    if not target.exists() or target.read_text(encoding="utf-8", errors="replace") != index:
        print("  nota  00 - Índice de Skills.md")
        if apply:
            target.write_text(index, encoding="utf-8", newline="\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--apply", action="store_true", help="aplica (sem isso, só mostra)")
    args = ap.parse_args()
    if not VAULT.exists():
        sys.exit(f"Vault não encontrado: {VAULT} (defina GABEBRAIN_VAULT)")
    skills = sync_skills(args.apply)
    sync_masters(args.apply)
    build_notes(skills, args.apply)
    print("APLICADO" if args.apply else "DRY-RUN — use --apply")


if __name__ == "__main__":
    main()

