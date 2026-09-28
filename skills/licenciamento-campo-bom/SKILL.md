---
name: licenciamento-campo-bom
description: >-
  Regras de conferência do licenciamento ambiental municipal de Campo Bom/RS (SEMA) usadas pelo
  sistema licenciamentoambiental: zoneamento do Plano Diretor (Lei 5.329/2022, Anexos 03 e 08),
  enquadramento CONSEMA 372/2018 (CODRAM x porte x potencial poluidor), resoluções COMDEMA
  vigentes (01/2017, 03/2017, 05/2019, 06/2019, 08/2022, 09/2023, 11/2025), conferência de ART/RRT
  por conselho (CREA, CRBio ANO/Nº, CAU) e documentos sempre exigidos (matrícula, identificação).
  Use ao analisar processos de licenciamento de Campo Bom, calibrar o sistema ou revisar pareceres.
---

# Licenciamento Ambiental — Campo Bom/RS (v1.0)

Base de regras do repositório `gabrielhklaser/licenciamentoambiental` (painel Streamlit +
parecer técnico). Toda regra abaixo cita a norma; ao divergir de TR ou formulário,
**vale a norma vigente** e a divergência é registrada.

> **Dados:** o repositório GitHub contém SOMENTE dados fictícios. Documentos reais de
> processos (pastas do Drive) servem apenas para testar localmente; scripts de conferência
> com dados reais ficam no scratchpad, nunca no repo.

---

## 1. Documentos sempre exigidos (mesmo que o checklist esqueça)

| Documento | Regra | Onde no código |
|---|---|---|
| **Matrícula atualizada do imóvel** (≤ 90 dias) | Exigência implícita de TODO processo | `validador_documentos.com_matricula_obrigatoria` |
| **Identificação do empreendedor** (CNH, RG, CIN) | Exigência implícita | `documento_identificacao.EXIGENCIA_IDENTIFICACAO` |

**Arquivo com nome de um documento e conteúdo de outro** (ex.: "matrícula" que é cartão CNPJ):
o tipo vem do CONTEÚDO; a exigência fica "não apresentada" e o parecer explica:
*"o arquivo 'X', apresentado como Cópia da matrícula, contém o comprovante de inscrição no CNPJ
e, portanto, não comprova essa exigência"* (`compilador_parecer.RE_ARQUIVO_TROCADO`).

## 2. ART / RRT — por conselho

| Conselho | Registro | Numeração |
|---|---|---|
| CREA | ART | sequencial (ex.: 12345678) — compara o número inteiro |
| **CRBio** | ART | **ANO/Nº** no documento (ex.: `2026/12645`); formulário costuma trazer `12645/2026` ou só dígitos → é a MESMA ART |
| CAU/BR | RRT (formulários às vezes escrevem "RTT") | RRT/RTT é EXCLUSIVO do CAU (arquitetos e urbanistas); ART nunca é do CAU |

- Equivalência: `AuditorTecnico.chaves_art` / `arts_equivalentes` (forma (ano, sequencial) nos dois
  sentidos + dígitos). Exibição CRBio: `formatar_numero_art` → `2026/12645`.
- Nome no layout numerado do CRBio: `2.Nome: FULANO` (não confundir o rótulo com o nome).
- **Etapas cobertas:** o mesmo nº declarado para várias etapas (seção 4.3) e para o RT do
  licenciamento (seção 8) — a "Descrição sumária" da ART diz o que ela cobre; etapas fora dela
  (ex.: PGRS numa ART de "cobertura vegetal") → REVISAO_MANUAL pedindo ART própria.
  RT da seção 8 exige "licenciamento ambiental" na atividade da ART.
- **ART repetida** (mesmo nº em vários arquivos): conferida uma vez; cópias remetem à primeira.

## 3. Zoneamento — Plano Diretor (Lei Municipal 5.329/2022)

- Anexo 03 georreferenciado sobre o limite IBGE 2024 (método: skill `gis-multicamadas` §8);
  precisão ~18 m mediana / 42 m p90. **A Certidão de Zoneamento do Município prevalece.**
- Zonas: ZR1, ZR2, ZR3, ZC, ZM1, ZM2, ZI, ZEIS, ZIA, Rural, planície de inundação, bacia de
  contenção, Mata Atlântica; sobreposições ZEIC e "áreas com restrições".
- **Anexo 8** (`config/plano_diretor.json`, texto literal de cada célula):
  - indústria por **grau poluidor** (= potencial poluidor CONSEMA do formulário) e **porte =
    área construída m²** (existentes + a construir, sem vagas — Art. 62 §1º); ex.: ZR1 proíbe
    toda indústria; ZR2 baixo ≤ 250 m², médio ≤ 250 m² com EVU; ZM baixo < 1.500 m² (EVU até
    5.000), médio < 1.000 (EVU até 3.000); alto só na ZI;
  - comércio/serviço inócuo, IA1 e IA2 por faixas de m²; ZI proíbe habitação;
  - acima da última faixa = **porte máximo excedido = proibido** (Art. 62);
  - ZEIC proíbe IA2 exceto templos; atividades especiais: nunca na ZR1, sempre EIV (Art. 61 §3º).
