# -*- coding: utf-8 -*-
"""
Genera apuntes teóricos y trabajos prácticos TUPaD: Markdown -> HTML autocontenido -> PDF.

    python generar.py contenido/U6_argumentos.md            # HTML + PDF en salida/
    python generar.py contenido/*.md --preview              # además, PNG de cada página para revisar
    python generar.py doc.md --out "C:/ruta/salida"

El .md empieza con un encabezado de datos entre líneas '---':

    ---
    tipo: apunte                 # apunte | tp
    materia: Programación I
    unidad_num: 6
    unidad_titulo: Funciones
    tema: Argumentos y valores de retorno     # (tp: usar 'titulo')
    revisor: Nombre Apellido                  # sin "Prof."; la plantilla lo agrega
    ---

El PDF se imprime con Chrome headless: no hace falta instalar nada más que
`pip install markdown pygments pymupdf`. Logo y fuentes van embebidos en el
HTML, así que el .html generado se puede abrir o mover sin la carpeta assets.
"""
import argparse
import base64
import glob
import html
import re
import shutil
import subprocess
import sys
from pathlib import Path

import markdown

RAIZ = Path(__file__).resolve().parent
OBLIGATORIOS = {
    "apunte": ["materia", "unidad_num", "unidad_titulo", "tema", "revisor"],
    "tp": ["materia", "unidad_num", "unidad_titulo", "titulo", "revisor"],
}

CHROME = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/usr/bin/google-chrome", "/usr/bin/google-chrome-stable", "/usr/bin/chromium", "/usr/bin/chromium-browser",
    "/snap/bin/chromium", "/usr/bin/microsoft-edge",
]


def data_uri(ruta: Path, mime: str) -> str:
    return f"data:{mime};base64," + base64.b64encode(ruta.read_bytes()).decode()


def leer_md(ruta: Path):
    texto = ruta.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", texto, re.S)
    if not m:
        sys.exit(f"{ruta.name}: falta el encabezado de datos entre líneas '---'.")
    datos = {}
    for linea in m.group(1).splitlines():
        linea = re.sub(r"\s+#.*$", "", linea).strip()
        if linea and ":" in linea:
            k, v = linea.split(":", 1)
            datos[k.strip().lower()] = v.strip().strip('"')
    tipo = datos.get("tipo", "apunte")
    if tipo not in OBLIGATORIOS:
        sys.exit(f"{ruta.name}: tipo '{tipo}' desconocido (apunte | tp).")
    faltan = [k for k in OBLIGATORIOS[tipo] if not datos.get(k)]
    if faltan:
        sys.exit(f"{ruta.name}: faltan datos en el encabezado: {', '.join(faltan)}")
    cuerpo = texto[m.end():]
    # Si el contenido ya trae su propio título grande (# ...), no se repite: la portada ya lo pone.
    cuerpo = re.sub(r"\A((?:\s*<!--.*?-->)*)\s*# [^\n]*\n", r"\1\n", cuerpo, flags=re.S)
    tiene_biblio = re.search(r"^## Bibliograf", cuerpo, re.M | re.I) is not None
    if tipo == "apunte" and not tiene_biblio:
        sys.exit(f"{ruta.name}: un apunte debe terminar con la sección '## Bibliografía' (obligatoria; si no se puede verificar, avisar).")
    if tipo == "tp" and tiene_biblio:
        sys.exit(f"{ruta.name}: el TP no lleva bibliografía.")
    return tipo, datos, cuerpo


def envolver_secciones(cuerpo: str, tipo: str) -> str:
    """Post-proceso del HTML: bloques de código, bibliografía y tarjetas de ejercicios."""
    # Cada bloque de código va dentro de .code-wrap (ver comentario en tupad.css).
    cuerpo = re.sub(r'(<div class="highlight">.*?</div>)', r'<div class="code-wrap">\1</div>', cuerpo, flags=re.S)

    # Partir por <h2> para tratar cada sección por separado.
    partes = re.split(r"(?=<h2[ >])", cuerpo)
    salida = []
    for parte in partes:
        titulo = re.match(r"<h2[^>]*>(.*?)</h2>", parte, re.S)
        nombre = re.sub(r"<[^>]+>", "", titulo.group(1)).strip().lower() if titulo else ""
        if nombre.startswith("bibliograf"):
            parte = f'<section class="bibliografia">{parte}</section>'
        elif tipo == "tp" and nombre.startswith(("ejercicio", "consigna")):
            cabeza, *ejercicios = re.split(r"(?=<h3[ >])", parte)
            bloques = []
            for ej in ejercicios:
                # "### Título [20 puntos]" -> etiqueta de puntaje a la derecha
                ej = re.sub(r"<h3([^>]*)>(.*?)\s*\[([^\]]+)\]\s*</h3>",
                            r'<h3\1>\2<span class="puntaje">\3</span></h3>', ej, count=1, flags=re.S)
                bloques.append(f'<div class="ejercicio">{ej}</div>')
            parte = cabeza + "".join(bloques)
        salida.append(parte)
    return "".join(salida)


