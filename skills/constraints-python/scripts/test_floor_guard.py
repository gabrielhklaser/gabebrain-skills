"""Testes do floor_guard em repositorios git temporarios."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

import floor_guard as fg

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="git ausente")

CONSTRAINTS = (
    "# Constraints\n\n## Piso\n\n- Cobertura das linhas alteradas: >= 80%\n"
    "- Sem segredos no codigo\n\n## Excecoes\n\n| ID | Regra |\n|----|-------|\n"
)


def sh(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    sh(tmp_path, "init", "-b", "main")
    sh(tmp_path, "config", "user.email", "t@t")
    sh(tmp_path, "config", "user.name", "t")
    (tmp_path / "app.py").write_text("def f():\n    return 1\n", encoding="utf-8")
    (tmp_path / "test_app.py").write_text("def test_f():\n    assert 1 == 1\n    assert f() == 1\n", encoding="utf-8")
    (tmp_path / "CONSTRAINTS.md").write_text(CONSTRAINTS, encoding="utf-8")
    sh(tmp_path, "add", "-A")
    sh(tmp_path, "commit", "-m", "base")
    return tmp_path


def rules(repo: Path) -> set[str]:
    return {f.rule for f in fg.run(repo, "main")}


def test_limpo_sem_mudancas(repo: Path) -> None:
    assert fg.run(repo, "main") == []


def test_noqa_novo_e_marcado(repo: Path) -> None:
    (repo / "app.py").write_text("import os  # noqa\n", encoding="utf-8")
    assert "silenced-checker" in rules(repo)


def test_skip_de_teste_e_marcado(repo: Path) -> None:
    (repo / "test_app.py").write_text("import pytest\n@pytest.mark.skip\ndef test_f():\n    assert 1\n", encoding="utf-8")
    assert "test-made-easier" in rules(repo)


def test_assercao_removida(repo: Path) -> None:
    (repo / "test_app.py").write_text("def test_f():\n    assert 1 == 1\n", encoding="utf-8")
    assert "assertion-removed" in rules(repo)


def test_teste_apagado(repo: Path) -> None:
    (repo / "test_app.py").unlink()
    assert "test-deleted" in rules(repo)


def test_stub_e_marcado(repo: Path) -> None:
    (repo / "app.py").write_text("def g():\n    raise NotImplementedError\n", encoding="utf-8")
    assert "unfinished-work" in rules(repo)


def test_arquivo_novo_nao_rastreado_e_lido(repo: Path) -> None:
    (repo / "novo.py").write_text("x: int = 'a'  # type: ignore\n", encoding="utf-8")
    assert "silenced-checker" in rules(repo)


def test_limite_afrouxado(repo: Path) -> None:
    (repo / "CONSTRAINTS.md").write_text(CONSTRAINTS.replace(">= 80%", ">= 60%"), encoding="utf-8")
    assert "threshold-loosened" in rules(repo)


def test_limite_apertado_e_silencioso(repo: Path) -> None:
    (repo / "CONSTRAINTS.md").write_text(CONSTRAINTS.replace(">= 80%", ">= 90%"), encoding="utf-8")
    assert rules(repo) == set()


def test_regra_removida(repo: Path) -> None:
    (repo / "CONSTRAINTS.md").write_text(CONSTRAINTS.replace("- Sem segredos no codigo\n", ""), encoding="utf-8")
    assert "rule-removed" in rules(repo)


def test_excecao_nova(repo: Path) -> None:
    (repo / "CONSTRAINTS.md").write_text(CONSTRAINTS + "| W1 | no-any |\n", encoding="utf-8")
    assert "new-exception" in rules(repo)


def test_constraintsignore_isenta_caminho(repo: Path) -> None:
    (repo / ".constraintsignore").write_text("legado/*\n", encoding="utf-8")
    (repo / "legado").mkdir()
    (repo / "legado" / "velho.py").write_text("import os  # noqa\n", encoding="utf-8")
    assert rules(repo) == set()


def test_exit_2_fora_de_git(tmp_path: Path) -> None:
    assert fg.main(["--repo", str(tmp_path)]) == 2


def test_exit_2_sem_merge_base(repo: Path) -> None:
    assert fg.main(["--repo", str(repo), "--base", "nao-existe"]) == 2


def test_exit_1_e_nao_imprime_conteudo(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (repo / "app.py").write_text("KEY = 'sk-SEGREDO123'  # noqa\n", encoding="utf-8")
    assert fg.main(["--repo", str(repo), "--base", "main"]) == 1
    err = capsys.readouterr().err
    assert "silenced-checker" in err and "SEGREDO123" not in err
