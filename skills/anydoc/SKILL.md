---
name: anydoc
description: "Conversor e leitor ultrarrápido de documentos de escritório e relatórios técnicos (Word .docx/.doc, Excel .xlsx/.xls/.ods, PowerPoint .pptx/.ppt, OpenDocument .odt, RTF, EPUB, CSV e PDF) para GitHub-Flavored Markdown. Essencial para ingestão, auditoria e revisão de laudos e processos de licenciamento ambiental no GabeBrain."
---

# Anydoc - Leitura e Conversão Universal de Documentos para Markdown

> Integração do motor [firecrawl/anydoc](https://github.com/firecrawl/anydoc) (Rust de alta performance com bindings Python `firecrawl-anydoc` e CLI Node) no ecossistema GabeBrain e no pipeline de Licenciamento Ambiental.

O `anydoc` permite converter qualquer documento técnico ou planilha em Markdown limpo e estruturado em **milissegundos** (single-digit milliseconds), preservando cabeçalhos, listas, notas e tabelas no formato GFM (GitHub-Flavored Markdown), ideal para processamento por agentes LLM e auditorias ambientais.

---

## 📄 Formatos Suportados

| Categoria | Extensões | Uso Típico no Licenciamento Ambiental |
|:---|:---|:---|
| **Word** | `.docx`, `.doc`, `.docm` | Laudos geológicos, memoriais descritivos, PGRS, PCA, PRAD, requerimentos |
| **Excel** | `.xlsx`, `.xls`, `.xlsm`, `.xlsb`, `.ods`, `.csv` | Planilhas de automonitoramento, ensaios de permeabilidade, vazões de poços |
| **OpenDocument** | `.odt`, `.ods`, `.odp` | Documentos públicos, termos de referência municipais |
| **Rich Text** | `.rtf` | Minutas contratuais, certidões e pareceres emitidos por sistemas legados |
| **PDF** | `.pdf` | Pareceres técnicos, ARTs, licenças anteriores, publicações de súmula |
| **PowerPoint** | `.pptx`, `.ppt`, `.odp` | Apresentações de audiências públicas e defesas de projetos |

---

## ⚡ Formas de Execução no GabeBrain

### 1. Via Módulo Python Local (`firecrawl-anydoc`)
O pacote está instalado no ambiente Python sob o nome de importação `anydoc`:

```python
import anydoc

# Conversão direta de arquivo para Markdown:
markdown = anydoc.to_markdown("caminho/para/laudo.docx")

# Conversão com suporte a OCR em nuvem (páginas escaneadas):
markdown = anydoc.to_markdown("scan.pdf", ocr="hosted")

# Conversão a partir de bytes em memória:
markdown = anydoc.to_markdown_bytes(conteudo_bytes, format="xlsx")

# Extração do modelo de documento com assets (imagens embutidas):
doc = anydoc.to_document(conteudo_bytes)
```

### 2. Via Script CLI do GabeBrain (`anydoc_cli.py`)
Para converter arquivos ou lotes inteiros de processos de licenciamento:

```powershell
# Converter um arquivo para stdout:
python "$HOME/.gemini/config/skills/anydoc/scripts/anydoc_cli.py" "laudo_geologico.docx"

# Salvar o markdown resultante em arquivo:
python "$HOME/.gemini/config/skills/anydoc/scripts/anydoc_cli.py" "planilha_efluentes.xlsx" -o "saida.md"

# Converter todos os documentos de uma pasta de processo:
python "$HOME/.gemini/config/skills/anydoc/scripts/anydoc_cli.py" "entradas_reais/processo_123" --batch-dir "docs_extraidos/processo_123"
```

### 3. Via CLI Global Node / npx
```powershell
npx -y @firecrawl/anydoc documento.docx -o documento.md
```

---

## 🌿 Aplicação no Repositório de Licenciamento Ambiental

No pipeline de licenciamento ambiental (`scratch/licenciamentoambiental`):

1. **Ingestão Multiformato:**
   O módulo [`licenciamento.leitor_anydoc.LeitorAnydoc`](file:///C:/Users/Gabriel/.gemini/antigravity/scratch/licenciamentoambiental/licenciamento/leitor_anydoc.py) processa não apenas PDFs, mas também planilhas de monitoramento (`.xlsx`), laudos em Word (`.docx`) e termos em OpenDocument (`.odt`), convertendo tudo para Markdown padronizado antes da análise das regras técnicas.

2. **Auditoria Técnica Sem Perda de Tabelas:**
   Tabelas de ensaios laboratoriais e limites de efluentes (Resolução CONSEMA 355/2017, CONAMA 430/2011) chegam frequentemente em formato `.xlsx` ou tabelas Word. O `anydoc` serializa essas matrizes em tabelas GFM Markdown perfeitamente alinhadas, permitindo que o `auditor_tecnico.py` compare diretamente parâmetros como DBO, DQO, pH e Coliformes.

3. **Fallback Inteligente:**
   - **Documentos de Texto e Planilhas:** Processados instantaneamente pelo `anydoc` (~5-20ms).
   - **Pranchas Cadastrais / Plantas Baixas (A0/A1):** Direcionadas ao `leitor_plantas.py` e `leitor_pdf.py` com OCR adaptativo em 300 DPI e filtros morfológicos.
   - **Formulários Escaneados:** Direcionados ao RapidOCR/Docling.

---

## 🎓 Aplicação na Dissertação de Mestrado (Computação Aplicada)

Para a preparação da apresentação da **banca de defesa de mestrado**:

1. **Extração de Figuras e Diagramas Embutidos:**
   Documentos `.docx` e apresentações `.pptx` armazenam diagramas e gráficos de alta resolução internamente. O `anydoc` extrai esses assets diretamente em formato bruto (PNG, SVG, JPEG) através de `doc = anydoc.to_document(bytes)` e `doc.assets`, preservando a fidelidade visual sem necessidade de capturas de tela manuais.

2. **Geração Automatizada de Diagramas Mermaid:**
   Transforma descrições conceituais da dissertação em diagramas executáveis (arquiteturas de software SAP-TAM, fluxos comunicativos de IHC e pipelines matemáticos de redução dimensional como LAMP e NCA).

3. **Montagem de Slides de Apresentação de Defesa:**
   O script [`dissertacao_diagramas.py`](file:///C:/Users/Gabriel/.gemini/config/skills/anydoc/scripts/dissertacao_diagramas.py) gera apresentações em Markdown (Marp/Reveal.js) com cabeçalho formal do PPGCA/Unisinos, seções de contextualização, problema, metodologia, validação estatística e conclusão.

---

## ⚠️ Tratamento de Erros e Exceções

O `anydoc` categoriza erros de conversão de forma clara:
- `anydoc.NeedsOcrError`: Páginas de PDF escaneadas ou apenas com imagens (sem camada de texto).
  - *Ação:* Usar `ocr="hosted"` ou encaminhar para o OCR local do GabeBrain (`leitor_pdf.py`).
- `anydoc.EncryptedError`: Documento protegido por senha.
- `anydoc.MalformedError`: Arquivo corrompido ou truncado.
- `anydoc.UnsupportedError`: Formato desconhecido ou não suportado.
