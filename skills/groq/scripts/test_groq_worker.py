from __future__ import annotations

import io
import json
import urllib.error

import pytest

import groq_worker as gw

REAL_READ_SECRETSTORE = gw._read_secretstore  # a fixture autouse troca o original nos testes


def _http_error(code: int, retry_after: str | None = None) -> urllib.error.HTTPError:
    headers = {"retry-after": retry_after} if retry_after else {}
    return urllib.error.HTTPError("http://x", code, "err", headers, io.BytesIO(b""))  # type: ignore[arg-type]


def _ok(content: str) -> dict:
    return {"choices": [{"message": {"content": content}}]}


@pytest.fixture(autouse=True)
def isolated_key_sources(monkeypatch):
    """Nenhum teste toca a chave real: registro e SecretStore vazios por padrao."""
    monkeypatch.setattr(gw, "_read_user_registry", lambda: None)
    monkeypatch.setattr(gw, "_read_secretstore", lambda: None)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)


def test_get_key_prefers_env_then_file(monkeypatch, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("GROQ_API_KEY=from-file\n", encoding="utf-8")
    assert gw.get_key(env_file) == "from-file"
    monkeypatch.setenv("GROQ_API_KEY", "from-env")
    assert gw.get_key(env_file) == "from-env"


def test_get_key_uses_secretstore_before_env_file(monkeypatch, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("GROQ_API_KEY=from-file\n", encoding="utf-8")
    monkeypatch.setattr(gw, "_read_secretstore", lambda: "from-store")
    assert gw.get_key(env_file) == "from-store"


def test_get_key_raises_when_missing(tmp_path):
    with pytest.raises(gw.GroqError, match="ausente"):
        gw.get_key(tmp_path / "nao-existe.env")


def _fake_run(returncode: int, stdout: str):
    def run(*args, **kwargs):
        return gw.subprocess.CompletedProcess(args, returncode, stdout=stdout, stderr="")
    return run


def test_read_secretstore_returns_stripped_value(monkeypatch):
    monkeypatch.setattr(gw.subprocess, "run", _fake_run(0, "gsk_abc\r\n"))
    assert REAL_READ_SECRETSTORE() == "gsk_abc"


def test_read_secretstore_failures_return_none(monkeypatch):
    monkeypatch.setattr(gw.subprocess, "run", _fake_run(1, ""))
    assert REAL_READ_SECRETSTORE() is None
    monkeypatch.setattr(gw.subprocess, "run", _fake_run(0, "   "))
    assert REAL_READ_SECRETSTORE() is None

    def no_powershell(*args, **kwargs):
        raise OSError("sem powershell")

    monkeypatch.setattr(gw.subprocess, "run", no_powershell)
    assert REAL_READ_SECRETSTORE() is None


def test_check_size_blocks_oversized_input():
    with pytest.raises(gw.GroqError, match="excede"):
        gw.check_size("x" * (gw.MAX_INPUT_TOKENS_EST * gw.CHARS_PER_TOKEN + 100))
    gw.check_size("texto curto")


def test_build_payload_json_mode_and_reasoning():
    p = gw.build_payload("s", "u", "openai/gpt-oss-120b", json_mode=True)
    assert p["response_format"] == {"type": "json_object"}
    assert p["reasoning_effort"] == "low"
    q = gw.build_payload("s", "u", "llama-3.3-70b-versatile", json_mode=False)
    assert "response_format" not in q and "reasoning_effort" not in q


def test_call_groq_retries_429_with_retry_after():
    calls: list[int] = []
    waits: list[float] = []

    def post(payload, key):
        calls.append(1)
        if len(calls) == 1:
            raise _http_error(429, "7")
        return _ok("feito")

    assert gw.call_groq({}, "k", post=post, sleep=waits.append) == "feito"
    assert len(calls) == 2 and waits == [7.0]


def test_call_groq_does_not_retry_client_error():
    def post(payload, key):
        raise _http_error(401)

    with pytest.raises(gw.GroqError, match="HTTP 401"):
        gw.call_groq({}, "k", post=post, sleep=lambda s: None)


def test_call_groq_gives_up_after_max_retries():
    def post(payload, key):
        raise _http_error(503)

    with pytest.raises(gw.GroqError, match="HTTP 503"):
        gw.call_groq({}, "k", post=post, sleep=lambda s: None)


def test_extract_returns_only_requested_fields():
    post = lambda payload, key: _ok(json.dumps({"vazao": "12 L/s", "poco": "P1", "extra": 1}))
    out = gw.extract("texto", ["vazao", "poco"], gw.DEFAULT_MODEL, "k", post=post, sleep=lambda s: None)
    assert out == {"vazao": "12 L/s", "poco": "P1"}


def test_extract_rejects_missing_fields_and_bad_json():
    with pytest.raises(gw.GroqError, match="ausentes"):
        gw.parse_fields_json('{"a": 1}', ["a", "b"])
    with pytest.raises(gw.GroqError, match="JSON valido"):
        gw.parse_fields_json("nao e json", ["a"])
    with pytest.raises(gw.GroqError, match="objeto"):
        gw.parse_fields_json("[1]", ["a"])


def test_summarize_strips_text():
    post = lambda payload, key: _ok("  resumo curto \n")
    assert gw.summarize("texto", 50, gw.DEFAULT_MODEL, "k", post=post, sleep=lambda s: None) == "resumo curto"


def test_main_status_without_key_fails(monkeypatch, capsys):
    monkeypatch.setattr(gw, "ENV_PATH", gw.Path("nao-existe.env"))
    assert gw.main(["status"]) == 1
    assert "ausente" in capsys.readouterr().err


def test_compose_uses_cheap_model_and_never_answers():
    seen: dict = {}

    def post(payload, key):
        seen.update(payload)
        return _ok("  Objetivo: listar poços.\nSaída: tabela.  \n")

    out = gw.compose("lista os pocos", gw.COMPOSE_MODEL, "k", post=post, sleep=lambda s: None)
    assert out == "Objetivo: listar poços.\nSaída: tabela."
    assert seen["model"] == "openai/gpt-oss-20b"
    system = seen["messages"][0]["content"].lower()
    assert "nao responda" in system and "nao invente" in system


def test_compose_blocks_oversized_prompt():
    big = "x" * (gw.MAX_INPUT_TOKENS_EST * gw.CHARS_PER_TOKEN + 100)
    with pytest.raises(gw.GroqError, match="excede"):
        gw.compose(big, gw.COMPOSE_MODEL, "k", post=lambda p, k: _ok("x"), sleep=lambda s: None)


def test_answer_returns_plain_text_with_selected_model():
    seen: dict = {}

    def post(payload, key):
        seen.update(payload)
        return _ok(" Brasília \n")

    assert gw.answer("capital do Brasil?", "qwen/qwen3.8-27b", "k", post=post, sleep=lambda s: None) == "Brasília"
    assert seen["model"] == "qwen/qwen3.8-27b"


def test_main_compose_reads_file_and_prints(monkeypatch, capsys, tmp_path):
    f = tmp_path / "p.txt"
    f.write_text("faca x", encoding="utf-8")
    monkeypatch.setattr(gw, "get_key", lambda *a, **k: "k")
    monkeypatch.setattr(gw, "compose", lambda text, model, key, **kw: f"[{model}] {text}")
    assert gw.main(["compose", "--file", str(f)]) == 0
    assert capsys.readouterr().out.strip() == "[openai/gpt-oss-20b] faca x"
