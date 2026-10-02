"""Reemplazo de texto dentro de PDF de Gamma (diapositivas) conservando el aspecto.

Idea: en estos PDF cada línea visual es un bloque de texto independiente. Se agrupan las líneas de un
párrafo (mismo borde izquierdo, misma fuente/tamaño/color, interlineado regular), se borra SOLO el texto
(redacción sin relleno: fondos, tarjetas y bordes no se tocan) y se recompone con la misma fuente, tamaño,
color y línea base, ajustando el corte de líneas al ancho original.

Uso como librería:
    from editar_pdf_texto import editar, volcar
    volcar("in.pdf", paginas=[3])                    # lista párrafos con su id
    editar("in.pdf", "out.pdf", ediciones, fuentes)  # ver docstring de editar()

Las fuentes originales de Gamma son subconjuntos sin tabla Unicode, así que no se pueden reutilizar:
se usan las mismas familias de código abierto (OFL) descargadas aparte (ver FUENTES).
"""
import re, statistics
import fitz

PREFIJOS = {  # prefijo del nombre de fuente del PDF -> clave de FUENTES
    "OpenSans-Regular": "OpenSans-Regular", "OpenSans-Bold": "OpenSans-Bold",
    "LibreBaskerville-Regular": "LibreBaskerville-Regular", "Nobile-Regular": "Nobile-Regular",
    "Nobile-Bold": "Nobile-Bold", "Corben-Regular": "Corben-Regular",
}


def _norm(s):
    return re.sub(r"\s+", " ", s).strip()


def _rgb(c):
    return ((c >> 16 & 255) / 255, (c >> 8 & 255) / 255, (c & 255) / 255)


def lineas(pg):
    out = []
    for b in pg.get_text("dict")["blocks"]:
        if b["type"] != 0:
            continue
        for l in b["lines"]:
            sp = [s for s in l["spans"] if s["text"].strip()]
            if not sp:
                continue
            s0 = sp[0]
            out.append(dict(bbox=fitz.Rect(l["bbox"]), text=_norm("".join(s["text"] for s in l["spans"])),
                            font=s0["font"].split("+")[-1], size=round(s0["size"], 1), color=s0["color"],
                            origin=s0["origin"],
                            bold=[_norm(s["text"]) for s in sp if "Bold" in s["font"] and _norm(s["text"])]))
    out.sort(key=lambda l: (round(l["bbox"].x0), l["bbox"].y0))
    return out


def parrafos(pg):
    ls = lineas(pg)
    usados, res = set(), []
    for i, l in enumerate(ls):
        if i in usados:
            continue
        grp = [i]; usados.add(i)
        ult = l
        while True:
            sig = None
            for j, m in enumerate(ls):
                if j in usados:
                    continue
                dy = m["bbox"].y0 - ult["bbox"].y0
                if (abs(m["bbox"].x0 - ult["bbox"].x0) < 2 and m["font"] == ult["font"] and m["size"] == ult["size"]
                        and m["color"] == ult["color"] and 0 < dy < 1.75 * ult["size"]):
                    if sig is None or dy < sig[0]:
                        sig = (dy, j)
            if sig is None:
                break
            grp.append(sig[1]); usados.add(sig[1]); ult = ls[sig[1]]
        res.append([ls[k] for k in grp])
    res.sort(key=lambda g: (g[0]["bbox"].y0, g[0]["bbox"].x0))
    return res


def volcar(pdf, paginas=None):
    d = fitz.open(pdf)
    for pn, pg in enumerate(d):
        if paginas and (pn + 1) not in paginas:
            continue
        print(f"== p{pn+1} {pg.rect.width:.0f}x{pg.rect.height:.0f}")
        for k, g in enumerate(parrafos(pg)):
            r = g[0]["bbox"]
            print(f" #{k:02d} L{len(g)} {g[0]['font'][:16]} {g[0]['size']} x{r.x0:.0f} y{r.y0:.0f} | "
                  + " ".join(l["text"] for l in g)[:110])


