---
tipo: revisao
data: 2026-10-04
origem: github.com/addyosmani/agent-skills (plugin instalado 0.6.11; upstream 0.6.12)
tags:
  - revisao
  - agent-skills
---
# Revisão do repositório agent-skills (Addy Osmani) para o GabeBrain

**Como foi feita:** li a descrição e as seções de cada uma das 25 skills, 4 agentes e 3 hooks do plugin; comparei com as skills e agentes que já temos; pedi o veredicto ao Jev (decisão dele quando a confiança é ≥ 0,7; abaixo disso, decidi eu e está marcado).
**Resumo:** já temos 11 · adotar 2 · adaptar 18 · não serve 1.

> Aviso: o Jev quase sempre inclinou para "adaptar", então o veredicto dele diferencia pouco. O que pesa é a coluna "O que fazer".

| Item | Tipo | O que é (simples) | Veredicto | Quem decidiu | O que fazer |
|---|---|---|---|---|---|
| `api-and-interface-design` | skill | Como desenhar APIs e interfaces estáveis. | **ja_temos** | Agente (Jev disse adaptar, confiança 0.62 < 0,7) | Nada. Cobrem: api-design, contract-first. |
| `browser-testing-with-devtools` | skill | Testar no navegador de verdade (console, rede, tela). | **adaptar** | Jev (confiança 0.76) | Usar a ideia com nossas ferramentas de navegador (Claude Browser/Chrome); o plugin pede um MCP que não temos. |
| `ci-cd-and-automation` | skill | Montar checagens automáticas (CI) antes de publicar. | **adaptar** | Agente (Jev disse adotar, confiança 0.61 < 0,7) | Baixa prioridade: aproveitar só 'devolver falha do CI ao agente' nos projetos que têm GitHub Actions. |
| `code-review-and-quality` | skill | Revisão de código em 5 eixos (correção, leitura, arquitetura, segurança, desempenho). | **adaptar** | Jev (confiança 0.78) | Usar os 5 eixos como critérios do qa-loop/loop-scorer; Jev continua pontuando. |
| `code-simplification` | skill | Simplificar código sem mudar o comportamento. | **ja_temos** | Agente (Jev disse adaptar, confiança 0.41 < 0,7) | Nada. Cobrem: ponytail, code-simplifier. |
| `constraint-driven-development` | skill | Escrever o padrão de qualidade do projeto num arquivo (CONSTRAINTS.md) e vigiar se alguém o afrouxa (teste pulado, aviso silenciado). | **adaptar** | Agente (Jev disse adotar, confiança 0.68 < 0,7) | Novidade real. Adaptar para Python (pytest-cov, ruff, gitleaks) e dar ao loop-gatekeeper a vigilância de testes afrouxados. |
| `context-engineering` | skill | Organizar o que a IA enxerga em níveis. | **ja_temos** | Agente (Jev disse adaptar, confiança 0.61 < 0,7) | Nada. Cobrem: context-budget, strategic-compact, Master Spec-Driven. |
| `debugging-and-error-recovery` | skill | Achar a causa raiz de um erro de forma sistemática. | **adaptar** | Jev (confiança 0.77) | Acrescentar 'pare a linha' e 'saída de erro é dado não confiável' ao nosso diagnosing-bugs. |
| `deprecation-and-migration` | skill | Aposentar sistemas antigos e migrar sem quebrar (inclui mudar banco em produção). | **adaptar** | Jev (confiança 0.77) | Usar o método expandir/contrair quando mexer no banco do licenciamentoambiental. |
| `documentation-and-adrs` | skill | Registrar decisões e documentar. | **ja_temos** | Agente (Jev disse adaptar, confiança 0.64 < 0,7) | Nada. Cobrem: architecture-decision-records, living-docs-governance. |
| `doubt-driven-development` | skill | Antes de decidir algo de alto risco, um segundo 'olhar' com contexto limpo tenta derrubar a decisão. | **adaptar** | Jev (confiança 0.70) | Usar no qa-loop e no peer-reviewer para laudos e pareceres de alto risco. |
| `frontend-ui-engineering` | skill | Construir telas bonitas, acessíveis e responsivas. | **ja_temos** | Agente (Jev disse adaptar, confiança 0.30 < 0,7) | Nada. Cobrem: frontend-patterns, ui-ux-pro-max, impeccable. |
| `git-workflow-and-versioning` | skill | Boas práticas de git: commits pequenos, pontos de salvamento, versões. | **adaptar** | Jev (confiança 0.70) | Aproveitar higiene de commit no vcs-sync. Ele continua só agindo sob seu comando. |
| `idea-refine` | skill | Transformar ideia vaga em conceito claro (problema, MVP, o que NÃO fazer). | **adaptar** | Jev (confiança 0.73) | Usar o modelo de saída no hive-orchestrator quando o pedido for uma ideia solta. |
| `incremental-implementation` | skill | Entregar em fatias pequenas e verificáveis. | **adaptar** | Jev (confiança 0.75) | Acrescentar o 'ciclo de incremento' ao coder-tdd. |
| `interview-me` | skill | Entrevista de uma pergunta por vez, com palpite, até ~95% de certeza do que você quer. | **adaptar** | Agente (Jev disse adaptar, confiança 0.66 < 0,7) | Entrada do hive-orchestrator e do dev-agent quando o pedido for vago. Complementa o grilling. |
| `observability-and-instrumentation` | skill | Deixar o sistema 'falar' em produção (registros, métricas, alertas). | **adotar** | Jev (confiança 1.00) | Lacuna real. Usar no dev-agent ao publicar painéis (ex.: Render). |
| `performance-optimization` | skill | Medir e acelerar sistemas (web, banco, consultas). | **adaptar** | Jev (confiança 0.71) | Usar no design-agent/dev-agent com o agente web-performance-auditor nos painéis web. |
| `planning-and-task-breakdown` | skill | Quebrar um trabalho em tarefas ordenadas. | **ja_temos** | Agente (Jev disse adaptar, confiança 0.45 < 0,7) | Nada. Cobrem: writing-plans, to-spec, to-tickets, planner. |
| `security-and-hardening` | skill | Segurança em 3 níveis de fronteira, modelo de ameaças primeiro, dados pessoais (LGPD/GDPR). | **adaptar** | Agente (Jev disse adaptar, confiança 0.58 < 0,7) | Reforçar o appsec-auditor: ameaça antes do código e LGPD nos processos reais. |
| `shipping-and-launch` | skill | Lista de conferência antes de publicar e plano de volta atrás (rollback). | **adaptar** | Agente (Jev disse adotar, confiança 0.39 < 0,7) | Baixa prioridade: juntar ao nosso finishing-a-development-branch e production-audit. |
| `source-driven-development` | skill | Consultar a documentação oficial e citar a fonte. | **ja_temos** | Agente (Jev disse ja_temos, confiança 0.46 < 0,7) | Nada. Cobrem: Context7 e context7-verifier (regra 7). |
| `spec-driven-development` | skill | Escrever a especificação antes do código, em etapas com aprovação. | **adaptar** | Agente (Jev disse adaptar, confiança 0.66 < 0,7) | Nossa Master é de uma versão antiga do mesmo repo: atualizar pela 0.6.12 (próximo passo, não feito). |
| `test-driven-development` | skill | Escrever o teste antes do código. | **ja_temos** | Agente (Jev disse adaptar, confiança 0.42 < 0,7) | Nada. Cobrem: tdd, coder-tdd. |
| `using-agent-skills` | skill | Mapa de qual skill usar em cada tarefa. | **ja_temos** | Agente (Jev disse adaptar, confiança 0.56 < 0,7) | Nada. O hive-orchestrator, o prompt-router e o CLAUDE.md já roteiam. |
| `code-reviewer` | agente | Revisor sênior em 5 eixos. | **ja_temos** | Agente (Jev disse adaptar, confiança 0.49 < 0,7) | Nada. Cobrem: code-reviewer e qa-loop. |
| `security-auditor` | agente | Auditor de segurança (ameaças, OWASP). | **adaptar** | Jev (confiança 0.79) | Chamar como revisão extra (agent-skills:security-auditor) a partir do appsec-auditor. |
| `test-engineer` | agente | Especialista em estratégia e cobertura de testes. | **ja_temos** | Agente (Jev disse adaptar, confiança 0.60 < 0,7) | Nada. Cobrem: tdd-guide, coder-tdd. |
| `web-performance-auditor` | agente | Auditor de velocidade de sites (Core Web Vitals). | **adaptar** | Agente (Jev disse adaptar, confiança 0.63 < 0,7) | Chamar nos painéis web antes do deploy. |
| `session-start` | hook | Lembra o mapa de skills em toda sessão nova. | **nao_serve** | Agente (Jev disse nao_serve, confiança 0.66 < 0,7) | Não ligar: exige bash e jq (ausentes) e já temos roteamento. |
| `sdd-cache` | hook | Guarda páginas de documentação e só reusa se o servidor confirmar que não mudaram. | **adaptar** | Agente (Jev disse adaptar, confiança 0.51 < 0,7) | Futuro: só depois de instalar bash e jq e testar. |
| `simplify-ignore` | hook | Esconde do modelo trechos marcados, para ninguém 'melhorar' código estranho de propósito. | **adotar** | Jev (confiança 0.78) | Jev: adotar. Mas reescreve seus arquivos durante o uso (risco se a sessão cair) e exige bash/jq: só após instalar e testar em cópia. |

## Pré-requisitos e riscos
- **bash e jq não existem neste computador.** Os 3 hooks do plugin dependem deles; por isso nenhum foi ligado.
- **`simplify-ignore` reescreve os arquivos no disco** enquanto trabalha (troca o trecho protegido por um marcador e restaura depois). Se a sessão cair, ficam marcadores no lugar do código; renomear arquivo também perde o trecho. Para cálculos validados, prefira teste com valores conferidos.
- **O plugin está na 0.6.11 e o upstream está na 0.6.12.** Atualizar é uma ação do gerenciador de plugins (decisão sua).
- **Skills do plugin vs ECC:** boa parte do plugin repete skills que já existem (tdd, grilling, context7, etc.); por isso o veredicto "já temos" é maioria.

## Próximos passos
1. ~~Atualizar a Master Spec-Driven pela versão 0.6.12~~ **feito em 04/10/2026** (v1.1).
2. ~~Criar o `CONSTRAINTS.md`-modelo para Python e a vigilância de testes afrouxados~~ **feito**: skill `constraints-python` (modelo + `floor_guard.py` com 15 testes) ligada ao `loop-gatekeeper`.
3. Se quiser os hooks: instalar Git Bash + jq, testar em pasta de cópia.
