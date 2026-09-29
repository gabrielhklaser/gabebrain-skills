#!/usr/bin/env python3
"""Cliente da API Jev (TypeSafe System One) - decide, nao escreve.

Sem dependencias externas. Chave lida de (nesta ordem):
  1. variavel de ambiente TYPESAFE_API_KEY
  2. <pasta da skill>/.env  (fora do Git e do vault; ver sync_gabebrain.py)

Comandos:
  setup                      pede a chave (oculta) e grava no .env da skill
  status                     diz se ha chave configurada (nunca a mostra)
  balance [--set USD]        saldo ESTIMADO (livro-caixa local); --set recalibra
  ask --state-file F --questions Q.json [--threshold 0.7] [--json]
  ask --state "texto" --questions Q.json
  selftest                   teste real com um e-mail de vendas ficticio

Formato de Q.json (chaves livres):
  {"lead": {"type": "score", "instructions": "...", "criteria": ["ruim", "medio", "bom"]},
   "tipo": {"type": "choice", "instructions": "...", "criteria": {"a": "desc", "b": "desc"}},
   "precisa": {"type": "noul", "instructions": "..."}}
"""
from __future__ import annotations

import argparse
import getpass
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ENDPOINT = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-latest"
KEY_VAR = "TYPESAFE_API_KEY"
DEFAULT_THRESHOLD = 0.7  # heuristica do GabeBrain: abaixo disso, quem decide e o agente
MAX_RETRIES = 3
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"

