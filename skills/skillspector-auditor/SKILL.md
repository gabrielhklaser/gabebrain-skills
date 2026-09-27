---
name: skillspector-auditor
description: Agente auditor de segurança de skills e ferramentas de IA (NVIDIA SkillSpector) no ecossistema GabeBrain. Varre e audita skills contra 71 padrões de vulnerabilidade (injeção de prompt, exfiltração de dados, escalada de privilégios, assinaturas YARA de malware, subprocessos perigosos e MCP least-privilege).
allowed-tools:
  - run_command
  - view_file
  - write_to_file
---

# SkillSpector Auditor - Agente de Segurança de Skills GabeBrain

Este agente integra o motor **NVIDIA SkillSpector** ao ecossistema GabeBrain para auditar, classificar e garantir a segurança de todas as skills e ferramentas utilizadas pelos agentes locais e na nuvem (Arena.ai).

## 🛡️ Capacidades e Cobertura de Detecção

O SkillSpector analisa o código fonte, scripts (`.py`, `.ps1`, `.sh`, `.vbs`), manifests e arquivos `SKILL.md` contra **71 padrões de segurança em 17 categorias**:
- **YR1 / YARA:** Assinaturas de malware, trojans, reverse shells e ransomware.
- **AST / Dangerous Code:** Execução arbitrária de comandos via `subprocess`, `os.system`, `eval`, `exec`.
- **PE / Privilege Escalation & Credential Access:** Acesso a arquivos de credenciais (`.env`, SSH keys, tokens).
- **SC / Supply Chain:** Bytecode Python órfão (`__pycache__`, `.pyc`), dependências não pinadas, desvio de empacotamento.
- **LP / Least Privilege:** Verificação de escopo de ferramentas declaradas (`allowed-tools` em `SKILL.md`).
- **PI / Prompt Injection & Evasion:** Padrões de manipulação de contexto, quebra de guardrails e ofuscação Unicode.

## 🚀 Como Executar

### 1. Auditoria Geral em Lote (Batch Scan)
Para varrer todas as skills ativas do GabeBrain:
```bash
python "C:\Users\Gabriel\.gemini\config\skills\skillspector-auditor\scripts\run_audit.py"
```

### 2. Auditoria Direta via CLI de uma Skill Específica
```bash
"C:\Users\Gabriel\.gemini\antigravity\scratch\SkillSpector\.venv\Scripts\skillspector.exe" scan "<CAMINHO_DA_SKILL>" --no-llm
```

### 3. Exportar Relatório em JSON ou Markdown
```bash
"C:\Users\Gabriel\.gemini\antigravity\scratch\SkillSpector\.venv\Scripts\skillspector.exe" scan "<CAMINHO_DA_SKILL>" --no-llm -f markdown -o relatorio_seguranca.md
```

## 📋 Diretrizes de Remediação no GabeBrain

1. **Bytecode compilado (`.pyc` / `__pycache__`):** Nunca versionar pastas `__pycache__` dentro de pastas de skills. Adicione ao `.gitignore`.
2. **Checagens de Rede em Scripts (`System.Net.Sockets.TcpClient`):** Substituir conexões brutas de socket por chamadas de conectividade seguras e documentadas (ex: `Test-NetConnection`) para evitar falso-positivo com a regra YARA `reverse_shell`.
3. **Escopo de Ferramentas:** Sempre declare o campo `allowed-tools` no frontmatter YAML de todo `SKILL.md`.
4. **Tratamento de Credenciais:** Carregar credenciais via variáveis de ambiente do sistema (`os.environ`) em vez de ler arquivos `.env` hardcoded.
