"""Apila página original (arriba) y editada (abajo) en un PNG. Uso: python comparar_pdf.py ORIG.pdf NUEVO.pdf SALIDA_PREFIJO pag1 pag2 ... [--dpi 50]"""
import sys, fitz
from PIL import Image
o, n, pref = sys.argv[1:4]; pgs = [int(x) for x in sys.argv[4:] if not x.startswith("--")]
dpi = 50
d1, d2 = fitz.open(o), fitz.open(n)
for k in pgs:
    ims = []
    for d in (d1, d2):
        pm = d[k - 1].get_pixmap(dpi=dpi); ims.append(Image.frombytes("RGB", (pm.width, pm.height), pm.samples))
    w, h = ims[0].size; c = Image.new("RGB", (w, h * 2 + 6), (255, 0, 0)); c.paste(ims[0], (0, 0)); c.paste(ims[1], (0, h + 6)); c.save(f"{pref}_p{k}.png")
print("ok", pgs)
