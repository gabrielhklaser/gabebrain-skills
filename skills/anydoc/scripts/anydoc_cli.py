#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
anydoc_cli.py - Utilitário CLI GabeBrain para conversão universal de documentos via anydoc.
Converte Word (.docx, .doc), Excel (.xlsx, .xls, .ods, .csv), PowerPoint (.pptx, .ppt),
OpenDocument (.odt), RTF e PDF em Markdown limpo e estruturado para LLMs e auditorias ambientais.
"""

import sys
import os
import argparse
from pathlib import Path
from typing import Optional, List

# Garantir UTF-8 no terminal Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    import anydoc
except ImportError:
    print("[ERRO] Módulo 'anydoc' (firecrawl-anydoc) não está instalado.", file=sys.stderr)
    print("Execute: pip install firecrawl-anydoc", file=sys.stderr)
    sys.exit(1)

EXTENSOES_SUPORTADAS = {
    ".doc", ".docx", ".docm",
    ".xls", ".xlsx", ".xlsm", ".xlsb", ".ods", ".csv",
    ".ppt", ".pptx", ".pps", ".ppsx", ".odp",
    ".odt", ".rtf", ".epub", ".pdf"
}

def converter_arquivo(
    caminho: Path,
    formato: Optional[str] = None,
    usar_ocr_remoto: bool = False
) -> Optional[str]:
    """Converte um arquivo individual para Markdown usando anydoc."""
    if not caminho.exists():
        print(f"[ERRO] Arquivo não encontrado: {caminho}", file=sys.stderr)
        return None

    try:
        ocr_mode = "hosted" if usar_ocr_remoto else None
        
        # Leitura por bytes se formato for explicitado
        if formato:
            dados = caminho.read_bytes()
            return anydoc.to_markdown_bytes(dados, format=formato)
        else:
            return anydoc.to_markdown(str(caminho), ocr=ocr_mode)

    except anydoc.NeedsOcrError:
        print(f"[AVISO] O PDF '{caminho.name}' possui páginas escaneadas que requerem OCR.", file=sys.stderr)
        print("        Use a flag '--ocr-hosted' ou processe com o OCR local do GabeBrain.", file=sys.stderr)
        return None
    except anydoc.EncryptedError:
        print(f"[ERRO] O arquivo '{caminho.name}' está criptografado ou protegido por senha.", file=sys.stderr)
        return None
    except anydoc.MalformedError as e:
        print(f"[ERRO] O arquivo '{caminho.name}' está corrompido: {e}", file=sys.stderr)
        return None
    except anydoc.UnsupportedError:
        print(f"[ERRO] O formato de '{caminho.name}' não é suportado pelo anydoc.", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[ERRO] Falha inesperada ao converter '{caminho.name}': {e}", file=sys.stderr)
        return None

def processar_lote(pasta_origem: Path, pasta_destino: Path, usar_ocr: bool = False):
    """Converte todos os arquivos suportados em um diretório recursivamente."""
    if not pasta_origem.exists() or not pasta_origem.is_dir():
        print(f"[ERRO] Pasta de origem inválida: {pasta_origem}", file=sys.stderr)
        return

    pasta_destino.mkdir(parents=True, exist_ok=True)
    arquivos = [p for p in pasta_origem.rglob("*") if p.is_file() and p.suffix.lower() in EXTENSOES_SUPORTADAS]

    print(f"📦 Iniciando conversão em lote: {len(arquivos)} documento(s) em '{pasta_origem.name}'")
    sucessos = 0
    falhas = 0

    for arq in arquivos:
        rel_path = arq.relative_to(pasta_origem)
        dest_file = pasta_destino / rel_path.with_suffix(".md")
        dest_file.parent.mkdir(parents=True, exist_ok=True)

        md = converter_arquivo(arq, usar_ocr_remoto=usar_ocr)
        if md:
            dest_file.write_text(md, encoding="utf-8")
            print(f"  [OK] {arq.name} -> {dest_file.name} ({len(md)} chars)")
            sucessos += 1
        else:
            print(f"  [FALHA] {arq.name}")
            falhas += 1

    print(f"\nConcluído: {sucessos} convertidos com sucesso, {falhas} falhas.")

def main():
    parser = argparse.ArgumentParser(
        description="GabeBrain anydoc CLI - Conversor universal de documentos (.docx, .xlsx, .pdf, .odt, etc.) para Markdown"
    )
    parser.add_argument("origem", type=Path, help="Arquivo ou pasta de origem a converter")
    parser.add_argument("-o", "--output", type=Path, help="Caminho do arquivo Markdown de saída")
    parser.add_argument("--batch-dir", type=Path, help="Pasta de saída para conversão de lote de diretório")
    parser.add_argument("--format", type=str, help="Formato explícito (ex: csv, docx, xlsx, pdf)")
    parser.add_argument("--ocr-hosted", action="store_true", help="Habilitar OCR na nuvem para páginas de PDF escaneadas")
    parser.add_argument("--detect-only", action="store_true", help="Apenas detecta e exibe o formato do arquivo")

    args = parser.parse_args()

    if args.detect_only:
        if args.origem.is_file():
            fmt = anydoc.format_from_path(str(args.origem))
            print(f"Formato detectado para '{args.origem.name}': {fmt}")
        else:
            print("[ERRO] --detect-only requer um arquivo único.", file=sys.stderr)
        return

    if args.batch_dir or args.origem.is_dir():
        dest = args.batch_dir or (args.origem.parent / f"{args.origem.name}_markdown")
        processar_lote(args.origem, dest, usar_ocr=args.ocr_hosted)
    else:
        md = converter_arquivo(args.origem, formato=args.format, usar_ocr_remoto=args.ocr_hosted)
        if md:
            if args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(md, encoding="utf-8")
                print(f"[OK] Markdown salvo em: {args.output}")
            else:
                print(md)

if __name__ == "__main__":
    main()