def _resaltados(pg, union, size):
    """Cajas de código en línea (rectángulos redondeados claros) contenidas en el párrafo y su texto."""
    hl = []
    raw = pg.get_text("rawdict")
    chars = [c for b in raw["blocks"] if b["type"] == 0 for l in b["lines"] for s in l["spans"] for c in s["chars"]]
    for dr in pg.get_drawings():
        r, fill = dr["rect"], dr.get("fill")
        if fill is None or len(dr["items"]) < 8:
            continue
        if (r.x0 >= union.x0 - 8 and r.x1 <= union.x1 + 8 and r.y0 >= union.y0 - 1.5 and r.y1 <= union.y1 + 1.5
                and 6 < r.width < 300 and r.height < size * 1.6):
            cs = [c for c in chars if r.x0 <= (c["bbox"][0] + c["bbox"][2]) / 2 <= r.x1
                  and r.y0 - 1 <= (c["bbox"][1] + c["bbox"][3]) / 2 <= r.y1 + 1]
            cs.sort(key=lambda c: (round(c["bbox"][1]), c["bbox"][0]))
            tok = "".join(c["c"] for c in cs).strip()
            if tok and cs:
                tw = cs[-1]["bbox"][2] - cs[0]["bbox"][0]
                base = cs[0]["origin"][1]
                hl.append(dict(rect=fitz.Rect(r), fill=fill, token=tok, padx=max(0, (r.width - tw) / 2),
                               up=base - r.y0, alto=r.height))
    return hl


def _ajustar(texto, medir, size, ancho):
    pal, ls, cur = texto.split(" "), [], ""
    for w in pal:
        t = (cur + " " + w).strip()
        if medir(t, size) <= ancho or not cur:
            cur = t
        else:
            ls.append(cur); cur = w
    ls.append(cur)
    return ls


