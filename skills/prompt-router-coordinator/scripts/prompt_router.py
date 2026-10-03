#!/usr/bin/env python3
"""
GabeBrain Prompt Router Coordinator
Motor de decisão e coordenação de prompts para orquestração tripartite:
Arena AI (Nuvem P1) vs Antigravity (Local P2) vs Claude Code (Terminal P3).

Regra da Arena AI: só para projetos estritamente na nuvem (repositório GitHub). Qualquer prompt
que mexa em arquivos locais do GabeBrain (vault, skills, agentes, plugin, pastas do computador)
vai para Antigravity ou Claude Code, porque a Arena não edita o disco local. Sem indício de
nuvem/repositório, o padrão também deixa de ser a Arena.

As regras vivem em ../routing_rules.json (fonte única, também lida pelo GabeBrain Hub).
"""

import sys
import re
import json
import argparse
from pathlib import Path

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

RULES_FILE = Path(__file__).resolve().parent.parent / "routing_rules.json"
LABELS = {"arena": "Arena AI", "antigravity": "Antigravity", "claude": "Claude Code"}


def load_rules(path: Path = RULES_FILE) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        raise SystemExit(f"Falha ao carregar regras de roteamento em {path}: {e}")


RULES = load_rules()


def _matches(patterns, text):
    return [p for p in patterns if re.search(p, text, re.IGNORECASE)]


def _result(target, current, reason, model, confidence, category, capabilities, handoff=None):
    return {
        "target_agent": target,
        "target_label": LABELS[target],
        "current_agent": current,
        "handoff_required": (target != current) if handoff is None else handoff,
        "reason": reason,
        "recommended_model": model,
        "confidence": confidence,
        "category": category,
        "capabilities_needed": capabilities,
    }


def evaluate_prompt(prompt: str, current_agent: str = "arena", history: str = "", rules: dict = RULES) -> dict:
    """
    Avalia a demanda do prompt no contexto da conversa e determina
    o agente ideal e se um Handoff dinâmico é necessário.
    """
    clean_p = (prompt or "").strip()
    clean_curr = (current_agent or "arena").strip().lower()
    local, claude, arena = rules["local"], rules["claude"], rules["arena"]

    # 1. Execução local estrita (Antigravity P2)
    if _matches(local["patterns"], clean_p):
        reason = next(
            (r["reason"] for r in local["reasons"] if re.search(r["when"], clean_p, re.IGNORECASE)),
            local["default_reason"],
        )
        return _result("antigravity", clean_curr, reason, local["model"], 0.96,
                       "LOCAL_EXECUTION", ["localhost", "local_files", "system_process"])

    # 2. Raciocínio analítico / terminal (Claude Code P3)
    if _matches(claude["patterns"], clean_p):
        return _result("claude", clean_curr, claude["reason"], claude["model"], 0.94,
                       "ANALYTICAL_TERMINAL", ["deep_reasoning", "interactive_terminal", "tdd"])

    explicit_cloud = bool(_matches(arena["patterns"], clean_p))
    local_harness = "claude" if clean_curr == "claude" else "antigravity"
    local_model = claude["model"] if local_harness == "claude" else local["model"]

    # 3. Nuvem explícita (GitHub, PR, "na nuvem"): Arena AI
    if explicit_cloud:
        return _result("arena", clean_curr, arena["reason"], arena["model"], 0.92,
                       "CLOUD_GITHUB", ["github", "cloud_container"])

    # 4. Arquivos locais do GabeBrain (vault, skills, agentes, plugin, pastas): a Arena não edita o disco local
    if _matches(local.get("soft_patterns", []), clean_p):
        return _result(local_harness, clean_curr, local["soft_reason"], local_model, 0.93,
                       "LOCAL_GABEBRAIN_FILES", ["local_files", "write_access"])

    # 5. Tarefa de repositório/código sem nada local: projeto na nuvem, Arena AI (P1)
    if _matches(arena.get("repo_patterns", []), clean_p):
        return _result("arena", clean_curr, arena["reason"], arena["model"], 0.85,
                       "CLOUD_GITHUB", ["github", "cloud_container"])

    # 6. Sem indício de projeto na nuvem: Claude Code ou Antigravity (nunca Arena por padrão)
    return _result(local_harness, clean_curr, arena["no_cloud_reason"], local_model, 0.80,
                   "NO_CLOUD_EVIDENCE", ["local_files"], handoff=(local_harness != clean_curr))


