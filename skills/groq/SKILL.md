---
name: groq
description: >-
  Operario barato via Groq (plano gratuito): extracao de campos em JSON e resumos de
  textos PUBLICOS ou ficticios (ex.: preencher registros da Fase 2 do deep-research,
  resumir trechos do acervo). Use quando o Gabriel pedir "use o Groq" ou houver lote
  grande de extracao/resumo mecanico sem dado privado. NAO decide (use o Jev) e NAO
  serve para redacao final nem para laudos/processos reais.
allowed-tools:
  - bash
  - read
---

# Groq — operário barato

**Papel:** gerar texto mecânico barato. Decisões continuam com o Jev (regra 9); qualidade final passa pelo `qa-loop`.
**Privacidade:** tudo enviado sai do computador (`api.groq.com`) e o plano gratuito tem política de dados menos favorável. **Nunca envie material privado** (processos, clientes, laudos, e-mails reais) sem perguntar ao Gabriel (regra 9c).
**Chave:** segredo `GROQ_API_KEY` no PowerShell SecretStore (criptografado por usuário do Windows). Ordem de leitura: variável de ambiente → variável de usuário → SecretStore → `.env` (nunca dentro do vault, que sincroniza com o Drive). Nunca imprimir a chave.
Cadastro/troca da chave (no seu terminal; o valor é pedido de forma oculta): `Set-Secret -Name GROQ_API_KEY`.

## Uso

```bash
python scripts/groq_worker.py status
python scripts/groq_worker.py extract --file trecho.txt --fields poco,vazao,data
python scripts/groq_worker.py summarize --file trecho.txt --max-words 100
python scripts/groq_worker.py compose --file pedido.txt     # reescreve o pedido como prompt claro (gpt-oss-20b); nao responde
python scripts/groq_worker.py answer --file pergunta.txt --model qwen/qwen3.8-27b   # resposta direta, sem ferramentas
```

`compose` e `answer` alimentam o roteador automático do GabeBrain Hub (o Groq reformata e o Jev classifica). O Hub só os chama depois da varredura local de privacidade.

## Limites do plano gratuito (verificados em 2026-10-02, mudam com frequência)

Modelos de chat (`openai/gpt-oss-120b`, `openai/gpt-oss-20b`, `qwen/qwen3.8-27b`): 30 req/min, 1.000 req/dia, 8K tokens/min, 200K tokens/dia. Whisper: 20 req/min, 2.000 req/dia. Limites por organização. O script recusa entrada acima de ~6.000 tokens e respeita `Retry-After` em 429 (até 3 tentativas). Em lote, divida em blocos e espere ~1 req a cada 2 s.

Fonte: https://console.groq.com/docs/rate-limits

## Testes

```bash
cd scripts && python -m pytest test_groq_worker.py -q
```
