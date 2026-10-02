"""Quita la marca 'Made with Gamma' (imagen del badge + link a gamma.app) de un PDF.
Uso: python quitar_marca_gamma.py ENTRADA.pdf SALIDA.pdf
No modifica la entrada. Solo toca el badge: imagen < 200x60 px pegada al borde inferior, y links a gamma.app."""
import sys, fitz

def limpiar(entrada, salida):
    d = fitz.open(entrada)
    badges = set()
    for pg in d:
        H = pg.rect.height
        for im in pg.get_image_info(xrefs=True):
            x0, y0, x1, y1 = im["bbox"]
            if im["xref"] and (x1 - x0) < 200 and (y1 - y0) < 60 and y0 > H * 0.85:
                badges.add((pg.number, im["xref"]))
    n_img = n_lnk = 0
    done = set()
    for pno, xref in sorted(badges):
        if xref in done:
            continue
        try:
            d[pno].delete_image(xref); done.add(xref); n_img += 1
        except Exception:
            pass
    for pg in d:
        for l in pg.get_links():
            if "gamma" in l.get("uri", "").lower():
                pg.delete_link(l); n_lnk += 1
    d.save(salida, garbage=4, deflate=True)
    return len(d), n_img, n_lnk

if __name__ == "__main__":
    p, i, l = limpiar(sys.argv[1], sys.argv[2])
    print(f"{sys.argv[2]}: {p} págs, {i} imagen(es) badge reemplazada(s), {l} links gamma quitados")