def incrustar_imagenes(cuerpo: str, base: Path) -> str:
    """Las imágenes del Markdown (img/xx.png) se incrustan en el HTML para que sea autocontenido."""
    def reemplazo(m):
        src = m.group(2)
        if src.startswith(("data:", "http:", "https:")):
            return m.group(0)
        ruta = (base / src).resolve()
        if not ruta.exists():
            sys.exit(f"Falta la imagen {src} (se busca junto al .md).")
        mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "gif": "image/gif", "svg": "image/svg+xml"}.get(
            ruta.suffix.lower().lstrip("."), "application/octet-stream")
        return f'{m.group(1)}{data_uri(ruta, mime)}{m.group(3)}'
    return re.sub(r'(<img[^>]*?src=")([^"]+)(")', reemplazo, cuerpo)


def construir_html(ruta_md: Path) -> tuple[str, dict]:
    tipo, datos, md_texto = leer_md(ruta_md)
    cuerpo = markdown.markdown(
        md_texto,
        extensions=["fenced_code", "codehilite", "tables", "admonition", "attr_list", "md_in_html", "sane_lists"],
        extension_configs={"codehilite": {"css_class": "highlight", "guess_lang": False}},
        output_format="html5",
    )
    cuerpo = envolver_secciones(cuerpo, tipo)
    cuerpo = incrustar_imagenes(cuerpo, ruta_md.parent)

    css = (RAIZ / "estilos" / "tupad.css").read_text(encoding="utf-8")
    css = (css.replace("{{LOGO}}", data_uri(RAIZ / "assets" / "logo-utn.png", "image/png"))
              .replace("{{FUENTE_INTER}}", data_uri(RAIZ / "assets/fuentes/Inter-variable.woff2", "font/woff2"))
              .replace("{{FUENTE_MONO}}", data_uri(RAIZ / "assets/fuentes/JetBrainsMono-variable.woff2", "font/woff2"))
              .replace("{{MATERIA}}", datos["materia"].replace("\\", "\\\\").replace('"', '\\"')))

    plantilla = (RAIZ / "plantillas" / f"{tipo}.html").read_text(encoding="utf-8")
    for clave, valor in datos.items():
        plantilla = plantilla.replace("{{" + clave.upper() + "}}", html.escape(valor))
    plantilla = plantilla.replace("{{CSS}}", css).replace("{{CONTENIDO}}", cuerpo)
    pendientes = sorted(set(re.findall(r"\{\{[A-Z_]+\}\}", plantilla)))
    if pendientes:
        sys.exit(f"{ruta_md.name}: quedaron marcas sin completar: {', '.join(pendientes)}")
    return plantilla, datos


def buscar_chrome() -> str:
    for c in CHROME + [shutil.which(n) or "" for n in ("chrome", "msedge", "google-chrome", "chromium")]:
        if c and Path(c).exists():
            return c
    sys.exit("No se encontró Chrome ni Edge para imprimir el PDF.")


def imprimir_pdf(ruta_html: Path, ruta_pdf: Path, chrome: str):
    # Chrome no siempre pisa un PDF existente: si quedara el viejo, se daría por bueno un PDF desactualizado.
    try:
        ruta_pdf.unlink(missing_ok=True)
    except PermissionError:
        sys.exit(f"No se puede reemplazar {ruta_pdf.name}: cerralo en el visor de PDF y volvé a generar.")
    r = subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        "--run-all-compositor-stages-before-draw", f"--print-to-pdf={ruta_pdf.resolve()}",
                        ruta_html.resolve().as_uri()], capture_output=True, text=True, timeout=180)
    if not ruta_pdf.exists():
        sys.exit(f"Chrome no generó el PDF: {(r.stderr or r.stdout)[:300]}")


def revisar_pdf(ruta_pdf: Path, preview: bool):
    import pymupdf
    doc = pymupdf.open(ruta_pdf)
    vacias = [i + 1 for i, p in enumerate(doc) if len(p.get_text().strip()) < 80 and not p.get_images()]
    if preview:
        carpeta = ruta_pdf.with_suffix("")
        carpeta.mkdir(exist_ok=True)
        for i, p in enumerate(doc):
            p.get_pixmap(dpi=80).save(carpeta / f"pagina_{i + 1:02d}.png")
    aviso = f"  ⚠ páginas casi vacías: {vacias}" if vacias else ""
    return doc.page_count, aviso


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entradas", nargs="+", help="archivos .md (acepta comodines)")
    ap.add_argument("--out", default=None, help="carpeta de salida (por defecto: salida/ junto al .md)")
    ap.add_argument("--solo-html", action="store_true", help="no imprimir el PDF")
    ap.add_argument("--preview", action="store_true", help="guardar un PNG por página para revisar")
    args = ap.parse_args()

    archivos = [Path(f) for e in args.entradas for f in (glob.glob(e) or [e])]
    chrome = None if args.solo_html else buscar_chrome()
    for md in archivos:
        out = Path(args.out) if args.out else md.parent / "salida"
        out.mkdir(parents=True, exist_ok=True)
        contenido, _ = construir_html(md)
        ruta_html = out / f"{md.stem}.html"
        ruta_html.write_text(contenido, encoding="utf-8")
        if args.solo_html:
            print(f"OK  {ruta_html}")
            continue
        ruta_pdf = out / f"{md.stem}.pdf"
        imprimir_pdf(ruta_html, ruta_pdf, chrome)
        paginas, aviso = revisar_pdf(ruta_pdf, args.preview)
        print(f"OK  {ruta_pdf}  ({paginas} páginas){aviso}")


if __name__ == "__main__":
    main()