- **Planície de inundação (Art. 41):** indústria alta e parcelamento proibidos; baixa/média só
  em edificação industrial pré-existente e autorizada, sem aumento de área nem de cota.
- ZEIS, ZIA, Rural, bacia de contenção e Mata Atlântica → análise específica (Rural:
  agroindústria de produtos locais; fracionamento mínimo 2 ha; parcelamento urbano proibido).
- Zona **limítrofe**: borda a menos de 50 m (incerteza + faixa de 30 m das ZM, Art. 34 §2º).
- EVU dispensável pela Comissão Técnica Urbanística; Art. 63 (desconformes) e Art. 64
  (excepcional em prédio industrial pré-existente, fora da ZR1) quando certidão ≠ Anexo 8.

## 4. CONSEMA 372/2018 (compilada 2025)

- Tabela `config/codram_consema372.json` (522 ramos) gerada por
  `ferramentas/extrair_codram_consema372.py`: no PDF compilado as linhas "Alterado pela
  Resolução X" são versões substituídas — vale a linha vigente de cada código.
- Conferir: código existe / não excluído; **potencial poluidor** declarado = tabela; **porte**
  pela medida na UNIDADE do CODRAM (área útil m²/ha, área total, construída, volume...).
- **Indústria = códigos 1000 a 3099** (gêneros industriais; 3100+ = obras/infraestrutura).
- CODRAM municipais: **3451,01** construção civil ≥ 500 m² (COMDEMA 05/2019, Médio);
  **3414,41** desmembramento urbano e **3414,45** rural (COMDEMA 09/2023, Licença Única).
- CONSEMA 520/2024 exclui o CODRAM de ERB.

## 5. Resoluções COMDEMA vigentes

| Resolução | Regra |
|---|---|
| 01/2017 | Comércio em geral, potencial baixo: pequeno ≤ 50 m², médio ≤ 200 m², grande > 200 m² |
| 03/2017 | LIR = LP + LI; LOR = LP + LI + LO (regularização) |
| 05/2019 | Construção civil/urbanização ≥ 500 m² → CODRAM 3451,01; porte soma áreas existentes; taxa Tabela A (Lei 4.439/2015) |
| 06/2019 | Esgoto de parcelamento: aprovação PRÉVIA da concessionária; rede coletora com separação absoluta (art. 8º); solução individual → gravame na matrícula para o Habite-se |
| **08/2022** | Supressão: alvará florestal; LCV com ART acima de 10 exemplares; **15 mudas por exemplar nativo OU exótico com DAP > 15 cm** e 10 mudas por metro estéreo abaixo; mudas ≥ 1,60 m (horto ≥ 1,80 m); conversão 7,5 URM/muda. Exóticas invasoras (Portaria SEMA 79/2013) dispensadas, exceto em parcelamento |
| 09/2023 | Desmembramento: urbano > 2.000 m² com vegetação/APP/sem infraestrutura; rural exige CAR, reserva legal e APP averbadas |
| 11/2025 | Retenção pluvial obrigatória com área construída ≥ 500 m² e em parcelamentos/desmembramentos: **V = 0,01 × área impermeabilizada (m³)**; estacionamento 30% permeável |
| ~~02/2017~~ | REVOGADA (3 mudas por exótico) — o TR RFO 2026 ainda a cita: vale a 08/2022 |
| ~~04/2019~~ | REVOGADA pela 08/2022 |

## 6. Como aplicar numa análise

1. Leia o formulário HTML (pleito, CODRAM, porte, potencial, área construída, coordenadas, ARTs).
2. Garanta as exigências implícitas (matrícula, identificação) e classifique anexos pelo CONTEÚDO.
3. Enquadramento CONSEMA → zona do Plano Diretor → exigências COMDEMA → ARTs por conselho.
4. Pendências entram no parecer em texto corrido (máx. 160 caracteres por item; nome de
   resultado sem a palavra "zoneamento" para não ser descartado como peça simples).
5. Confirme com o analista o que é classificação preliminar (natureza inócuo/IA1/IA2).

## 7. Fontes

Lei Municipal 5.329/2022 (PDDT); Resolução CONSEMA 372/2018 compilada 2025; Resoluções COMDEMA
citadas; Lei Municipal 4.439/2015 (taxas); Lei 4.966/2020 (arborização urbana); Lei 12.651/2012.
Acervo local das leis: pasta "leis" da mesa de trabalho da SEMA (não versionada).