def run_tests():
    """Bateria de testes de validação para o roteador de prompts."""
    test_cases = [
        ("ok, agora suba o servidor local na porta 3000 para eu testar a interface", "arena", "antigravity", True),
        ("execute o teste local com npm run dev para ver se compila", "arena", "antigravity", True),
        ("consulte na biblioteca geológica a cota 10-Trabalho sobre hidrogeologia", "arena", "antigravity", True),
        ("crie um componente React no repositório licenciamentoambiental com os botões de ação", "arena", "arena", False),
        ("faça um refactoring analítico rigoroso usando TDD no terminal", "arena", "claude", True),
        ("continue ajustando o texto", "antigravity", "antigravity", False),
        ("agora faça o push para github", "antigravity", "arena", True),
        ("edite a skill groq do gabebrain e atualize o script", "arena", "antigravity", True),
        ("ajuste o plugin gabebrain-hub no vault do obsidian", "arena", "antigravity", True),
        ("salve o relatório em C:\\GabeBrain\\GabeBrain\\notas", "arena", "antigravity", True),
        ("atualize o README do repositório gabebrain-skills no github", "antigravity", "arena", True),
        ("refatore o código da API no repositório licenciamentoambiental", "antigravity", "arena", True),
        ("explique o que é krigagem", "arena", "antigravity", True),
        ("mantenha a sessão e continue com o texto", "claude", "claude", False),
    ]

    print("\n--- INICIANDO BATERIA DE TESTES DO PROMPT ROUTER COORDINATOR ---")
    all_passed = True
    for idx, (prompt, curr, expected_target, expected_handoff) in enumerate(test_cases, 1):
        res = evaluate_prompt(prompt, current_agent=curr)
        passed = res["target_agent"] == expected_target and res["handoff_required"] == expected_handoff
        status = "✓ PASSOU" if passed else "✗ FALHOU"
        print(f"[{idx}] {status} | Prompt: \"{prompt[:45]}...\"")
        print(f"    Target: {res['target_agent']} (Esperado: {expected_target}) | Handoff: {res['handoff_required']}")
        print(f"    Motivo: {res['reason']}")
        all_passed = all_passed and passed

    print("---------------------------------------------------------------")
    print("✓ TODOS OS TESTES PASSARAM COM SUCESSO!\n" if all_passed else "✗ ALGUNS TESTES FALHARAM.\n")
    return all_passed


def main():
    parser = argparse.ArgumentParser(description="GabeBrain Prompt Router Coordinator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    eval_p = subparsers.add_parser("evaluate", help="Avalia o prompt e determina o agente ideal e necessidade de handoff")
    eval_p.add_argument("--prompt", required=True, help="Texto do prompt")
    eval_p.add_argument("--current-agent", default="arena", help="Agente atual da sessão (arena, antigravity, claude)")
    eval_p.add_argument("--history", default="", help="Histórico prévio da conversa (opcional)")

    subparsers.add_parser("test", help="Executa testes unitários de validação")

    args = parser.parse_args()

    if args.command == "evaluate":
        res = evaluate_prompt(args.prompt, current_agent=args.current_agent, history=args.history)
        print(json.dumps(res, ensure_ascii=False, indent=2))

    elif args.command == "test":
        sys.exit(0 if run_tests() else 1)


if __name__ == "__main__":
    main()
