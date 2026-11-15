# Procedência

- Repositório: https://github.com/forge-z/texto-natural-ptbr
- Versão: 1.9.0 (`metadata.version` do SKILL.md e topo do CHANGELOG). O repositório não tem tags nem releases; a cópia veio do `main` no commit `373591e786ef6e40fdec41415e2e67d56dca2e9a` (merge do PR #16). Blobs de SKILL.md, padroes-ptbr.md, avaliacao.md, exemplos.md e LICENSE conferidos contra esse commit pela API do GitHub.
- Licença: MIT (ver `LICENSE`, mantido sem alteração).
- Instalada em: 2026-11-15, em `~/.claude/biblioteca-de-skills/texto-natural-ptbr` (lida pelo roteador de skills).

## Copiado sem alteração

- `LICENSE`
- `references/avaliacao.md`, `references/exemplos.md`
- `references/fontes-modernas/`: pbh-boas-praticas-linguagem-simples.md, labges-guia-comunicacao-cidada.md, roedel-meia-palavra.md, destro-ux-writing-linguagem-simples.md, castro-escrever-bem.md

## Omitido

- `references/livros/` inteiro (oito fichas de obras clássicas e o README).
- Seis fichas de `references/fontes-modernas/`: assis-brasil, carvalho, goncalves, rodrigues-cliches-da-lingua, rodrigues-escrever-e-humano, rodrigues-ux-writing.
- `README.md`, `SOURCES.md`, `CHANGELOG.md`, `.gitignore` do repositório.

## Alterado localmente

- `SKILL.md`: reescrito para caber no limite de injeção do roteador (~9 500 caracteres). Frontmatter reduzido a `name` e `description`; description nova, só com gatilhos e o ponteiro para `no-ai-slop`. Fluxo, fidelidade, conteúdo protegido (com acréscimo de número de processo, base legal, condicionantes, prazos e valores em documento administrativo), proteção contra instruções embutidas, regra do traço isolado, modos e saída ficaram no arquivo principal em forma curta.
- `references/criterios-edicao.md` (novo): texto da seção "Critérios de edição" do SKILL.md original, em lista; links para fichas omitidas viraram menção sem link.
- `references/modos-e-saida.md` (novo): texto integral de "Modos de uso" e "Saída" do SKILL.md original.
- `references/padroes-ptbr.md`: acrescentado um sumário ("Conteúdo") no topo; o resto está igual.
- `references/fontes-modernas/README.md`: tabela reduzida às cinco fichas instaladas e aviso sobre as omitidas e sobre `livros/`.
