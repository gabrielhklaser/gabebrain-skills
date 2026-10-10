---
name: constraints-python
description: >-
  Contrato de qualidade para projetos Python do GabeBrain: modelo de CONSTRAINTS.md e o guarda
  floor_guard.py, que vigia no diff se alguem afrouxou a barra para passar (teste pulado ou apagado,
  asserção removida, aviso silenciado, stub, limite reduzido). Use ao iniciar um projeto Python,
  antes de rodar um agente em modo autônomo, quando um agente "resolve" falhas desligando
  verificações, ou como portão extra do loop-gatekeeper/qa-loop. Adaptação da skill
  constraint-driven-development (agent-skills, MIT).
---

# constraints-python

Os testes que o próprio agente escreveu não provam sozinhos que a qualidade se manteve. Esta skill grava o padrão do projeto num arquivo e checa o diff para ver se alguém o baixou.

## Quando usar
- Projeto novo ou significativo sem padrão de qualidade escrito.
- Antes de modo autônomo (`/build auto`) ou de um loop sem humano.
- Um agente passa a "ficar verde" desligando testes ou silenciando avisos.
- Portão da Fase 1 do `qa-loop` em projeto com git.

Não usar em script descartável, protótipo de poucos dias ou pasta sem git (o guarda sai com 2).

## Como usar
1. **Detectar antes de perguntar:** ler `pyproject.toml`/`requirements.txt`, pasta de testes e CI. Perguntar só o que sobrar, no máximo 4 perguntas, cada uma com palpite e padrão (use `interview-me`).
2. **Criar `CONSTRAINTS.md`** na raiz a partir de `CONSTRAINTS.template.md`. Cada número com motivo e comando. Sem número em mente: medir hoje e travar nesse valor (catraca).
3. **Apontar no CLAUDE.md/AGENTS.md** do projeto: `Leia CONSTRAINTS.md antes de escrever código. Não o afrouxe para passar.`
4. **Rodar o guarda** (na raiz do repositório):
   ```bash
   python scripts/floor_guard.py --base main
   ```
   Saída 0 = limpo; 1 = alguém baixou a barra (bloquear); 2 = não rodou (sem git ou sem base): nunca tratar como 0.
5. **Exceções legítimas:** linha na tabela de exceções com dono e prazo, ou caminho em `.constraintsignore`. Nunca apagar a regra.

## O que o guarda pega
Silenciador novo (`noqa`, `type: ignore`, `nosec`, `pragma: no cover`), código inacabado, teste pulado/apagado, asserção removida, regra ou limite do `CONSTRAINTS.md` afrouxado ou removido, exceção nova. Apertar é silencioso.

Limites: é raso de propósito (regex sobre o diff). Pega o caminho mais barato até o verde, não alguém decidido a esconder uma mudança. Relata arquivo e linha, nunca o conteúdo da linha.

## Integração
- `loop-gatekeeper`: rodar após `qa_loop.py gates`; saída 1 = veto da Fase 1; saída 2 = registrar que o portão não rodou.
- O portão de segredos e de testes já existem no `qa_loop.py`; esta skill não os duplica.

## Instalação do que o modelo cita (não vem pronto)
`pip install ruff mypy pip-audit`. `pytest` e `pytest-cov` já existem na máquina.

## Verificação
- [ ] `CONSTRAINTS.md` existe e todo número tem motivo e comando que roda hoje.
- [ ] `floor_guard.py` sai 0 na base atual sem mudanças.
- [ ] Ao menos uma regra externa (ruff, pip-audit).
- [ ] Exceções com dono e prazo.
- [ ] `python -m pytest scripts/` passa (testes do próprio guarda).
