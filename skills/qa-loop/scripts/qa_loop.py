#!/usr/bin/env python3
"""qa-loop: portoes deterministicos + pontuacao Jev + decisao LIMITADA do loop gerador->avaliador.

Principios (ver SKILL.md):
  1. Medir antes de opinar: testes, compilacao, schema e segredos rodam de verdade (gates).
  2. Jev pontua pilares e vetos (barato); o agente so decide o que o Jev marcar INCERTO.
  3. O loop NUNCA e infinito: teto de iteracoes, estagnacao e veto sao codigo, nao convencao.

Comandos:
  gates  --paths A B ... [--test-cmd "pytest -q"] [--out gates.json]
  score  --rubric dev|geo|ciencia --spec-file S --artifact-file A [--gates gates.json]
         [--privado] [--override pilar=0.8 ...] [--out score.json]
  decide --history-file H.json --score score.json [--max-iter 3]
  validate --file saida.json
"""
from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

APPROVAL_SCORE = 85.0
DEFAULT_MAX_ITERATIONS = 3
HARD_MAX_ITERATIONS = 5          # teto absoluto: --max-iter acima disso e recusado
STALL_MIN_GAIN = 3.0             # ganho minimo de nota entre rodadas consecutivas
JEV_THRESHOLD = 0.7              # abaixo disso o agente decide (regra do ecossistema)
VETO_P = 0.7                     # P(sim) a partir da qual o veto do Jev vale
ARTIFACT_CHAR_LIMIT = 12_000
GATE_TIMEOUT_S = 120
SKILL_DIR = Path(__file__).resolve().parent.parent
JEV_SCRIPT = SKILL_DIR.parent / "jev" / "scripts" / "jev.py"

SECRET_PATTERNS = (
    re.compile(r"(?i)(api[_-]?key|secret|token|passwd|password)\s*[=:]\s*['\"][A-Za-z0-9_\-./+=]{16,}['\"]"),
    re.compile(r"\b(sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16})\b"),
    re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"),
)
REQUIRED_OUTPUT = {"nota_final": (int, float), "status": str,
                   "analise_breve": str, "feedbacks_de_correcao": list}
VALID_STATUS = {"APROVADO", "REPROVADO", "ESCALAR", "PENDENTE_AGENTE"}


@dataclass(frozen=True)
class Gate:
    name: str
    passed: bool
    critical: bool
    detail: str

    def as_dict(self) -> dict[str, Any]:
        return {"name": self.name, "passed": self.passed,
                "critical": self.critical, "detail": self.detail}


# ----------------------------------------------------------------- gates

def gate_compile(path: Path) -> Gate:
    try:
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
    except (SyntaxError, ValueError) as err:
        return Gate(f"compile:{path.name}", False, True, str(err))
    return Gate(f"compile:{path.name}", True, True, "ok")


def gate_json(path: Path) -> Gate:
    try:
        json.loads(path.read_text(encoding="utf-8-sig"))
    except ValueError as err:
        return Gate(f"json:{path.name}", False, True, str(err))
    return Gate(f"json:{path.name}", True, True, "ok")


def gate_secrets(path: Path) -> Gate:
    text = path.read_text(encoding="utf-8", errors="replace")
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            return Gate(f"segredo:{path.name}", False, True, "padrao de segredo/token encontrado")
    return Gate(f"segredo:{path.name}", True, True, "ok")


def gate_tests(command: str, cwd: Path | None = None) -> Gate:
    try:
        result = subprocess.run(shlex.split(command), capture_output=True, text=True,
                                timeout=GATE_TIMEOUT_S, cwd=cwd, check=False)
    except (OSError, subprocess.TimeoutExpired) as err:
        return Gate("testes", False, True, f"nao executou: {err}")
    tail = (result.stdout + result.stderr).strip().splitlines()[-3:]
    return Gate("testes", result.returncode == 0, True, " | ".join(tail) or f"exit {result.returncode}")


