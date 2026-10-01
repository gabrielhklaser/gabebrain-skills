---
name: qa-loop
description: >-
  Loop de qualidade LIMITADO entre um agente gerador e um avaliador: portoes deterministicos
  (testes, compilacao, JSON, segredos) + pontuacao de pilares pelo Jev + decisao com teto de
  iteracoes, deteccao de estagnacao e veto. Use depois que qualquer agente entregar codigo,
  laudo, texto ou pesquisa e a entrega precisar ser validada antes de ir ao Gabriel/vcs-sync.
allowed-tools:
  - bash
  - read
  - write
---

# qa-loop — mede, pontua barato, decide com limite

Script: `.claude/skills/qa-loop/scripts/qa_loop.py` (Python 3.10+, sem dependencias). Testes: `pytest scripts/`.

## Regra central: o loop nunca e infinito
Garantido em codigo (`decide`), nao so em texto:
- **Teto:** 3 iteracoes por padrao; `--max-iter` e limitado a 5 (`HARD_MAX_ITERATIONS`).
- **Estagnacao:** ganho < 3 pontos entre rodadas consecutivas (ou regressao) => `ESCALAR`.
- **Veto:** gate critico falho ou veto do Jev => reprova, qualquer que seja a nota.
- **Fim obrigatorio:** o loop so termina em `APROVADO` ou `ESCALAR` (decide o Gabriel). Nunca "repete ate passar".

## Fluxo de uma rodada
0. `classify --artifact-file X` — o Jev escolhe a rubrica (`dev|geo|ciencia`) e diz se a entrega e **trivial**
   (trivial => so os gates, sem ciclo de revisao). Confianca < 0,7 => o agente escolhe.
1. `gates` — mede de verdade: compila `.py`, valida `.json`, varre segredos, roda `--test-cmd`.
2. `score` — o Jev responde os pilares (`score`) e vetos (`noul`) da rubrica numa unica chamada barata.
   Pilar com confianca < 0,7 volta como `incerto`: o agente pontua e reenvia com `--override pilar=0..1`.
3. `decide` — grava o historico e devolve `APROVADO | REPROVADO | ESCALAR | PENDENTE_AGENTE`.
4. Se `REPROVADO`: **o agente escreve** o feedback (o Jev nao escreve), citando evidencia (`arquivo:linha`,
   saida do teste) dos pilares fracos e gates falhos. Tom objetivo, sem agressividade.
5. `validate` — confere o JSON final antes de entregar.

```bash
python qa_loop.py gates --paths entrega.py --test-cmd "python -m pytest -q" --out gates.json
python qa_loop.py score --rubric dev --spec-file spec.txt --artifact-file entrega.py --gates gates.json --out score.json
python qa_loop.py decide --history-file historico.json --score score.json --max-iter 3
```

## Quando usar Jev x agente
| Etapa | Quem |
|---|---|
| Pontuar pilares, detectar vetos | **Jev** (centavos; ~ms) |
| Medir testes/sintaxe/segredos | **codigo** (gates) |
| Pilar `incerto`, escrever feedback, resolver ESCALAR | **agente** |
| Avaliacao profunda de dominio (UI viva, parecer academico, appsec) | avaliadores existentes, chamados por cima |

**Privacidade:** o Jev envia texto para `api.typesafe.ai`. O script detecta **localmente** CPF, CNPJ, e-mail,
telefone e numero de processo/protocolo/matricula e, se achar, **nao envia nada** (modo `agente (privado detectado)`).
So use `--autorizado-privado` depois que o Gabriel autorizar. `--privado` forca o modo local (o agente pontua tudo
via `--override`). Jev indisponivel cai no mesmo modo automaticamente. A heuristica e um piso, nao garantia: material
sensivel sem esses padroes (laudos reais, dados de clientes) continua exigindo pergunta ao Gabriel.

**Chave:** `TYPESAFE_API_KEY` (variavel de usuario do Windows, compartilhada por Claude, Antigravity e Codex).

## Rubricas (`rubricas/*.json`)
`dev` (codigo), `geo` (laudos/hidrologia/GIS/licenciamento), `ciencia` (texto academico/pesquisa). Pesos somam 100;
aprovacao >= 85 sem veto. Para criar outra, copie uma e ajuste `pilares` e `vetos`.

## Saida final obrigatoria (validada por `validate`)
```json
{"nota_final": 0, "status": "APROVADO|REPROVADO|ESCALAR", "analise_breve": "2 linhas",
 "feedbacks_de_correcao": ["acao concreta com evidencia"], "iteracao": 1, "modo": "jev|agente"}
```
