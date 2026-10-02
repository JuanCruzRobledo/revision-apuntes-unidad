#!/usr/bin/env python3
"""Preflight de dependencias de la skill revision-apuntes-unidad.

Uso: python preflight.py [--sin-gamma]
Verifica lo necesario ANTES de empezar y dice exactamente qué instalar si falta algo.
Código de salida: 0 = todo lo obligatorio está; 1 = falta algo obligatorio.
"""
import importlib.util
import os
import shutil
import sys
from pathlib import Path

HOME = Path.home()
OBLIG, OPC = [], []


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


def chequeo(lista, ok, nombre, como_instalar, detalle=""):
    lista.append((ok, nombre, como_instalar, detalle))


def main():
    sin_gamma = "--sin-gamma" in sys.argv
    chequeo(OBLIG, sys.version_info >= (3, 10), "Python 3.10+", "Instalar Python 3.10 o superior", sys.version.split()[0])
    chequeo(OBLIG, modulo("docx"), "python-docx", "pip install python-docx")
    chequeo(OBLIG, modulo("fitz"), "PyMuPDF (fitz)", "pip install pymupdf")
    chequeo(OBLIG, modulo("PIL"), "Pillow", "pip install pillow")
    chequeo(OBLIG, skill_instalada("tup-campus-navigator"), "skill tup-campus-navigator (lee el aula)",
            "git clone https://github.com/Group-Active-IA/Skill-Moodle.git ~/.claude/skills/tup-campus-navigator\n"
            "      bash ~/.claude/skills/tup-campus-navigator/install.sh   (en Windows, desde Git Bash)\n"
            "      Si no tenés acceso al repo, pedilo a coordinación. Alternativa: Claude in Chrome con tu sesión del campus abierta.")
    lo = word_o_libreoffice()
    chequeo(OPC, lo is not None, "Microsoft Word o LibreOffice (revisar el layout de los .docx)",
            "Instalar LibreOffice (libreoffice.org). Sin esto la revisión visual del Word queda 100% a cargo del tutor.", lo or "")
    chequeo(OPC, modulo("youtube_transcript_api"), "youtube-transcript-api (transcripciones de videos)",
            "pip install youtube-transcript-api  (si no está, se trabaja con los guiones)")
    if not sin_gamma:
        chequeo(OPC, (Path(__file__).resolve().parent.parent / "assets" / "fonts" / "OpenSans-Regular.ttf").exists(),
                "Fuentes incluidas en assets/fonts (para editar PDF de Gamma)", "Reinstalar la skill")
    falta = False
    print("== Preflight de revision-apuntes-unidad ==")
    for titulo, lista in (("OBLIGATORIO", OBLIG), ("RECOMENDADO", OPC)):
        print(f"\n{titulo}")
        for ok, nombre, como, det in lista:
            print(f"  [{'OK' if ok else 'FALTA'}] {nombre}" + (f"  ({det})" if det else ""))
            if not ok:
                print(f"         -> {como}")
                if titulo == "OBLIGATORIO":
                    falta = True
    print("\nNo se puede seguir hasta resolver lo OBLIGATORIO." if falta else "\nTodo lo obligatorio está. Se puede seguir.")
    return 1 if falta else 0


if __name__ == "__main__":
    sys.exit(main())