def run_gates(paths: list[Path], test_cmd: str | None = None) -> list[Gate]:
    gates: list[Gate] = []
    for path in paths:
        if not path.is_file():
            gates.append(Gate(f"existe:{path.name}", False, True, "arquivo inexistente"))
            continue
        if path.suffix == ".py":
            gates.append(gate_compile(path))
        elif path.suffix == ".json":
            gates.append(gate_json(path))
        if path.suffix in {".py", ".js", ".ts", ".json", ".md", ".env", ".yaml", ".yml", ".toml"}:
            gates.append(gate_secrets(path))
    if test_cmd:
        gates.append(gate_tests(test_cmd))
    return gates


# --------------------------------------------------------------- rubricas

def load_rubric(name: str) -> dict[str, Any]:
    path = SKILL_DIR / "rubricas" / f"{name}.json"
    if not path.is_file():
        raise SystemExit(f"Rubrica inexistente: {name} (use dev, geo ou ciencia)")
    rubric = json.loads(path.read_text(encoding="utf-8"))
    total = sum(p["peso"] for p in rubric["pilares"])
    if abs(total - 100) > 1e-6:
        raise SystemExit(f"Rubrica {name}: pesos somam {total}, esperado 100")
    return rubric


def build_questions(rubric: dict[str, Any]) -> dict[str, Any]:
    questions: dict[str, Any] = {
        p["id"]: {"type": "score", "instructions": p["pergunta"], "criteria": p["criterios"]}
        for p in rubric["pilares"]
    }
    for veto in rubric.get("vetos", []):
        questions[f"veto_{veto['id']}"] = {"type": "noul", "instructions": veto["pergunta"]}
    return questions


def build_state(spec: str, artifact: str, gates: list[dict[str, Any]]) -> str:
    evidence = "\n".join(f"- [{'OK' if g['passed'] else 'FALHOU'}] {g['name']}: {g['detail']}"
                         for g in gates) or "- (nenhum gate executado)"
    clipped = artifact[:ARTIFACT_CHAR_LIMIT]
    note = "" if len(artifact) <= ARTIFACT_CHAR_LIMIT else "\n[... artefato truncado ...]"
    return (f"ESPECIFICACAO E REGRAS ORIGINAIS:\n{spec}\n\n"
            f"EVIDENCIAS MEDIDAS (confiaveis, executadas de verdade):\n{evidence}\n\n"
            f"ARTEFATO ENTREGUE:\n{clipped}{note}")


# -------------------------------------------------------------------- Jev

def ask_jev(state: str, questions: dict[str, Any]) -> dict[str, Any]:
    """Chama o jev.py existente (uma unica chamada, varias perguntas = barato)."""
    with tempfile.TemporaryDirectory() as tmp:
        state_file, q_file = Path(tmp) / "state.txt", Path(tmp) / "q.json"
        state_file.write_text(state, encoding="utf-8")
        q_file.write_text(json.dumps(questions, ensure_ascii=False), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(JEV_SCRIPT), "ask", "--state-file", str(state_file),
             "--questions", str(q_file), "--threshold", str(JEV_THRESHOLD), "--json"],
            capture_output=True, text=True, timeout=90, check=False)
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout).strip() or "jev.py falhou")
    return json.loads(result.stdout)


