#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
no_ai_slop_audit.py - Auditor Científico & Estilístico Anti-AI Slop
Baseado na metodologia de Peter Yang (petergyang/no-ai-slop) adaptado para
escrita acadêmica, publicações científicas e dissertações do GabeBrain.
"""

import sys
import re
import argparse
from pathlib import Path
import statistics
from typing import List, Tuple, Dict, Any

# Configuração de encoding para terminal Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Catálogo completo de padrões com regex, descrição e recomendação de correção
PATTERNS = [
    # 1. Palavras banidas diretamente (EN e PT)
    (
        r"\bdelv(e|es|ed|ing)\b",
        "Palavra banida: 'delve'",
        "Substitua por examine, analyze, investigate ou vá direto ao fato.",
        "Palavras Banidas"
    ),
    (
        r"\bmergulh(ar|a|am|ou|ando)\s+(profundamente|a\s+fundo)\b",
        "Tradução clichê de 'delve': 'mergulhar profundamente'",
        "Elimine a metáfora; indique a metodologia concreta (analisar, formalizar, computar).",
        "Palavras Banidas"
    ),
    (
        r"\btapestr(y|ies)\b",
        "Palavra banida: 'tapestry'",
        "Substitua por context, domain, structure, framework.",
        "Palavras Banidas"
    ),
    (
        r"\bmosaicos?\s+complexos?\b",
        "Clichê de IA: 'mosaico complexo'",
        "Defina o domínio técnico ou a arquitetura específica.",
        "Palavras Banidas"
    ),
    (
        r"\bcrucial\b",
        "Adjetivo inflado de IA: 'crucial'",
        "Substitua por essential, necessary, primary ou demonstre a evidência.",
        "Palavras Banidas"
    ),
    (
        r"\bpivotal\b",
        "Adjetivo inflado de IA: 'pivotal'",
        "Indique o marco experimental ou conceitual específico.",
        "Palavras Banidas"
    ),
    (
        r"\bgame-?changers?\b",
        "Jargão comercial de IA: 'game-changer'",
        "Substitua pelo ganho empírico comprovado (ex: redução de latência).",
        "Palavras Banidas"
    ),
    (
        r"\bdivisor\s+de\s+águas\b",
        "Jargão comercial de IA: 'divisor de águas'",
        "Substitua pela contribuição científica específica.",
        "Palavras Banidas"
    ),
    (
        r"\b(testament|stands\s+as\s+a\s+testament)\b",
        "Clichê de IA: 'stands as a testament'",
        "Declare a constatação técnica diretamente.",
        "Palavras Banidas"
    ),
    (
        r"\btestemunho\s+vivo\b",
        "Clichê de IA: 'testemunho vivo'",
        "Substitua pela evidência empírica ou resultado quantitativo.",
        "Palavras Banidas"
    ),
    (
        r"\b(beacon|multifaceted|transformative|supercharge|ever-evolving)\b",
        "Jargão inflado de marketing de IA",
        "Corte o adjetivo e mantenha o rigor da terminologia acadêmica.",
        "Palavras Banidas"
    ),
    (
        r"\b(ecossistema\s+dinâmico|patamar\s+superior|transformador|multifacetad[oa]s?)\b",
        "Jargão inflado de marketing de IA em português",
        "Use a terminologia exata da computação.",
        "Palavras Banidas"
    ),

    # 2. Muletas de Abertura (Throat-Clearing)
    (
        r"\b(it\s+is\s+worth\s+noting\s+that|it('?s|\s+is)\s+important\s+to\s+note\s+that)\b",
        "Throat-clearing: 'it is important to note that'",
        "Corte o preâmbulo e afirme o fato diretamente.",
        "Throat-Clearing"
    ),
    (
        r"\b(vale\s+ressaltar\s+que|cabe\s+destacar\s+que|é\s+importante\s+(notar|destacar|ressaltar)\s+que)\b",
        "Muleta de abertura acadêmica: 'vale ressaltar que'",
        "Corte a muleta. Inicie a frase diretamente no objeto ou método.",
        "Throat-Clearing"
    ),
    (
        r"\b(here('?s|\s+is)\s+the\s+thing|let\s+me\s+be\s+clear|the\s+truth\s+is)\b",
        "Abertura teatral de IA",
        "Vá direto à tese ou afirmação.",
        "Throat-Clearing"
    ),
    (
        r"\b(no\s+cenário\s+(atual|contemporâneo)|no\s+que\s+tange\s+a|no\s+mundo\s+de\s+hoje)\b",
        "Clichê de introdução de IA: 'no cenário atual'",
        "Abra com o problema de pesquisa ou a lacuna técnica imediata.",
        "Throat-Clearing"
    ),
    (
        r"\b(in\s+today('?s)?\s+(fast-paced\s+)?world|in\s+the\s+age\s+of)\b",
        "Clichê de introdução de IA: 'in today's world'",
        "Defina o escopo do problema tecnológico.",
        "Throat-Clearing"
    ),

    # 3. Contrastes Binários Falsos
    (
        r"\b(it('?s|\s+is)\s+not\s+(just\s+)?[^.?!;]+[.,]\s*it('?s|\s+is)\s+[^.?!;]+)\b",
        "Contraste Binário: 'It's not X. It's Y.'",
        "Declare a afirmativa Y diretamente sem o contraste estilístico.",
        "Contrastes Binários"
    ),
    (
        r"\b(não\s+se\s+trata\s+(apenas\s+)?de\s+[^.?!;]+[.,]\s*mas\s+(sim\s+)?de\s+[^.?!;]+)\b",
        "Contraste Binário: 'Não se trata de X, mas de Y'",
        "Afirme a proposta metodológica diretamente.",
        "Contrastes Binários"
    ),

    # 4. Weasel Attribution (Citações Vagas de IA)
    (
        r"\b(experts\s+agree|industry\s+reports\s+suggest|studies\s+show\s+that|many\s+argue)\b",
        "Weasel Attribution: 'studies show that' / 'experts agree'",
        "Indique os autores e o ano específico (ex: Joia et al., 2011) ou corte.",
        "Weasel Attribution"
    ),
    (
        r"\b(estudos\s+demonstram\s+que|especialistas\s+apontam|diversos\s+autores\s+afirmam|pesquisas\s+indicam)\b",
        "Atribuição Doninha: 'estudos apontam que' sem citação",
        "Insira a citação formal (Autor, Ano) ou cite o dado exato.",
        "Weasel Attribution"
    ),

    # 5. Superficial Analysis (-ing clauses vazias)
    (
        r",\s*(highlighting|underscoring|reflecting|showcasing|emphasizing)\s+(the\s+importance|the\s+need|the\s+role)\b",
        "Análise superficial: oração trailing -ing vazia",
        "Substitua pela consequência funcional ou pela métrica observada.",
        "Análise Superficial"
    ),
    (
        r",\s*(destacando|ressaltando|evidenciando|reforçando)\s+(a\s+importância|o\s+papel|a\s+necessidade)\b",
        "Gerúndio superficial de IA",
        "Exponha a causalidade técnica ou o impacto no sistema.",
        "Análise Superficial"
    ),

    # 6. Colon Reveals e Dramatização Teatral
    (
        r"(the\s+secret|the\s+key|the\s+result|o\s+segredo|a\s+chave|o\s+resultado|a\s+grande\s+sacada):\s+[a-z]",
        "Colon Reveal: revelação teatral com dois pontos",
        "Reescreva como frase contínua padrão com voz ativa.",
        "Dramatização"
    ),

    # 7. Summary-Recap Clichês
    (
        r"^(in\s+summary|in\s+conclusion|ultimately|overall)[,\s]",
        "Abertura de resumo óbvia: 'in conclusion'",
        "Inicie a seção diretamente nos achados e limitações da pesquisa.",
        "Fechamentos Clichês"
    ),
    (
        r"^(em\s+suma|em\s+conclusão|concluindo|em\s+resumo)[,\s]",
        "Abertura de resumo óbvia: 'em conclusão'",
        "Vá direto para a contribuição final e próximos passos.",
        "Fechamentos Clichês"
    ),
]

def clean_document(text: str) -> str:
    """Remove blocos de código, comentários e tags LaTeX para análise textual limpa."""
    # Remove markdown code blocks
    cleaned = re.sub(r"```[\s\S]*?```", "", text)
    cleaned = re.sub(r"`[^`]+`", "", cleaned)
    # Remove markdown/HTML comments
    cleaned = re.sub(r"<!--[\s\S]*?-->", "", cleaned)
    # Remove LaTeX comments
    cleaned = re.sub(r"%.*$", "", cleaned, flags=re.MULTILINE)
    return cleaned

def extract_sentences(text: str) -> List[str]:
    """Divide o texto em frases válidas para análise estatística de cadência."""
    # Divide por pontuação terminal
    raw_sentences = re.split(r"[.!?]+", text)
    sentences = []
    for s in raw_sentences:
        clean_s = re.sub(r"\s+", " ", s).strip()
        words = clean_s.split()
        if len(words) >= 3:
            sentences.append(clean_s)
    return sentences

def audit_file(file_path: Path) -> Dict[str, Any]:
    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    raw_text = file_path.read_text(encoding="utf-8", errors="ignore")
    cleaned_text = clean_document(raw_text)
    lines = raw_text.splitlines()

    matches = []
    category_counts = {}

    for idx, line in enumerate(lines, start=1):
        # Ignora linhas de código ou comentários puros
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("%") or stripped.startswith("#"):
            continue

        for pattern, name, advice, category in PATTERNS:
            found = list(re.finditer(pattern, line, re.IGNORECASE))
            for f in found:
                matches.append({
                    "line": idx,
                    "matched_text": f.group(0),
                    "name": name,
                    "advice": advice,
                    "category": category,
                    "context": stripped
                })
                category_counts[category] = category_counts.get(category, 0) + 1

    sentences = extract_sentences(cleaned_text)
    stats = {}
    if sentences:
        lengths = [len(s.split()) for s in sentences]
        stats["total_sentences"] = len(sentences)
        stats["mean_length"] = round(statistics.mean(lengths), 2)
        stats["stdev_length"] = round(statistics.stdev(lengths) if len(lengths) > 1 else 0.0, 2)
        stats["short_sentences"] = sum(1 for l in lengths if l <= 8)
        stats["long_sentences"] = sum(1 for l in lengths if l >= 35)

    return {
        "file": str(file_path),
        "filename": file_path.name,
        "total_issues": len(matches),
        "category_counts": category_counts,
        "issues": matches,
        "cadence_stats": stats
    }

def print_audit_report(results: Dict[str, Any]):
    print("=" * 78)
    print(f"🔬 GABEBRAIN NO-AI-SLOP AUDIT: {results['filename']}")
    print("=" * 78)

    total = results["total_issues"]
    if total == 0:
        print("✅ NENHUM PADRÃO OU CLICHÊ DE IA DETECTADO NO TEXTO!")
    else:
        print(f"⚠️  {total} OCORRÊNCIA(S) DE AI-SLOP / CLICHÊS IDENTIFICADAS:")
        print("-" * 78)
        for cat, count in results["category_counts"].items():
            print(f"   • {cat}: {count} ocorrência(s)")
        print("-" * 78)

        for issue in results["issues"][:30]:  # Limita aos primeiros 30 para visualização amigável
            print(f"Linha {issue['line']}: [{issue['category']}] {issue['name']}")
            print(f"   Trecho: \"{issue['matched_text']}\"")
            print(f"   Contexto: ...{issue['context'][:100]}...")
            print(f"   💡 Correção: {issue['advice']}\n")

        if len(results["issues"]) > 30:
            print(f"... e mais {len(results['issues']) - 30} ocorrências omitidas.")

    stats = results.get("cadence_stats")
    if stats:
        print("=" * 78)
        print("🎼 MÉTRICA DE CADÊNCIA & BURSTINESS (Ritmo Humano)")
        print("=" * 78)
        print(f"• Total de Sentenças: {stats['total_sentences']}")
        print(f"• Comprimento Médio: {stats['mean_length']} palavras/sentença")
        print(f"• Desvio Padrão de Ritmo: {stats['stdev_length']}")
        print(f"• Frases Curtas e Assertivas (≤ 8 palavras): {stats['short_sentences']}")
        print(f"• Frases Longas / Analíticas (≥ 35 palavras): {stats['long_sentences']}")

        stdev = stats["stdev_length"]
        if stdev < 4.0:
            print("\n⚠️ ALERTA DE METRÔNOMO DE IA:")
            print("   O desvio padrão está abaixo de 4.0. Todas as frases possuem quase o mesmo")
            print("   tamanho, criando um ritmo monótono sintético característico de LLMs.")
            print("   👉 Dica: Alterne sentenças diretas de 5 a 10 palavras com análises de 25 a 35 palavras.")
        else:
            print("\n✅ BOA VARIABILIDADE HUMANA:")
            print("   O ritmo apresenta boa alternância entre períodos curtos e compostos.")

    print("=" * 78)
    print("Regra de Ouro: 'Cada palavra paga aluguel'. Se puder cortar sem perder")
    print("significado metodológico ou precisão dos dados, corte.")
    print("=" * 78)

def main():
    parser = argparse.ArgumentParser(description="Auditor Anti-AI Slop para Artigos Científicos do GabeBrain.")
    parser.add_argument("file", type=Path, help="Caminho do arquivo (.md, .tex, .txt) a ser auditado")
    args = parser.parse_args()

    try:
        report = audit_file(args.file)
        print_audit_report(report)
    except Exception as e:
        print(f"[ERRO] Falha ao processar auditoria: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
