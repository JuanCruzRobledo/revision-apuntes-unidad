#!/usr/bin/env python3
"""Convierte un PDF de documento (no de presentación) a Markdown para la plantilla TUPaD.

Uso: python pdf_a_md.py ENTRADA.pdf SALIDA_DIR [--sin-encabezado-pagina] [--json]
Genera SALIDA_DIR/<nombre>.md y SALIDA_DIR/img/ con cada diagrama o ilustración recortado como PNG.

Solo usa PyMuPDF (ya es dependencia obligatoria de la skill): sirve en cualquier equipo sin instalar nada más.
Es un BORRADOR ESTRUCTURADO, no una conversión ciega. Lo que reconoce: títulos (por tamaño de letra), párrafos, listas,
bloques de código (por fuente distinta del cuerpo + fondo), código en línea, cuadros destacados (por color de fondo),
columnas (corte XY) y figuras (dibujos vectoriales o imágenes, recortados como PNG con su texto como descripción).
Lo que NO puede garantizar se deja marcado en el .md con `<!-- REVISAR: ... -->` para que el corrector y el tutor lo vean.
verificar_fidelidad.py comprueba después que no se haya perdido texto ni figuras.
"""
import json
import re
import statistics
import sys
from pathlib import Path

import fitz  # PyMuPDF


def esc(t):
    """Escapa < > & del texto corriente: un `<persistence-unit>` suelto sería HTML y el navegador lo ocultaría."""
    return re.sub(r"&(?=#?\w+;)", "&amp;", t).replace("<", "&lt;").replace(">", "&gt;")


def lum(c):
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def rgb_int(c):
    return ((c >> 16) & 255) / 255, ((c >> 8) & 255) / 255, (c & 255) / 255


def es_codigo_linea(t):
    return bool(re.search(r"[;{}]|\(\)|^\s{2,}\S|^\s*(//|@\w+|public |private |class |import |return |if \(|for \()", t))


class Linea:
    def __init__(self, bbox, spans):
        self.bbox = fitz.Rect(bbox)
        self.spans = spans
        self.texto = "".join(s["text"] for s in spans)
        s0 = max(spans, key=lambda s: len(s["text"]))
        self.size = round(s0["size"], 1)
        self.bloque = None
        self.font = s0["font"].split("+")[-1]
        self.color = rgb_int(s0["color"])
        self.bold = "bold" in self.font.lower() or bool(s0["flags"] & 16)


def contenedores(page):
    """Rectángulos de fondo que agrupan contenido (tarjetas, cajas de código, cuadros destacados)."""
    out = []
    W, H = page.rect.width, page.rect.height
    for d in page.get_drawings():
        r, f = d["rect"], d.get("fill")
        if f is None or r.width < 30 or r.height < 14:
            continue
        if r.width > W - 20 and r.height > H - 120:  # fondos de página
            continue
        out.append((fitz.Rect(r), f))
    return out


def figuras_vectoriales(page, cont):
    """Cúmulos de dibujos vectoriales que son diagramas (curvas/polígonos), no cajas ni fondos."""
    W, H = page.rect.width, page.rect.height
    figs = []
    for r in page.cluster_drawings():
        if r.width > W - 20 and r.height > H - 120:
            continue
        if r.width < 40 or r.height < 40:
            continue
        # Un cúmulo cuyo borde coincide con un contenedor de color plano es una caja, no un diagrama
        if any(abs(r.x0 - c.x0) < 3 and abs(r.y0 - c.y0) < 3 and abs(r.x1 - c.x1) < 3 and abs(r.y1 - c.y1) < 3 for c, _ in cont):
            continue
        n_curvas = sum(1 for d in page.get_drawings() if fitz.Rect(d["rect"]).intersects(r)
                       and any(it[0] in ("c", "qu") for it in d["items"]))
        n_dib = sum(1 for d in page.get_drawings() if fitz.Rect(d["rect"]).intersects(r))
        if n_curvas >= 1 or n_dib >= 8:
            figs.append(fitz.Rect(r))
    # Fusionar los que se solapan
    fusion = True
    while fusion:
        fusion = False
        for i, a in enumerate(figs):
            for b in figs[i + 1:]:
                if a.intersects(b):
                    figs.remove(b); figs[i] = a | b; fusion = True; break
            if fusion:
                break
    return figs


