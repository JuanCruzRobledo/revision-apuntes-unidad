#!/usr/bin/env python3
"""Preflight de dependencias de la skill revision-apuntes-unidad.

Uso: python preflight.py [--sin-gamma] [--con-plantilla]
--con-plantilla: exige también lo necesario para generar teoría y TP con la plantilla (Chrome o Edge, markdown, pygments).
Sin esa opción, lo de la plantilla se muestra pero no frena (hay unidades que solo tienen presentaciones).
Verifica lo necesario ANTES de empezar y dice exactamente qué instalar si falta algo.
Código de salida: 0 = todo lo obligatorio está; 1 = falta algo obligatorio.
"""
import importlib.util
import os
import shutil
import sys
from pathlib import Path

HOME = Path.home()
OBLIG, OPC, PLANT = [], [], []


def modulo(nombre):
    return importlib.util.find_spec(nombre) is not None


def skill_instalada(nombre):
    bases = [HOME / ".claude" / "skills", HOME / ".agents" / "skills", Path.cwd() / ".claude" / "skills"]
    return any((b / nombre / "SKILL.md").exists() for b in bases)


def word_o_libreoffice():
    if shutil.which("soffice") or shutil.which("libreoffice"):
        return "LibreOffice"
    candidatos = [
        r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
        r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE",
        "/Applications/Microsoft Word.app",
        "/Applications/LibreOffice.app",
    ]
    return "Word/LibreOffice" if any(os.path.exists(c) for c in candidatos) else None


def navegador_pdf():
    candidatos = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe", r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/usr/bin/google-chrome", "/usr/bin/google-chrome-stable", "/usr/bin/chromium", "/usr/bin/chromium-browser",
        "/snap/bin/chromium", "/usr/bin/microsoft-edge",
    ]
    for c in candidatos:
        if os.path.exists(c):
            return c
    for n in ("chrome", "msedge", "google-chrome", "chromium"):
        if shutil.which(n):
            return shutil.which(n)
    return None


def chequeo(lista, ok, nombre, como_instalar, detalle=""):
    lista.append((ok, nombre, como_instalar, detalle))


def main():
    sin_gamma = "--sin-gamma" in sys.argv
    chequeo(OBLIG, sys.version_info >= (3, 10), "Python 3.10+", "Instalar Python 3.10 o superior", sys.version.split()[0])
    chequeo(OBLIG, modulo("docx"), "python-docx", "pip install python-docx")
    chequeo(OBLIG, modulo("fitz"), "PyMuPDF (fitz)", "pip install pymupdf")
    chequeo(OBLIG, modulo("PIL"), "Pillow", "pip install pillow")
    # Leer el aula admite dos vías: la skill del campus TUP o Claude in Chrome (no detectable desde Python)
    chequeo(OPC, skill_instalada("tup-campus-navigator"), "skill tup-campus-navigator (lee el aula, solo campus TUP)",
            "git clone https://github.com/Group-Active-IA/Skill-Moodle.git ~/.claude/skills/tup-campus-navigator\n"
            "      bash ~/.claude/skills/tup-campus-navigator/install.sh   (en Windows, desde Git Bash)\n"
            "      Si no tenés acceso al repo, o tu campus es otro: usá Claude in Chrome con tu sesión del campus abierta.\n"
            "      Hace falta UNA de las dos vías para leer el aula.")
    lo = word_o_libreoffice()
    chequeo(OPC, lo is not None, "Microsoft Word o LibreOffice (revisar el layout de los .docx)",
            "Instalar LibreOffice (libreoffice.org). Sin esto la revisión visual del Word queda 100% a cargo del tutor.", lo or "")
    chequeo(OPC, modulo("youtube_transcript_api"), "youtube-transcript-api (transcripciones de videos)",
            "pip install youtube-transcript-api  (si no está, se trabaja con los guiones)")
    if not sin_gamma:
        chequeo(OPC, (Path(__file__).resolve().parent.parent / "assets" / "fonts" / "OpenSans-Regular.ttf").exists(),
                "Fuentes incluidas en assets/fonts (para editar PDF de Gamma)", "Reinstalar la skill")
    # Plantilla única (teoría y TP): Markdown -> HTML -> PDF con Chrome o Edge
    chequeo(PLANT, modulo("markdown"), "markdown", "pip install markdown")
    chequeo(PLANT, modulo("pygments"), "pygments (resaltado de código)", "pip install pygments")
    nav = navegador_pdf()
    chequeo(PLANT, nav is not None, "Chrome o Edge (imprime el PDF de la plantilla)",
            "Instalar Google Chrome o Microsoft Edge (en Linux: chromium)", nav or "")
    chequeo(PLANT, (Path(__file__).resolve().parent.parent / "assets" / "plantilla" / "generar.py").exists(),
            "Plantilla incluida en assets/plantilla", "Reinstalar la skill")
    con_plantilla = "--con-plantilla" in sys.argv
    falta = False
    print("== Preflight de revision-apuntes-unidad ==")
    for titulo, lista in (("OBLIGATORIO", OBLIG), ("PLANTILLA (obligatorio si hay teoría o TP)" , PLANT), ("RECOMENDADO", OPC)):
        print(f"\n{titulo}")
        for ok, nombre, como, det in lista:
            print(f"  [{'OK' if ok else 'FALTA'}] {nombre}" + (f"  ({det})" if det else ""))
            if not ok:
                print(f"         -> {como}")
                if titulo == "OBLIGATORIO" or (con_plantilla and titulo.startswith("PLANTILLA")):
                    falta = True
    print("\nNo se puede seguir hasta resolver lo OBLIGATORIO." if falta else "\nTodo lo obligatorio está. Se puede seguir.")
    return 1 if falta else 0


if __name__ == "__main__":
    sys.exit(main())
