#!/usr/bin/env python3
"""Verifica que al pasar un documento a la plantilla no se perdió ni se agregó contenido sin registrar.

Uso:
  python verificar_fidelidad.py conversion FUENTE.pdf|.docx BASE.md   # la conversión a Markdown no perdió texto ni figuras
  python verificar_fidelidad.py cambios   BASE.md FINAL.md            # diff palabra por palabra: debe coincidir con <id>_cambios.md
  python verificar_fidelidad.py pdf       FINAL.md SALIDA.pdf         # la plantilla no se comió contenido del Markdown final
Opciones: --json   |   --max N (líneas de diff a mostrar, por defecto 40)
Código de salida: 0 = sin diferencias; 1 = hay diferencias (leerlas: pueden ser cambios legítimos del corrector).
Es un control MECÁNICO por palabras: no reemplaza la lectura ni la revisión manual del tutor.
"""
import difflib
import html
import json
import re
import sys
from collections import Counter
from pathlib import Path

import fitz  # PyMuPDF

TOKEN = re.compile(r"\w+", re.UNICODE)


def palabras(texto):
    return [t.lower() for t in TOKEN.findall(texto)]


def texto_md(md, con_alt=True):
    """Texto legible de un Markdown: sin comentarios, sin sintaxis; el alt de las figuras es opcional."""
    md = re.sub(r"<!--\s*(REVISAR|Página)[^>]*?-->", " ", md, flags=re.S)  # solo marcas de la skill; un comentario dentro del código es contenido
    md = re.sub(r"(\]\()[^)]*(\))", lambda m: "]", md) if False else md
    md = re.sub(r"(?<!!)\[([^\]]*)\]\(([^)]*)\)", r" \1 ", md)  # enlaces: cuenta el texto, no el destino
    md = re.sub(r"^---\s*\n.*?\n---\s*\n", " ", md, count=1, flags=re.S)  # encabezado de datos
    md = re.sub(r"^\s*```\w*\s*$", " ", md, flags=re.M)  # vallas de código (y su lenguaje)
    md = re.sub(r"!\[([^\]]*)\]\([^)]*\)",
                lambda m: f" {m.group(1)} " if (con_alt and m.group(1) != "Figura") else " ", md)
    md = re.sub(r"^\s*!!!\s+\w+(\s+\"[^\"]*\")?", " ", md, flags=re.M)
    return html.unescape(re.sub(r"[`*#>|\-]{1,}", " ", md))


def texto_fuente(ruta):
    ruta = Path(ruta)
    if ruta.suffix.lower() == ".pdf":
        d = fitz.open(ruta)
        partes = []
        for p in d:
            for b in p.get_text("blocks"):
                t = b[4].strip()
                if b[1] > p.rect.height - 60 and re.fullmatch(r"\d{1,3}", t):  # número de página
                    continue
                partes.append(t)
        return " ".join(partes)
    import docx
    d = docx.Document(str(ruta))
    partes = [p.text for p in d.paragraphs]
    for t in d.tables:
        for fila in t.rows:
            partes += [c.text for c in fila.cells]
    return " ".join(partes)


def figuras_fuente(ruta):
    ruta = Path(ruta)
    if ruta.suffix.lower() != ".pdf":
        return None
    d = fitz.open(ruta)
    conteo = Counter()
    for p in d:
        for im in p.get_image_info(xrefs=True):
            conteo[im["xref"]] += 1
    return conteo


def comparar(a, b, max_lineas):
    """a = referencia, b = candidato. Devuelve (faltan, sobran, líneas de diff legibles)."""
    ca, cb = Counter(a), Counter(b)
    faltan, sobran = ca - cb, cb - ca
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    diff = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            continue
        diff.append((op, " ".join(a[i1:i2])[:200], " ".join(b[j1:j2])[:200], " ".join(a[max(0, i1 - 6):i1])))
    return faltan, sobran, diff