def agrupar_libres(lineas):
    """Une líneas contiguas de una misma columna (cada línea puede venir como bloque suelto en el PDF)."""
    n = len(lineas)
    padre = list(range(n))

    def raiz(i):
        while padre[i] != i:
            padre[i] = padre[padre[i]]; i = padre[i]
        return i
    for i in range(n):
        for j in range(n):
            a, b = lineas[i], lineas[j]
            gap = b.bbox.y0 - a.bbox.y1
            if -2 <= gap < 1.6 * max(a.size, b.size) and abs(a.bbox.x0 - b.bbox.x0) < 60                     and min(a.bbox.x1, b.bbox.x1) - max(a.bbox.x0, b.bbox.x0) > 0:
                padre[raiz(i)] = raiz(j)
    comp = {}
    for i, l in enumerate(lineas):
        comp.setdefault(raiz(i), []).append(l)
    return list(comp.values())


def columnas(lineas):
    """Separa en columnas las líneas de un bloque: un salto grande de x0 entre líneas ordenadas por x0 abre otra columna."""
    ls = sorted(lineas, key=lambda l: l.bbox.x0)
    grupos = [[ls[0]]]
    for ln in ls[1:]:
        if ln.bbox.x0 - grupos[-1][-1].bbox.x0 > 90:
            grupos.append([ln])
        else:
            grupos[-1].append(ln)
    return grupos


def clases_de_titulo(titulos):
    """Agrupa tamaños de título parecidos (±12 %) en una misma clase; devuelve {tamaño: n.º de clase}."""
    clases, ref = {}, []
    for t in sorted(titulos, reverse=True):
        for i, r in enumerate(ref):
            if t >= r * 0.78:
                clases[t] = i; break
        else:
            ref.append(t); clases[t] = len(ref) - 1
    return clases


def xy_cut(items, bbox_of):
    """Orden de lectura: corta por el hueco más grande, horizontal (filas) o vertical (columnas)."""
    if len(items) <= 1:
        return list(items)

    def mejor_corte(clave0, clave1):
        orden = sorted(items, key=lambda i: clave0(bbox_of(i)))
        tope, mejor = clave1(bbox_of(orden[0])), (-1, None)
        for k in range(1, len(orden)):
            hueco = clave0(bbox_of(orden[k])) - tope
            if hueco >= 0 and hueco > mejor[0]:
                mejor = (hueco, k)
            tope = max(tope, clave1(bbox_of(orden[k])))
        return mejor[0], mejor[1], orden
    hy, ky, por_y = mejor_corte(lambda r: r.y0, lambda r: r.y1)
    hx, kx, por_x = mejor_corte(lambda r: r.x0, lambda r: r.x1)
    if ky is None and kx is None:
        return sorted(items, key=lambda i: (bbox_of(i).y0, bbox_of(i).x0))
    if kx is not None and (ky is None or hx > hy * 1.5 and hx > 8):
        return xy_cut(por_x[:kx], bbox_of) + xy_cut(por_x[kx:], bbox_of)
    if ky is not None:
        return xy_cut(por_y[:ky], bbox_of) + xy_cut(por_y[ky:], bbox_of)
    return xy_cut(por_x[:kx], bbox_of) + xy_cut(por_x[kx:], bbox_of)


