#!/usr/bin/env python3
"""Convierte un .docx a Markdown para la plantilla TUPaD, conservando todo el contenido.

Uso: python docx_a_md.py ENTRADA.docx SALIDA_DIR
Genera SALIDA_DIR/<nombre>.md y SALIDA_DIR/img/ (imágenes del documento).

Solo usa python-docx (ya es dependencia obligatoria de la skill): funciona igual en Windows, macOS y Linux sin instalar nada más.
Reconoce: títulos (estilos Heading/Título), listas, tablas, negrita/cursiva, código en línea y bloques de código
(fuente monoespaciada o estilo "Code/Código"), enlaces e imágenes. Lo que no puede interpretar lo deja como texto plano:
no descarta nada. Después de convertir, verificar_fidelidad.py comprueba que no se perdió texto.
Es un borrador estructurado: el lenguaje de los bloques de código se adivina y se marca con <!-- REVISAR -->.
"""
import re
import sys
from pathlib import Path

import docx
from docx.oxml.ns import qn

MONO = ("consolas", "courier", "mono", "menlo", "monaco", "cascadia", "lucida console", "source code", "fira code", "inconsolata")


def esc(t):
    """Escapa < > & del texto corriente: un `<persistence-unit>` suelto sería HTML y el navegador lo ocultaría."""
    return re.sub(r"&(?=#?\w+;)", "&amp;", t).replace("<", "&lt;").replace(">", "&gt;")


def es_mono_run(run, estilo_parrafo_codigo):
    f = (run.font.name or "").lower()
    return estilo_parrafo_codigo or any(m in f for m in MONO)


def parrafo_es_codigo(p):
    est = (p.style.name or "").lower()
    if any(k in est for k in ("code", "código", "codigo", "preformatted", "source")):
        return True
    runs = [r for r in p.runs if r.text.strip()]
    return bool(runs) and all(any(m in (r.font.name or "").lower() for m in MONO) for r in runs)


def adivinar_lenguaje(texto):
    t = texto
    if re.search(r"^\s*<\?xml|<persistence|<project|</\w+>", t, re.M):
        return "xml"
    if re.search(r"\b(SELECT|INSERT INTO|CREATE TABLE|UPDATE \w+ SET|DELETE FROM)\b", t):
        return "sql"
    if re.search(r"^\s*(def |import \w+$|print\()", t, re.M) and not re.search(r"[;{]\s*$", t, re.M):
        return "python"
    if re.search(r"\b(public|private|class|interface|import java|System\.out|@Entity|@Override)\b", t):
        return "java"
    if re.search(r"^\s*(mvn|git|cd|java|javac|npm|pip) ", t, re.M):
        return "bash"
    return "text"


def runs_a_md(p, doc, img_dir, contador):
    """Texto del párrafo con negrita, cursiva, código en línea, enlaces e imágenes."""
    partes = []

    def run_md(r):
        out = []
        for hijo in r._r:
            if hijo.tag == qn("w:drawing") or hijo.tag == qn("w:pict"):
                for blip in hijo.iter(qn("a:blip")):
                    rid = blip.get(qn("r:embed"))
                    if rid and rid in doc.part.related_parts:
                        parte = doc.part.related_parts[rid]
                        ext = Path(parte.partname).suffix or ".png"
                        contador[0] += 1
                        nombre = f"fig{contador[0]:02d}{ext}"
                        (img_dir / nombre).write_bytes(parte.blob)
                        out.append(f"![Figura](img/{nombre})\n<!-- REVISAR: imagen del documento; su contenido no se audita por texto. -->")
        t = r.text
        if not t:
            return "".join(out)
        if not t.strip():
            return t + "".join(out)
        pre = suf = ""
        if any(m in (r.font.name or "").lower() for m in MONO):
            pre = suf = "`"
        else:
            t = esc(t)
        if pre:
            pass
        elif r.bold and r.italic:
            pre = suf = "***"
        elif r.bold:
            pre = suf = "**"
        elif r.italic:
            pre = suf = "*"
        m = re.match(r"^(\s*)(.*?)(\s*)$", t, re.S)
        return "".join(out) + f"{m.group(1)}{pre}{m.group(2)}{suf}{m.group(3)}"

    from docx.text.run import Run
    for hijo in p._p:
        if hijo.tag == qn("w:r"):
            partes.append(run_md(Run(hijo, p)))
        elif hijo.tag == qn("w:hyperlink"):
            rid = hijo.get(qn("r:id"))
            url = doc.part.rels[rid].target_ref if rid and rid in doc.part.rels else ""
            txt = "".join(run_md(Run(r, p)) for r in hijo.findall(qn("w:r")))
            partes.append(f"[{txt}]({url})" if url and txt.strip() else txt)
    return re.sub(r"``|\*\*\*\*", "", "".join(partes))


