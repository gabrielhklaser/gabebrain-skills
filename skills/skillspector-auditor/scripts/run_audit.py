#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SkillSpector Runner & Auditor para o GabeBrain
Executa auditoria estática e comportamental nas skills do ecossistema.
"""

import sys
import subprocess
from pathlib import Path

SKILLSPECTOR_DIR = Path(r"C:\Users\Gabriel\.gemini\antigravity\scratch\SkillSpector")
VENV_PYTHON = SKILLSPECTOR_DIR / ".venv" / "Scripts" / "python.exe"
SKILLS_DIR = Path(r"C:\Users\Gabriel\.gemini\config\skills")

def run_audit(target_dir=None, output_format="terminal", output_file=None):
    if not VENV_PYTHON.exists():
        print(f"[ERRO] Ambiente virtual do SkillSpector não encontrado em {VENV_PYTHON}")
        sys.exit(1)

    target = Path(target_dir) if target_dir else SKILLS_DIR
    cmd = [
        str(VENV_PYTHON),
        "-m", "contrib.batch_scan.batch_scan",
        str(target),
        "--no-llm",
        "-f", output_format
    ]
    if output_file:
        cmd.extend(["-o", str(output_file)])

    print(f"[*] Executando SkillSpector Batch Scan em: {target}")
    result = subprocess.run(cmd, cwd=str(SKILLSPECTOR_DIR), text=True, encoding="utf-8", errors="replace")
    return result.returncode

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    fmt = sys.argv[2] if len(sys.argv) > 2 else "terminal"
    out = sys.argv[3] if len(sys.argv) > 3 else None
    sys.exit(run_audit(target, fmt, out))