def convertir(pdf, salida, con_encabezado_pagina=False):
    doc = fitz.open(pdf)
    salida = Path(salida); (salida / "img").mkdir(parents=True, exist_ok=True)
    # Tamaño del cuerpo = el más frecuente (por cantidad de caracteres)
    pesos = {}
    for p in doc:
        for b in p.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                for s in l["spans"]:
                    k = round(s["size"], 1); pesos[k] = pesos.get(k, 0) + len(s["text"])
    cuerpo = max(pesos, key=pesos.get)
    tamanos_titulo = sorted({k for k in pesos if k > cuerpo * 1.15}, reverse=True)
    fuente_cuerpo = None
    md, avisos, figuras, stats = [], [], 0, {"paginas": doc.page_count, "figuras": 0, "codigo": 0, "cuadros": 0}
    primer_titulo = True

    for pn, page in enumerate(doc, 1):
        cont = contenedores(page)
        figs = figuras_vectoriales(page, cont)
        info = page.get_image_info()
        # imágenes raster: se descarta el logo repetido del encabezado
        for im in info:
            r = fitz.Rect(im["bbox"])
            if r.y1 < 70 and r.x0 < 160:
                continue
            if abs(im["height"] / max(im["width"], 1) - 0.3) < 0.02 and im["width"] >= 400:  # logo UTN
                continue
            if r.width > 30 and r.height > 30:
                figs.append(r)
        figs = [f for i, f in enumerate(figs) if not any(g != f and g.contains(f) for g in figs)]

        # Líneas de texto
        lineas = []
        for b in page.get_text("dict")["blocks"]:
            if b["type"] != 0:
                continue
            for l in b["lines"]:
                if not "".join(s["text"] for s in l["spans"]).strip():
                    continue
                ln = Linea(l["bbox"], l["spans"])
                ln.bloque = b["number"]
                # número de página aislado
                if ln.bbox.y0 > page.rect.height - 60 and re.fullmatch(r"\d{1,3}", ln.texto.strip()):
                    continue
                lineas.append(ln)
        pesos_p = {}
        for ln in lineas:
            pesos_p[ln.size] = pesos_p.get(ln.size, 0) + len(ln.texto)
        cuerpo_p = max(pesos_p, key=pesos_p.get) if pesos_p else cuerpo
        titulos_p = sorted({sz for sz in pesos_p if sz > cuerpo_p * 1.15}, reverse=True)
        if fuente_cuerpo is None and lineas:
            fuente_cuerpo = max(((l.font, len(l.texto)) for l in lineas if abs(l.size - cuerpo) < 0.6),
                                key=lambda x: x[1], default=(None, 0))[0]

        # Asignar líneas a figura o a contenedor
        bloques = {}  # clave -> {"rect":..., "fill":..., "lineas":[]}
        figura_txt = {i: [] for i in range(len(figs))}
        for ln in lineas:
            c = ln.bbox
            en_fig = next((i for i, f in enumerate(figs) if f.contains(fitz.Point((c.x0 + c.x1) / 2, (c.y0 + c.y1) / 2))), None)
            if en_fig is not None:
                figura_txt[en_fig].append(ln.texto.strip()); continue
            mejor = None
            for i, (r, f) in enumerate(cont):
                if r.contains(fitz.Point((c.x0 + c.x1) / 2, (c.y0 + c.y1) / 2)) and r.height > 22:
                    if mejor is None or r.get_area() < cont[mejor][0].get_area():
                        mejor = i
            clave = ("c", mejor) if mejor is not None else ("l", None)
            bloques.setdefault(clave, {"rect": cont[mejor][0] if mejor is not None else None,
                                       "fill": cont[mejor][1] if mejor is not None else None, "lineas": []})
            bloques[clave]["lineas"].append(ln)

        # Los textos sin contenedor se agrupan por el bloque original del PDF (así las columnas no se mezclan)
        items = []
        libres = {}
        for clave, b in bloques.items():
            if clave[0] == "c":
                cols = columnas(b["lineas"])
                if len(cols) == 1:
                    items.append(("txt", b["rect"], b))
                else:  # un fondo que abarca varias columnas (tarjetas lado a lado)
                    for ls in cols:
                        r = fitz.Rect(ls[0].bbox)
                        for g in ls:
                            r |= g.bbox
                        items.append(("txt", r, {"rect": b["rect"], "fill": b["fill"], "lineas": ls}))
            else:
                for ln in b["lineas"]:
                    libres.setdefault(ln.bloque, []).append(ln)
        for ls in agrupar_libres([l for v in libres.values() for l in v]):
            r = fitz.Rect(ls[0].bbox)
            for g in ls:
                r |= g.bbox
            items.append(("txt", r, {"rect": None, "fill": None, "lineas": ls}))
        for i, f in enumerate(figs):
            items.append(("fig", f, {"idx": i}))
        # Una figura con un título y un texto justo debajo, en la misma columna, forma una figura con pie
        usados = set()
        for fi, it in enumerate(list(items)):
            if it[0] != "fig" or it[1].width > 0.5 * (page.rect.width - 76):  # solo ilustraciones chicas; un diagrama ancho no lleva pie
                continue
            cands = []
            for tj, t in enumerate(items):
                if t[0] != "txt" or tj in usados:
                    continue
                ancho = min(it[1].x1, t[1].x1) - max(it[1].x0, t[1].x0)
                gap = t[1].y0 - it[1].y1
                if -2 <= gap <= 45 and ancho > 0.5 * min(it[1].width, t[1].width):
                    cands.append((gap, tj))
            if cands:
                tj = min(cands)[1]
                usados.add(tj)
                items[fi] = ("figcap", it[1] | items[tj][1], {"fig": it, "txt": items[tj]})
        items = [t for k, t in enumerate(items) if k not in usados]
        orden = xy_cut(items, lambda it: it[1])

        md.append(f"<!-- Página {pn} -->" if con_encabezado_pagina else "")
        ancho_util = page.rect.width - 2 * 38  # márgenes del original (≈ ancho del texto)

        def figura_md(rect, b):
            nonlocal figuras
            figuras += 1; stats["figuras"] += 1
            nombre = f"p{pn:02d}_fig{figuras:02d}.png"
            page.get_pixmap(dpi=200, clip=rect + (-4, -4, 4, 4)).save(salida / "img" / nombre)
            alt = " / ".join(figura_txt[b["idx"]])[:1000].replace("[", "(").replace("]", ")")
            pct = max(15, min(100, round(rect.width / ancho_util * 100)))  # conserva la proporción del original
            return (f'![{alt or "Figura"}](img/{nombre}){{: style="width: {pct}%" }}\n'
                    f"<!-- REVISAR: figura recortada de la página {pn}; su texto interno no se audita por texto, lo mira el tutor. -->")

        for tipo, rect, b in orden:
            if tipo == "fig":
                md.append(figura_md(rect, b))
                continue
            if tipo == "figcap":
                f_it, t_it = b["fig"], b["txt"]
                pie = bloque_a_md(t_it[2], page, cuerpo_p, titulos_p, fuente_cuerpo, stats, avisos, pn, primer_titulo)
                md.append('<figure markdown="1">\n' + figura_md(f_it[1], f_it[2]) + '\n<figcaption markdown="1">\n'
                          + pie + "\n</figcaption>\n</figure>")
                continue
            md.append(bloque_a_md(b, page, cuerpo_p, titulos_p, fuente_cuerpo, stats, avisos, pn, primer_titulo))
            if any(l.size in titulos_p for l in b["lineas"]):
                primer_titulo = False
    texto = "\n\n".join(x for x in md if x.strip()) + "\n"
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    # El primer título del documento es el título general (generar.py lo descarta: la primera hoja ya lo pone)
    texto = re.sub(r"^#{2,4} ", "# ", texto, count=1, flags=re.M)
    ruta = salida / (Path(pdf).stem + ".md")
    ruta.write_text(texto, encoding="utf-8")
    return ruta, stats, avisos


