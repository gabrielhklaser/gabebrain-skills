#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SkillSpector runner for installations that provide the scanner locally.

This wrapper does not vendor or install SkillSpector. Configure
SKILLSPECTOR_DIR if the local checkout lives somewhere other than its default
per-user scratch directory. SKILLS_DIR can point at another skill collection.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SKILLSPECTOR_DIR = Path(
    os.environ.get("SKILLSPECTOR_DIR")
    or Path.home() / ".gemini" / "antigravity" / "scratch" / "SkillSpector"
).expanduser()
VENV_PYTHON = SKILLSPECTOR_DIR / ".venv" / (
    "Scripts/python.exe" if os.name == "nt" else "bin/python"
)
SKILLS_DIR = Path(os.environ.get("SKILLS_DIR") or REPO_ROOT / "skills").expanduser()


def run_audit(target_dir=None, output_format="terminal", output_file=None):
    if not VENV_PYTHON.is_file():
        print(
            "[ERRO] SkillSpector não está disponível neste ambiente. "
            "Instale-o no diretório configurado ou defina SKILLSPECTOR_DIR.",
            file=sys.stderr,
        )
        return 1

    target = Path(target_dir).expanduser().resolve() if target_dir else SKILLS_DIR.resolve()
    cmd = [
        str(VENV_PYTHON),
        "-m", "contrib.batch_scan.batch_scan",
        str(target),
        "--no-llm",
        "-f", output_format,
    ]
    if output_file:
        cmd.extend(["-o", str(Path(output_file).expanduser())])

    print(f"[*] Executando SkillSpector Batch Scan em: {target}")
    try:
        result = subprocess.run(
            cmd,
            cwd=str(SKILLSPECTOR_DIR),
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=900,
            check=False,
        )
        return result.returncode
    except subprocess.TimeoutExpired:
        print("[ERRO] A auditoria excedeu o limite de 900 segundos.", file=sys.stderr)
        return 124
    except OSError as exc:
        print(f"[ERRO] Não foi possível iniciar o SkillSpector: {exc}", file=sys.stderr)
        return 127


def main(argv=None):
    parser = argparse.ArgumentParser(description="Executa auditoria SkillSpector offline (sem LLM).")
    parser.add_argument("target", nargs="?", help="Diretório da skill; por padrão usa o diretório local skills/.")
    parser.add_argument("format", nargs="?", choices=("terminal", "markdown", "json"), default="terminal")
    parser.add_argument("output", nargs="?", help="Arquivo de saída opcional.")
    args = parser.parse_args(argv)
    return run_audit(args.target, args.format, args.output)


if __name__ == "__main__":
    raise SystemExit(main())
