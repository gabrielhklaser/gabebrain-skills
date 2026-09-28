---
name: biblioteca-triagem
description: >-
  Tria e destila documentos do acervo técnico do GabeBrain (até 50 mil tokens).
  Lê o documento de forma econômica (uma leitura, quatro saídas), extraindo tipo (A/L/T/N/M/S/R/C/D),
  autor e ano validados na folha de rosto, nível de confiança da fonte (A-E) e gerando a
  nota destilada no Obsidian com citação exata de página para cada achado técnico.
  Use quando o usuário pedir triagem, destilação, conferência de autoria ou resumo com evidências.
---

# Triagem e Destilação Documental (GabeBrain)

Esta skill executa a triagem estruturada e destilação de documentos técnicos de até **50 mil tokens** (para documentos maiores, use `biblioteca-mapa-documento`).

O princípio fundamental é: **uma leitura, quatro saídas**. Ler o documento é o recurso computacional mais caro; extrair um campo de cada vez desperdiçaria contexto.

---

## 📋 As Quatro Saídas

| # | Saída | Destino |
|:---:|:---|:---|
| **1** | `tipo` (`A`/`L`/`T`/`N`/`M`/`S`/`R`/`C`/`D`) | `Metadata/triagem.csv` |
| **2** | `autor` + `ano` conferidos na folha de rosto | `Metadata/triagem.csv` |
| **3** | `confianca_fonte` (`A` a `E`) + justificativa | `Metadata/triagem.csv` |
| **4** | **Nota destilada** com achados e páginas | Pasta indicada por `biblioteca.py cota` |

Também confirma ou contesta a classe/método atribuída pelo classificador inicial.

Colunas de `Metadata/triagem.csv`:
`arquivo,codigo,tipo,autor,ano,fonte_autoria,confianca_fonte,justificativa_fonte,metodo_sugerido,lido_em,modelo`

---

## 🛠️ Procedimento Operacional Passo a Passo

### Pré-requisito: Conferir Trava e Hub
1. Verifique se não há pipeline em execução:
   `Test-Path "$HOME/Meu Drive/Obsidian_GabeBrain/GabeBrain/10-Trabalho/Geologia/Biblioteca Geologica/Metadata/pipeline.lock"`
2. O método precisa de um Hub (ex: `00 - GPR (indice).md`). Se não existir, crie-o antes.

### Etapa A — Medir o Lote ANTES de Ler
Cada texto extraído está em `.../Biblioteca Geologica/Metadata/texto/<slug>.txt`.
Estime tokens como: `bytes / 4`.

Apresente a estimativa ao usuário antes de iniciar a leitura:
```
Lote: GPR, 5 documentos
  menor: 4,2 k tokens | maior: 38 k tokens | total: 84 k tokens
  1 documento acima de 50 k -> desviado para biblioteca-mapa-documento
```

### Etapa B — Leitura Econômica
- **Acima de 50 k tokens**: Desvie para `biblioteca-mapa-documento`.
- **Abaixo de 50 k tokens**: Faça leitura seletiva/fatiada:
  ```powershell
  $BIB = "$HOME/Meu Drive/Obsidian_GabeBrain/GabeBrain/10-Trabalho/Geologia/Biblioteca Geologica/Scripts/biblioteca.py"
  python $BIB ler <COTA> 1-20
  ```
  *(Nunca abra o `.txt` inteiro de uma vez).*

### Etapa C — Classificação e Validação

#### C1 · Tipologia Documental
- `A`: Artigo (periódico ou anais de congresso)
- `L`: Livro ou capítulo de livro
- `T`: Tese, dissertação de mestrado, TCC
- `N`: Norma técnica, regulamento, portaria legal
- `M`: Manual técnico (de equipamento ou software)
- `S`: Slide, apostila, material didático
- `R`: Relatório técnico institucional/pericial
- `C`: Carta, mapa temático
- `D`: Administrativo / não-bibliográfico

#### C2 · Autoria e Ano (Folha de Rosto)
Metadados internos de PDF frequentemente erram (ex: nome do software ou computador). **Leia a folha de rosto**.
Se o documento não declarar ano ou autor com clareza, **deixe em branco em vez de chutar**.

#### C3 · Confiança da Fonte
- `A`: Norma técnica, artigo revisado por pares (peer-reviewed) -> citação incondicional.
- `B`: Livro-texto consagrado, tese/dissertação defendida -> citação incondicional.
- `C`: Relatório técnico institucional (CPRM/SGB, USGS, ANA, ANM, IG) -> citar identificando o órgão.
- `D`: Apostila, material didático sem revisão -> contextualização, não como prova pericial.
- `E`: Origem duvidosa ou desconhecida -> não citar até validar.

---

## 📝 Formato da Nota Destilada

Para saber onde gravar:
```powershell
python $BIB cota <COTA>
# Use o caminho de pasta devolvido pelo comando.
```

Nome do arquivo da nota: `<COTA>-Doc - <Autor> <Ano> (<gancho curto>).md`

```markdown
---
title: <Autor> <Ano> - <gancho>
aliases: ["<Autor> <Ano>"]
tags:
  - <metodo>
  - bibliografia
  - documento-destilado
type: reference
created: YYYY-MM-DD
status: note
related:
  - "[[<ficha-do-documento>]]"
  - "[[00 - <Metodo> (indice)]]"
---

# <Autor> (<Ano>) — <Resumo essencial em uma linha>

**Citação Formal:** <Autor(es)>, <Ano>. <Título do Trabalho>. <Veículo/Editora>, <páginas>.

**Registro na Biblioteca:** [[<ficha-do-documento>]] · `<COTA>` · Confiança: `<Letra>`

## Do que trata
<Parágrafo conciso resumindo o escopo e contexto do documento.>

## Principais Achados Técnicos (com página exata)
- <Achado técnico, critério ou parâmetro>, p. <N>
- <Equação empírica ou limite regulatório>, p. <N>
- <Valor numérico ou faixa de resistividade/velocidade>, p. <N>

## Aplicação Prática no GabeBrain
<Conexão com os trabalhos de geologia, hidrogeologia, geoprocessamento ou laudos ambientais do usuário.>

## Ver Também
- [[<outra-nota-relevante>]]
```

---

## 🔒 Regras de Integridade
1. **Todo achado precisa de página:** Informação sem página não entra na nota.
2. **Fórmulas de PDF:** Muitas vezes fontes matemáticas de PDFs saem truncadas. Marque como `"não conferida"` se houver ambiguidade.
3. **Fichas são intocáveis:** Metadados vão para `triagem.csv`. Depois de salvar o lote no CSV e as notas, rode:
   ```powershell
   powershell -NoProfile -File "...\00_rodar_pipeline.ps1" -So 5,9
   ```
   para que o script `05_gerar_fichas.py` integre os dados automaticamente na ficha.