def spans_a_md(ln, page):
    """Texto de una línea con negrita, cursiva y código en línea."""
    partes = []
    for s in ln.spans:
        t = s["text"]
        if not t.strip():
            partes.append(t); continue
        fn = s["font"].lower()
        negrita = "bold" in fn or bool(s["flags"] & 16)
        cursiva = "italic" in fn or bool(s["flags"] & 2)
        # código en línea: fondo gris pequeño detrás del span
        r = fitz.Rect(s["bbox"])
        en_linea = any(d.get("fill") and abs(lum(d["fill"]) - 0.94) < 0.05 and d["rect"].height < 22 and d["rect"].width < 400
                       and fitz.Rect(d["rect"]).contains(r + (1, 1, -1, -1)) for d in page.get_drawings())
        pre, suf = ("", "")
        if en_linea:
            pre = suf = "`"
        elif negrita and not ln.bold:
            pre = suf = "**"
        elif cursiva:
            pre = suf = "*"
        m = re.match(r"^(\s*)(.*?)(\s*)$", t, re.S)
        cuerpo_t = m.group(2) if en_linea else esc(m.group(2))
        partes.append(f"{m.group(1)}{pre}{cuerpo_t}{suf}{m.group(3)}")
    out = "".join(partes)
    return re.sub(r"``|\*\*\*\*", "", out)


