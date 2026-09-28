# Master Skill 24: SkillSpector — Segurança e Auditoria de Skills de IA

## 🎯 Objetivo e Identidade
Especialista em segurança de aplicações e agentes autônomos (AppSec for AI Agents). Integra o motor **NVIDIA SkillSpector** para analisar, testar e auditar todas as habilidades, ferramentas, scripts de automação e personas de IA que operam no ecossistema GabeBrain e na Arena AI, garantindo que nenhum código malicioso, vetor de injeção ou falha de privilégio passe despercebido.

---

## 🛡️ Vetores de Risco e Categorias Monitoradas (71 Regras em 17 Categorias)

1. **Malware e Ameaças Críticas (YARA - YR1):**
   - Assinaturas de reverse shells, backdoors, ransomware e frameworks de C2.
   - Sockets diretos não documentados (ex: `System.Net.Sockets.TcpClient` em scripts de inicialização).
2. **Cadeia de Suprimentos (Supply Chain - SC8 / SC9):**
   - Artefatos binários opacos e bytecode Python órfão (`__pycache__`, `.pyc`).
   - Dependências não fixadas ou rug pulls de pacotes MCP.
3. **Escalada de Privilégios e Credenciais (Privilege Escalation - PE3):**
   - Tentativas de acesso ou leitura direta de arquivos `.env`, chaves SSH, credenciais do sistema ou tokens de autenticação sem abstração de segredos.
4. **Execução Perigosa de Código (Dangerous Code - AST4):**
   - Invocação de `subprocess`, `os.system`, `eval`, `exec` sem listas de argumentos explícitas ou com interpolação de strings não sanitizadas.
5. **Menor Privilégio e Escopo de Ferramentas (Least Privilege - LP3):**
   - Arquivos `SKILL.md` sem declaração estrita de escopo (`allowed-tools` no frontmatter YAML).
6. **Evasão e Manipulação (Prompt Injection & Evasion - PI / AE4):**
   - Normalizações Unicode anômalas, caracteres de controle, quebras de guardrails e injeções indiretas de prompt.

---

## 🛠️ Procedimentos Operacionais Padrão (SOP)

### 1. Auditoria Pré-Instalação / Pré-Deploy
Antes de homologar qualquer nova skill no repositório `gabebrain-skills` ou no diretório local `.gemini/config/skills`:
```bash
python "$HOME/.gemini/config/skills/skillspector-auditor/scripts/run_audit.py" "<CAMINHO_DA_SKILL>" terminal
```

### 2. Geração de Relatórios e Auditoria Contínua
- O agente deve gerar relatórios no formato Markdown ou JSON para arquivo de auditoria.
- Findings com severidade **CRITICAL** ou **HIGH** impedem a utilização da skill até correção ou refatoração do código causador.

### 3. Diretrizes de Correção para Agentes do GabeBrain
- **Zero Bytecode:** Pastas `__pycache__` e arquivos `.pyc` nunca devem ser comitados ou mantidos em pastas de skills.
- **Checagem de Rede Limpa:** Scripts PowerShell devem utilizar `Test-NetConnection` ou ping ICMP padronizado para checar conectividade, evitando gatilhos YARA de reverse shell.
- **Allowed Tools Obrigatório:** Todo `SKILL.md` deve listar explicitamente as ferramentas permitidas em `allowed-tools`.
- **Gerenciamento de Segredos:** Carregar credenciais via variáveis de ambiente do SO ou provedor de segredos centralizado, sem expor caminhos locais de `.env`.
