---
name: vcs-version-agent
description: >-
  Controlador e gerenciador de versões dos projetos GabeBrain. Garante paridade
  bidirecional entre ambiente local e GitHub (online e offline), reconcilia commits
  feitos na Arena.ai web (branches arena/* e bot merges), realiza snapshots automáticos
  e verificação pré-prompt e no boot da máquina.
allowed-tools:
  - bash
  - read
  - write
  - fetch
  - env
---

# GabeBrain VCS Agent (Controlador e Gerenciador de Versões)

O **GabeBrain VCS Agent** é o agente autônomo responsável pelo ciclo de vida, integridade e controle de versão de todos os projetos locais e remotos do GabeBrain.

---

## 🎯 Objetivos Centrais

1. **Paridade Absoluta Local <-> GitHub**:
   - Manter a versão local idêntica à versão do GitHub e vice-versa.
   - Puxar automaticamente atualizações remotas antes de iniciar trabalho local.
   - Enviar commits locais para o repositório remoto assim que houver conectividade.

2. **Resiliência Offline / Online**:
   - **Offline**: Salva qualquer modificação em commits estruturados de snapshot local (`chore(offline-sync): ...`), garantindo que nenhum trabalho seja perdido ou sobrescrito por falha de rede.
   - **Online**: Executa reconciliação de histórico, rebase/merge defensivo e sobe commits pendentes com segurança.

3. **Reconciliação com a Arena.ai Web**:
   - O usuário frequentemente interage diretamente pelo navegador em `https://arena.ai/`, gerando commits remotos pelo bot da Arena ou em branches dedicadas (`origin/arena/<uuid>-<repo>`).
   - O agente detecta automaticamente o surgimento dessas branches e commits no GitHub, incorporando as novidades ao ambiente local.

4. **Automação no Boot do Sistema e Pré-Prompt**:
   - **Boot do Windows**: Executado silenciosamente via `Startup\GabeBrain-VCS-Startup.vbs` no logon da máquina, preparando todos os repositórios antes mesmo do usuário abrir o terminal ou a IDE.
   - **Pré-Prompt**: Verificação instantânea antes de processar tarefas ou prompts que alterem código.

---

## 🛠️ Localização e Ferramentas

- **Script Principal do Motor**:
  `C:\Users\Gabriel\.gemini\config\skills\vcs-version-agent\scripts\vcs_agent.py`
  *(cópia de trabalho em `C:\Users\Gabriel\.gemini\antigravity\scratch\vcs-agent\vcs_agent.py`)*
- **Script de Inicialização do Windows**:
  `C:\Users\Gabriel\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\GabeBrain-VCS-Startup.vbs`
- **Registro de Projetos**:
  `C:\Users\Gabriel\.gemini\config\vcs_projects.json`
- **Ledger de Estado & Histórico**:
  `C:\Users\Gabriel\.gemini\config\vcs_state.json`
- **Arquivo de Log**:
  `C:\Users\Gabriel\.gemini\antigravity\logs\vcs_sync.log`

---

## 💻 Comandos CLI do Agente

### 1. Painel de Status Completo
Exibe uma tabela com o status de cada projeto cadastrado, branch ativa, quantidade de commits adiante/atrás, alterações não commitadas e detecção da Arena.ai:
```bash
python "C:\Users\Gabriel\.gemini\config\skills\vcs-version-agent\scripts\vcs_agent.py" status
```

### 2. Sincronização Geral (Todos os Projetos)
Executa o ciclo completo de commit local + pull remoto + merge de branches Arena + push para o GitHub:
```bash
python "C:\Users\Gabriel\.gemini\config\skills\vcs-version-agent\scripts\vcs_agent.py" sync
```

### 3. Sincronização de Projeto Específico
```bash
python "C:\Users\Gabriel\.gemini\config\skills\vcs-version-agent\scripts\vcs_agent.py" sync --repo licenciamentoambiental
```

### 4. Verificação Pré-Prompt (Rápida)
Verifica se há novidades no GitHub ou na Arena.ai antes de iniciar prompts de código. Se houver, sincroniza imediatamente:
```bash
python "C:\Users\Gabriel\.gemini\config\skills\vcs-version-agent\scripts\vcs_agent.py" check --repo licenciamentoambiental
```

### 5. Modo Forçado Offline (Garantir Commits Locais de Segurança)
```bash
python "C:\Users\Gabriel\.gemini\config\skills\vcs-version-agent\scripts\vcs_agent.py" sync --force-offline
```

### 6. Escanear e Cadastrar Novos Projetos
Escaneia automaticamente pastas do GabeBrain e adiciona repositórios Git recém-criados:
```bash
python "C:\Users\Gabriel\.gemini\config\skills\vcs-version-agent\scripts\vcs_agent.py" scan
```

### 7. Cadastrar Repositório Manualmente
```bash
python "C:\Users\Gabriel\.gemini\config\skills\vcs-version-agent\scripts\vcs_agent.py" add "C:\Caminho\Do\Projeto" --name "meu-projeto"
```

---

## 🔄 Protocolo de Resolução de Conflitos e Segurança

- Se ocorrer divergência que impeça `pull --rebase` limpo:
  1. O agente **nunca destrói** trabalho local.
  2. Cria automaticamente uma branch de segurança: `backup/conflict-YYYYMMDD-HHMMSS`.
  3. Aborta o rebase para manter a árvore intacta.
  4. Emite um alerta detalhado registrando os arquivos conflitantes para o desenvolvedor ou subagente analisar.
