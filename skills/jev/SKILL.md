---
name: jev
description: >-
  Classifica, pontua e decide com o Jev (TypeSafe System One), um modelo que nao escreve:
  recebe texto + perguntas tipadas e responde em ~instantes por quase nada. Use quando o
  Gabriel pedir "use Jev para classificar/triar/pontuar estes textos" (e-mails, notas,
  tickets, leads, trechos de documentos), quando houver lote de itens para rotular, ou
  quando uma decisao curta (escolher opcao, dar nota, probabilidade sim/nao) puder sair
  do agente principal. Nao use para gerar texto.
allowed-tools:
  - bash
  - read
  - write
---

# Jev — decide, você escreve

**Regra do ecossistema:** Jev decide, o agente escreve. Quando Jev não tiver certeza, o agente decide.
**Privacidade:** tudo enviado ao Jev sai do computador (API `api.typesafe.ai`). **Pergunte ao Gabriel antes de enviar qualquer coisa privada** (e-mails reais, dados de clientes, processos, dados pessoais, notas do vault marcadas como sensíveis). Texto público ou fictício pode ir sem perguntar.

## Como funciona (doc: https://docs.typesafe.ai/llms.txt)

- Endpoint: `POST https://api.typesafe.ai/v1/systemone`, `Authorization: Bearer <TYPESAFE_API_KEY>`, modelo `jev-latest` (hoje resolve para `jev-1.13.x`). Chamada **direta** — não usa OpenRouter.
- Corpo: `{"state": <texto|objeto>, "model": "jev-latest", "questions": {<id>: <pergunta>}}`. Várias perguntas por chamada (barato: faça perguntas especulativas e filtre no código).
- 3 tipos de pergunta, e só esses:
  | tipo | `criteria` | resposta |
  |---|---|---|
  | `choice` | objeto `{opcao: descrição}` | `choice`, `probabilities`, `confidence` |
  | `score` | lista ordenada `["ruim","ok","ótimo"]` | `score` (contínuo, 0..n-1), `legend`, `probabilities`, `confidence` |
  | `noul` | opcional `{"true":..,"false":..}` | `noul` = P(sim), sem `confidence` |
- Confiança é um segundo eixo: a resposta diz *o quê*; `confidence` diz *se vale agir*. O script marca `INCERTO` abaixo de 0,7 (limiar do GabeBrain, ajustável com `--threshold`; para `noul` usa a distância de 0,5). **Incerto = o agente decide.**
- Erros: 401 chave inválida, 422 pedido inválido, 429 rate limit, 529 sobrecarga (o script faz backoff exponencial em 429/529).

## Uso

`$JEV` = `C:\Users\Gabriel\.gemini\config\skills\jev\scripts\jev.py`

```bash
python "$JEV" status                                   # há chave? (nunca a mostra)
python "$JEV" setup                                    # Gabriel digita a chave (oculta) no terminal
python "$JEV" balance [--set USD]                      # saldo ESTIMADO; --set recalibra com o valor do console
python "$JEV" selftest                                 # teste real com e-mail fictício
python "$JEV" ask --state-file texto.txt --questions perguntas.json [--threshold 0.7] [--json]
```

`perguntas.json` — chaves livres:
```json
{"tipo": {"type": "choice", "instructions": "Que tipo de documento é este?",
          "criteria": {"laudo": "Laudo técnico", "norma": "Norma ou regulamento", "outro": "Outro"}},
 "relevante": {"type": "noul", "instructions": "Trata de hidrogeologia?"}}
```

## Fluxo para "use Jev para classificar estes"

1. Defina com o Gabriel (ou infira) as perguntas; escreva o JSON em arquivo temporário.
2. **Checagem de privacidade**: o conteúdo é privado? Se sim, pergunte antes de enviar.
3. Para cada item: `ask --json`. Em lote, um `state` por chamada (a API julga um estado por vez).
4. Consolide numa tabela: item, resposta, confiança. Itens `INCERTO` você mesmo decide, dizendo que foi você.
5. Reporte tempo total, tokens, custo e saldo estimado (o `ask --json` traz `cost_usd` e `balance_usd_estimated`).

## Saldo (estimado, não real)

A API da TypeSafe **não expõe saldo** (sem endpoint de billing nem cabeçalho de crédito; só `/v1/models` e `POST /v1/systemone`). Por isso `jev.py` mantém um livro-caixa local em `%LOCALAPPDATA%\gabebrain\jev\ledger.json`: saldo = crédito inicial (US$ 10) − gasto calculado com os tokens que a API reporta. Preço usado: **US$ 0,042 / 1M tokens de entrada, saída grátis** (cookbook da doc, jev-1.12, 2026-09 — confirme no console). Cada chamada (Claude, Antigravity ou Hub) atualiza o mesmo arquivo; o painel do GabeBrain Hub o exibe. Sempre diga "estimado". Se o console mostrar valor diferente: `jev.py balance --set <USD>`.

## Chave e segurança

- `setup` grava `TYPESAFE_API_KEY` em `C:\Users\Gabriel\.gemini\config\skills\jev\.env` (local; `.gitignore` e o sync do vault já excluem `.env`). Alternativa: variável de ambiente `TYPESAFE_API_KEY`.
- Nunca peça a chave no chat, nunca a imprima, nunca a grave no vault/Drive.
- Chave compartilhada por acidente → revogar em https://console.typesafe.ai/keys.
