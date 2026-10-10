"""floor_guard: vigia, no diff, as jogadas que baixam a barra de qualidade (versao Python).

Adaptado do floor-guard de referencia da skill constraint-driven-development
(github.com/addyosmani/agent-skills, MIT). Mesmo contrato, padroes para Python.

Uso:  python floor_guard.py [--base REF] [--repo DIR]
Saida: 0 limpo | 1 violacao do piso (bloquear) | 2 nao conseguiu rodar (nunca ler como 0).
Relata regra, arquivo e linha; nunca imprime o conteudo das linhas (podem ter segredo).
Apertar e silencioso; afrouxar e barulhento.
"""
from __future__ import annotations

import argparse
import fnmatch
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

DEFAULT_BASES = ("origin/main", "origin/master", "main", "master")

SUPPRESSIONS = re.compile(
    r"#\s*noqa|#\s*type:\s*ignore|#\s*pyright:\s*ignore|#\s*pylint:\s*disable|#\s*nosec"
    r"|nosemgrep|gitleaks:allow|pragma:\s*no\s*(cover|branch)"
)
STUBS = re.compile(
    r"raise\s+NotImplementedError|except(\s+[\w.,() ]+)?(\s+as\s+\w+)?\s*:\s*pass\b|\bTODO\b"
)
SKIPS = re.compile(
    r"@pytest\.mark\.(skip|skipif|xfail)|\bpytest\.(skip|xfail)\(|@unittest\.(skip|expectedFailure)|\.skipTest\("
)
ASSERTIONS = re.compile(r"\bassert\b|pytest\.raises|self\.assert\w*")
EXCEPTION_ROW = re.compile(r"^\|\s*[WE]\d+\s*\|")
TEST_PATH = re.compile(r"(^|/)(test_[^/]*|[^/]*_test)\.py$|(^|/)tests?/")

MIN_BEFORE = re.compile(
    r"(>=|>|≥|at least|minimum|\bmin\b|no less than|not fall|not drop|no mínimo|mínimo|pelo menos|não pode cair)\s*$"
)
MAX_BEFORE = re.compile(
    r"(<=|<|≤|at most|maximum|\bmax\b|no more than|under|below|not grow|not exceed|no máximo|máximo|até|não pode crescer)\s*$"
)
MIN_AFTER = re.compile(r"^\s*\S*\s*(or more|or higher|ou mais|must not fall|não pode cair)")
MAX_AFTER = re.compile(r"^\s*\S*\s*(or less|or lower|ou menos|must not grow|não pode crescer)")
HUNK = re.compile(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@")


class GuardError(Exception):
    """O guarda nao conseguiu rodar (vira exit 2)."""


@dataclass(frozen=True)
class Change:
    file: str
    line: int
    text: str


@dataclass(frozen=True)
class Finding:
    rule: str
    file: str
    line: int
    detail: str = ""


def git(repo: Path, *args: str) -> str:
    try:
        out = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True,
                             encoding="utf-8", errors="replace", check=False)
    except OSError as exc:
        raise GuardError(f"git indisponivel: {exc}") from exc
    if out.returncode != 0:
        raise GuardError(f"git {' '.join(args)}: {out.stderr.strip()[:200]}")
    return out.stdout


def find_merge_base(repo: Path, base: str | None) -> str:
    candidates = (base,) if base else DEFAULT_BASES
    for ref in candidates:
        try:
            return git(repo, "merge-base", ref, "HEAD").strip()
        except GuardError:
            continue
    raise GuardError("sem merge base (use --base REF)")


def parse_diff(diff: str) -> tuple[list[Change], list[Change], list[str]]:
    """Retorna (adicionadas, removidas, arquivos_removidos)."""
    added: list[Change] = []
    removed: list[Change] = []
    deleted: list[str] = []
    file = old_file = ""
    in_header = False
    old_no = new_no = 0
    for line in diff.split("\n"):
        if line.startswith("diff --git"):
            in_header = True
        elif line.startswith("@@"):
            in_header = False
            m = HUNK.match(line)
            if m:
                old_no, new_no = int(m.group(1)), int(m.group(2))
        elif in_header:
            if line.startswith("--- "):
                old_file = re.sub(r"^a/", "", line[4:])
            elif line.startswith("+++ "):
                new_file = re.sub(r"^b/", "", line[4:])
                file = old_file if new_file == "/dev/null" else new_file
                if new_file == "/dev/null":
                    deleted.append(file)
        elif line.startswith("+"):
            added.append(Change(file, new_no, line[1:]))
            new_no += 1
        elif line.startswith("-"):
            removed.append(Change(file, old_no, line[1:]))
            old_no += 1
    return added, removed, deleted


def untracked_as_added(repo: Path) -> list[Change]:
    names = git(repo, "ls-files", "--others", "--exclude-standard").split("\n")
    out: list[Change] = []
    for name in filter(None, names):
        try:
            text = (repo / name).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        out.extend(Change(name, i, ln) for i, ln in enumerate(text.splitlines(), 1))
    return out


