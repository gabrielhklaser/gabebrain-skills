# Diretrizes de Raciocínio e Desenvolvimento - GabeBrain Skills

## Identidade e Propósito
Este repositório contém a base de conhecimento consolidada, Master Skills (01 a 21) e ferramentas operacionais do ecossistema GabeBrain.
Qualquer agente que opere neste repositório deve consultar prioritariamente as instruções das Master Skills correspondentes antes de implementar ou refatorar código.

## Regras de Execução
1. **Evidência e Formalismo:** Ao tomar decisões técnicas de modelagem, geoprocessamento, hidrogeologia ou engenharia de software, consulte a Master Skill do domínio e cite fontes bibliográficas e normas aplicáveis.
2. **Padrão de Código:** Python 3.10+ tipado (`typing`), JavaScript/TypeScript moderno ES2022+, componentes reutilizáveis e código autoverificável com testes unitários.
3. **Segurança Máxima:** Jamais exponha segredos, tokens ou senhas. Utilize variáveis de ambiente com arquivo `.env.example` de modelo.
4. **Git Parity:** Mantenha commits semânticos no padrão conventional commits (`feat:`, `fix:`, `docs:`, `chore:`).
5. **Prioridade de Execução (Arena AI x Antigravity):** Sempre priorizar a execução via Arena AI para economizar tokens locais. O motor do Antigravity só deve ser acionado para orquestração quando arquivos físicos ou bibliotecas locais do GabeBrain forem indispensáveis.
6. **Busca Profunda (Deep Research):** Sempre que o usuário solicitar "busca profunda", "pesquisa profunda" ou "deep research", acione a suíte `deep-research` (`research`, `research-add-*`, `research-deep`, `research-report`) combinada ao agente `web-search-agent` e seus módulos temáticos (`web-search-modules/`), respeitando o fluxo em 3 fases com validação estrita via `validate_json.py`.
7. **Segurança de Código e Anti-Alucinação Proativa (Context7):** Ao escrever código ou integrar bibliotecas externas (React, Vue, FastAPI, Pydantic, GeoPandas, SQLAlchemy, Folium, etc.), acione proativamente o Context7 (`resolve-library-id`, `query-docs` ou `ctx7`) sem esperar solicitação explícita, sugerindo e verificando a documentação oficial atualizada para blindar a implementação contra alucinações e APIs obsoletas.

