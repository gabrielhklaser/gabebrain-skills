---
name: arena-ai-controller
description: >-
  Controls the Arena AI platform (https://arena.ai/) in Agent Mode. Use this skill
  whenever the user wants to interact with Arena AI, relay prompts to Arena AI,
  connect GitHub repositories, select branches, or recover lost repository connections
  by opening a new chat and pushing conversation branch changes.
allowed-tools:
  - bash
  - read
  - write
  - fetch
  - env
---

# Arena AI Controller Skill

This skill enables Antigravity to automate and control the **Arena AI** platform (`https://arena.ai/`), specializing in **Agent Mode**, GitHub repository integration, and automated failover recovery.

## Regra de Ouro: Priorização Absoluta da Execução no Arena AI (Economia de Tokens)

1. **Prioridade 1 (Padrão de Execução - Nuvem Arena AI):**
   - O agente deve **SEMPRE priorizar este caminho**: delegar tarefas para execução na plataforma **Arena AI**.
   - As skills devem ser consumidas diretamente pelo Arena AI a partir do repositório `gabrielhklaser/gabebrain-skills` (ou no repositório conectado do projeto).
   - Qualquer geração de código, testes, refatoração, análises extensas e tarefas iterativas devem rodar dentro da infraestrutura do Arena AI, economizando os tokens locais do Antigravity.

2. **Prioridade 2 (Exceção: Uso do Motor Antigravity apenas quando necessário arquivo do GabeBrain):**
   - O motor local do Antigravity **SÓ deve ser acionado** quando for estritamente necessário acessar arquivos físicos ou bibliotecas locais do GabeBrain que não existem no repositório GitHub:
     - Acervo físico da Biblioteca Geológica no Google Drive (`10-Trabalho/Geologia/Biblioteca Geologica/`).
     - Textos integrais e notas estruturadas do acervo Docling / Mestrado no disco local.
     - Ferramentas locais de desktop (ex: QGIS Desktop, automações do SO).
   - **Fluxo Híbrido nesses casos:** O Antigravity atua unicamente como **Orquestrador** (faz a busca e leitura cirúrgica do trecho/página necessária via scripts locais da biblioteca) e despacha o prompt com esse contexto embutido para o **Arena AI executar** o restante.

---

## Capabilities

1. **Persistent Authentication**: Automatically signs in using user credentials and keeps session cookies active.
2. **Prompt Relaying**: Takes user prompts from chat and sends them to Arena AI Agent Mode, streaming and returning the agent's responses.
3. **GitHub Repository & Branch Management**: Automatically enables the GitHub toggle, lists repositories, and selects target repositories and branches.
4. **Automated Failover & Recovery**: If Arena AI loses its connection to the working repository, this skill:
   - Identifies the conversation's active branch.
   - Starts a fresh conversation on Arena AI.
   - Reconnects the GitHub repository and branch.
   - Issues the reload and push instruction so all project changes and history are preserved and pushed to GitHub.

---

## Tooling & Helper Scripts

The automation engine is located at:
`C:\Users\Gabriel\.gemini\config\skills\arena-ai-controller\scripts\arena_agent.py`
and in the workspace scratch at:
`C:\Users\Gabriel\.gemini\antigravity\scratch\arena-controller\arena_agent.py`

### CLI Commands

#### 1. Verify Login & Session Status
```bash
python "C:\Users\Gabriel\.gemini\config\skills\arena-ai-controller\scripts\arena_agent.py" login
```

#### 2. List Connected GitHub Repositories
```bash
python "C:\Users\Gabriel\.gemini\config\skills\arena-ai-controller\scripts\arena_agent.py" list-repos
```

#### 3. Send Prompt to Arena AI Agent
```bash
python "C:\Users\Gabriel\.gemini\config\skills\arena-ai-controller\scripts\arena_agent.py" send --prompt "YOUR PROMPT HERE" --repo "gabrielhklaser/REPO_NAME" --branch "BRANCH_NAME"
```

#### 4. Automatic Reconnection & Push Recovery
When Arena AI drops the repository connection or fails to sync:
```bash
python "C:\Users\Gabriel\.gemini\config\skills\arena-ai-controller\scripts\arena_agent.py" recover-push --repo "gabrielhklaser/REPO_NAME" --branch "BRANCH_NAME"
```

This command will:
1. Open a new chat session at `https://arena.ai/agent`.
2. Connect to the specified GitHub repository and select the branch.
3. Send the command to reload the prior conversation state and push modified files directly to GitHub.
