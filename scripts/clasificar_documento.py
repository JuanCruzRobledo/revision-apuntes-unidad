#!/usr/bin/env python3
"""Sugiere qué tipo de documento es un archivo del aula: presentación (Gamma u otra), documento (para la plantilla) u otro.

Uso: python clasificar_documento.py ARCHIVO [ARCHIVO ...] [--json]
Es solo una SUGERENCIA para la Fase 1: la clasificación final la confirma el tutor, archivo por archivo.
Señales en PDF: página apaisada o 16:9 (presentación), link a gamma.app o marca "Made with Gamma", poco texto por página.
Un PDF generado con Gamma pero en página A4 vertical con texto corrido es un DOCUMENTO, no una presentación.
Los .docx se sugieren como documento; los .pptx, como presentación.
Resultado: presentacion | documento | otro, más el motivo. TP o apunte se decide leyendo el contenido (Fase 1).
"""
import json
import sys
from pathlib import Path

import fitz


def clasificar_pdf(ruta):
    d = fitz.open(ruta)
    p0 = d[0].rect
    w, h = p0.width, p0.height
    gamma = any("gamma.app" in (l.get("uri") or "").lower() for p in d for l in p.get_links())
    apaisada = w > h * 1.2
    texto_por_pagina = sum(len(p.get_text()) for p in d) / max(len(d), 1)
    senales = []
    if gamma:
        senales.append("link a gamma.app")
    if apaisada:
        senales.append(f"página apaisada {w:.0f}x{h:.0f}")
    if texto_por_pagina < 600:
        senales.append(f"poco texto por página ({texto_por_pagina:.0f} caracteres)")
    if apaisada or (gamma and abs(w / h - 16 / 9) < 0.1):
        return "presentacion", senales
    if gamma and not apaisada:
        senales.append("página vertical con texto corrido: documento hecho con Gamma")
    if texto_por_pagina >= 600 and not apaisada:
        return "documento", senales or [f"página vertical {w:.0f}x{h:.0f} con texto corrido"]
    return "otro", senales or ["no hay señales claras: decide el tutor"]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__); return 2
    res = []
    for a in args:
        ext = Path(a).suffix.lower()
        if ext == ".pdf":
            tipo, motivo = clasificar_pdf(a)
        elif ext == ".docx":
            tipo, motivo = "documento", ["Word"]
        elif ext == ".pptx":
            tipo, motivo = "presentacion", ["PowerPoint"]
        else:
            tipo, motivo = "otro", [f"extensión {ext}"]
        res.append({"archivo": a, "sugerencia": tipo, "motivo": motivo})
    if "--json" in sys.argv:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        for r in res:
            print(f"{r['sugerencia']:13} {Path(r['archivo']).name}  ({'; '.join(r['motivo'])})")
        print("\nEs una sugerencia: el tutor confirma el tipo (y si es apunte o TP) en la Fase 1.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
