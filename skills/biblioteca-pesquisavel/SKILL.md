---
name: biblioteca-pesquisavel
description: >-
  Motor de busca lexical, leitura seletiva por página e indexação do acervo técnico
  do GabeBrain (Biblioteca Geológica/Técnica). Use sempre que precisar buscar referências
  técnicas, consultar citações exatas com página, ler trechos de PDFs por cota, listar
  o catálogo por método, conferir a integridade da biblioteca ou rodar o pipeline de
  processamento para novos PDFs inseridos em _entrada.
---

# Biblioteca Pesquisável (GabeBrain)

Esta skill conecta o Antigravity à **Biblioteca Técnica Pesquisável** do GabeBrain, transformando o acervo de PDFs em texto indexado por página, com cotas padronizadas (`GPR-001`, `HVS-042`, etc.), fichas no Obsidian e notas destiladas com citação verificada.

---

## 📍 Localização dos Scripts e Acervo

- **Raiz da Biblioteca**: `C:\Users\Gabriel\Meu Drive\Obsidian_GabeBrain\GabeBrain\10-Trabalho\Geologia\Biblioteca Geologica\`
- **Scripts**: `C:\Users\Gabriel\Meu Drive\Obsidian_GabeBrain\GabeBrain\10-Trabalho\Geologia\Biblioteca Geologica\Scripts\`
- **Porta de Entrada CLI**: `biblioteca.py`
- **Launcher do Pipeline**: `00_rodar_pipeline.ps1`
- **Pasta de Entrada de Novos PDFs**: `.../Biblioteca Geologica/Arquivos pdf/_entrada/`

---

## 🔍 Regra de Ouro: Consultar Antes de Responder

Quando o usuário fizer uma pergunta técnica (geologia, geofísica, hidrogeologia, geotecnia, meio ambiente, etc.), **nunca responda apenas pelo conhecimento geral da LLM**.

Siga a ordem de evidência:
1. **Bibliografia Citada (Documento + Página)**: Busca direta no acervo via `biblioteca.py`.
2. **Notas e Fichas do Vault**: Notas destiladas existentes no GabeBrain.
3. **Conhecimento Geral**: Declarado explicitamente como tal se não houver no acervo.

⚠️ **A busca é léxica:** Termos em português não encontram textos em inglês. Busque em ambos os idiomas (ex: `"permeabilidade"` e `"permeability"`).

---

## ⚡ Comandos da Porta Única (`biblioteca.py`)

Execute os comandos usando o Python configurado (`BIBLIOTECA_PYTHON` ou `python`):

```powershell
$BIB = "C:\Users\Gabriel\Meu Drive\Obsidian_GabeBrain\GabeBrain\10-Trabalho\Geologia\Biblioteca Geologica\Scripts\biblioteca.py"
```

### 1. Buscar Termo no Acervo (Documento + Página + Trecho)
```powershell
python $BIB buscar "termo" --palavra --compacto
# Filtrando por método/classe:
python $BIB buscar "resistividade" --palavra --metodo ERT --compacto
```

### 2. Ler Páginas Específicas por Cota
**Nunca abra o arquivo .txt completo de um documento longo**. Leia apenas as páginas necessárias:
```powershell
python $BIB ler GPR-001 15-20
python $BIB ler HVS-042 3
```

### 3. Resolver Cota ou Saber Onde Salvar Nota Destilada
```powershell
python $BIB cota GPR-001
# Devolve o arquivo correspondente, título, método e pasta onde a nota destilada deve nascer.
```

### 4. Consultar o Catálogo
```powershell
python $BIB catalogo --metodo GPR
python $BIB catalogo
```

### 5. Diagnóstico de Saúde da Biblioteca
Verifica se algum documento está escondido da busca, órfão ou com metadados inconsistentes:
```powershell
python $BIB saude
```

### 6. Mapa Estrutural de Documento Grande (Gratuito em Tokens)
```powershell
python $BIB mapa "Parte do Nome do Livro"
```

---

## 🔄 Fluxo de Novos Documentos (Pipeline)

Quando novos PDFs forem colocados em `Arquivos pdf/_entrada/`:

1. Verifique se não há trava ativa (`Metadata/pipeline.lock`).
2. Execute o pipeline:
   ```powershell
   powershell -ExecutionPolicy Bypass -File "C:\Users\Gabriel\Meu Drive\Obsidian_GabeBrain\GabeBrain\10-Trabalho\Geologia\Biblioteca Geologica\Scripts\00_rodar_pipeline.ps1" -PularOcr
   ```
3. Atualize cotas, catálogo e manifesto:
   ```powershell
   $SCRIPTS = "C:\Users\Gabriel\Meu Drive\Obsidian_GabeBrain\GabeBrain\10-Trabalho\Geologia\Biblioteca Geologica\Scripts"
   python "$SCRIPTS\14_codificar.py"
   python "$SCRIPTS\19_catalogo.py"
   python "$SCRIPTS\21_manifesto.py"
   ```
4. Verifique a saúde do acervo:
   ```powershell
   python "$SCRIPTS\biblioteca.py" saude
   ```

---

## 🚫 Diretrizes Estritas
- **Nunca edite fichas geradas (`Obsidian/Fichas/*.md`) à mão**: O script `05_gerar_fichas.py` as sobrescreve a cada passe.
- **Nunca renomeie PDFs manualmente**: Use sempre `12_renomear_documento.py` para sincronizar PDF, texto extraído, ficha e links Obsidian.
- **Correção de classificação de método**: Insira uma linha em `Metadata/classe_fixada.csv` (`arquivo,classe,motivo,data`) e rode `00_rodar_pipeline.ps1 -So 3,4,5`.
- **Nunca delete PDFs ou notas**: Mova para `99-Arquivo/lixeira/`.