# Livro-caixa local: a API da TypeSafe nao expoe saldo (sem endpoint/cabecalho), entao o saldo
# e ESTIMADO = credito inicial - gasto calculado pelos tokens que a propria API reporta.
# Fica fora do vault/Drive; o painel do GabeBrain Hub le o mesmo arquivo.
LEDGER_PATH = Path(os.environ.get("JEV_LEDGER") or (
    Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local") / "gabebrain" / "jev" / "ledger.json"))
DEFAULT_INITIAL_USD = 10.0
DEFAULT_PRICE_IN = 0.042   # US$ por 1M de tokens de entrada (cookbook da doc, jev-1.12, 2026-09)
DEFAULT_PRICE_OUT = 0.0    # saida gratuita

SELFTEST_EMAIL = (
    "Assunto: Parceria para escritorios de geologia\n\n"
    "Oi Gabriel, sou a Marina, diretora de operacoes da TerraLab (35 pessoas). "
    "Vimos seu trabalho com mapeamento hidrogeologico e queremos contratar uma "
    "consultoria de 6 meses, orcamento de ate R$ 180 mil. Podemos conversar "
    "na quinta, as 15h? Preciso fechar fornecedor ate o fim do mes."
)
SELFTEST_QUESTIONS: dict[str, Any] = {
    "lead": {
        "type": "score",
        "instructions": "Quao promissor e este lead comercial?",
        "criteria": ["Sem potencial", "Morno", "Promissor", "Excelente"],
    },
    "tipo_email": {
        "type": "choice",
        "instructions": "Que tipo de e-mail e este?",
        "criteria": {
            "venda": "Proposta ou pedido de compra/contratacao",
            "suporte": "Problema com produto ou servico existente",
            "spam": "Mensagem em massa, irrelevante ou golpe",
            "outro": "Nenhuma das anteriores",
        },
    },
    "resposta_pessoal": {
        "type": "noul",
        "instructions": "Este e-mail precisa de uma resposta pessoal (nao automatica)?",
    },
}


def clean_key(raw: str) -> str:
    """Remove controles (ex.: ^V do Ctrl+V colado no getpass) e cola duplicada."""
    key = "".join(c for c in raw if c.isprintable() and not c.isspace()).strip("\"'")
    half, odd = divmod(len(key), 2)
    if not odd and half and key[:half] == key[half:]:
        return key[:half]
    return key


def load_key() -> str | None:
    key = os.environ.get(KEY_VAR)
    if key:
        return clean_key(key)
    if ENV_PATH.is_file():
        for line in ENV_PATH.read_text(encoding="utf-8-sig").splitlines():
            name, _, value = line.partition("=")
            if name.strip() == KEY_VAR and value.strip():
                return clean_key(value)
    return None


def call_jev(state: Any, questions: dict[str, Any], key: str) -> tuple[dict, float]:
    body = json.dumps({"state": state, "model": MODEL, "questions": questions}).encode()
    request = urllib.request.Request(
        ENDPOINT,
        data=body,
        method="POST",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    for attempt in range(MAX_RETRIES + 1):
        started = time.perf_counter()
        try:
            with urllib.request.urlopen(request, timeout=30) as resp:
                return json.loads(resp.read()), time.perf_counter() - started
        except urllib.error.HTTPError as err:
            detail = err.read().decode(errors="replace")
            retryable = err.code in (429, 529)
            if retryable and attempt < MAX_RETRIES:
                time.sleep(2**attempt)  # backoff exponencial, como a doc recomenda
                continue
            raise SystemExit(f"Erro HTTP {err.code} da API Jev: {detail}")
        except urllib.error.URLError as err:
            raise SystemExit(f"Falha de rede ao chamar a API Jev: {err.reason}")
    raise SystemExit("Esgotadas as tentativas de chamada a Jev.")


def new_ledger(initial_usd: float) -> dict:
    return {
        "initial_usd": initial_usd, "spent_usd": 0.0, "calls": 0,
        "input_tokens": 0, "output_tokens": 0,
        "price_in_per_mtok": DEFAULT_PRICE_IN, "price_out_per_mtok": DEFAULT_PRICE_OUT,
        "since": time.strftime("%Y-%m-%dT%H:%M:%S"), "updated": None,
    }


def load_ledger() -> dict:
    if not LEDGER_PATH.is_file():
        return new_ledger(DEFAULT_INITIAL_USD)
    return {**new_ledger(DEFAULT_INITIAL_USD), **json.loads(LEDGER_PATH.read_text(encoding="utf-8"))}


def save_ledger(ledger: dict) -> None:
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = LEDGER_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(ledger, indent=2), encoding="utf-8")
    tmp.replace(LEDGER_PATH)  # troca atomica: o Hub nunca le arquivo pela metade


def call_cost(usage: dict, ledger: dict) -> float:
    return (usage.get("input_tokens", 0) * ledger["price_in_per_mtok"]
            + usage.get("output_tokens", 0) * ledger["price_out_per_mtok"]) / 1_000_000


def record_usage(usage: dict) -> tuple[float, dict | None]:
    """Soma a chamada ao livro-caixa. Falha de contabilidade nao derruba a classificacao."""
    try:
        ledger = load_ledger()
        cost = call_cost(usage, ledger)
        updated = {
            **ledger,
            "spent_usd": ledger["spent_usd"] + cost,
            "calls": ledger["calls"] + 1,
            "input_tokens": ledger["input_tokens"] + usage.get("input_tokens", 0),
            "output_tokens": ledger["output_tokens"] + usage.get("output_tokens", 0),
            "updated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        save_ledger(updated)
        return cost, updated
    except (OSError, ValueError, KeyError) as err:
        print(f"aviso: nao consegui atualizar o saldo local ({err})", file=sys.stderr)
        return call_cost(usage, new_ledger(DEFAULT_INITIAL_USD)), None


def balance_of(ledger: dict) -> float:
    return ledger["initial_usd"] - ledger["spent_usd"]


def summarize(answer: dict, threshold: float) -> tuple[str, bool]:
    """Devolve (texto legivel, decidido?). noul nao traz confianca: usa distancia de 0.5."""
    kind = answer.get("type")
    if kind == "choice":
        conf = answer.get("confidence", 0.0)
        return f"{answer['choice']} (confianca {conf:.2f})", conf >= threshold
    if kind == "score":
        conf = answer.get("confidence", 0.0)
        legend = answer.get("legend", {})
        label = legend.get(str(round(answer["score"])), "?")
        return f"{answer['score']:.2f} ~ {label} (confianca {conf:.2f})", conf >= threshold
    if kind == "noul":
        p = answer["noul"]
        certeza = abs(p - 0.5) * 2
        return f"P(sim)={p:.2f}", certeza >= threshold
    return json.dumps(answer, ensure_ascii=False), False


def run_ask(state: Any, questions: dict, threshold: float, as_json: bool) -> int:
    key = load_key()
    if not key:
        raise SystemExit("Sem chave. Rode: python jev.py setup")
    response, elapsed = call_jev(state, questions, key)
    usage = response.get("usage", {})
    cost, ledger = record_usage(usage)
    balance = None if ledger is None else balance_of(ledger)
    if as_json:
        out = {**response, "latency_s": round(elapsed, 3), "threshold": threshold,
               "cost_usd": cost, "balance_usd_estimated": balance}
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0
    saldo = "" if balance is None else f"  |  saldo est.: US$ {balance:.4f}"
    print(f"modelo: {response.get('model')}  |  tempo: {elapsed:.2f}s  |  "
          f"{usage.get('input_tokens', 0)} tokens in / {usage.get('output_tokens', 0)} out  |  "
          f"custo: US$ {cost:.6f}{saldo}")
    for qid, answer in response.get("answers", {}).items():
        text, decided = summarize(answer, threshold)
        flag = "" if decided else "  << INCERTO: o agente decide"
        print(f"- {qid}: {text}{flag}")
    return 0


def cmd_setup(_: argparse.Namespace) -> int:
    print("Cole a chave de https://console.typesafe.ai/keys (a digitacao fica oculta).")
    print("Dica: cole com clique direito ou Shift+Insert (Ctrl+V pode inserir caractere invisivel).")
    key = clean_key(getpass.getpass("TYPESAFE_API_KEY: "))
    if not key:
        raise SystemExit("Nada digitado; nada gravado.")
    ENV_PATH.write_text(f"{KEY_VAR}={key}\n", encoding="utf-8")
    print(f"Chave gravada em {ENV_PATH} (arquivo local, ignorado pelo Git e pelo sync do vault).")
    return 0


def cmd_status(_: argparse.Namespace) -> int:
    print("chave configurada: " + ("sim" if load_key() else "NAO (rode: python jev.py setup)"))
    return 0


def cmd_balance(args: argparse.Namespace) -> int:
    if args.set is not None:
        if args.set < 0:
            raise SystemExit("--set precisa de um valor >= 0 (saldo atual em US$).")
        save_ledger(new_ledger(args.set))  # recalibra: confira o valor real no console.typesafe.ai
        print(f"Livro-caixa recalibrado: saldo = US$ {args.set:.2f}")
        return 0
    ledger = load_ledger()
    print(f"saldo estimado: US$ {balance_of(ledger):.4f}  (inicial US$ {ledger['initial_usd']:.2f} - gasto US$ {ledger['spent_usd']:.6f})")
    print(f"{ledger['calls']} chamadas, {ledger['input_tokens']} tokens in / {ledger['output_tokens']} out  |  "
          f"preco: US$ {ledger['price_in_per_mtok']}/1M in, US$ {ledger['price_out_per_mtok']}/1M out")
    print("Estimativa local: a API nao informa saldo real. Confira em https://console.typesafe.ai e recalibre com: balance --set <USD>")
    return 0


def cmd_ask(args: argparse.Namespace) -> int:
    if bool(args.state) == bool(args.state_file):
        raise SystemExit("Use exatamente um de --state / --state-file.")
    state = args.state or Path(args.state_file).read_text(encoding="utf-8")
    questions = json.loads(Path(args.questions).read_text(encoding="utf-8"))
    return run_ask(state, questions, args.threshold, args.json)


def cmd_selftest(args: argparse.Namespace) -> int:
    print("E-mail de teste (ficticio):\n" + SELFTEST_EMAIL + "\n")
    return run_ask(SELFTEST_EMAIL, SELFTEST_QUESTIONS, args.threshold, False)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Jev: decide, nao escreve.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("setup").set_defaults(func=cmd_setup)
    sub.add_parser("status").set_defaults(func=cmd_status)
    bal = sub.add_parser("balance")
    bal.add_argument("--set", type=float, help="recalibra: define o saldo atual em US$")
    bal.set_defaults(func=cmd_balance)
    ask = sub.add_parser("ask")
    ask.add_argument("--state")
    ask.add_argument("--state-file")
    ask.add_argument("--questions", required=True)
    ask.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    ask.add_argument("--json", action="store_true")
    ask.set_defaults(func=cmd_ask)
    test = sub.add_parser("selftest")
    test.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    test.set_defaults(func=cmd_selftest)
    return parser


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
