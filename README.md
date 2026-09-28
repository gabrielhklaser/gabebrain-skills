# GabeBrain Skills & Agents Hub 🧠⚡

Repositório central de **Master Skills**, agentes especializados e protocolos operacionais do ecossistema **GabeBrain** (@gabrielhklaser).

Projetado especificamente para integração com o **Arena AI** (`https://arena.ai/`), permitindo que prompts enviados a partir do **Antigravity** executem diretamente no ambiente de nuvem do Arena AI consumindo as habilidades, diretrizes e padrões de engenharia consolidados do ecossistema.

---

## 🏛️ Arquitetura Híbrida: Antigravity (Orquestrador) x Arena AI (Executor)

Para economizar a cota de tokens do Antigravity e acelerar entregas pesadas:

- **Arena AI (Executor em Nuvem):**
  - Conectado a este repositório no GitHub via seletor nativo do Arena AI.
  - Executa tarefas pesadas de codificação, refatoração, criação de testes, processamento de dados e pipelines complexas em container cloud isolado.
  - **Custo de tokens locais:** Zero.
- **Antigravity (Orquestrador Local):**
  - Envia comandos de alto nível para o Arena AI através do subagente/skill `arena-ai-controller`.
  - Atua como ponte quando tarefas exigem acesso aos acervos físicos locais (PDFs da Biblioteca Geológica no Google Drive, extrações Docling no disco, QGIS Desktop).
  - Extrai cirurgicamente apenas as evidências necessárias e as envia prontas no prompt para o Arena AI continuar a execução.

Consulte o detalhamento completo em [`protocols/arena_antigravity_bridge.md`](protocols/arena_antigravity_bridge.md).

---

## 📚 Catálogo das 26 Master Skills

As Master Skills residem no diretório [`master-skills/`](master-skills/) e formam a base teórica e normativa de raciocínio de todos os agentes:

