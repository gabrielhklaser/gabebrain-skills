#!/usr/bin/env python3
"""Operario barato do GabeBrain: extracao/resumo em lote via Groq (plano gratuito).

NAO decide (isso e do Jev) e NAO recebe material privado (processos, clientes, laudos reais).
Sem dependencias externas. Chave lida de (nesta ordem):
  1. variavel de ambiente GROQ_API_KEY
  2. variavel de USUARIO do Windows (registro)
  3. <pasta da skill>/.env

Comandos:
  setup                                    pede a chave (oculta) e grava no .env da skill
  status                                   diz se ha chave (nunca a mostra)
  extract --file F --fields a,b,c          devolve JSON com exatamente esses campos
  summarize --file F [--max-words 120]     resumo curto
Opcoes comuns: --model, --json (saida crua)
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

ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
KEY_VAR = "GROQ_API_KEY"
DEFAULT_MODEL = "openai/gpt-oss-120b"
# Free tier (console.groq.com/docs/rate-limits, 2026-10-02): 30 RPM, 1K RPD, 8K TPM, 200K TPD.
MAX_INPUT_TOKENS_EST = 6000  # folga sob o teto de 8K TPM (entrada + saida)
CHARS_PER_TOKEN = 4
MIN_KEY_LEN = 20  # chaves Groq (gsk_...) tem ~56 caracteres; barra colagem truncada
MAX_RETRIES = 3
MAX_RETRY_WAIT_S = 60.0
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


class GroqError(RuntimeError):
    """Falha de configuracao, limite ou resposta invalida."""


def _read_env_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        name, sep, value = line.partition("=")
        if sep and name.strip() == KEY_VAR and value.strip():
            return value.strip().strip('"').strip("'")
    return None


def _read_user_registry() -> str | None:
    try:
        import winreg  # type: ignore[import-not-found]
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            value, _ = winreg.QueryValueEx(key, KEY_VAR)
            return value or None
    except (ImportError, OSError):
        return None


def get_key(env_path: Path | None = None) -> str:
    key = os.environ.get(KEY_VAR) or _read_user_registry() or _read_env_file(env_path or ENV_PATH)
    if not key:
        raise GroqError(f"{KEY_VAR} ausente (variavel de usuario ou .env da skill)")
    return key


def save_key(key: str, env_path: Path = ENV_PATH) -> None:
    key = key.strip()
    if not key:
        raise GroqError("chave vazia")
    if len(key) < MIN_KEY_LEN:
        raise GroqError(f"chave curta demais ({len(key)} caracteres); a colagem falhou? tente de novo")
    env_path.write_text(f"{KEY_VAR}={key}\n", encoding="utf-8")


def estimate_tokens(text: str) -> int:
    return len(text) // CHARS_PER_TOKEN + 1


def check_size(text: str) -> None:
    if estimate_tokens(text) > MAX_INPUT_TOKENS_EST:
        raise GroqError(
            f"entrada ~{estimate_tokens(text)} tokens excede {MAX_INPUT_TOKENS_EST} "
            "(limite de 8K TPM do plano gratuito); divida em blocos"
        )


def build_payload(system: str, user: str, model: str, json_mode: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": model,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    if model.startswith("openai/gpt-oss"):
        payload["reasoning_effort"] = "low"
    return payload


def _post(payload: dict[str, Any], key: str, timeout: float = 60.0) -> dict[str, Any]:
    request = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "User-Agent": "gabebrain-groq-worker/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 (https fixo)
        return json.loads(response.read().decode("utf-8"))


def call_groq(payload: dict[str, Any], key: str, post=_post, sleep=time.sleep) -> str:
    """Chama a API com retry em 429/5xx respeitando Retry-After; devolve o texto."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            body = post(payload, key)
            content = body["choices"][0]["message"]["content"]
            if not content:
                raise GroqError("resposta vazia")
            return content
        except urllib.error.HTTPError as exc:
            retryable = exc.code == 429 or exc.code >= 500
            if not retryable or attempt == MAX_RETRIES:
                raise GroqError(f"HTTP {exc.code} da Groq") from exc
            wait = float(exc.headers.get("retry-after") or 2 ** attempt)
            sleep(min(wait, MAX_RETRY_WAIT_S))
        except urllib.error.URLError as exc:
            if attempt == MAX_RETRIES:
                raise GroqError(f"erro de rede: {exc.reason}") from exc
            sleep(2 ** attempt)
        except (KeyError, IndexError, json.JSONDecodeError) as exc:
            raise GroqError("resposta fora do formato esperado") from exc
    raise GroqError("tentativas esgotadas")


def parse_fields_json(raw: str, fields: list[str]) -> dict[str, Any]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise GroqError("modelo nao devolveu JSON valido") from exc
    if not isinstance(data, dict):
        raise GroqError("JSON nao e um objeto")
    missing = [f for f in fields if f not in data]
    if missing:
        raise GroqError(f"campos ausentes: {', '.join(missing)}")
    return {f: data[f] for f in fields}


def extract(text: str, fields: list[str], model: str, key: str, **kw: Any) -> dict[str, Any]:
    check_size(text)
    system = (
        "Extraia dados do texto. Responda SOMENTE com um objeto JSON com exatamente estas "
        f"chaves: {', '.join(fields)}. Use null quando a informacao nao estiver no texto. "
        "Nao invente nada."
    )
    raw = call_groq(build_payload(system, text, model, json_mode=True), key, **kw)
    return parse_fields_json(raw, fields)


def summarize(text: str, max_words: int, model: str, key: str, **kw: Any) -> str:
    check_size(text)
    system = (
        f"Resuma o texto em ate {max_words} palavras, em portugues, sem inventar "
        "informacoes que nao estejam nele."
    )
    return call_groq(build_payload(system, text, model, json_mode=False), key, **kw).strip()


def _load_text(args: argparse.Namespace) -> str:
    return Path(args.file).read_text(encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    sub.add_parser("setup")
    for name in ("extract", "summarize"):
        p = sub.add_parser(name)
        p.add_argument("--file", required=True)
        p.add_argument("--model", default=DEFAULT_MODEL)
        if name == "extract":
            p.add_argument("--fields", required=True)
        else:
            p.add_argument("--max-words", type=int, default=120)
    args = parser.parse_args(argv)

    try:
        if args.cmd == "setup":
            save_key(getpass.getpass(f"Cole a {KEY_VAR} (oculta): "))
            print(f"chave gravada em {ENV_PATH}")
            return 0
        if args.cmd == "status":
            get_key()
            print("chave GROQ_API_KEY configurada")
            return 0
        key = get_key()
        text = _load_text(args)
        if args.cmd == "extract":
            fields = [f.strip() for f in args.fields.split(",") if f.strip()]
            print(json.dumps(extract(text, fields, args.model, key), ensure_ascii=False, indent=2))
        else:
            print(summarize(text, args.max_words, args.model, key))
        return 0
    except (GroqError, OSError) as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
