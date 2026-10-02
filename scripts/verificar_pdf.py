#!/usr/bin/env python3
"""Verificación independiente de un PDF (presentación Gamma u otro).

Uso: python verificar_pdf.py ARCHIVO.pdf [--original ORIGINAL.pdf] [--sin-persona] [--patron REGEX ...]
- Links a gamma.app y marca "Made with Gamma" medida POR PÍXELES en el rectángulo del badge
  (solo aplica a PDF de Gamma; contar imágenes da falsos positivos: la herramienta deja una imagen en blanco).
- Patrones de redacción (segunda/primera persona, futuros), con el estilo por defecto de tercera persona.
  --sin-persona los desactiva (cuando CRITERIOS.md fija otro estilo).
- --patron REGEX (repetible): suma patrones propios de la materia, por ejemplo una convención técnica obsoleta que
  CRITERIOS.md prohíbe. Ejemplo: --patron "javax" en una materia que migró a otro namespace.
- Con --original: cuántas páginas cambiaron respecto del original (solo deben cambiar las editadas).
"""
import re
import sys

import fitz

BADGE = fitz.Rect(754, 467, 893, 500)  # esquina inferior derecha en páginas de 900x507 pt (formato Gamma)
PATRONES = {
    "segunda_persona": r"\b(tú|vos|tu|tus|puedes|podés|considera|usa|uses|imagina|recuerda|fíjate|avisame)\b",
    "primera_persona": r"\b(vamos|veremos|nuestr[oa]s?|hemos|aprendimos|esperamos|aplicaremos)\b",
    "futuro": r"\b\w{4,}(ará|arán|erá|erán|irá|irán)\b",
}


def azul_marino(pix):
    s, n = pix.samples, pix.n
    return sum(1 for i in range(0, len(s), n) if s[i] < 45 and s[i + 1] < 60 and 60 < s[i + 2] < 140)


def main():
    if len(sys.argv) < 2:
        print(__doc__); return 2
    ruta = sys.argv[1]
    orig = sys.argv[sys.argv.index("--original") + 1] if "--original" in sys.argv else None
    d = fitz.open(ruta)
    print(f"== {ruta}  ({len(d)} páginas, {d[0].rect.width:.0f}x{d[0].rect.height:.0f} pt)")
    links = sum(1 for p in d for l in p.get_links() if "gamma" in l.get("uri", "").lower())
    print("Links a gamma.app:", links)
    # El badge solo se mide si la página tiene el tamaño típico de Gamma
    if abs(d[0].rect.width - 900) < 5:
        por_pagina = [azul_marino(p.get_pixmap(clip=BADGE, dpi=100)) for p in d]
        sospechosas = [i + 1 for i, v in enumerate(por_pagina) if v > 1500]
        print("Páginas con píxeles azul marino en el rectángulo del badge:", sospechosas or "ninguna")
        if sospechosas:
            print("   -> MIRAR esas páginas: una marca real da ~4000 px por página; si hay una sola página con foto oscura, es la portada.")
    texto = " ".join(p.get_text() for p in d)
    plano = re.sub(r"\s+", " ", texto)
    patrones = {} if "--sin-persona" in sys.argv else dict(PATRONES)
    args = sys.argv
    for i, a in enumerate(args):
        if a == "--patron" and i + 1 < len(args):
            patrones[f"propio:{args[i + 1]}"] = args[i + 1]
    for k, p in patrones.items():
        hits = list(re.finditer(p, plano, re.I))
        print(f"{k:16}{len(hits)}")
        for m in hits[:8]:
            print("     ...", plano[max(0, m.start() - 55):m.end() + 45].strip(), "...")
    if orig:
        o = fitz.open(orig)
        cambiaron = []
        for i in range(min(len(o), len(d))):
            a, b = o[i].get_pixmap(dpi=40), d[i].get_pixmap(dpi=40)
            if a.samples != b.samples:
                cambiaron.append(i + 1)
        print(f"Páginas distintas al original: {len(cambiaron)} -> {cambiaron}  (páginas: {len(o)} vs {len(d)})")
    print("\nLeer cada coincidencia en contexto: \"usa\" o \"considera\" en tercera persona es válido.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