def bloque_a_md(b, page, cuerpo, titulos, fuente_cuerpo, stats, avisos, pn, primer_titulo):
    lineas = sorted(b["lineas"], key=lambda l: (round(l.bbox.y0), l.bbox.x0))
    fill = b["fill"]
    # --- ¿bloque de código? fuente distinta del cuerpo y aspecto de código
    distintas = [l for l in lineas if l.font != fuente_cuerpo and l.size <= cuerpo + 0.6 and not l.font.lower().startswith(("roboto",))]
    cod = [l for l in lineas if es_codigo_linea(l.texto)]
    if lineas and len(distintas) >= 0.6 * len(lineas) and len(cod) >= 0.4 * len(lineas):
        stats["codigo"] += 1
        crudas = [l.texto.rstrip() for l in lineas]
        comun = min((len(t) - len(t.lstrip()) for t in crudas if t.strip()), default=0)
        txt = "\n".join(t[comun:] for t in crudas)
        return f"```java\n{txt}\n```\n<!-- REVISAR: lenguaje del bloque asumido (java); líneas largas pueden venir partidas en el PDF. -->"
    # --- cuadro destacado por color de fondo
    prefijo = ""
    oscuro = fill is not None and lum(fill) < 0.5
    azul_claro = fill is not None and fill[2] > fill[0] + 0.1 and lum(fill) >= 0.5 and lum(fill) < 0.88
    cuerpo_md = parrafos(lineas, page, cuerpo, titulos, primer_titulo, dentro_de_cuadro=oscuro or azul_claro)
    if oscuro or azul_claro:
        stats["cuadros"] += 1
        tipo = "importante" if re.match(r"\s*(\*\*)?Importante", cuerpo_md) else "nota"
        sangrado = "\n".join(("    " + x) if x.strip() else "" for x in cuerpo_md.splitlines())
        return f'!!! {tipo} ""\n{sangrado}'.replace(' ""', "", 1) if False else f"!!! {tipo}\n{sangrado}"
    return cuerpo_md


def parrafos(lineas, page, cuerpo, titulos, primer_titulo, dentro_de_cuadro=False):
    conteo = {}
    for x in lineas:
        conteo[x.size] = conteo.get(x.size, 0) + 1
    out, actual, prev = [], [], None

    def cerrar():
        nonlocal actual
        if actual:
            out.append(" ".join(actual).strip()); actual = []
    for l in lineas:
        t = spans_a_md(l, page).strip()
        if not t:
            continue
        # título
        if l.size in titulos and not dentro_de_cuadro and len(t) <= 110 and conteo[l.size] <= 3:
            cerrar()
            nivel = 2 if l.size >= cuerpo * 1.7 else 3
            if prev is not None and prev.size == l.size and out and out[-1].startswith("#" * nivel + " "):
                out[-1] += " " + t  # título partido en varias líneas
            else:
                out.append("#" * nivel + " " + t)
            prev = l; continue
        # título de tarjeta: fuente de títulos (slab) de tamaño intermedio
        if "slab" in l.font.lower() and l.size > cuerpo * 0.75:
            cerrar()
            out.append(f"**{t}**" + ("" if re.fullmatch(r"\d{1,2}", t) else "  ")); prev = l; continue
        # viñeta: pequeño cuadrado/círculo relleno a la izquierda de la línea
        marca = any(d.get("fill") and fitz.Rect(d["rect"]).width < 9 and fitz.Rect(d["rect"]).height < 9
                    and l.bbox.x0 - 32 < d["rect"].x1 <= l.bbox.x0 - 2 and abs((d["rect"].y0 + d["rect"].y1) / 2 - (l.bbox.y0 + l.bbox.y1) / 2) < l.size
                    for d in page.get_drawings())
        if marca:
            cerrar(); actual = ["- " + t]; prev = l; continue
        if prev is not None and l.bbox.y0 - prev.bbox.y1 > l.size * 0.55 and not (actual and actual[0].startswith("- ") and l.bbox.x0 > prev.bbox.x0 - 1 and False):
            cerrar()
        if actual and actual[0].startswith("- ") and l.bbox.y0 - prev.bbox.y1 > l.size * 0.55:
            cerrar()
        actual.append(t)
        prev = l
    cerrar()
    return "\n\n".join(out)


def main():
    if len(sys.argv) < 3:
        print(__doc__); return 2
    ruta, stats, avisos = convertir(sys.argv[1], sys.argv[2], con_encabezado_pagina="--sin-encabezado-pagina" not in sys.argv)
    if "--json" in sys.argv:
        print(json.dumps({"md": str(ruta), **stats, "avisos": avisos}, ensure_ascii=False))
    else:
        print(f"OK {ruta}  páginas={stats['paginas']} figuras={stats['figuras']} bloques_de_código={stats['codigo']} cuadros={stats['cuadros']}")
        print("Revisá las marcas <!-- REVISAR --> y corré verificar_fidelidad.py antes de seguir.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
