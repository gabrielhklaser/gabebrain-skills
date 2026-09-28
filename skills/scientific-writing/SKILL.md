---
name: scientific-writing
description: Estruturacao formal de artigos e dissertacoes cientificas (IEEE, ACM, SBC, Elsevier). Conduz a redacao secao por secao (Abstract, Introducao em Piramide Invertida, Trabalhos Relacionados Taxonomicos, Metodologia Rigorosa, Resultados e Discussao) com alta densidade tecnica e formalismo academico.
---

# Scientific Writing Agent Skill

Especialista em redação científica de alto nível para Computação Aplicada, Ciência de Dados e Geociências Computacionais, alinhado aos padrões IEEE Transactions, ACM Computing Surveys, Elsevier e SBC (Sociedade Brasileira de Computação).

## 1. Estrutura Canônica de Artigo Científico

### Abstract (Resumo Estruturado em 5 Frases)
1. **Contexto & Relevância**: O domínio geral e sua importância contemporânea.
2. **Problema & Lacuna (Gap)**: O desafio específico não resolvido pela literatura atual.
3. **Proposta / Solução**: O método, algoritmo ou arquitetura introduzida pelo trabalho.
4. **Resultados Quantitativos**: Métricas exatas de validação empírica (ex: precisão, speedup, erro médio).
5. **Impacto & Contribuição**: O significado prático ou teórico do achado para a área.

### Introdução (Técnica da Pirâmide Invertida)
- **Parágrafo 1**: Contexto amplo do domínio de pesquisa.
- **Parágrafo 2**: Estado da arte e esforços existentes.
- **Parágrafo 3**: A lacuna aberta (The Problem / The Gap) e por que abordagens atuais falham.
- **Parágrafo 4**: A nossa abordagem e hipótese central.
- **Parágrafo 5**: Sumário de contribuições explícitas (bullet points acionáveis):
  - *Contribuição 1 (Conceitual/Metodológica)*: Nova formulação ou ontologia.
  - *Contribuição 2 (Algorítmica/Sistêmica)*: Arquitetura, pipeline ou implementação.
  - *Contribuição 3 (Empírica)*: Validação experimental sobre benchmarks públicos.
- **Parágrafo 6**: Organização do restante do documento ("O restante deste artigo está organizado como segue...").

### Trabalhos Relacionados (Related Work - Estrutura Taxonômica)
- **PROIBIDO**: Lista cronológica de resumos isolados ("Autor A fez X. Autor B fez Y.").
- **OBRIGATÓRIO**: Agrupamento temático em subseções por categoria metodológica.
- **Tabela Comparativa de Taxonomia**:
  | Método / Artigo | Paradigma | Dataset | Limitação Crítica | Como nosso trabalho difere |
  | :--- | :--- | :--- | :--- | :--- |

### Metodologia (Methodology / Proposed Architecture)
- **Formulação Matemática do Problema**: Definição formal de variáveis, grafos, tuplas, conjuntos e restrições.
- **Arquitetura Geral**: Diagrama conceitual de fluxo de dados.
- **Algoritmo Passo a Passo**: Pseudocódigo no padrão formal (*Algorithm* block).
- **Reprodutibilidade**: Parâmetros, hardware, seeds aleatórias e hiperparâmetros expressos em tabela.

### Resultados e Validação Empírica (Experiments & Evaluation)
- **Questões de Pesquisa (Research Questions - RQs)**:
  - **RQ1**: O método proposto supera os baselines do estado da arte?
  - **RQ2**: Qual a contribuição isolada de cada componente (Ablation Study)?
  - **RQ3**: Como o sistema escala perante volumes massivos de dados?
- **Gráficos e Legendas Auto-Contidas**: Uma figura e sua legenda devem ser compreensíveis sem que o leitor precise recorrer ao corpo do texto.

### Discussão & Conclusão
- Confronto direto dos resultados com a literatura existente (confirmações e divergências).
- Limitações abertas (ameaças à validade interna e externa).
- Trabalhos futuros concretos (sem clichês vagos).
