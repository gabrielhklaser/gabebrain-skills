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

The automation engine (fonte canônica) is located at:
`C:\Users\Gabriel\.gemini\config\skills\arena-ai-controller\scripts\arena_agent.py`

Cópias espelhadas (manter idênticas à canônica): `GabeBrain\.claude\skills\…`, `GabeBrain\.agents\skills\…` e o repo `gabebrain-skills`. As pastas `scratch\arena-controller\` e `scratch\agentearena\` são versões antigas — não usar.

Credenciais ficam só no `.env` da skill (`ARENA_EMAIL`, `ARENA_PASSWORD`, opcional `ARENA_USER_DATA_DIR`). Sem fallback no código.

### Dados de sessão são descartáveis

O perfil do navegador (cookies de login) fica em `ARENA_USER_DATA_DIR`, por padrão `C:\Users\Gabriel\.gemini\antigravity\scratch\arena_user_data`. Ele **nunca** deve ficar dentro do vault ou do Google Drive: o script avisa se estiver.

- Pode ser apagado a qualquer momento: `arena_agent.py purge-session`. O próximo uso refaz o login pelo `.env`.
- Com `ARENA_PURGE_AFTER_USE=1` no `.env`, o perfil é apagado ao fim de cada execução. É mais seguro, mas exige login a cada uso.
- Pastas `.session_data` de versões antigas da skill são removidas automaticamente a cada execução.

### Skills GabeBrain na nuvem

Em conversas **novas**, o `send` prefixa o prompt com uma instrução para o Arena consultar as skills do repo `gabebrain-skills`: `superpowers-coding-agent` para código, `no-ai-slop` e `escrita-tecnica-humanizada` para texto. Desative com `--no-skill-prefix` ou troque o texto via `ARENA_SKILL_PREFIX` no `.env`. Follow-ups e cliques de confirmação não recebem o prefixo.

### Verificação dos seletores

`status` retorna `selectors: {ok, counts, broken}`. Se `ok` for `false`, a UI do Arena mudou e os seletores em `arena_agent.py` (`EDITOR_SELECTOR`, `MESSAGE_SELECTOR`) precisam de ajuste. O `send` também inclui `warnings` no resultado quando não encontra nenhuma mensagem, e o Hub mostra esses avisos na nota.

### Roteamento antes de despachar

Antes de enviar ao Arena, passe o prompt pelo `prompt-router-coordinator` (regras em `routing_rules.json`, as mesmas que o Hub usa). Se ele indicar `antigravity` (localhost, Drive, Biblioteca, QGIS) ou `claude`, não despache para o Arena.

### Contrato de saída (`send` / `recover-push`)

A última linha do stdout é `[RESULT_JSON] {…}` (JSON em uma linha). Durante a execução, `[CONVERSATION_URL] <url>` é emitido assim que a conversa existe.

| `status` | Significado | Ação |
|---|---|---|
| `success` | Geração terminou | Registrar resposta |
| `waiting_user_input` | Agente pediu confirmação/escolha (`options`) | Responder com `send --conversation-url <url> --prompt "<opção>"` |
| `timeout` | Tempo local esgotou, agente segue rodando na nuvem | Não reenviar o prompt; retomar pela mesma `conversation_url` |

`response` contém apenas as mensagens novas desde o envio (não o histórico inteiro da conversa).

Um prompt curto (≤35 caracteres) que coincide exatamente com o texto de um botão visível vira clique, mas só quando `--conversation-url` é informado.

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

#### 3b. Status / Connect
```bash
python "C:\Users\Gabriel\.gemini\config\skills\arena-ai-controller\scripts\arena_agent.py" status
python "C:\Users\Gabriel\.gemini\config\skills\arena-ai-controller\scripts\arena_agent.py" connect --repo "gabrielhklaser/REPO_NAME" [--branch "BRANCH_NAME"]
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
