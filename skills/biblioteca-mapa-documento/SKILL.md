---
name: biblioteca-mapa-documento
description: >-
  Mapeia e extrai conhecimento de documentos extensos (>50 mil tokens, livros técnicos,
  manuais e teses) do acervo do GabeBrain. Em vez de ler o PDF inteiro, extrai o esqueleto
  estrutural de capítulos de forma gratuita e executa mergulhos direcionados apenas nas seções
  de maior densidade técnica (conclusões, tabelas, fórmulas e normas), gerando notas do tipo Mapa.
---

# Mapeamento e Mineração de Documentos Grandes

Livros técnicos, tratados geológicos e manuais de 500 a 1000 páginas não devem ser lidos de ponta a ponta por LLMs — isso esgotaria janelas de contexto e inflaria custos. Esta skill transforma grandes volumes em **mapas estruturais navegáveis** com mergulhos analíticos seletivos.

---

## ⚡ Quando Utilizar
- Documento com mais de **50 mil tokens** (verificado via tamanho do `.txt` dividido por 4).
- Livros de referência técnica (ex: Reynolds, Telford, Davis, Loke).
- Manuais de equipamentos e diretrizes de grandes órgãos (USGS, USBR, CPRM).

---

## 🧭 Etapa 1 — Extração Estrutural Gratuita

Execute o script de estrutura para obter capítulos, intervalos de páginas e contagem de tokens sem gastar leitura com a LLM:

```powershell
$SCRIPTS = "$HOME/Meu Drive/Obsidian_GabeBrain/GabeBrain/10-Trabalho/Geologia/Biblioteca Geologica/Scripts"
python "$SCRIPTS\17_estrutura_documento.py" "<parte do nome ou cota>" --max 60
```

### Rotas de Detecção e Confiança:
1. **Sumário embutido no PDF (Bookmarks / ToC)**: Confiança alta.
2. **Sumário detectado no texto (OCR/Tabela de Conteúdo)**: Confiança média.
3. **Fatia fixa (divisão por blocos de páginas)**: Confiança baixa (usada apenas como mapa de orçamento).

⚠️ **Atenção para `TRECHO SEM ESTRUTURA`**: Se uma seção contiver mais de 15% do documento sem divisões identificadas, nunca envie para leitura direta. Em vez disso, busque termos específicos dentro do trecho:
```powershell
python "$SCRIPTS\06_buscar.py" "termo" --palavra --arquivo "<nome_do_arquivo>"
```

---

## 🎯 Etapa 2 — Seleção de Seções e Orçamento

Apresente o mapa preliminar e as seções mais densas (marcadas com 🔥 pelo script) ao usuário:

```
Documento: Applied Geophysics (Telford et al.) — 790 p., 420 k tokens
Rota: Sumário embutido no PDF
Seções de alta densidade para GPR / Eletrorresistividade:
  1. Chapter 5: Electrical Properties of Rocks    p. 283-340   (24 k tokens) 🔥
  2. Chapter 6: Resistivity Methods                p. 341-410   (31 k tokens) 🔥
Deseja mergulhar nas seções 1 e 2? (Orçamento: 55 k tokens)
```

---

## 🔬 Etapa 3 — O Mergulho Analítico

Após a confirmação, leia cirurgicamente apenas as páginas das seções selecionadas:
```powershell
python "$SCRIPTS\biblioteca.py" ler <COTA> 283-340
```

Concentre a extração em 4 pilares:
1. **Conclusões e Diretrizes de Campo**: Recomendações práticas e limitações de método.
2. **Tabelas de Valores Físicos**: Faixas de resistividade, condutividade hidráulica, velocidades sísmicas e constantes dielétricas com unidades e litologias.
3. **Equações Fundamentais**: Fórmulas com a descrição clara de cada variável. Se notar formatação matemática truncada por OCR, registre `"fórmula não conferida"`.
4. **Critérios Normativos e Parâmetros de Projeto**: Limites de corte e parâmetros analíticos.

---

## 📄 Etapa 4 — Criação da Nota de Mapa no Obsidian

Para saber a pasta correta:
```powershell
python "$SCRIPTS\biblioteca.py" cota <COTA>
```

Nome do arquivo: `<COTA>-Mapa - <Título Curto>.md`

```markdown
---
title: <COTA>-Mapa - <Título Curto>
tags:
  - <metodo>
  - bibliografia
  - documento-mapa
type: reference
created: YYYY-MM-DD
status: growing
related:
  - "[[<ficha-do-documento>]]"
  - "[[00 - <Metodo> (indice)]]"
---

# <Título Completo do Documento> — Mapa de Leitura

**Citação:** <Referência bibliográfica completa.>  
**Registro no Acervo:** [[<ficha-do-documento>]] · `<COTA>` · Total: <N> páginas (<X> mil tokens)

> [!NOTE]
> **Documento Extenso — Leitura Seletiva:** Estrutura gerada por <rota>. Mergulho analítico focado nas seções: <lista de seções>.

## Visão Geral do Documento
<Síntese do escopo geral da obra em 1 a 2 parágrafos.>

## Mapa Estrutural do Documento
| Seção / Capítulo | Páginas | Tokens Aprox. | Relevância / Temas Cobertos |
|:---|:---:|:---:|:---|
| Cap. 1: Introdução | 1–25 | 10 k | Histórico e conceitos fundamentais |
| Cap. 5: Propriedades Elétricas | 283–340 | 24 k | Constantes dielétricas e resistividades 🔥 |
| Cap. 6: Métodos Elétricos | 341–410 | 31 k | Arranjos Wenner/Schlumberger, inversão 2D 🔥 |

## Mergulhos Realizados

### Seção: Propriedades Elétricas das Rochas (p. 283–340)
- **Tabelas e Valores:** Faixa de condutividade de granitos sãos (10^4 a 10^6 ohm.m), p. 291.
- **Equações:** Lei de Archie adaptada para solos arenosos saturados, p. 305.
- **Conclusões:** Limitações de profundidade em terrenos de alta condutividade superficial, p. 320.

## Aplicação no GabeBrain
<Como os dados extraídos apoiam projetos de geologia, recursos hídricos ou laudos periciais.>

## O que NÃO Foi Lido Neste Passe
- *Cap. 2 a 4 (Gravimetria e Magnetometria): Não lidos.*
- *Cap. 7 a 11 (Sísmica de Reflexão e Métodos Radioativos): Não lidos.*
```

---

## 📊 Relatório Obrigatório ao Usuário
Ao concluir a elaboração do mapa, sempre reporte:
- Rota de extração utilizada.
- Economia obtida (ex: *"Lidos 55 k de 420 k tokens — cobertura cirúrgica de 13% da obra"*).
- Alerta sobre seções ignoradas ou dados pendentes de validação gráfica.
