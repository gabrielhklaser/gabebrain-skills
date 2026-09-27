#!/usr/bin/env python3
"""
peer_review_checklist.py
Auditoria estrutural e métrica para manuscritos científicos (Markdown e LaTeX).
"""

import sys
import re
import argparse
from pathlib import Path

REQUIRED_SECTIONS = [
    ("Introdução / Motivation", [r"introdução", r"introduction", r"motivação", r"motivation"]),
    ("Trabalhos Relacionados / State of the Art", [r"trabalhos relacionados", r"related work", r"estado da arte", r"background"]),
    ("Metodologia / Proposta / Arquitetura", [r"metodologia", r"methodology", r"método", r"arquitetura", r"architecture", r"proposta", r"approach"]),
    ("Experimentos / Resultados / Avaliação", [r"experimento", r"resultado", r"avaliação", r"evaluation", r"results", r"experiments"]),
    ("Discussão / Ameaças à Validade", [r"discussão", r"discussion", r"ameaças à validade", r"threats to validity", r"limitações", r"limitations"]),
    ("Conclusão / Trabalhos Futuros", [r"conclusão", r"conclusions", r"trabalhos futuros", r"future work"]),
]

def audit_paper(file_path: Path):
    if not file_path.exists():
        print(f"[ERRO] Arquivo não encontrado: {file_path}")
        sys.exit(1)
        
    text = file_path.read_text(encoding="utf-8", errors="ignore")
    words = len(re.findall(r"\b\w+\b", text))
    lines = text.splitlines()
    
    print("=" * 60)
    print(f"📊 CHECKLIST DE AUDITORIA CIENTÍFICA: {file_path.name}")
    print("=" * 60)
    print(f"• Total de Palavras: {words:,}")
    print(f"• Total de Linhas: {len(lines):,}")
    
    # Check Abstract
    has_abstract = bool(re.search(r"(abstract|resumo)", text, re.IGNORECASE))
    if has_abstract:
        abstract_match = re.search(r"(?:abstract|resumo)\s*[:\n]+(.*?)(?=\n#|\n\n\w+|\Z)", text, re.IGNORECASE | re.DOTALL)
        if abstract_match:
            ab_words = len(re.findall(r"\b\w+\b", abstract_match.group(1)))
            print(f"• Resumo/Abstract: [OK] ({ab_words} palavras)")
            if ab_words < 100 or ab_words > 300:
                print(f"  ⚠️ Atenção: Tamanho do resumo ideal para SBC/IEEE costuma ser entre 150 e 250 palavras.")
        else:
            print("• Resumo/Abstract: [OK] detectado no texto.")
    else:
        print("• Resumo/Abstract: ❌ NÃO ENCONTRADO!")

    print("\n--- 🧭 Seções Canônicas Essenciais ---")
    score_sections = 0
    for sec_name, patterns in REQUIRED_SECTIONS:
        found = False
        for p in patterns:
            if re.search(rf"^#+\s+.*{p}", text, re.IGNORECASE | re.MULTILINE) or re.search(rf"\\section\{{.*{p}.*\}}", text, re.IGNORECASE):
                found = True
                break
        if found:
            print(f"  [OK] {sec_name}")
            score_sections += 1
        else:
            print(f"  [FALTA] {sec_name}")

    print("\n--- 🔬 Elementos de Rigor Metodológico ---")
    # Figures
    figs = len(re.findall(r"!\[.*?\]\(.*?\)|\\begin\{figure\}", text))
    print(f"• Figuras/Diagramas: {figs}")
    
    # Tables
    tables = len(re.findall(r"\|.*?\|.*?\|\n\|[-:\s|]+\|", text)) + len(re.findall(r"\\begin\{table\}", text))
    print(f"• Tabelas: {tables}")
    
    # Formulas / Math blocks
    math_blocks = len(re.findall(r"\$\$.*?\$\$|\\begin\{equation\}", text, re.DOTALL))
    inline_math = len(re.findall(r"(?<!\$)\$(?!\$).+?(?<!\$)\$(?!\$)", text))
    print(f"• Fórmulas Matemáticas: {math_blocks} blocos formais, {inline_math} equações inline")
    
    # Citations
    cits_md = len(re.findall(r"\[@[\w\-]+\]|\[[\w\s,]+,\s*\d{4}\]", text))
    cits_tex = len(re.findall(r"\\cite\{.*?\}", text))
    total_cits = cits_md + cits_tex
    print(f"• Citações Bibliográficas Detectadas: {total_cits}")

    print("\n" + "=" * 60)
    readiness = (score_sections / len(REQUIRED_SECTIONS)) * 100
    print(f"Índice de Estrutura Canônica: {readiness:.1f}%")
    if readiness >= 80:
        print("Status: Manuscrito com boa cobertura estrutural para revisão por pares.")
    else:
        print("Status: Manuscrito incompleto. Adicione as seções ausentes antes de submeter ao revisor.")
    print("=" * 60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Checklist para manuscritos científicos.")
    parser.add_argument("file", type=Path, help="Caminho do arquivo markdown ou latex do artigo")
    args = parser.parse_args()
    audit_paper(args.file)
