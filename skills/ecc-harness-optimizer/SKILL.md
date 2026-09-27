---
name: ecc-harness-optimizer
description: Sistema operacional de harness e otimizador de agentes (Everything Claude Code - ECC) no ecossistema GabeBrain. Gerencia economia de tokens, planejamento em 6 fases (Plan-Test-Implement-Review-Verify-Remember), engenharia de contexto, TDD, loop de verificação e memória durável compartilhada via SQLite entre Claude Code, Antigravity, Arena AI e Obsidian.
allowed-tools:
  - bash
  - read
  - write
  - fetch
  - env
---

# ECC Harness Optimizer - Sistema Operacional de Agentes GabeBrain

O **ECC Harness Optimizer** implementa a arquitetura de engenharia de contexto e harness operacional do **ECC (Everything Claude Code)** para governar e otimizar todos os agentes do ecossistema GabeBrain.

## Objetivos e Capacidades
- **Otimização de Contexto:** Redução drástica do desperdício de tokens por meio de compactação estratégica (`strategic-compact`) e orçamentação de contexto (`context-budget`).
- **Pipeline de Execução em Fases:**
  1. `Plan`: Formulação de escopo, dependências e canvas antes de tocar no código.
  2. `Test`: TDD (Red-Green-Refactor) com criação prévia de specs de validação.
  3. `Implement`: Modificações cirúrgicas com diffs mínimos.
  4. `Review`: Revisão estrita de padrões e auditoria de segurança com o SkillSpector.
  5. `Verify`: Verificação em dois passos garantindo que todos os testes passem.
  6. `Remember`: Registro persistente de handoffs e lições no SQLite (`~/.claude/ecc/state.db`).
- **Otimizador de Prompts Nativo:** Transforma rascunhos de prompts gerados no Obsidian ou chat em comandos blindados e mapeados para as ferramentas ideais.

## Como Executar

### 1. Diagnóstico do Estado do ECC
```bash
ecc status
```

### 2. Consulta Inteligente de Componentes
Descobre skills, agentes e perfis ideais para uma determinada solicitação:
```bash
ecc consult "DESCRICAO_DA_TAREFA"
```

### 3. Memória Durável e Handoffs entre Sessões
```bash
# Gravar handoff de contexto
ecc memory handoff --from antigravity --target arena --title "Sessao concluida" --stdin

# Buscar contexto persistido
ecc memory search "TERMO_DE_BUSCA"
```

### 4. Verificação de Saúde e Integridade dos Agentes
```bash
ecc doctor
```
