#!/usr/bin/env python3
"""Funil antes do LLM: codigo corta o grosso, o Jev tria o resto, so o que sobra vai para o modelo.

Camada 1 (codigo, gratis e deterministica): regras de regras.yaml/json sobre uma lista de candidatos
    (JSONL, JSON ou CSV): campos obrigatorios, dominios, janela de datas, limites numericos, palavras,
    duplicatas por URL normalizada, ordenacao e limite.
Camada 2 (Jev, opcional, centavos): uma pergunta sim/nao por item (--jev-pergunta). P >= limiar aprova,
    P <= 1-limiar descarta, o meio fica marcado `_funil_incerto` para o agente decidir.
Camada 3 (LLM): fora deste script; o agente le so o arquivo de saida.

Uso:
    python funil.py --entrada candidatos.jsonl --regras regras.yaml --saida aprovados.jsonl \
        [--jev-pergunta "Trata de recarga de aquifero?" --jev-campos titulo,resumo --jev-limiar 0.7]
Grava tambem <saida>.relatorio.json com quantos itens cada regra cortou.
Privacidade: a camada Jev envia o texto para fora do computador; use so com dados publicos.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import re
import sys
import unicodedata
import urllib.request
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import parse_qsl, urlencode, urlsplit

Item = dict[str, Any]
JEV_SCRIPT = Path.home() / ".claude" / "skills" / "jev" / "scripts" / "jev.py"
JEV_TIMEOUT_S = 20
JEV_STATE_CHARS = 2000
KNOWN_RULES = {"campos_obrigatorios", "dominios_permitidos", "dominios_bloqueados", "data", "numeros",
               "palavras", "dedupe", "ordenar", "limite"}
TRACKING_PARAMS = re.compile(r"^(utm_\w+|fbclid|gclid|ref|si|feature)$", re.IGNORECASE)


# ---------- normalizacao ----------

def fold(text: Any) -> str:
    """Minusculas e sem acento, para comparar palavras."""
    raw = unicodedata.normalize("NFKD", str(text or ""))
    return "".join(c for c in raw if not unicodedata.combining(c)).casefold()


def normalize_url(url: str) -> str:
    parts = urlsplit(str(url).strip())
    host = parts.netloc.lower().removeprefix("www.")
    query = urlencode(sorted((k, v) for k, v in parse_qsl(parts.query) if not TRACKING_PARAMS.match(k)))
    path = parts.path.rstrip("/")
    return f"{host}{path}" + (f"?{query}" if query else "")


def host_of(url: Any) -> str:
    return urlsplit(str(url or "").strip()).netloc.lower().split(":")[0].removeprefix("www.")


def domain_matches(url: Any, domains: Iterable[str]) -> bool:
    host = host_of(url)
    return any(host == d or host.endswith("." + d) for d in (x.lower().removeprefix("www.") for x in domains))


def to_number(value: Any) -> float | None:
    """Aceita 42, '1.200.000', '1,200.5', '2,5'. Devolve None se nao for numero."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return value
    text = re.sub(r"\s", "", str(value or ""))
    if not re.fullmatch(r"-?[\d.,]+", text):
        return None
    if "," in text and "." in text:
        decimal = "," if text.rfind(",") > text.rfind(".") else "."
        text = text.replace("." if decimal == "," else ",", "").replace(decimal, ".")
    elif "," in text:
        text = text.replace(",", ".") if text.count(",") == 1 else text.replace(",", "")
    elif text.count(".") > 1 or re.fullmatch(r"-?\d{1,3}\.\d{3}", text):
        text = text.replace(".", "")
    try:
        number = float(text)
    except ValueError:
        return None
    return int(number) if number.is_integer() else number


def to_date(value: Any) -> date | None:
    text = str(value or "").strip()[:10]
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


# ---------- camada 1: codigo ----------

def first_failure(item: Item, rules: dict[str, Any]) -> str | None:
    """Nome da primeira regra que corta o item, ou None se ele passa."""
    for field in rules.get("campos_obrigatorios", []):
        if item.get(field) in (None, ""):
            return "campos_obrigatorios"
    url_field = rules.get("dedupe") or "url"
    if rules.get("dominios_permitidos") and not domain_matches(item.get(url_field), rules["dominios_permitidos"]):
        return "dominios_permitidos"
    if rules.get("dominios_bloqueados") and domain_matches(item.get(url_field), rules["dominios_bloqueados"]):
        return "dominios_bloqueados"
    if "data" in rules:
        cfg = rules["data"]
        when = to_date(item.get(cfg.get("campo", "data")))
        since, until = to_date(cfg.get("desde")), to_date(cfg.get("ate"))
        if when is None or (since and when < since) or (until and when > until):
            return "data"
    for field, bounds in rules.get("numeros", {}).items():
        number = to_number(item.get(field))
        if number is None or ("min" in bounds and number < bounds["min"]) or (
                "max" in bounds and number > bounds["max"]):
            return f"numeros.{field}"
    words = rules.get("palavras")
    if words:
        text = fold(" ".join(str(item.get(f, "")) for f in words.get("campos", [])))
        if not all(fold(w) in text for w in words.get("todas", [])):
            return "palavras.todas"
        if words.get("alguma") and not any(fold(w) in text for w in words["alguma"]):
            return "palavras.alguma"
        if any(fold(w) in text for w in words.get("nenhuma", [])):
            return "palavras.nenhuma"
    return None


