#!/usr/bin/env python3
"""
anti_slop_audit.py
Linter estilístico para detecção de AI slop, clichês e variabilidade sintática em textos acadêmicos.
"""

import sys
import re
import argparse
from pathlib import Path
import statistics

# Lista de termos e clichês frequentemente gerados por IA
BANNED_PATTERNS = [
    (r"\bdelve\b", "delve (troque por examine, analyze, investigate ou vá direto ao ponto)"),
    (r"\btapestry\b", "tapestry (troque por context, domain, structure)"),
    (r"\bcrucial\b", "crucial (use essential, necessary, critical ou mostre por que é importante)"),
    (r"\bpivotal\b", "pivotal (adjetivo inflado de IA)"),
    (r"\bgame-changer\b", "game-changer (jargão informal/comercial)"),
    (r"\btestament\b", "testament / 'serves as a testament' (clichê de IA)"),
    (r"\bsheds light on\b", "sheds light on (metáfora vazia)"),
    (r"\bimportant to note that\b", "important to note that (muleta verbal desnecessária)"),
    (r"\bvale ressaltar que\b", "vale ressaltar que (elimine e afirme diretamente o fato)"),
    (r"\bcabe destacar que\b", "cabe destacar que (elimine e afirme diretamente)"),
    (r"\bé importante notar que\b", "é importante notar que (elimine a muleta)"),
    (r"\bmergulhar profundamente\b", "mergulhar profundamente (clichê de tradução de delve)"),
    (r"\bmosaico complexo\b", "mosaico complexo (clichê de tradução de complex tapestry)"),
    (r"^(in summary|in conclusion|em suma|em conclusão)[,\s]", "início com muleta de resumo (comece com a constatação técnica direta)"),
]

def analyze_style(file_path: Path):
    if not file_path.exists():
        print(f"[ERRO] Arquivo não encontrado: {file_path}")
        sys.exit(1)
        
    text = file_path.read_text(encoding="utf-8", errors="ignore")
    
    # Remove code blocks and comments for text analysis
    clean_text = re.sub(r"```[\s\S]*?```", "", text)
    clean_text = re.sub(r"<!--[\s\S]*?-->", "", clean_text)
    
    # Split into sentences
    sentences = [s.strip() for s in re.split(r"[.!?]+", clean_text) if len(s.strip().split()) > 3]
    
    print("=" * 60)
    print(f"✍️ AUDITORIA ESTILÍSTICA & ANTI-AI SLOP: {file_path.name}")
    print("=" * 60)
    
    # 1. Search for banned patterns
    findings = []
    for pattern, advice in BANNED_PATTERNS:
        matches = list(re.finditer(pattern, clean_text, re.IGNORECASE | re.MULTILINE))
        if matches:
            findings.append((advice, len(matches)))
            
    if findings:
        print("\n⚠️ Clichês e Padrões de IA Encontrados:")
        for advice, count in findings:
            print(f"  • [{count}x] {advice}")
    else:
        print("\n✅ Nenhum clichê óbvio de IA detectado!")

    # 2. Sentence length analysis (burstiness)
    if sentences:
        lengths = [len(s.split()) for s in sentences]
        mean_len = statistics.mean(lengths)
        stdev_len = statistics.stdev(lengths) if len(lengths) > 1 else 0.0
        
        print("\n--- 🎼 Ritmo e Variabilidade de Frases (Cadência) ---")
        print(f"• Total de Frases Analisadas: {len(sentences)}")
        print(f"• Comprimento Médio: {mean_len:.1f} palavras/frase")
        print(f"• Desvio Padrão (Variação de Ritmo): {stdev_len:.1f}")
        
        if stdev_len < 4.0:
            print("  ⚠️ Alerta de Ritmo Monótono: Frases com comprimento excessivamente uniforme (marca de IA).")
            print("     Dica: Alterne períodos curtos e objetivos com períodos mais longos e compostos.")
        else:
            print("  ✅ Boa alternância de cadência entre períodos curtos e períodos explicativos.")
            
        long_sentences = [l for l in lengths if l > 45]
        if long_sentences:
            print(f"  ⚠️ {len(long_sentences)} frase(s) com mais de 45 palavras (podem gerar sobrecarga cognitiva).")

    print("\n" + "=" * 60)
    print("Dica de Humanização: Leia os parágrafos em voz alta.")
    print("Se soar como um comunicado institucional ou um resumo padronizado de chatbot, reescreva na voz do pesquisador.")
    print("=" * 60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auditoria de Anti-AI Slop e Estilo Técnico.")
    parser.add_argument("file", type=Path, help="Caminho do arquivo markdown do artigo")
    args = parser.parse_args()
    analyze_style(args.file)
