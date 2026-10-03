#!/usr/bin/env python3
"""Control mecánico de la bibliografía de un apunte: la conversión a APA 7 no puede inventar datos.

Uso:
  python verificar_bibliografia.py apa BIBLIOGRAFIA.md              # APA 7 vs. original del aula (una vez por materia)
  python verificar_bibliografia.py uso FINAL.md BIBLIOGRAFIA.md     # la bibliografía del apunte sale de la lista APA 7
Opción: --json

BIBLIOGRAFIA.md (<trabajo>/fuentes/bibliografia.md) tiene dos listas numeradas con el mismo orden:
  ## Referencias (original)    <- transcripción textual del aula (sin emojis decorativos)
  ## Referencias (APA 7)       <- conversión: solo reordena y da formato a datos que ya estaban en el original
Una referencia que no se puede convertir porque falta un dato obligatorio se escribe en la lista APA como
`[INCOMPLETA: falta título]` y bloquea los apuntes que la usen hasta que el tutor la complete en el aula.

Comprobaciones de `apa`: misma cantidad de ítems; cada palabra o número de la versión APA debe estar en el original (si no, posible dato
inventado: FALLA); estructura APA (autor, `(año)` o `(s. f.)`, título, cierre); datos del original que se perdieron (informativo).
Código de salida 1 si algo obligatorio falla. NO reemplaza la confirmación del tutor.
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

# Conectores y marcas propias del formato APA 7 en español que no vienen del original
PERMITIDAS = {"s", "f", "ed", "eds", "y", "en", "de", "la", "el", "vol", "pp", "cap", "recuperado", "ª", "a", "https", "http", "doi", "org", "n"}


def sin_acentos(t):
    return "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn")


def tokens(t):
    t = re.sub(r"[\U0001F300-\U0001FAFF☀-➿️]", " ", t)  # emojis decorativos
    return [x for x in re.findall(r"\w+", sin_acentos(t).lower())]


def leer_listas(ruta):
    texto = Path(ruta).read_text(encoding="utf-8")
    partes = re.split(r"^##\s+", texto, flags=re.M)
    listas = {}
    for p in partes[1:]:
        titulo, _, cuerpo = p.partition("\n")
        items = [m.group(1).strip() for m in re.finditer(r"^\s*\d+\.\s+(.*\S)\s*$", cuerpo, re.M)]
        listas[titulo.strip().lower()] = items
    return listas


def buscar(listas, clave):
    for k, v in listas.items():
        if clave in k:
            return v
    return None


def verificar_apa(ruta):
    listas = leer_listas(ruta)
    orig, apa = buscar(listas, "original"), buscar(listas, "apa")
    res = {"fallas": [], "avisos": [], "incompletas": []}
    if orig is None or apa is None:
        res["fallas"].append("faltan las secciones '## Referencias (original)' y/o '## Referencias (APA 7)'")
        return res
    if len(orig) != len(apa):
        res["fallas"].append(f"hay {len(orig)} referencias originales y {len(apa)} en APA: tienen que corresponderse una a una")
        return res
    for i, (o, a) in enumerate(zip(orig, apa), 1):
        if a.upper().startswith("[INCOMPLETA"):
            res["incompletas"].append(f"{i}. {a}  (original: {o[:80]})")
            continue
        to, ta = set(tokens(o)), tokens(a)
        nuevos = [t for t in ta if t not in to and t not in PERMITIDAS and not (len(t) == 1 and any(x.startswith(t) for x in to))]
        if nuevos:
            res["fallas"].append(f"{i}. APA tiene datos que NO están en el original (posible invención): {sorted(set(nuevos))} -> {a[:90]}")
        iniciales = {t for t in ta if len(t) == 1}
        perdidos = [t for t in tokens(o) if t not in set(ta) and (len(t) > 3 or t.isdigit()) and t[0] not in iniciales
                    and t not in ("libro", "link", "https", "http", "www", "edition", "edicion", "edition")]
        if perdidos:
            res["avisos"].append(f"{i}. datos del original que no figuran en APA: {sorted(set(perdidos))[:8]}")
        if not re.search(r"\((\d{4}[a-z]?|s\. ?f\.)\)", a):
            res["fallas"].append(f"{i}. falta el año entre paréntesis, o '(s. f.)' si no tiene fecha: {a[:90]}")
        elif not re.match(r"^[^()]{3,}\(", a):
            res["fallas"].append(f"{i}. falta el autor antes del año: {a[:90]}")
        if not re.search(r"\)\.\s+\S", a):
            res["fallas"].append(f"{i}. falta el título después del año (formato 'Autor. (Año). Título.'): {a[:90]}")
    return res


def verificar_uso(ruta_final, ruta_biblio):
    listas = leer_listas(ruta_biblio)
    apa = buscar(listas, "apa") or []
    final = Path(ruta_final).read_text(encoding="utf-8")
    m = re.search(r"^##\s+Bibliograf[^\n]*\n(.*?)(?=^##\s|\Z)", final, re.M | re.S)
    res = {"fallas": [], "avisos": [], "incompletas": []}
    if not m:
        res["fallas"].append("el apunte no tiene '## Bibliografía'")
        return res
    items = [x.group(1).strip() for x in re.finditer(r"^\s*\d+\.\s+(.*\S)\s*$", m.group(1), re.M)]
    if not items:
        res["fallas"].append("la sección Bibliografía no tiene una lista numerada")
    norm = lambda t: " ".join(tokens(re.sub(r"[*_`]", "", t)))
    base = {norm(a): a for a in apa}
    vistos = set()
    for i, it in enumerate(items, 1):
        n = norm(it)
        if n in vistos:
            res["fallas"].append(f"{i}. referencia repetida: {it[:80]}")
        vistos.add(n)
        if n not in base:
            res["fallas"].append(f"{i}. NO está en la lista APA 7 de la materia (no se agregan fuentes por fuera del aula): {it[:90]}")
        elif base[n].upper().startswith("[INCOMPLETA"):
            res["fallas"].append(f"{i}. referencia incompleta: no se puede usar hasta que el tutor la complete en el aula")
    if re.search(r"<!--\s*REVISAR[^>]*bibliograf", final, re.I | re.S):
        res["avisos"].append("hay una marca REVISAR sobre la selección de referencias: el tutor decide cuáles lleva el apunte")
    res["avisos"].append(f"el apunte usa {len(items)} de {len(apa)} referencias de la materia")
    return res


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args or args[0] not in ("apa", "uso") or (args[0] == "apa" and len(args) != 2) or (args[0] == "uso" and len(args) != 3):
        print(__doc__); return 2
    res = verificar_apa(args[1]) if args[0] == "apa" else verificar_uso(args[1], args[2])
    if "--json" in sys.argv:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(f"== bibliografía ({args[0]})")
        for k, t in (("fallas", "FALLA"), ("incompletas", "INCOMPLETA"), ("avisos", "aviso")):
            for x in res[k]:
                print(f"  [{t}] {x}")
        if not res["fallas"]:
            print("  Sin fallas mecánicas. Falta la confirmación del tutor (tabla original -> APA 7).")
    return 1 if res["fallas"] else 0


if __name__ == "__main__":
    sys.exit(main())
