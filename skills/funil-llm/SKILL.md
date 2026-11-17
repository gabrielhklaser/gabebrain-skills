---
name: funil-llm
description: >-
  Funil antes do LLM (conselho do Karpathy): codigo corta o grosso, o Jev tria o resto e so o que sobra vai
  para o modelo. Use quando houver muitos candidatos para analisar com IA (resultados de busca, scraping,
  videos, artigos, linhas de tabela, registros de banco) e antes de transcrever, ler na integra ou extrair
  campos de cada um. Nao use para um item so nem para material privado na camada Jev.
---

# funil-llm — código, depois Jev, depois LLM

Nunca mande 100% de uma lista ao modelo. Primeiro filtre com código (grátis), depois tríe com o Jev (centavos), e só então leia, transcreva ou extraia com o LLM.

| Camada | Quem | Custo | O que faz |
|---|---|---|---|
| 1 | `scripts/funil.py` + `regras.yaml` | zero | obrigatórios, domínios, datas, números, palavras, duplicatas, ordem, limite |
| 2 | Jev (`--jev-pergunta`) | centavos | uma pergunta sim/não por item; P ≥ 0,7 aprova, P ≤ 0,3 descarta, o meio fica `_funil_incerto` |
| 3 | LLM (você, Groq, subagente) | caro | só lê o arquivo de saída |

## Quando é obrigatório

- **Mais de 20 candidatos** antes de qualquer leitura integral, transcrição (`watch`) ou extração (`groq`).
- Na Fase 2 do deep research (`web-scout`, `research-deep`): os resultados de busca de cada item passam pelo funil antes de abrir as páginas.
- Tabela ou banco grande: filtre com pandas/SQL até ficar só o que a pergunta precisa; nunca exporte tudo para o modelo.

Com 20 candidatos ou menos, a camada 1 basta (sem Jev).

## Uso

`$FUNIL` = `C:\Users\Gabriel\.claude\biblioteca-de-skills\funil-llm\scripts\funil.py`

```bash
python "$FUNIL" --entrada candidatos.jsonl --regras regras.yaml --saida aprovados.jsonl
python "$FUNIL" --entrada candidatos.jsonl --regras regras.yaml --saida aprovados.jsonl \
    --jev-pergunta "A fonte traz dados de recarga de aquífero?" --jev-campos titulo,resumo
```

Entrada: JSONL, JSON (lista ou `{"itens": [...]}`) ou CSV. Saída: JSONL e `aprovados.relatorio.json` com quantos itens cada regra cortou.

## regras.yaml

Todas as chaves são opcionais; chave desconhecida dá erro (sem filtro silencioso). Modelo em `regras.exemplo.yaml`.

```yaml
campos_obrigatorios: [url, titulo]
dedupe: url                       # URL normalizada: sem www, barra final e utm_*
dominios_bloqueados: [pinterest.com, quora.com]
dominios_permitidos: []           # vazio = todos
data: {campo: data, desde: 2024-01-01, ate: 2026-12-31}
numeros: {views: {min: 1000000}}  # aceita "1.200.000" e "2,5"
palavras: {campos: [titulo, resumo], todas: [], alguma: [aquífero, groundwater], nenhuma: [casino]}
ordenar: {campo: views, desc: true}
limite: 50
```

## Regras

- **Leia o relatório.** Corte demais (saída 0 ou regra cortando > 90%) ⇒ afrouxe a regra e diga ao Gabriel qual mudou. Não pule o funil.
- **Itens `_funil_incerto`**: você decide (exceção (a) do mandato 9) e declara que foi você.
- **Jev indisponível**: o script deixa tudo passar e registra `indisponivel`; siga com a camada 1 e avise.
- **Privacidade**: a camada 2 envia texto para fora. Processos, clientes, laudos e e-mails reais só com o OK do Gabriel; a camada 1 é local e sempre pode.
- Filtrar é decisão determinística (exceção (d) do mandato 9): não precisa do Jev para escolher a regra, só para triar o que a regra não resolve.

## Testes

`cd scripts && python -m unittest test_funil`
