---
name: skillspector-auditor
description: Agente auditor de segurança de skills e ferramentas de IA (NVIDIA SkillSpector) no ecossistema GabeBrain. Varre e audita skills contra 71 padrões de vulnerabilidade (injeção de prompt, exfiltração de dados, escalada de privilégios, assinaturas YARA de malware, subprocessos perigosos e MCP least-privilege).
allowed-tools:
  - bash
  - read
  - write
  - fetch
  - env
---

# SkillSpector Auditor - Agente de Segurança de Skills GabeBrain

Este agente integra o motor NVIDIA SkillSpector ao ecossistema GabeBrain para auditar, classificar e garantir a segurança de todas as skills e ferramentas utilizadas pelos agentes locais e na nuvem (Arena.ai).

## Capacidades e Cobertura de Detecção

O SkillSpector analisa o código fonte, scripts de automação, manifests e arquivos de documentação contra 71 padrões de segurança em 17 categorias:
- **YR1 / YARA:** Assinaturas de malware, trojans, reverse shells e ransomware.
- **AST / Dangerous Code:** Execução arbitrária de comandos sem sanitização.
- **PE / Privilege Escalation:** Acesso indevido a credenciais e segredos.
- **SC / Supply Chain:** Bytecode Python órfão, dependências não pinadas, desvio de empacotamento.
- **LP / Least Privilege:** Verificação de escopo de ferramentas declaradas no frontmatter.
- **PI / Prompt Injection & Evasion:** Padrões de manipulação de contexto e quebra de guardrails.

## Como Executar

### 1. Auditoria Geral em Lote (Batch Scan)
Para varrer todas as skills ativas do GabeBrain:
```bash
python run_audit.py
```

### 2. Auditoria Direta via CLI de uma Skill Específica
```bash
skillspector scan TARGET_DIR --no-llm
```

### 3. Exportar Relatório em JSON ou Markdown
```bash
skillspector scan TARGET_DIR --no-llm -f markdown -o relatorio_seguranca.md
```

## Diretrizes de Remediação no GabeBrain

1. **Bytecode compilado:** Nunca versionar pastas de cache compilado dentro de pastas de skills.
2. **Checagens de Rede em Scripts:** Substituir conexões brutas de socket por chamadas de conectividade seguras e documentadas para evitar falso-positivo com a regra YARA de reverse shell.
3. **Escopo de Ferramentas:** Sempre declare o campo de ferramentas permitidas no frontmatter YAML de toda skill.
4. **Tratamento de Credenciais:** Carregar credenciais via variáveis de ambiente do sistema em vez de ler arquivos locais fixos.