PRIVATE_PATTERNS = {
    "cpf": re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b"),
    "cnpj": re.compile(r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b"),
    "email": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
    "telefone": re.compile(r"\(?\b\d{2}\)?\s?9?\d{4}-?\d{4}\b"),
    "processo": re.compile(r"(?i)\b(processo|protocolo|matr[ií]cula|requerente)\b.{0,20}\d"),
}
RUBRIC_CHOICES = {
    "dev": "Codigo, scripts, testes, configuracao de software",
    "geo": "Laudo, hidrologia, GIS, geologia, licenciamento ambiental, dados tecnicos numericos",
    "ciencia": "Texto academico, artigo, revisao de literatura, sintese de pesquisa",
}
CLASSIFY_QUESTIONS: dict[str, Any] = {
    "rubrica": {"type": "choice", "instructions": "Que tipo de entrega e esta?",
                "criteria": RUBRIC_CHOICES},
    "trivial": {"type": "noul", "instructions":
                "Esta entrega e trivial (ajuste de poucas linhas, texto curto, sem logica nova), "
                "dispensando um ciclo de revisao?"},
}


def looks_private(text: str) -> list[str]:
    """Heuristica LOCAL (nada sai do computador): categorias de dado pessoal/de processo encontradas."""
    return [name for name, pattern in PRIVATE_PATTERNS.items() if pattern.search(text)]


def classify_with_jev(response: dict[str, Any]) -> dict[str, Any]:
    answers = response.get("answers", {})
    pick = answers.get("rubrica", {})
    sure = float(pick.get("confidence", 0.0)) >= JEV_THRESHOLD
    p_trivial = float(answers.get("trivial", {}).get("noul", 0.0))
    return {"rubrica": pick.get("choice") if sure else None, "rubrica_incerta": not sure,
            "trivial": p_trivial >= VETO_P, "p_trivial": round(p_trivial, 2),
            "custo_usd": response.get("cost_usd", 0.0)}


def pillar_fraction(answer: dict[str, Any], levels: int) -> tuple[float, bool]:
    """Nota continua do Jev (0..n-1) -> fracao 0..1; True se a confianca basta."""
    fraction = max(0.0, min(1.0, float(answer["score"]) / (levels - 1)))
    return fraction, float(answer.get("confidence", 0.0)) >= JEV_THRESHOLD


def score_with_jev(rubric: dict[str, Any], response: dict[str, Any],
                   overrides: dict[str, float]) -> dict[str, Any]:
    answers = response.get("answers", {})
    pillars: list[dict[str, Any]] = []
    for p in rubric["pilares"]:
        override = overrides.get(p["id"])
        if override is not None:
            fraction, certain, source = override, True, "agente"
        elif p["id"] in answers:
            fraction, certain = pillar_fraction(answers[p["id"]], len(p["criterios"]))
            source = "jev"
        else:
            fraction, certain, source = 0.0, False, "ausente"
        pillars.append({"id": p["id"], "peso": p["peso"], "fracao": round(fraction, 3),
                        "pontos": round(p["peso"] * fraction, 1), "fonte": source,
                        "incerto": not certain})
    vetos, vetos_incertos = [], []
    for v in rubric.get("vetos", []):
        answer = answers.get(f"veto_{v['id']}")
        if answer is None:
            continue
        p_yes = float(answer["noul"])
        if p_yes >= VETO_P:
            vetos.append(v["id"])
        elif p_yes > 1 - VETO_P:
            vetos_incertos.append(v["id"])
    return {"pilares": pillars, "vetos_jev": vetos, "vetos_incertos": vetos_incertos,
            "nota": round(sum(x["pontos"] for x in pillars), 1),
            "custo_usd": response.get("cost_usd", 0.0)}


def fallback_scoring(rubric: dict[str, Any]) -> dict[str, Any]:
    """Modo --privado ou Jev indisponivel: nada sai do computador; o agente pontua tudo."""
    pillars = [{"id": p["id"], "peso": p["peso"], "fracao": 0.0, "pontos": 0.0,
                "fonte": "ausente", "incerto": True} for p in rubric["pilares"]]
    return {"pilares": pillars, "vetos_jev": [], "vetos_incertos": [], "nota": 0.0, "custo_usd": 0.0}


# ---------------------------------------------------------------- decisao

def decide(history: list[dict[str, Any]], max_iter: int = DEFAULT_MAX_ITERATIONS) -> dict[str, Any]:
    """Decide a proxima acao. Sempre termina: aprova, reprova com nova rodada ou escala ao Gabriel."""
    limit = min(max(max_iter, 1), HARD_MAX_ITERATIONS)
    if not history:
        raise ValueError("historico vazio")
    current = history[-1]
    round_no = len(history)
    if current.get("pendente"):
        return {"status": "PENDENTE_AGENTE", "motivo": "pilares incertos: agente deve pontuar (--override)"}
    if current["veto"]:
        verdict = "REPROVADO"
    elif current["nota"] >= APPROVAL_SCORE:
        return {"status": "APROVADO", "motivo": f"nota {current['nota']} >= {APPROVAL_SCORE}", "iteracao": round_no}
    else:
        verdict = "REPROVADO"
    if round_no >= limit:
        return {"status": "ESCALAR", "motivo": f"limite de {limit} iteracoes atingido", "iteracao": round_no}
    if round_no >= 2 and current["nota"] - history[-2]["nota"] < STALL_MIN_GAIN:
        return {"status": "ESCALAR", "iteracao": round_no,
                "motivo": f"estagnou: ganho < {STALL_MIN_GAIN} pontos entre rodadas"}
    return {"status": verdict, "motivo": "veto ativo" if current["veto"] else "abaixo do limiar",
            "iteracao": round_no, "proxima_iteracao": round_no + 1, "restantes": limit - round_no}


def validate_output(data: dict[str, Any]) -> list[str]:
    errors = [f"campo ausente ou tipo errado: {k}" for k, t in REQUIRED_OUTPUT.items()
              if not isinstance(data.get(k), t)]
    if not errors:
        if data["status"] not in VALID_STATUS:
            errors.append(f"status invalido: {data['status']}")
        if not 0 <= data["nota_final"] <= 100:
            errors.append("nota_final fora de 0..100")
        if data["status"] == "REPROVADO" and not data["feedbacks_de_correcao"]:
            errors.append("REPROVADO exige feedbacks_de_correcao")
    return errors


# -------------------------------------------------------------------- CLI

def _parse_overrides(items: list[str]) -> dict[str, float]:
    out: dict[str, float] = {}
    for item in items:
        key, _, value = item.partition("=")
        fraction = float(value)
        if not key or not 0 <= fraction <= 1:
            raise SystemExit(f"--override invalido: {item} (use pilar=0..1)")
        out[key] = fraction
    return out


def cmd_gates(args: argparse.Namespace) -> int:
    gates = run_gates([Path(p) for p in args.paths], args.test_cmd)
    payload = {"gates": [g.as_dict() for g in gates],
               "veto": any(g.critical and not g.passed for g in gates)}
    _emit(payload, args.out)
    return 0


def _may_send(args: argparse.Namespace, *texts: str) -> tuple[bool, str]:
    """Guarda de privacidade: so envia ao Jev sem --privado, sem dado sensivel ou com autorizacao."""
    if args.privado:
        return False, "agente (privado)"
    found = looks_private("\n".join(texts))
    if found and not args.autorizado_privado:
        print(f"aviso: possivel dado privado ({', '.join(found)}); nada enviado ao Jev. "
              "Pergunte ao Gabriel e, se ele autorizar, use --autorizado-privado.", file=sys.stderr)
        return False, "agente (privado detectado)"
    return True, "jev"


def cmd_classify(args: argparse.Namespace) -> int:
    text = Path(args.artifact_file).read_text(encoding="utf-8", errors="replace")
    allowed, modo = _may_send(args, text)
    if not allowed:
        _emit({"rubrica": None, "rubrica_incerta": True, "trivial": False, "modo": modo}, None)
        return 0
    try:
        payload = {**classify_with_jev(ask_jev(text[:ARTIFACT_CHAR_LIMIT], CLASSIFY_QUESTIONS)), "modo": modo}
    except (RuntimeError, ValueError, OSError, subprocess.TimeoutExpired) as err:
        print(f"aviso: Jev indisponivel ({err})", file=sys.stderr)
        payload = {"rubrica": None, "rubrica_incerta": True, "trivial": False, "modo": "agente (jev indisponivel)"}
    _emit(payload, None)
    return 0


def cmd_score(args: argparse.Namespace) -> int:
    rubric = load_rubric(args.rubric)
    gates = json.loads(Path(args.gates).read_text(encoding="utf-8")) if args.gates else {"gates": [], "veto": False}
    overrides = _parse_overrides(args.override)
    result = fallback_scoring(rubric)
    spec = Path(args.spec_file).read_text(encoding="utf-8")
    artifact = Path(args.artifact_file).read_text(encoding="utf-8", errors="replace")
    allowed, modo = _may_send(args, spec, artifact)
    if allowed:
        state = build_state(spec, artifact, gates["gates"])
        try:
            result = score_with_jev(rubric, ask_jev(state, build_questions(rubric)), overrides)
        except (RuntimeError, ValueError, OSError, subprocess.TimeoutExpired) as err:
            print(f"aviso: Jev indisponivel ({err}); o agente pontua", file=sys.stderr)
            modo = "agente (jev indisponivel)"
    if modo.startswith("agente"):
        result = score_with_jev(rubric, {"answers": {}}, overrides)
    failed = [g["name"] for g in gates["gates"] if g["critical"] and not g["passed"]]
    pending = [p["id"] for p in result["pilares"] if p["incerto"]]
    payload = {**result, "modo": modo, "veto": bool(failed or result["vetos_jev"]),
               "vetos_gates": failed, "pendente": pending}
    _emit(payload, args.out)
    return 0


def cmd_decide(args: argparse.Namespace) -> int:
    path = Path(args.history_file)
    history = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else []
    score = json.loads(Path(args.score).read_text(encoding="utf-8"))
    history = [*history, {"nota": score["nota"], "veto": score["veto"], "pendente": bool(score["pendente"])}]
    decision = decide(history, args.max_iter)
    if decision["status"] != "PENDENTE_AGENTE":
        path.write_text(json.dumps(history, indent=2), encoding="utf-8")
    _emit({**decision, "nota": score["nota"]}, None)
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    errors = validate_output(json.loads(Path(args.file).read_text(encoding="utf-8")))
    print(json.dumps({"valido": not errors, "erros": errors}, ensure_ascii=False))
    return 1 if errors else 0


def _emit(payload: dict[str, Any], out: str | None) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if out:
        Path(out).write_text(text, encoding="utf-8")
    print(text)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="qa-loop: loop de qualidade limitado.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gates")
    g.add_argument("--paths", nargs="+", required=True)
    g.add_argument("--test-cmd")
    g.add_argument("--out")
    g.set_defaults(func=cmd_gates)
    s = sub.add_parser("score")
    s.add_argument("--rubric", required=True)
    s.add_argument("--spec-file", required=True)
    s.add_argument("--artifact-file", required=True)
    s.add_argument("--gates")
    s.add_argument("--privado", action="store_true")
    s.add_argument("--autorizado-privado", action="store_true",
                   help="so apos o Gabriel autorizar enviar material sensivel ao Jev")
    s.add_argument("--override", nargs="*", default=[])
    s.add_argument("--out")
    s.set_defaults(func=cmd_score)
    c = sub.add_parser("classify")
    c.add_argument("--artifact-file", required=True)
    c.add_argument("--privado", action="store_true")
    c.add_argument("--autorizado-privado", action="store_true")
    c.set_defaults(func=cmd_classify)
    d = sub.add_parser("decide")
    d.add_argument("--history-file", required=True)
    d.add_argument("--score", required=True)
    d.add_argument("--max-iter", type=int, default=DEFAULT_MAX_ITERATIONS)
    d.set_defaults(func=cmd_decide)
    v = sub.add_parser("validate")
    v.add_argument("--file", required=True)
    v.set_defaults(func=cmd_validate)
    return parser


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
