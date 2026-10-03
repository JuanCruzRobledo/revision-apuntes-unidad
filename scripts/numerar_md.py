#!/usr/bin/env python3
"""Imprime un Markdown con líneas numeradas ([L012] texto), para que el detector cite ubicaciones exactas.

Uso: python numerar_md.py ARCHIVO.md [SALIDA.txt]
Equivale a extraer_docx.py pero para el Markdown base de la plantilla (teoría y TP).
"""
import sys
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print(__doc__); return 2
    lineas = Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
    out = "\n".join(f"[L{i:03d}] {l}" for i, l in enumerate(lineas, 1))
    if len(sys.argv) > 2:
        Path(sys.argv[2]).write_text(out + "\n", encoding="utf-8")
        print(f"OK {sys.argv[2]} ({len(lineas)} líneas)")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