| # | Master Skill | Descrição e Foco Técnico |
|:---:|:---|:---|
| **01** | [`Master_GIS_Geoprocessamento`](master-skills/Master_GIS_Geoprocessamento.md) | GeoPandas, Shapely, PyQGIS, Leaflet, Folium, SRS/EPSG, operações topológicas |
| **02** | [`Master_Hidrologia_e_Recursos_Hidricos`](master-skills/Master_Hidrologia_e_Recursos_Hidricos.md) | Telemetria ANA, curvas-chave, bacias hidrográficas, balanço hídrico superficial |
| **03** | [`Master_Auditoria_Documental_e_PDF`](master-skills/Master_Auditoria_Documental_e_PDF.md) | Extração de laudos, análise de conformidade ambiental, OCR, regex forense |
| **04** | [`Master_Seguranca_e_Auditoria_de_Codigo`](master-skills/Master_Seguranca_e_Auditoria_de_Codigo.md) | OWASP Top 10, sanitização de inputs, proteção de credenciais, AppSec |
| **05** | [`Master_Frontend_Design_e_UI_Engineering`](master-skills/Master_Frontend_Design_e_UI_Engineering.md) | Tailwind, React, Vue, CSS Tokens, Micro-interações, acessibilidade WCAG |
| **06** | [`Master_Orquestracao_e_Hive_Mind_Agentes`](master-skills/Master_Orquestracao_e_Hive_Mind_Agentes.md) | Protocolos multi-agente, consenso distribuído, hive mind, delegação |
| **07** | [`Master_Arena_AI_Agent_Controller`](master-skills/Master_Arena_AI_Agent_Controller.md) | Automação Playwright, GitHub branches arena/*, auto-failover, reconexão |
| **08** | [`Master_Spec_Driven_Development_e_Engenharia_Contexto`](master-skills/Master_Spec_Driven_Development_e_Engenharia_Contexto.md) | SDD, TDD, prompts baseados em especificações rígidas, contratos de API |
| **09** | [`Master_Transcricao_Ritmo_e_Notacao_Musical`](master-skills/Master_Transcricao_Ritmo_e_Notacao_Musical.md) | DSP de áudio, detecção de transientes, MusicXML, quantização rítmica |
| **10** | [`Master_Paleoclima_e_Geologia_Espacial`](master-skills/Master_Paleoclima_e_Geologia_Espacial.md) | Reconstruções paleogeográficas, interpolação climática, Deep Time |
| **11** | [`Master_Docling_Leitor_Documentos_GabeBrain`](master-skills/Master_Docling_Leitor_Documentos_GabeBrain.md) | IBM Docling, extração de tabelas complexas, equações LaTeX, chunking estruturado |
| **12** | [`Master_Biblioteca_Pesquisavel_e_Acervo_Tecnico`](master-skills/Master_Biblioteca_Pesquisavel_e_Acervo_Tecnico.md) | Busca léxica por página, citação formal estrita com cota e página |
| **13** | [`Master_Ontologias_e_Modelagem_Conhecimento`](master-skills/Master_Ontologias_e_Modelagem_Conhecimento.md) | Web Semântica, OWL, RDF, SPARQL, OntoUFO, modelagem conceitual |
| **14** | [`Master_IHC_e_Engenharia_Semiotica`](master-skills/Master_IHC_e_Engenharia_Semiotica.md) | Avaliação de comunicabilidade, Jakobson, design centrado no usuário |
| **15** | [`Master_Machine_Learning_e_Ciencia_de_Dados`](master-skills/Master_Machine_Learning_e_Ciencia_de_Dados.md) | Algoritmos espaciais, k-NN, DBSCAN, projeções LAMP/NCA, validação cruzada |
| **16** | [`Master_Engenharia_e_Arquitetura_Software`](master-skills/Master_Engenharia_e_Arquitetura_Software.md) | SWEBOK v4, Clean Architecture, SOLID, padrões de projeto, CI/CD |
| **17** | [`Master_Geoestatistica_e_Modelagem_Espacial`](master-skills/Master_Geoestatistica_e_Modelagem_Espacial.md) | Variografia, krigagem ordinária/indicadora, simulação estocástica SGS |
| **18** | [`Master_Geofisica_Computacional_e_Inversao`](master-skills/Master_Geofisica_Computacional_e_Inversao.md) | Campos potenciais (gravimetria/magnetometria), FFT, inversão geofísica |
| **19** | [`Master_Geotectonica_e_Cinematica_Placas`](master-skills/Master_Geotectonica_e_Cinematica_Placas.md) | Tectônica global, polos de Euler, abertura oceânica, ciclos de Wilson |
| **20** | [`Master_Geologia_Estrutural_e_Tensores`](master-skills/Master_Geologia_Estrutural_e_Tensores.md) | Elipsóide de deformação, tensores de tensão, critério Mohr-Coulomb |
| **21** | [`Master_Hidrogeologia_e_Modelagem_Fluxo`](master-skills/Master_Hidrogeologia_e_Modelagem_Fluxo.md) | Lei de Darcy, equação de Theis, ensaios de bombeamento, modelagem numérica |
| **22** | [`Master_Canva_Image_e_Design_Agent`](master-skills/Master_Canva_Image_e_Design_Agent.md) | Automação Canva Pro Playwright, design gráfico, manipulação de imagem Pillow |
| **23** | [`Master_Revisao_Cientifica_e_Escrita_Humanizada`](master-skills/Master_Revisao_Cientifica_e_Escrita_Humanizada.md) | Peer Review rigoroso (SBC/IEEE/ACM), Anti-AI Slop, conversão dissertação -> artigo |
| **24** | [`Master_SkillSpector_Seguranca_e_Auditoria_Skills`](master-skills/Master_SkillSpector_Seguranca_e_Auditoria_Skills.md) | NVIDIA SkillSpector: auditoria AppSec de skills de IA, 71 padrões, YARA, AST e Least Privilege |
| **25** | [`Master_ECC_Harness_e_Otimizacao_Agentes`](master-skills/Master_ECC_Harness_e_Otimizacao_Agentes.md) | Everything Claude Code: harness OS, economia de tokens, ciclo 6-fases, TDD e memória durável SQLite |
| **26** | [`Master_Superpowers_Engenharia_Codigo_e_Prompts`](master-skills/Master_Superpowers_Engenharia_Codigo_e_Prompts.md) | Superpowers: metodologia disciplinada de código a partir de prompts, brainstorming e planos atômicos |

---

## 🛠️ Habilidades Executáveis (`skills/`)

Além das diretrizes teóricas, o repositório contém as implementações executáveis das ferramentas do agente:

1. **`arena-ai-controller`**: Driver Playwright para automação de sessões, relê de prompts e reconexão resiliente com a plataforma Arena AI.
2. **`gis-multicamadas`**: Gerador e manipulador de mapas Leaflet/Folium em múltiplas camadas (geologia, poços, drenagem, vias) com medição métrica e alternância de basemaps.
3. **`vcs-version-agent`**: Agente de paridade bidirecional (GitHub <-> Local), fusão de branches `arena/*` e snapshots offline.
4. **`biblioteca-pesquisavel`**: Motor de indexação e busca léxica por página no acervo técnico.
5. **`biblioteca-triagem`**: Destilador de laudos, extração de confiança (A-E) e geração de fichas de síntese.
6. **`biblioteca-mapa-documento`**: Extrator de estrutura de documentos extensos (>50k tokens) e mergulho direcionado em capítulos técnicos.
7. **`computacao-aplicada`**: Módulo de acesso ao acervo do Mestrado PPGCA/Unisinos estruturado via Docling.
8. **`canva-image-agent`**: Automação do Canva Pro via Playwright e motor local de manipulação gráfica (redimensionamento Lanczos, corte, otimização).
9. **`revisor-cientifico-peer-review`**: Simulador de parecerista sênior (SBC/IEEE/ACM/Elsevier) com auditoria em 5 etapas e checklist canônico de manuscritos.
10. **`escrita-tecnica-humanizada`**: Guia anti-AI slop, modulação de burstiness, voz ativa, densidade semântica e linter de estilo acadêmico.
11. **`skillspector-auditor`**: Agente e scanner de segurança para skills de agentes de IA baseado no NVIDIA SkillSpector.
12. **`ecc-harness-optimizer`**: Sistema operacional de harness e otimizador de contexto/tokens de agentes (Everything Claude Code - ECC).
13. **`superpowers-coding-agent`**: Agente de desenvolvimento disciplinado de código a partir de prompts (obra/superpowers).
14. **`desktop-screenshot`**: Captura de telas de aplicações desktop e publicação em PRs do GitHub com URLs imutáveis e commits de snapshots (sem hosts de imagem terceiros).
15. **`sprout-cli`**: Interface CLI multi-agente para mensageria Nostr (canais/DMs), workflows, feed de eventos, proteções de branch e memória persistente chave-valor (`mem`).
16. **`github-research`**: Pesquisa especializada de histórico de issues, PRs mesclados e código via GitHub CLI (`gh`).
17. **`anydoc`**, **`no-ai-slop`**, **`prompt-router-coordinator`**, **`scientific-writing`**, **`scientific-thinking-scholar-evaluation`**: conversão de documentos, filtro anti-slop, roteamento de prompts entre agentes e escrita/avaliação científica.

### 🔁 Sincronização (este repo é a fonte da verdade)

```bash
python scripts/sync_gabebrain.py            # mostra o que mudaria
python scripts/sync_gabebrain.py --apply    # aplica
```

- `skills/` → `~/.gemini/config/skills` (todas) e `.claude/skills` / `.agents/skills` do vault (só as que já estão lá).
- `master-skills/` ← `📚 Biblioteca de Agentes/` do vault (lá é onde se edita).
- Regenera as notas `20-Skills/` do vault.
- Nunca copia `.env`/perfis de navegador para o vault; remove `.env` que encontrar lá.
- Se um destino foi editado **depois** do repo, reporta `CONFLITO` e não sobrescreve.

---

## 👥 Personas & Agentes Especializados (`agents/`)

- **`meadow-core/`**: Pack multi-agente derivado do ecossistema Buzz:
  - **`@Skip`** (`agents/skip.persona.md`): Orquestrador central que coordena a equipe, delega trabalho e sintetiza resultados.
  - **`@Bana`** (`agents/bana.persona.md`): Revisor arquitetural com foco no big picture, simplicidade e integridade.
  - **`@Lev`** (`agents/lev.persona.md`): Especialista em segurança, auditoria de código, auth, injeção e superfície de ataque.

---

## 🚀 Como Usar no Arena AI

1. Acesse o [Arena AI Agent Mode](https://arena.ai/agent).
2. Ative a integração com o GitHub no painel direito.
3. Conecte o repositório `gabrielhklaser/gabebrain-skills` (ou inclua-o nas instruções de contexto do seu projeto principal).
4. Envie prompts como:
   > *"Com base nas diretrizes do GabeBrain em `master-skills/Master_GIS_Geoprocessamento.md`, implemente a camada de buffer hidrogeológico e plote no mapa interativo."*
5. O Arena AI lerá as skills diretamente, executará as alterações e fará o push de volta para o GitHub.