def apply_rules(items: list[Item], rules: dict[str, Any]) -> tuple[list[Item], dict[str, Any]]:
    unknown = set(rules) - KNOWN_RULES
    if unknown:
        raise ValueError(f"regra desconhecida: {', '.join(sorted(unknown))} (validas: {', '.join(sorted(KNOWN_RULES))})")
    cuts: dict[str, int] = {}
    kept: list[Item] = []
    seen: set[str] = set()
    for item in items:
        reason = first_failure(item, rules)
        if reason is None and rules.get("dedupe"):
            key = normalize_url(item.get(rules["dedupe"], ""))
            reason = "dedupe" if key in seen else None
            seen.add(key)
        if reason:
            cuts[reason] = cuts.get(reason, 0) + 1
        else:
            kept.append(item)
    order = rules.get("ordenar")
    if order:
        missing = float("-inf") if order.get("desc", True) else float("inf")
        kept.sort(key=lambda i: to_number(i.get(order["campo"])) if to_number(i.get(order["campo"])) is not None
                  else missing, reverse=order.get("desc", True))
    limit = rules.get("limite")
    if limit is not None and len(kept) > limit:
        cuts["limite"] = len(kept) - limit
        kept = kept[:limit]
    return kept, {"entrada": len(items), "saida": len(kept), "cortes": cuts}


# ---------- camada 2: Jev ----------

def load_jev():
    spec = importlib.util.spec_from_file_location("jev_client", JEV_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def ask_jev(jev, key: str, state: dict[str, Any], questions: dict[str, Any]) -> dict[str, Any]:
    body = json.dumps({"state": state, "model": jev.MODEL, "questions": questions}).encode()
    request = urllib.request.Request(jev.ENDPOINT, data=body, method="POST",
                                     headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=JEV_TIMEOUT_S) as resp:
        return json.loads(resp.read())


def jev_triage(items: list[Item], question: str, fields: list[str],
               threshold: float = 0.7) -> tuple[list[Item], dict[str, Any]]:
    """Uma pergunta sim/nao por item. Sem chave ou com erro, o item passa (o Jev nunca descarta por falha)."""
    report = {"entrada": len(items), "aprovados": 0, "incertos": 0, "descartados": 0, "erros": 0}
    try:
        jev = load_jev()
        key = jev.load_key()
    except (OSError, AttributeError, SyntaxError) as err:
        return items, {**report, "indisponivel": f"nao carreguei o jev.py ({err})"}
    if not key:
        return items, {**report, "indisponivel": "sem TYPESAFE_API_KEY"}
    questions = {"relevante": {"type": "noul", "instructions": question}}
    kept: list[Item] = []
    for item in items:
        state = {f: str(item.get(f, ""))[:JEV_STATE_CHARS] for f in fields}
        try:
            response = ask_jev(jev, key, state, questions)
            if hasattr(jev, "record_usage"):
                jev.record_usage(response.get("usage", {}))
            prob = float(response["answers"]["relevante"]["noul"])
        except (OSError, KeyError, ValueError, TypeError) as err:
            report["erros"] += 1
            kept.append({**item, "_funil_incerto": True, "_funil_erro": str(err)[:120]})
            continue
        if prob >= threshold:
            report["aprovados"] += 1
            kept.append({**item, "_funil_jev": round(prob, 3)})
        elif prob <= 1 - threshold:
            report["descartados"] += 1
        else:
            report["incertos"] += 1
            kept.append({**item, "_funil_jev": round(prob, 3), "_funil_incerto": True})
    return kept, report


# ---------- entrada e saida ----------

def read_items(path: Path) -> list[Item]:
    text = path.read_text(encoding="utf-8-sig")
    if path.suffix.lower() == ".csv":
        return list(csv.DictReader(text.splitlines()))
    if path.suffix.lower() == ".jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    data = json.loads(text)
    return data if isinstance(data, list) else data.get("itens") or data.get("items") or []


def read_rules(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8-sig")
    if path.suffix.lower() in (".yaml", ".yml"):
        import yaml  # so quando as regras vierem em YAML
        return yaml.safe_load(text) or {}
    return json.loads(text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--entrada", required=True, type=Path)
    parser.add_argument("--regras", type=Path, help="regras.yaml ou .json (sem regras: so o Jev, se pedido)")
    parser.add_argument("--saida", required=True, type=Path)
    parser.add_argument("--jev-pergunta", help="pergunta sim/nao para a triagem (dados publicos apenas)")
    parser.add_argument("--jev-campos", default="titulo,resumo", help="campos enviados ao Jev, separados por virgula")
    parser.add_argument("--jev-limiar", type=float, default=0.7)
    args = parser.parse_args(argv)

    items = read_items(args.entrada)
    kept, report_code = apply_rules(items, read_rules(args.regras) if args.regras else {})
    report: dict[str, Any] = {"codigo": report_code}
    if args.jev_pergunta:
        kept, report["jev"] = jev_triage(kept, args.jev_pergunta, args.jev_campos.split(","), args.jev_limiar)

    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text("".join(json.dumps(i, ensure_ascii=False) + "\n" for i in kept), encoding="utf-8")
    report["saida_final"] = len(kept)
    report_path = args.saida.with_name(args.saida.stem + ".relatorio.json")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"funil: {len(items)} -> codigo {report_code['saida']}"
          + (f" -> jev {len(kept)}" if "jev" in report else "") + f" | relatorio: {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
