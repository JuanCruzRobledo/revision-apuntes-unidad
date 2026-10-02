#!/usr/bin/env python3
"""Convierte uno o más .docx a PDF con Microsoft Word (Windows) o LibreOffice, y verifica el resultado.

Uso: python word_a_pdf.py ARCHIVO.docx [ARCHIVO2.docx ...] [--salida CARPETA]
- Sin --salida, el PDF queda al lado del .docx, con el mismo nombre.
- Usa Word si está instalado (mejor fidelidad con documentos de Word); si no, LibreOffice (soffice).
- Resuelve rutas cortas de Windows (con "~"), que hacen fallar la exportación de Word.
- Verifica: número de páginas del PDF vs. el que informa Word, páginas casi en blanco y tamaño de página.

El PDF generado también queda PENDIENTE de la revisión manual del tutor (compuerta_revision.py lo incluye).
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path


def ruta_larga(p: Path) -> str:
    """Devuelve la ruta absoluta sin formato corto 8.3 (en Windows el '~' rompe la exportación de Word)."""
    p = p.resolve()
    if os.name == "nt":
        import ctypes
        buf = ctypes.create_unicode_buffer(4096)
        if ctypes.windll.kernel32.GetLongPathNameW(str(p), buf, 4096):
            return buf.value
    return str(p)


def con_word(docx: str, pdf: str):
    """Exporta con Word por COM (PowerShell). Devuelve el número de páginas según Word, o None si no se pudo."""
    esc = lambda s: s.replace("'", "''")
    ps = (
        "$ErrorActionPreference='Stop';"
        "$w=New-Object -ComObject Word.Application;$w.Visible=$false;$w.DisplayAlerts=0;"
        f"try{{$d=$w.Documents.Open('{esc(docx)}',$false,$true);"
        f"$d.ExportAsFixedFormat('{esc(pdf)}',17);"
        "Write-Output ('PAGINAS='+$d.ComputeStatistics(2));$d.Close($false)}"
        "finally{$w.Quit()}"
    )
    r = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, timeout=240)
    if r.returncode != 0 or not os.path.exists(pdf):
        return None, (r.stderr or r.stdout).strip()[:300]
    for linea in r.stdout.splitlines():
        if linea.startswith("PAGINAS="):
            return int(linea.split("=")[1]), ""
    return -1, ""


def con_libreoffice(docx: str, salida_dir: str):
    exe = shutil.which("soffice") or shutil.which("libreoffice")
    if not exe:
        return False, "LibreOffice no está instalado"
    r = subprocess.run([exe, "--headless", "--convert-to", "pdf", "--outdir", salida_dir, docx],
                       capture_output=True, text=True, timeout=240)
    return r.returncode == 0, (r.stderr or r.stdout).strip()[:300]


def verificar(pdf: str, paginas_word):
    import fitz
    d = fitz.open(pdf)
    avisos = []
    if paginas_word and paginas_word > 0 and paginas_word != len(d):
        avisos.append(f"Word informa {paginas_word} páginas y el PDF tiene {len(d)}")
    for i, p in enumerate(d, 1):
        if len(p.get_text().strip()) < 5 and not p.get_images():
            avisos.append(f"la página {i} está en blanco")
    return len(d), (d[0].rect.width, d[0].rect.height), avisos


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__); return 2
    salida = None
    if "--salida" in args:
        i = args.index("--salida"); salida = Path(args[i + 1]); args = args[:i] + args[i + 2:]
        salida.mkdir(parents=True, exist_ok=True)
    codigo = 0
    for a in args:
        src = Path(a)
        if not src.exists():
            print(f"NO EXISTE: {a}"); codigo = 1; continue
        destino = (salida or src.parent) / (src.stem + ".pdf")
        docx, pdf = ruta_larga(src), ruta_larga(destino.parent) + os.sep + destino.name
        paginas, motor, err = None, "", ""
        if os.name == "nt":
            paginas, err = con_word(docx, pdf)
            motor = "Microsoft Word" if paginas is not None else ""
        if not motor:
            ok, err2 = con_libreoffice(docx, str(Path(pdf).parent))
            motor = "LibreOffice" if ok else ""
            err = err2 or err
        if not motor or not os.path.exists(pdf):
            print(f"FALLÓ {src.name}: {err or 'sin motor disponible'}\n  Instalá Microsoft Word o LibreOffice.")
            codigo = 1; continue
        n, (w, h), avisos = verificar(pdf, paginas)
        print(f"OK  {src.name} -> {Path(pdf).name}  [{motor}] {n} págs, {w:.0f}x{h:.0f} pt")
        for av in avisos:
            print(f"    AVISO: {av}"); codigo = max(codigo, 0)
    print("\nEl PDF también debe ser revisado manualmente por el tutor antes de subir.")
    return codigo


if __name__ == "__main__":
    sys.exit(main())
