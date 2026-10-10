# Constraints

Última revisão: AAAA-MM-DD por @responsavel

> Leia este arquivo antes de escrever código. Não o afrouxe para fazer uma mudança passar.
> Todo número tem um motivo e um comando que o verifica. Sem comando, é desejo, não regra.

## Piso (sempre valendo, sem instalar nada)

- Sem comentários novos que silenciam verificação: `# noqa`, `# type: ignore`, `# nosec`, `# pylint: disable`, `# pragma: no cover`
- Sem código inacabado: `raise NotImplementedError`, `except: pass`, `TODO` no lugar da implementação
- Sem teste pulado ou apagado sem motivo escrito no commit (`skip`, `skipif`, `xfail`)
- Sem asserção removida de teste que continua existindo
- Sem segredos no código
- Este arquivo não é afrouxado para passar uma mudança

Verificado por: `python scripts/floor_guard.py --base main` (sai 1 se algo acima aparecer no diff).

## Aplicado com números

| Dimensão | Regra | Verificado por | Roda em |
|----------|-------|----------------|---------|
| Testes | Todos passam | `python -m pytest -q` | fim da tarefa, CI |
| Cobertura | Linhas alteradas: >= 80% | `python -m pytest --cov --cov-report=lcov` + diff | fim da tarefa |
| Segredos | Nenhum padrão de chave/token | `python qa_loop.py gates --paths <arquivos>` (portão de segredos do qa-loop) | toda edição |
| Estilo/erros | Zero erros do ruff | `python -m ruff check .` (instalar: `pip install ruff`) | toda edição |
| Tipos | Zero erros novos | `python -m mypy .` (instalar: `pip install mypy`) | fim da tarefa |
| Dependências | Nada de severidade alta ou maior | `python -m pip_audit` (instalar: `pip install pip-audit`) | CI |

Ao menos uma regra deve ser **externa** (opina sem depender dos testes do projeto): `pip_audit` e `ruff` cumprem.

## Medido, ainda não imposto (catraca: não pode piorar)

| Métrica | Hoje | Direção |
|---------|------|---------|
| Cobertura do projeto | (medir e preencher) | não pode cair |

Medir primeiro e travar nesse valor é melhor que inventar um número que a base não atinge.

## Exceções

| ID | Regra | Caminho | Motivo | Dono | Expira |
|----|-------|---------|--------|------|--------|
| (nenhuma) | | | | | |

Toda exceção tem dono e prazo (padrão: 90 dias). Caminhos isentos do guarda ficam em `.constraintsignore`.
