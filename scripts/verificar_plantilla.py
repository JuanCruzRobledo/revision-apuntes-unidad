#!/usr/bin/env python3
"""Verificación mecánica de un documento generado con la plantilla TUPaD.

Uso: python verificar_plantilla.py FINAL.md SALIDA.pdf [--sin-persona]
Comprueba el Markdown (encabezado de datos, tipo, bibliografía solo en teoría, marcas de plantilla sin completar,
marcas <!-- REVISAR --> pendientes) y el PDF (primera hoja: materia, unidad, etiqueta, revisor; pie con numeración;
patrones de redacción con verificar_docx.PATRONES). Código de salida 1 si algo obligatorio falla.
NO reemplaza la lectura completa ni la revisión manual del tutor.
"""
import re
import sys
from pathlib import Path

import fitz

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verificar_docx import PATRONES, PATRONES_DE_ESTILO  # noqa: E402

OBLIGATORIOS = {"apunte": ["materia", "unidad_num", "unidad_titulo", "tema", "revisor"],
                "tp": ["materia", "unidad_num", "unidad_titulo", "titulo", "revisor"]}
ETIQUETA = {"apunte": "apunte teórico", "tp": "trabajo práctico"}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 2:
        print(__doc__); return 2
    md = Path(args[0]).read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", md, re.S)
    fallas = []
    datos = {}
    if not m:
        print("FALLA: falta el encabezado de datos."); return 1
    for linea in m.group(1).splitlines():
        linea = re.sub(r"\s+#.*$", "", linea).strip()
        if ":" in linea:
            k, v = linea.split(":", 1); datos[k.strip().lower()] = v.strip().strip('"')
    tipo = datos.get("tipo", "apunte")
    if tipo not in OBLIGATORIOS:
        print(f"FALLA: tipo '{tipo}' desconocido."); return 1
    for k in OBLIGATORIOS[tipo]:
        if not datos.get(k):
            fallas.append(f"falta el dato '{k}' en el encabezado")
    cuerpo = md[m.end():]
    tiene_biblio = re.search(r"^## Bibliograf", cuerpo, re.M | re.I) is not None
    if tipo == "apunte" and not tiene_biblio:
        fallas.append("el apunte no tiene '## Bibliografía' (obligatoria; sale de la sección 0 del aula)")
    if tipo == "tp" and tiene_biblio:
        fallas.append("el TP no lleva bibliografía")
    if re.search(r"\{\{[A-Z_]+\}\}|Nombre Apellido|Título del", md):
        fallas.append("quedan marcas de plantilla sin completar")
    pendientes = len(re.findall(r"<!--\s*REVISAR", cuerpo))

    d = fitz.open(args[1])
    p1 = re.sub(r"\s+", " ", d[0].get_text())
    for etiqueta, patron in (("Materia", rf"Materia:\s*{re.escape(datos.get('materia', ''))}"),
                             ("Unidad", rf"UNIDAD\s*{re.escape(datos.get('unidad_num', ''))}"),
                             ("Etiqueta de tipo", ETIQUETA[tipo]),
                             ("Revisor", rf"Revisor de la unidad:\s*Prof\.\s*{re.escape(datos.get('revisor', ''))}")):
        if not re.search(patron, p1, re.I):
            fallas.append(f"primera hoja sin '{etiqueta}'")
    if tipo == "tp" and re.search(r"Tema\s*\d", p1):
        fallas.append("el TP no lleva línea de Tema")
    pie = all(re.search(rf"Página\s*{i + 1}\s*de\s*{len(d)}", d[i].get_text()) for i in range(len(d)))
    if not pie:
        fallas.append("el pie no tiene 'Página N de M' en todas las hojas")
    ultima = " ".join(p.get_text() for p in d[max(0, len(d) - 2):])
    if tipo == "apunte" and not re.search(r"Bibliograf", ultima, re.I):
        fallas.append("la bibliografía no está al final del PDF")

    texto = re.sub(r"\s+", " ", " ".join(p.get_text() for p in d))
    sin_persona = "--sin-persona" in sys.argv
    print(f"== {args[1]}  (tipo {tipo}, {len(d)} páginas)")
    for k, p in PATRONES.items():
        if k in ("markdown",) or (sin_persona and k in PATRONES_DE_ESTILO):
            continue
        hits = list(re.finditer(p, texto, re.I if k != "emoji" else 0))
        print(f"{k:24}{len(hits)}")
        for h in hits[:6]:
            print("     ...", texto[max(0, h.start() - 55):h.end() + 45].strip(), "...")
    print(f"Marcas <!-- REVISAR --> en el Markdown: {pendientes} (cada una la resuelve el corrector o la mira el tutor)")
    if fallas:
        print("\nFALLAS:"); [print(" -", f) for f in fallas]
        return 1
    print("\nPrimera hoja, etiqueta, pie y bibliografía: OK. Falta la lectura completa y la revisión manual del tutor.")
    print("Leer cada coincidencia de persona/futuro en contexto antes de reportarla (hay falsos positivos).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
