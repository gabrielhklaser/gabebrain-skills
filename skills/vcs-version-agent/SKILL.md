---
name: vcs-version-agent
description: >-
  Controlador e gerenciador de versões dos projetos GabeBrain. Verifica o estado
  local e remoto, reconcilia commits feitos na Arena.ai web (branches arena/* e
  bot merges) e executa sincronizações somente sob comando explícito do usuário.
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

1. **Inspeção Local <-> GitHub**:
   - Exibir alterações locais, commits à frente/atrás e branches `arena/*` pendentes.
   - O modo de verificação pode atualizar referências com `git fetch`, mas não altera a árvore de trabalho nem envia commits.
   - Pull, merge, commit e push só ocorrem após comando explícito `sync`.

2. **Resiliência Offline / Online**:
   - **Offline**: a sincronização manual pode criar um commit local; não há snapshot automático de arquivos modificados.
   - **Online**: a sincronização manual pode fazer rebase/pull e enviar commits já existentes.
   - Arquivos não commitados são preservados por padrão; incluí-los requer `--commit-dirty` e um único `--repo` explícito.

3. **Reconciliação com a Arena.ai Web**:
   - O usuário pode interagir pelo navegador em `https://arena.ai/`, criando commits remotos em branches `origin/arena/<uuid>-<repo>`.
   - O agente detecta essas branches e commits para revisão; auto-merge exige as duas opções locais de aprovação documentadas abaixo.

4. **Verificação no Boot e Pré-Prompt**:
   - **Boot do Windows**: `Startup\GabeBrain-VCS-Startup.vbs` executa uma verificação, sem commit, pull, merge ou push.
   - **Pré-prompt**: `check` informa divergências e não sincroniza automaticamente.

---

## 🛠️ Localização e Ferramentas

- **Script principal**: `skills/vcs-version-agent/scripts/vcs_agent.py` (execute da raiz deste repositório).
- **Script de inicialização do Windows**: `skills/vcs-version-agent/scripts/GabeBrain-VCS-Startup.vbs`; sem `GABEBRAIN_SKILLS_DIR`, espera o checkout instalado em `%USERPROFILE%\.gemini\config\skills`.
- **Configuração e estado**: `%USERPROFILE%\.gemini\config\vcs_projects.json` e `vcs_state.json` no Windows, ou `~/.gemini/config/` nos demais sistemas. `GABEBRAIN_CONFIG_DIR` permite substituir esse diretório.
- **Logs**: `%USERPROFILE%\.gemini\antigravity\logs\vcs_sync.log` no Windows, ou `~/.gemini/antigravity/logs/` nos demais sistemas. No POSIX, diretórios e arquivos de configuração/log recebem permissões privadas.
- URLs remotas podem conter credenciais; mantenha a configuração local protegida e prefira credenciais Git gerenciadas pelo sistema, não URLs com senha.

## 💻 Comandos CLI do Agente

Execute os exemplos a partir da raiz do repositório.

### 1. Painel de Status Completo
Exibe o status dos projetos já cadastrados, branch ativa, quantidade de commits adiante/atrás e alterações não commitadas. Não descobre nem registra repositórios automaticamente:
```bash
python skills/vcs-version-agent/scripts/vcs_agent.py status
```

### 2. Sincronização Geral (Projetos Cadastrados)
Executa pull/rebase e push de commits já existentes nos projetos cadastrados e limpos. Projetos com arquivos não commitados são **ignorados sem alterações**; por padrão, o comando não faz `git add`, commit ou push de mudanças de trabalho:
```bash
python skills/vcs-version-agent/scripts/vcs_agent.py sync
```

### 3. Sincronização de Projeto Específico
```bash
python skills/vcs-version-agent/scripts/vcs_agent.py sync --repo licenciamentoambiental
```

### Incluir alterações locais após revisão (opt-in)
Confira `git status` e inspecione cada arquivo. `--commit-dirty` exige `--repo` para limitar a operação a um projeto; online, o commit pode ser enviado ao GitHub:
```bash
python skills/vcs-version-agent/scripts/vcs_agent.py sync --repo licenciamentoambiental --commit-dirty
```

### 4. Verificação Pré-Prompt e no Boot
`check` atualiza referências remotas com `git fetch` quando online e apenas informa divergências. Não faz commit, pull, merge ou push; o script executado no boot usa o mesmo modo de verificação:
```bash
python skills/vcs-version-agent/scripts/vcs_agent.py check --repo licenciamentoambiental
```

### 5. Modo Forçado Offline (sem push)
O modo offline não envia dados. Alterações locais continuam preservadas; para criar um snapshot, use `--commit-dirty` junto de `--repo` após revisar os arquivos:
```bash
python skills/vcs-version-agent/scripts/vcs_agent.py sync --repo licenciamentoambiental --force-offline --commit-dirty
```

### 6. Escanear e Cadastrar Novos Projetos
A descoberta de repositórios é explícita; `status` e `sync` atuam apenas na lista local já cadastrada:
```bash
python skills/vcs-version-agent/scripts/vcs_agent.py scan
```

### 7. Cadastrar Repositório Manualmente
```bash
python skills/vcs-version-agent/scripts/vcs_agent.py add "/caminho/do/projeto" --name "meu-projeto"
```

### Auto-merge de branches da Arena.ai
Por padrão, branches `origin/arena/*` são apenas detectadas; não são incorporadas automaticamente. O merge permanece desativado até que o proprietário inspecione explicitamente os commits e defina **ambas** as opções no arquivo local `vcs_projects.json`:

```json
{
  "auto_merge_arena": true,
  "arena_merge_reviewed": true
}
```

Configurações antigas que tenham apenas `auto_merge_arena: true` continuam sem merge automático.

## 🔄 Protocolo de Resolução de Conflitos e Segurança

- Se ocorrer divergência que impeça `pull --rebase` limpo:
  1. O agente **nunca destrói** trabalho local.
  2. Cria automaticamente uma branch de segurança: `backup/conflict-YYYYMMDD-HHMMSS`.
  3. Aborta o rebase para manter a árvore intacta.
  4. Emite um alerta detalhado registrando os arquivos conflitantes para o desenvolvedor ou subagente analisar.