def informar(titulo, faltan, sobran, diff, max_lineas, como_json):
    ok = not faltan and not sobran
    if como_json:
        print(json.dumps({"modo": titulo, "ok": ok, "palabras_que_faltan": dict(faltan), "palabras_que_sobran": dict(sobran),
                          "diferencias": diff[:max_lineas]}, ensure_ascii=False, indent=2))
        return ok
    print(f"== {titulo}: {'SIN DIFERENCIAS' if ok else 'HAY DIFERENCIAS'}")
    if faltan:
        print(f"  Palabras que FALTAN en el resultado: {sum(faltan.values())}")
    if sobran:
        print(f"  Palabras que SOBRAN en el resultado: {sum(sobran.values())}")
    for op, antes, despues, ctx in (diff[:max_lineas] if not ok else []):
        print(f"  [{op}] ...{ctx} | ANTES: {antes or '(nada)'} | DESPUÉS: {despues or '(nada)'}")
    if len(diff) > max_lineas:
        print(f"  ... y {len(diff) - max_lineas} diferencias más (usá --max o --json)")
    return ok


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    max_l = int(sys.argv[sys.argv.index("--max") + 1]) if "--max" in sys.argv else 40
    if "--max" in sys.argv:
        args = [a for a in args if a != str(max_l)]
    if len(args) != 3 or args[0] not in ("conversion", "cambios", "pdf"):
        print(__doc__); return 2
    modo, x, y = args
    como_json = "--json" in sys.argv
    if modo == "conversion":
        faltan, sobran, diff = comparar(palabras(texto_fuente(x)), palabras(texto_md(Path(y).read_text(encoding="utf-8"))), max_l)
        ok = informar("conversión fuente -> Markdown", faltan, sobran, diff, max_l, como_json)
        n_md = len(re.findall(r"!\[[^\]]*\]\(", Path(y).read_text(encoding="utf-8")))
        if not como_json:
            print(f"  Figuras recortadas en el Markdown: {n_md}. Los diagramas y las imágenes no se auditan por texto: "
                  f"compará las páginas de la fuente a ojo.")
    elif modo == "cambios":
        a = palabras(texto_md(Path(x).read_text(encoding="utf-8")))
        b = palabras(texto_md(Path(y).read_text(encoding="utf-8")))
        faltan, sobran, diff = comparar(a, b, max_l)
        informar("cambios BASE -> FINAL (cada diferencia debe estar en el registro de cambios)", faltan, sobran, diff, max_l, como_json)
        ok = True  # informativo: los cambios del corrector son esperables
    else:
        md = Path(x).read_text(encoding="utf-8")
        md = re.sub(r"^---\s*\n.*?\n---\s*\n", "", md, count=1, flags=re.S)  # encabezado de datos
        md = re.sub(r"\A((?:\s*<!--.*?-->)*)\s*# [^\n]*\n", r"\1\n", md, flags=re.S)  # el título general lo reemplaza la primera hoja
        d = fitz.open(y)
        pdf = " ".join(p.get_text() for p in d)
        # La plantilla agrega la primera hoja y el pie: solo importa que NADA del Markdown falte en el PDF
        faltan = Counter(palabras(texto_md(md, con_alt=False))) - Counter(palabras(pdf))
        ok = informar("Markdown final -> PDF (nada del Markdown puede faltar)", faltan, Counter(), [], max_l, como_json)
        n_md = len(re.findall(r"!\[[^\]]*\]\(", md))
        conteo = Counter()
        for p in d:
            for im in p.get_image_info(xrefs=True):
                conteo[im["xref"]] += 1
        n_pdf = sum(1 for _, v in conteo.items() if v == 1)
        if not como_json:
            print(f"  Figuras en el Markdown: {n_md} | imágenes únicas en el PDF (sin el logo repetido): {n_pdf}")
        if n_pdf < n_md:
            ok = False
            print("  FALTAN figuras en el PDF.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
