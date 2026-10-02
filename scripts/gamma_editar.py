"""Edición de texto en el lugar para PDF exportados de Gamma (PyMuPDF), con las fuentes reales.

Las fuentes (OFL, Google Fonts) están en assets/fonts/ ya fijadas al peso que usa Gamma.
Uso:
    from gamma_editar import dump, aplicar
    dump("entrada.pdf", [5, 8])                        # ver bloques/líneas/fuentes de esas páginas
    aplicar("entrada.pdf", "salida.pdf", [ {p:5, modo:'bloque', buscar:'Puedes configurar', nuevo:'...'} ])

Modos:
  'span'   : buscar dentro de una línea (span). 'nuevo' puede ser texto completo del span, o ('sub', viejo, nuevo).
  'agregar': inserta una línea nueva en (x, y) con la fuente/tamaño/color de un span de referencia ('ref').
  'bloque' : reemplaza el párrafo completo (todas las líneas del bloque que contiene 'buscar'),
             re-ajustando saltos de línea al ancho original (o 'ancho').
Nunca toca fondos, imágenes ni vectores: la redacción solo elimina texto.
"""
import os, sys, fitz

AQUI = os.path.dirname(os.path.abspath(__file__))
FUENTES = os.path.join(AQUI, "..", "assets", "fonts")
_cache = {}


def _font(nombre_pdf):
    base = nombre_pdf.split("+")[-1]            # 'LFRRED+InstrumentSans-Medium' -> 'InstrumentSans-Medium'
    ruta = os.path.join(FUENTES, base + ".ttf")
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"Sin fuente para {nombre_pdf} (esperada {ruta})")
    if ruta not in _cache:
        _cache[ruta] = fitz.Font(fontfile=ruta)
    return _cache[ruta]


def _color(c):
    return tuple(((c >> s) & 255) / 255 for s in (16, 8, 0))


def _bloques(page):
    out = []
    for b in page.get_text("dict")["blocks"]:
        if b.get("type") != 0:
            continue
        lines = [l for l in b["lines"] if any(s["text"].strip() for s in l["spans"])]
        if lines:
            out.append(lines)
    return out


def dump(pdf, paginas):
    d = fitz.open(pdf)
    for n in paginas:
        print(f"===== página {n}")
        for i, lines in enumerate(_bloques(d[n - 1])):
            fonts = {s["font"].split("+")[-1] for l in lines for s in l["spans"]}
            bb = [round(v) for v in (min(l["bbox"][0] for l in lines), min(l["bbox"][1] for l in lines),
                                     max(l["bbox"][2] for l in lines), max(l["bbox"][3] for l in lines))]
            sz = round(lines[0]["spans"][0]["size"], 1)
            col = hex(lines[0]["spans"][0]["color"])
            txt = " // ".join("".join(s["text"] for s in l["spans"]) for l in lines)
            print(f"[b{i}] {bb} sz={sz} col={col} f={sorted(fonts)} n={len(lines)} :: {txt[:300]}")


def _borrar(page, rects):
    for r in rects:
        r = fitz.Rect(r)
        h = r.height * 0.12
        page.add_redact_annot(fitz.Rect(r.x0 - 0.5, r.y0 + h, r.x1 + 0.5, r.y1 - h), fill=False)
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)


def _envolver(texto, font, size, ancho):
    lineas, actual = [], ""
    for w in texto.split(" "):
        prueba = (actual + " " + w).strip()
        if actual and font.text_length(prueba, size) > ancho:
            lineas.append(actual); actual = w
        else:
            actual = prueba
    lineas.append(actual)
    return lineas


def aplicar(entrada, salida, ediciones):
    d = fitz.open(entrada)
    log = []
    for e in ediciones:
        page = d[e["p"] - 1]
        modo = e.get("modo", "bloque")
        if modo == "agregar":
            cand = [s_ for lines_ in _bloques(page) for l in lines_ for s_ in l["spans"] if e["ref"] in s_["text"]]
            if not cand:
                raise ValueError(f"p{e['p']} agregar: referencia '{e['ref']}' no encontrada")
            s_ = cand[0]
            tw = fitz.TextWriter(page.rect)
            tw.append(fitz.Point(e["x"], e["y"]), e["nuevo"], font=_font(s_["font"]), fontsize=s_["size"])
            tw.write_text(page, color=_color(s_["color"]))
            log.append((e["p"], "(línea nueva)", e["nuevo"][:60]))
        elif modo == "span":
            cand = [(l, s) for lines in _bloques(page) for l in lines for s in l["spans"] if e["buscar"] in s["text"]]
            if len(cand) != 1:
                raise ValueError(f"p{e['p']} span '{e['buscar']}': {len(cand)} coincidencias")
            l, s = cand[0]
            nuevo = e["nuevo"]
            if isinstance(nuevo, tuple):
                nuevo = s["text"].replace(nuevo[1], nuevo[2])
            f = _font(s["font"])
            _borrar(page, [s["bbox"]])
            tw = fitz.TextWriter(page.rect)
            tw.append(fitz.Point(*s["origin"]), nuevo, font=f, fontsize=s["size"])
            tw.write_text(page, color=_color(s["color"]))
            log.append((e["p"], s["text"].strip()[:60], nuevo.strip()[:60]))
        else:
            # Gamma exporta cada línea de un párrafo como un bloque aparte: se toma la línea que contiene
            # 'buscar' y las 'n' líneas consecutivas siguientes (en orden de lectura) como un solo párrafo.
            todas = [l for lines_ in _bloques(page) for l in lines_]
            idx = [i for i, l in enumerate(todas) if e["buscar"] in "".join(s["text"] for s in l["spans"])]
            if len(idx) != 1:
                raise ValueError(f"p{e['p']} bloque '{e['buscar']}': {len(idx)} coincidencias")
            lines = todas[idx[0]: idx[0] + e.get("n", 1)]
            s0 = lines[0]["spans"][0]
            f = _font(s0["font"])
            size, color = s0["size"], _color(s0["color"])
            x0 = lines[0]["spans"][0]["origin"][0]
            y0 = lines[0]["spans"][0]["origin"][1]
            ancho = e.get("ancho") or (max(l["bbox"][2] for l in lines) - x0)
            lh = (lines[1]["spans"][0]["origin"][1] - y0) if len(lines) > 1 else e.get("interlineado", size * 1.4)
            _borrar(page, [l["bbox"] for l in lines])
            tw = fitz.TextWriter(page.rect)
            ys = []
            derecha = max(l["bbox"][2] for l in lines)
            for k, linea in enumerate(_envolver(e["nuevo"], f, size, ancho)):
                x = derecha - f.text_length(linea, size) if e.get("alinear") == "derecha" else x0
                tw.append(fitz.Point(x, y0 + k * lh), linea, font=f, fontsize=size); ys.append(y0 + k * lh)
            tw.write_text(page, color=color)
            log.append((e["p"], " ".join("".join(s["text"] for s in l["spans"]) for l in lines)[:60],
                        f"{len(ys)} línea(s) (antes {len(lines)})"))
    d.save(salida, garbage=4, deflate=True)
    return log


if __name__ == "__main__":
    dump(sys.argv[1], [int(x) for x in sys.argv[2:]])
