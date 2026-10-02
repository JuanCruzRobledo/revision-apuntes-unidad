#!/usr/bin/env python3
"""Control previo a PUBLICAR un repo: revisa el CONTENIDO y los METADATOS de los commits.

Uso: python escaneo_privacidad.py [CARPETA_DEL_REPO] [--permitir texto1,texto2]
Sale con código 1 (y NO hay que publicar) si encuentra:
  - emails reales en autor o committer de cualquier commit alcanzable (solo se aceptan @users.noreply.github.com),
  - emails, rutas locales de usuario, credenciales o tokens en el contenido de cualquier commit alcanzable.
Lección aprendida: un escaneo que solo mira los archivos no ve el email del autor del commit, que en un repo público
queda visible (incluso por la API y por <commit>.patch) y NO desaparece borrando el archivo: hay que reescribir el historial
o recrear el repo. Revisar los metadatos ANTES del primer push.
"""
import re
import subprocess
import sys
from pathlib import Path

NOREPLY = re.compile(r"@users\.noreply\.github\.com$", re.I)
PATRONES = {
    "email": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    "ruta_local_windows": r"[A-Za-z]:[\\/]+(Users|Documents and Settings)[\\/]+[^\s\\/\"']+",
    "ruta_local_unix": r"/(home|Users)/[a-z0-9._-]{2,}/",
    "nombre_corto_8.3": r"\b[A-Z0-9]{6}~\d\b",
    "token_github": r"\b(gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b",
    "clave_api": r"\b(sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{30,})\b",
    "asignacion_secreta": r"(?i)\b(password|passwd|secret|api[_-]?key|token)\b\s*[:=]\s*['\"][^'\"\s]{6,}['\"]",
}
# Archivos de licencia de terceros (fuentes OFL) traen emails de sus autores por requisito de la licencia.
EXCLUIR = (r"^assets/fonts/OFL-.*\.txt$", r".*\.ttf$", r".*\.(png|jpg|jpeg|gif|pdf|zip)$")


def git(repo, *a):
    r = subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    permitir = []
    if "--permitir" in sys.argv:
        permitir = sys.argv[sys.argv.index("--permitir") + 1].split(","); args = [a for a in args if a not in permitir and a != ",".join(permitir)]
    repo = Path(args[0] if args else ".").resolve()
    if not (repo / ".git").exists():
        print(f"{repo} no es un repo git"); return 2
    problemas = []
    # 1) metadatos
    for linea in git(repo, "log", "--all", "--format=%H|%an|%ae|%cn|%ce").splitlines():
        h, an, ae, cn, ce = (linea.split("|") + [""] * 5)[:5]
        for rol, mail in (("autor", ae), ("committer", ce)):
            if mail and not NOREPLY.search(mail) and mail not in permitir:
                problemas.append(f"METADATO commit {h[:7]} {rol}: email real <{mail}>")
    # 2) contenido de todos los commits alcanzables
    vistos = set()
    for c in git(repo, "rev-list", "--all").split():
        for archivo in git(repo, "ls-tree", "-r", "--name-only", c).splitlines():
            if any(re.match(p, archivo) for p in EXCLUIR):
                continue
            blob = git(repo, "rev-parse", f"{c}:{archivo}").strip()
            if (blob, archivo) in vistos:
                continue
            vistos.add((blob, archivo))
            texto = git(repo, "show", f"{c}:{archivo}")
            for nombre, pat in PATRONES.items():
                for m in re.finditer(pat, texto):
                    val = m.group(0)
                    if any(p and p in val for p in permitir):
                        continue
                    if nombre == "email" and NOREPLY.search(val):
                        continue
                    problemas.append(f"CONTENIDO {nombre} en {archivo} (commit {c[:7]}): {val[:60]}")
    if problemas:
        print("NO PUBLICAR. Se encontraron datos que no deberían quedar públicos:")
        for p in dict.fromkeys(problemas):
            print("  -", p)
        print("\nSi ya hay commits con email real, hay que reescribir el historial o recrear el repo antes del primer push.")
        return 1
    print("OK: sin emails reales en los commits ni datos personales/credenciales en el contenido.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
