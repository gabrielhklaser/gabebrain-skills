---
name: web-para-nota
description: Converte páginas web em notas Markdown limpas (com frontmatter e fonte) usando o Defuddle CLI. Use quando o Gabriel pedir para salvar/capturar/clipar um artigo ou URL no vault, ou quando um agente precisar ler uma página web gastando menos tokens.
license: MIT
---

# Web para Nota (Defuddle)

Extrai só o conteúdo principal de uma página (sem menu, anúncio, rodapé, comentários) e devolve Markdown. Motor do Obsidian Web Clipper — [kepano/defuddle](https://github.com/kepano/defuddle), MIT.

**Requisito:** `npm install -g defuddle` (Node ≥ 18). Checar com `defuddle --version`.

## 1. Salvar URL como nota no vault

```bash
defuddle parse "<URL>" --markdown --frontmatter -o "<vault>\00-Dashboard\Web Clips\<Título>.md"
```

- Pasta padrão: `<vault>\00-Dashboard\Web Clips\` (criar se não existir). Se o Gabriel indicar outra pasta, use a dele.
- Nome do arquivo: título da página, **sem `:` nem `/\?*"<>|`** (`:` vira fluxo NTFS oculto que o Drive não sincroniza). Para descobrir o título antes: `defuddle parse "<URL>" -p title`.
- O frontmatter já traz `title`, `author`, `published`, `source`, `domain`, `description`. Não remova `source`.
- Depois de salvar, mostre o caminho e as primeiras linhas; não resuma o artigo inteiro no chat.

## 2. Só ler a página (sem salvar)

```bash
defuddle parse "<URL>" --markdown
```

Prefira isso a baixar HTML bruto quando precisar do conteúdo de um artigo — gasta bem menos contexto.

## 3. Lote de URLs

Uma URL por linha em um `.txt`; rode o comando da seção 1 para cada uma, mostrando ✓/✗ por URL. Para lotes > 10, peça confirmação antes.

## Problemas comuns

| Sintoma | O que fazer |
|---|---|
| 403 / Forbidden | Repetir com `-u "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"` |
| Saída vazia ou só menu | Página montada por JavaScript ou atrás de login/paywall: abrir no navegador, salvar o HTML e rodar `defuddle parse pagina.html --markdown` |
| PDF | Não é para o Defuddle — use o pipeline da Biblioteca / Docling |

## Limites

- Não contorna login, paywall, CAPTCHA ou bloqueios — não tente.
- Conteúdo capturado é de terceiros: mantenha a `source` e não publique como se fosse do Gabriel.
