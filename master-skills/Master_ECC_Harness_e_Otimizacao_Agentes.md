---
tipo: agente-master
origem:
  - "gabebrain-skills/skills/ecc-harness-optimizer"
versao: 1.0
data_consolidacao: 2026-09-28
tags:
  - agente
  - dominio/engenharia-software
  - ecc
  - harness
  - master-skill
  - otimizacao-tokens
  - tipo/agente-master
---
# Master Skill 25: ECC — Harness Operating System e Otimização de Agentes

## 🎯 Objetivo e Identidade
Sistema Operacional de Contexto e Harness para Agentes Autônomos (**Everything Claude Code / Enhanced Coding Context**). Atua como a **espinha dorsal de execução e otimização** do ecossistema GabeBrain, garantindo economia extrema de tokens, preservação de contexto, planejamento em fases, ciclo rigoroso de TDD/verificação e memória durável compartilhada entre todos os agentes (Antigravity, Arena AI, Claude Code e Obsidian).

---

## 🧠 Filosofia Central do ECC no GabeBrain
> *"Otimize a janela de contexto ao máximo. Persista todo o resto em memória durável."*

Em vez de permitir que os agentes acumulem conversas gigantescas que diluem o raciocínio e desperdiçam cotas de tokens, o ECC impõe uma disciplina operacional de **alta densidade informacional** e **execução orientada a fases**.

---

## ⚡ Pilares de Otimização Aplicados a Todos os Agentes

### 1. Pipeline Estruturado de 6 Fases (ECC Execution Loop)
Todos os agentes do GabeBrain (seja desenvolvendo código, redigindo laudos ambientais, consultando geologia ou gerando mapas GIS) operam sob o ciclo:
1. **Plan (Planejamento e Decomposição):** Mapeamento prévio de intenções, escopo e dependências (`plan-canvas`, `prompt-optimizer`). Nenhum arquivo é alterado antes da aprovação do plano.
2. **Test (TDD / Critérios de Sucesso):** Definição de testes ou specs de validação antes da implementação (`tdd-workflow`).
3. **Implement (Execução Cirúrgica):** Edição pontual com menor diff possível, mantendo integridade e docstrings.
4. **Review (Auditoria de Código e Segurança):** Verificação de lint, anti-AI slop e análise de risco (`delivery-gate`, `skillspector-auditor`).
5. **Verify (Loop de Verificação):** Execução do pipeline de testes e conferência real antes de declarar conclusão (`verification-loop`).
6. **Remember (Memória Durável & Aprendizado):** Registro durável de handoffs e padrões no banco SQLite do ECC (`ecc memory`, `continuous-learning-v2`).

### 2. Engenharia e Compactação Estratégica de Contexto (`strategic-compact`)
- **Ponto de Troca de Fase:** Compactação manual ou sugerida após a fase de exploração/pesquisa, preservando apenas o plano para a execução.
- **Prevenção de Truncamento Arbitrário:** Evita perdas catastróficas de instruções no meio de tarefas complexas.
- **Alocação Racional de Tokens:** Leitura seletiva de páginas (`biblioteca.py ler`) e consultas cirúrgicas via MCP em vez de ingestão de arquivos massivos no contexto imediato.

### 3. Memória Durável Multi-Harness (`ecc memory`)
- Armazenamento em SQLite centralizado (`~/.claude/ecc/state.db`).
- Compartilhamento de contexto persistente entre diferentes plataformas:
  - Antigravity (orquestrador local)
  - Arena AI (executor em nuvem)
  - Claude Code / Obsidian (edição de notas e prompts)

### 4. Otimizador de Prompts Nativo (`prompt-optimizer`)
- Analisa rascunhos de prompts gerados no Obsidian ou no chat.
- Detecta intenção, escopo e stack tecnológico do projeto.
- Conecta automaticamente as melhores skills e ferramentas do GabeBrain antes do disparo do comando.

---

## 🛠️ Procedimentos Operacionais Padrão (SOP)

### 1. Diagnóstico e Status do Ecossistema ECC
Para auditar a saúde das instalações, sessões ativas e banco de dados de estado:
```bash
ecc status
```

### 2. Consulta Inteligente de Componentes e Estratégia
Recomenda agentes, perfis e skills adequadas para uma determinada tarefa a partir de linguagem natural:
```bash
ecc consult "auditoria de seguranca em scripts python"
ecc consult "refatoracao de api com tdd e testes e2e"
```

### 3. Registro e Recuperação de Memória entre Sessões (Handoffs)
Transferir contexto consolidado entre plataformas sem poluir o histórico:
```bash
# Gravar handoff de contexto
ecc memory handoff --from antigravity --target arena --title "Migracao concluida" --stdin

# Buscar contexto persistido
ecc memory search "decisao de arquitetura do pipeline"
```

### 4. Verificação de Saúde e Integridade dos Agentes
Diagnosticar ou reparar componentes e configurações alteradas:
```bash
ecc doctor
ecc repair --dry-run
```

---

## 🔄 Matriz de Atuação com os Agentes do GabeBrain

| Agente do GabeBrain | Papel Otimizado pelo ECC | Benefício Direto |
| :--- | :--- | :--- |
| **Arena AI Controller (21)** | Despacha prompts otimizados pelo pipeline ECC para containers na nuvem | Redução de tokens e maior taxa de sucesso na primeira execução |
| **VCS Version Agent (22)** | Integrado ao lifecycle de commit seguro e handoffs de branches | Paridade bidirecional garantida com histórico durável |
| **SkillSpector Auditor (24)** | Atua como gatekeeper de segurança na fase de Review do ECC | Zero vulnerabilidades antes da fusão de código |
| **Docling & Biblioteca (11-14)** | Fornece extração cirúrgica de evidências para o contexto do ECC | Janela de contexto limpa e sem ruído de PDFs brutos |
| **GIS Multicamadas (20)** | Executa mapas em camadas sob validação do loop de verificação | Mapas e coordenadas conferidos antes da entrega |
