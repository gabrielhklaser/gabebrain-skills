from __future__ import annotations

import io
import json
import urllib.error

import pytest

import groq_worker as gw


def _http_error(code: int, retry_after: str | None = None) -> urllib.error.HTTPError:
    headers = {"retry-after": retry_after} if retry_after else {}
    return urllib.error.HTTPError("http://x", code, "err", headers, io.BytesIO(b""))  # type: ignore[arg-type]


def _ok(content: str) -> dict:
    return {"choices": [{"message": {"content": content}}]}


def test_get_key_prefers_env_then_file(monkeypatch, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("GROQ_API_KEY=from-file\n", encoding="utf-8")
    monkeypatch.setattr(gw, "_read_user_registry", lambda: None)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    assert gw.get_key(env_file) == "from-file"
    monkeypatch.setenv("GROQ_API_KEY", "from-env")
    assert gw.get_key(env_file) == "from-env"


def test_get_key_raises_when_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(gw, "_read_user_registry", lambda: None)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(gw.GroqError, match="ausente"):
        gw.get_key(tmp_path / "nao-existe.env")


def test_save_key_roundtrip_and_rejects_empty(monkeypatch, tmp_path):
    env_file = tmp_path / ".env"
    fake = "gsk_" + "a" * 40
    gw.save_key(f"  {fake}  ", env_file)
    monkeypatch.setattr(gw, "_read_user_registry", lambda: None)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    assert gw.get_key(env_file) == fake
    with pytest.raises(gw.GroqError, match="vazia"):
        gw.save_key("   ", env_file)
    with pytest.raises(gw.GroqError, match="curta"):
        gw.save_key("x", env_file)


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
    monkeypatch.setattr(gw, "_read_user_registry", lambda: None)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setattr(gw, "ENV_PATH", gw.Path("nao-existe.env"))
    assert gw.main(["status"]) == 1
    assert "ausente" in capsys.readouterr().err