def tabla_a_md(t):
    filas = []
    for fila in t.rows:
        celdas = []
        vistos = set()
        for c in fila.cells:
            if id(c._tc) in vistos:
                continue
            vistos.add(id(c._tc))
            celdas.append(" <br> ".join(esc(x.text.strip()) for x in c.paragraphs if x.text.strip()).replace("|", "\\|"))
        filas.append(celdas)
    if not filas:
        return ""
    ancho = max(len(f) for f in filas)
    filas = [f + [""] * (ancho - len(f)) for f in filas]
    out = ["| " + " | ".join(filas[0]) + " |", "|" + "---|" * ancho]
    out += ["| " + " | ".join(f) + " |" for f in filas[1:]]
    return "\n".join(out)


def convertir(ruta, salida):
    d = docx.Document(str(ruta))
    salida = Path(salida)
    img_dir = salida / "img"
    img_dir.mkdir(parents=True, exist_ok=True)
    contador = [0]
    md, codigo = [], []

    def cerrar_codigo():
        if codigo:
            txt = "\n".join(codigo).rstrip()
            md.append(f"```{adivinar_lenguaje(txt)}\n{txt}\n```\n<!-- REVISAR: lenguaje del bloque de código adivinado. -->")
            codigo.clear()

    from docx.table import Table
    from docx.text.paragraph import Paragraph
    for hijo in d.element.body.iterchildren():
        if hijo.tag == qn("w:p"):
            p = Paragraph(hijo, d)
            if parrafo_es_codigo(p) and p.text.strip() != "" or (codigo and parrafo_es_codigo(p)):
                codigo.append(p.text.replace("\t", "    "))
                continue
            cerrar_codigo()
            texto = runs_a_md(p, d, img_dir, contador).strip()
            if not texto:
                continue
            est = (p.style.name or "").lower()
            m = re.match(r"(heading|t[ií]tulo)\s*(\d)", est)
            if est in ("title", "título") :
                md.append("# " + texto)
            elif m:
                md.append("#" * min(int(m.group(2)) + 1, 4) + " " + texto)
            elif p._p.pPr is not None and p._p.pPr.numPr is not None or "list" in est or "lista" in est:
                md.append(("1. " if ("number" in est or "numer" in est) else "- ") + texto)
            else:
                md.append(texto)
        elif hijo.tag == qn("w:tbl"):
            cerrar_codigo()
            md.append(tabla_a_md(Table(hijo, d)))
    cerrar_codigo()
    # listas contiguas sin línea en blanco entre ítems
    texto = "\n\n".join(x for x in md if x.strip()) + "\n"
    texto = re.sub(r"(\n- [^\n]*)\n\n(?=- )", r"\1\n", texto)
    texto = re.sub(r"(\n\d+\. [^\n]*)\n\n(?=1\. )", r"\1\n", texto)
    ruta_md = salida / (Path(ruta).stem + ".md")
    ruta_md.write_text(texto, encoding="utf-8")
    return ruta_md, contador[0]


def main():
    if len(sys.argv) < 3:
        print(__doc__); return 2
    ruta_md, n_img = convertir(sys.argv[1], sys.argv[2])
    print(f"OK {ruta_md}  imágenes={n_img}")
    print("Revisá las marcas <!-- REVISAR --> y corré verificar_fidelidad.py conversion antes de seguir.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
