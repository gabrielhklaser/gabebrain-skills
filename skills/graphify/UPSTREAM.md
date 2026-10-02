# UPSTREAM

- Fonte: https://github.com/safishamsi/graphify
- Commit: `ef4450d9c28acb2b8cdc22d369c1777b77148eef` (2026-09-30)
- Licenca: Apache-2.0 (arquivo `LICENSE` nesta pasta)
- Importada no GabeBrain em 2026-10-02 apos varredura SkillSpector (`--no-llm`) e revisao manual.
- Observacoes: Variante Windows (`skill-windows.md` + `skills/windows/references`). Na primeira execucao o skill instala o pacote PyPI `graphifyy` (uv/pip). Importada SEM hooks: nao rodar `graphify install`/`graphify hook install`. Sem GEMINI/GOOGLE_API_KEY a extracao semantica usa o proprio agente (gasta a assinatura).