def editar(entrada, salida, ediciones, fuentes, extra_lineas=1, verbose=True):
    """ediciones: lista de dict(pagina=1.., match='texto del párrafo (normalizado)', nuevo='texto',
                                modo='parrafo'|'linea', ancho=None, tamanio_min=0.9)
    fuentes: dict clave->ruta .ttf. Devuelve lista de (edicion, estado)."""
    d = fitz.open(entrada)
    fobj = {k: fitz.Font(fontfile=v) for k, v in fuentes.items()}
    informe = []
    for e in ediciones:
        pg = d[e["pagina"] - 1]
        grupos = parrafos(pg)
        cand = []
        for g in grupos:
            if e.get("modo") == "linea":
                cand += [[l] for l in g if e["match"] in l["text"]]
            elif e["match"] in " ".join(l["text"] for l in g):
                cand.append(g)
        if len(cand) != 1:
            informe.append((e, f"ERROR coincidencias={len(cand)}")); continue
        g = cand[0]
        clave = next((v for k, v in PREFIJOS.items() if g[0]["font"].startswith(k)), None)
        if clave is None or clave not in fobj:
            informe.append((e, f"ERROR fuente {g[0]['font']}")); continue
        ft = fobj[clave]; size0 = g[0]["size"]
        bclave = clave.replace("Regular", "Bold") if "Regular" in clave else None
        fb = fobj.get(bclave)
        if "negritas" in e:
            btok = list(e["negritas"])
        else:
            btok = sorted({t for l in g for t in l.get("bold", [])}, key=len, reverse=True)
        if fb is None or clave.endswith("Bold"):
            btok = []
        pat_b = re.compile("(" + "|".join(re.escape(t) for t in btok) + ")") if btok else None

        def segs(txt):
            if not pat_b:
                return [(txt, False)]
            out_, pos = [], 0
            for m_ in pat_b.finditer(txt):
                if m_.start() > pos:
                    out_.append((txt[pos:m_.start()], False))
                out_.append((m_.group(0), True)); pos = m_.end()
            if pos < len(txt):
                out_.append((txt[pos:], False))
            return out_

        def medir(txt, size_):
            return sum((fb if bo else ft).text_length(t_, size_) for t_, bo in segs(txt))
        x0 = min(l["bbox"].x0 for l in g)
        ancho = e.get("ancho") or (max(l["bbox"].x1 for l in g) - x0)
        pitch = (statistics.median([g[i + 1]["origin"][1] - g[i]["origin"][1] for i in range(len(g) - 1)])
                 if len(g) > 1 else size0 * 1.59)
        base1 = g[0]["origin"][1]
        union = fitz.Rect(g[0]["bbox"])
        for l in g:
            union |= l["bbox"]
        otras = [l["bbox"] for gg in grupos for l in gg if l not in g]
        orig_txt = " ".join(l["text"] for l in g)
        if "reemplazos" in e:
            nuevo_txt = orig_txt
            for viejo, nue in e["reemplazos"]:
                if viejo not in nuevo_txt:
                    nuevo_txt = None; break
                nuevo_txt = nuevo_txt.replace(viejo, nue)
            if nuevo_txt is None:
                informe.append((e, f"ERROR reemplazo no encontrado: {viejo!r} en {orig_txt[:80]!r}")); continue
        else:
            nuevo_txt = e["nuevo"]
        nuevo_txt = _norm(nuevo_txt)
        ok, size = False, size0
        while size >= size0 * e.get("tamanio_min", 0.9) - 1e-6:
            ls = _ajustar(nuevo_txt, medir, size, ancho)
            if e.get("modo") == "linea":
                ls_ok = len(ls) == 1
            else:
                ls_ok = len(ls) <= e.get("max_lineas", len(g) + extra_lineas)
            if ls_ok:
                fin = fitz.Rect(x0, union.y0, x0 + ancho, base1 + (len(ls) - 1) * pitch + size * 0.3)
                if not any(fin.intersects(o) and not (o in [l["bbox"] for l in g]) and
                           fin.y1 > o.y0 + 1 and o.y1 > union.y1 + 0.5 for o in otras):
                    ok = True; break
            size = round(size - 0.2, 1)
        if not ok:
            informe.append((e, "NO CABE")); continue
        cx = (min(l["bbox"].x0 for l in g) + max(l["bbox"].x1 for l in g)) / 2

        rx = max(l["bbox"].x1 for l in g)

        def xlinea(linea, _cx=cx, _rx=rx, _size=size, _x0=x0, _al=e.get("alinear") or ("centro" if e.get("centro") else "izq")):
            if _al == "centro":
                return _cx - medir(linea, _size) / 2
            if _al == "derecha":
                return _rx - medir(linea, _size)
            return _x0

        hl = _resaltados(pg, union, size0)
        if hl:   # quitar las cajas viejas: solo gráficos totalmente cubiertos por el párrafo
            pg.add_redact_annot(fitz.Rect(union.x0 - 1, union.y0 - 1.2, union.x1 + 1, union.y1 + 1.2), fill=False)
            pg.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE,
                                graphics=fitz.PDF_REDACT_LINE_ART_REMOVE_IF_COVERED,
                                text=fitz.PDF_REDACT_TEXT_NONE)
        r = fitz.Rect(union.x0 - 0.5, union.y0 + 0.5, union.x1 + 0.5, union.y1 - 0.5)
        pg.add_redact_annot(r, fill=False)
        pg.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)
        nombre = "F" + clave.replace("-", "")
        pg.insert_font(fontname=nombre, fontfile=fuentes[clave])
        nombre_b = ("F" + bclave.replace("-", "")) if (fb is not None and btok) else None
        if nombre_b:
            pg.insert_font(fontname=nombre_b, fontfile=fuentes[bclave])
        if hl:   # redibujar las cajas bajo las mismas palabras del texto nuevo
            tokens = {}
            for h in hl:
                tokens.setdefault(h["token"], h)
            if e.get("resaltar"):   # indicar a mano las palabras a resaltar (p. ej. si el original estaba partido)
                tokens = {t: hl[0] for t in e["resaltar"]}
            for i, linea in enumerate(ls):
                for tok, h in tokens.items():
                    for m in re.finditer(r"(?<![\w.])" + re.escape(tok) + r"(?!\w)", linea):
                        xs = xlinea(linea) + medir(linea[:m.start()], size)
                        wt = medir(tok, size)
                        yb = base1 + i * pitch
                        caja = fitz.Rect(xs - h["padx"], yb - h["up"], xs + wt + h["padx"], yb - h["up"] + h["alto"])
                        pg.draw_rect(caja, color=None, fill=h["fill"], radius=0.18)
        for i, linea in enumerate(ls):
            yb = base1 + i * pitch
            xl = xlinea(linea)
            xcur = xl
            for t_, bo in segs(linea):
                kw = {"morph": (fitz.Point(xcur, yb), fitz.Matrix(1, 0, 0.21, 1, 0, 0))} if e.get("cursiva") else {}
                pg.insert_text((xcur, yb), t_, fontname=(nombre_b if bo else nombre), fontsize=size,
                               color=_rgb(g[0]["color"]), **kw)
                xcur += (fb if bo else ft).text_length(t_, size)
        aplicadas = [t for t in btok if any(t in l_ for l_ in ls)]
        extra = f" | negritas orig={btok} aplicadas={aplicadas}" if btok else ""
        informe.append((e, f"OK {len(g)}->{len(ls)} líneas, tamaño {size0}->{size}{extra}"))
    d.save(salida, garbage=4, deflate=True)
    if verbose:
        for e, s in informe:
            print(f"p{e['pagina']} {s} | {e['match'][:50]}")
    return informe