def rule_key(text: str) -> str | None:
    s = text.strip()
    if s.startswith("|"):
        cells = [c.strip() for c in s.split("|") if c.strip()]
        return cells[0] if cells else ""
    if re.match(r"^[-*] ", s):
        return s[2:].split(":")[0].strip()
    return None


def thresholds(text: str) -> list[tuple[float, str | None]]:
    out: list[tuple[float, str | None]] = []
    for m in re.finditer(r"\d+(?:\.\d+)?", text):
        before = text[max(0, m.start() - 24):m.start()].lower()
        after = text[m.end():m.end() + 40].lower()
        if MIN_BEFORE.search(before) or MIN_AFTER.search(after):
            direction: str | None = "min"
        elif MAX_BEFORE.search(before) or MAX_AFTER.search(after):
            direction = "max"
        else:
            direction = None
        out.append((float(m.group(0)), direction))
    return out


def weakened(old: str, new: str) -> str | None:
    before, after = thresholds(old), thresholds(new)
    for direction in ("min", "max", None):
        was = [n for n, d in before if d == direction]
        now = [n for n, d in after if d == direction]
        for i, b in enumerate(was):
            if i >= len(now):
                return "threshold-removed"
            n = now[i]
            if n == b:
                continue
            if direction is None:
                return "threshold-changed"
            if (direction == "min" and n < b) or (direction == "max" and n > b):
                return "threshold-loosened"
    return None


def constraint_findings(added: list[Change], removed: list[Change]) -> list[Finding]:
    found: list[Finding] = []
    new_rules = [c for c in added if c.file.endswith("CONSTRAINTS.md") and rule_key(c.text) is not None]
    for old in (c for c in removed if c.file.endswith("CONSTRAINTS.md") and rule_key(c.text) is not None):
        match = next((n for n in new_rules if rule_key(n.text) == rule_key(old.text)), None)
        if match is None:
            if not EXCEPTION_ROW.match(old.text.strip()):
                found.append(Finding("rule-removed", old.file, old.line, rule_key(old.text) or ""))
            continue
        verdict = weakened(old.text, match.text)
        if verdict:
            found.append(Finding(verdict, old.file, old.line, rule_key(old.text) or ""))
    return found


def analyse(added: list[Change], removed: list[Change], deleted: list[str],
            ignore: list[str]) -> list[Finding]:
    def skip(file: str) -> bool:
        return any(fnmatch.fnmatch(file, pat) for pat in ignore)

    found: list[Finding] = []
    for c in added:
        if skip(c.file):
            continue
        if c.file.endswith(".py") or c.file.endswith("CONSTRAINTS.md"):
            if SUPPRESSIONS.search(c.text):
                found.append(Finding("silenced-checker", c.file, c.line))
            if c.file.endswith(".py") and STUBS.search(c.text):
                found.append(Finding("unfinished-work", c.file, c.line))
            if c.file.endswith(".py") and SKIPS.search(c.text):
                found.append(Finding("test-made-easier", c.file, c.line))
        if c.file.endswith("CONSTRAINTS.md") and EXCEPTION_ROW.match(c.text.strip()):
            found.append(Finding("new-exception", c.file, c.line))
    for f in deleted:
        if TEST_PATH.search(f) and not skip(f):
            found.append(Finding("test-deleted", f, 0))
    for c in removed:
        if TEST_PATH.search(c.file) and c.file not in deleted and not skip(c.file) and ASSERTIONS.search(c.text):
            found.append(Finding("assertion-removed", c.file, c.line))
    found.extend(f for f in constraint_findings(added, removed) if not skip(f.file))
    return found


def load_ignore(repo: Path) -> list[str]:
    path = repo / ".constraintsignore"
    if not path.is_file():
        return []
    return [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.startswith("#")]


def run(repo: Path, base: str | None) -> list[Finding]:
    top = Path(git(repo, "rev-parse", "--show-toplevel").strip())
    merge_base = find_merge_base(top, base)
    added, removed, deleted = parse_diff(git(top, "diff", "--unified=0", merge_base, "--"))
    added.extend(untracked_as_added(top))
    return analyse(added, removed, deleted, load_ignore(top))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--base", help="ref de base (padrao: origin/main, origin/master, main, master)")
    ap.add_argument("--repo", default=".", help="pasta dentro do repositorio git")
    args = ap.parse_args(argv)
    try:
        findings = run(Path(args.repo).resolve(), args.base)
    except GuardError as exc:
        print(f"floor-guard: nao rodou: {exc}", file=sys.stderr)
        return 2
    if not findings:
        print("floor-guard: limpo")
        return 0
    print(f"floor-guard: {len(findings)} violacao(oes) do piso:", file=sys.stderr)
    for f in findings:
        where = f"{f.file}:{f.line}" if f.line else f.file
        print(f"  [{f.rule}] {where} {f.detail}".rstrip(), file=sys.stderr)
    print("\nCada item baixa a barra. Corrija o codigo ou registre uma excecao rastreada.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
