#!/usr/bin/env python3
"""Compuerta de REVISIÓN MANUAL obligatoria del tutor, antes de subir nada al aula.

Subcomandos (todos reciben --trabajo CARPETA, la carpeta de trabajo que contiene corregidos/):
  generar               Crea REVISION_MANUAL.md y revision_manual.json con UN casillero por archivo corregido
                        (cada .docx, .pdf, .pptx, .md, .txt dentro de corregidos/, salvo _descartado/).
  estado                Muestra qué archivos están confirmados, pendientes o modificados tras la confirmación.
  confirmar ARCHIVO     Registra la confirmación del tutor (--por "Nombre"). SOLO se ejecuta después de que el
                        tutor haya dicho EXPLÍCITAMENTE en el chat que revisó ese archivo. Guarda el hash:
                        si el archivo cambia después, la confirmación se invalida.
  orden                 Genera ORDEN_DE_SUBIDA.md. SE NIEGA (código 2) si falta alguna confirmación.

Principio: la skill nunca declara un archivo "listo para subir" por sí sola.
"""
import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

EXT = {".docx", ".pdf", ".pptx", ".md", ".txt"}
CHECK = {
    ".docx": ["Primera hoja: materia, unidad, tema, revisor y bibliografía numerada (APA 7)",
              "Pie de página con numeración de páginas", "Tablas y bloques de código se ven bien",
              "Se lee completo y suena natural (sin frases de IA, sin segunda ni primera persona)",
              "Los datos técnicos y las versiones coinciden con lo que se ve en la unidad",
              "Dudas abiertas del informe de cambios resueltas o aceptadas"],
    ".pdf": ["Se abre y tiene todas las páginas", "Sin marca de agua ni links a Gamma (mirar la esquina inferior derecha)",
             "Texto editado sin desbordes ni fuentes distintas", "Diagramas e imágenes: sin rótulos deformados ni errores",
             "Dudas abiertas del informe de cambios resueltas o aceptadas"],
}
DEFAULT_CHECK = ["Se abre correctamente", "El contenido es el esperado y no tiene errores", "Dudas abiertas resueltas o aceptadas"]


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def archivos(trabajo: Path):
    base = trabajo / "corregidos"
    return sorted(p for p in base.rglob("*") if p.is_file() and p.suffix.lower() in EXT and "_descartado" not in p.parts)


def cargar(trabajo: Path):
    j = trabajo / "revision_manual.json"
    return json.loads(j.read_text(encoding="utf8")) if j.exists() else {"archivos": {}}


def guardar(trabajo: Path, data):
    (trabajo / "revision_manual.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf8")


def estado_de(trabajo: Path, data):
    out = {}
    for p in archivos(trabajo):
        rel = p.relative_to(trabajo).as_posix()
        reg = data["archivos"].get(rel)
        if not reg or not reg.get("confirmado_por"):
            est = "PENDIENTE"
        elif reg.get("sha256") != sha(p):
            est = "MODIFICADO (revisar de nuevo)"
        else:
            est = "CONFIRMADO"
        out[rel] = (est, reg or {})
    return out


def cmd_generar(trabajo: Path):
    data = cargar(trabajo)
    lineas = ["# Revisión manual obligatoria", "",
              "**Ningún archivo está listo para subir hasta que el tutor lo haya revisado y confirmado, uno por uno.**",
              "La verificación automática no reemplaza esta revisión: los subagentes pueden haber revisado el aspecto visual solo en parte, "
              "y los errores dentro de imágenes no se detectan por texto.", "",
              "Cómo confirmar: decirle al agente, por cada archivo, \"revisé <archivo>, está bien\". El agente lo registra con "
              "`compuerta_revision.py confirmar`. Si un archivo cambia después, la confirmación se invalida.", ""]
    for p in archivos(trabajo):
        rel = p.relative_to(trabajo).as_posix()
        data["archivos"].setdefault(rel, {})
        lineas += [f"## [ ] {rel}", ""] + [f"- [ ] {c}" for c in CHECK.get(p.suffix.lower(), DEFAULT_CHECK)] + ["- Confirmado por: _pendiente_", ""]
    (trabajo / "REVISION_MANUAL.md").write_text("\n".join(lineas), encoding="utf8")
    guardar(trabajo, data)
    print(f"REVISION_MANUAL.md generado con {len(data['archivos'])} archivo(s). Todos PENDIENTES.")


def cmd_estado(trabajo: Path):
    data = cargar(trabajo)
    est = estado_de(trabajo, data)
    for rel, (e, reg) in est.items():
        quien = f"  por {reg['confirmado_por']} el {reg['fecha']}" if reg.get("confirmado_por") else ""
        print(f"[{e:28}] {rel}{quien}")
    pend = [r for r, (e, _) in est.items() if e != "CONFIRMADO"]
    print(f"\n{len(est) - len(pend)}/{len(est)} confirmados." + ("" if not pend else f" Faltan {len(pend)}: no se puede generar el orden de subida."))
    return len(pend)


def cmd_confirmar(trabajo: Path, archivo: str, por: str, nota: str):
    p = (trabajo / archivo) if not Path(archivo).is_absolute() else Path(archivo)
    if not p.exists():
        sys.exit(f"No existe: {p}")
    rel = p.resolve().relative_to(trabajo.resolve()).as_posix()
    data = cargar(trabajo)
    data["archivos"][rel] = {"confirmado_por": por, "fecha": dt.datetime.now().strftime("%Y-%m-%d %H:%M"), "sha256": sha(p), "nota": nota}
    guardar(trabajo, data)
    print(f"Confirmado: {rel} por {por}")


def cmd_orden(trabajo: Path):
    data = cargar(trabajo)
    est = estado_de(trabajo, data)
    if not est:
        sys.exit("No hay archivos en corregidos/. Nada que ordenar.")
    pend = [r for r, (e, _) in est.items() if e != "CONFIRMADO"]
    if pend:
        print("NO SE GENERA ORDEN_DE_SUBIDA.md: falta la revisión manual del tutor en:")
        for r in pend:
            print(f"  - {r}  [{est[r][0]}]")
        print("\nCada archivo debe ser revisado a mano por el tutor y confirmado explícitamente. No hay atajo.")
        return 2
    lineas = ["# Orden de subida al aula", "",
              "Todos los archivos fueron revisados manualmente y confirmados por el tutor (ver registro al final).", "",
              "Regla: en cada actividad, primero se reemplazan los apuntes viejos por los nuevos (mismo orden) y después se agrega el documento formal. "
              "No borrar un apunte viejo hasta comprobar que el nuevo se abre bien en el aula. Borrar SOLO apuntes reemplazados; "
              "no tocar cuestionarios, prácticas, resoluciones ni adjuntos de código.", "",
              "| Paso | Carpeta | Archivo |", "|---|---|---|"]
    n = 1
    por_carpeta = {}
    for rel in est:
        por_carpeta.setdefault(Path(rel).parent.as_posix(), []).append(rel)
    for carpeta, fs in sorted(por_carpeta.items()):
        for rel in sorted(fs, key=lambda r: (r.lower().endswith(".docx"), r)):  # PDF/otros primero, Word al final
            lineas.append(f"| {n} | {carpeta} | {Path(rel).name} |"); n += 1
    lineas += ["", "## Registro de confirmaciones del tutor", "", "| Archivo | Confirmado por | Fecha |", "|---|---|---|"]
    for rel, (_, reg) in est.items():
        lineas.append(f"| {rel} | {reg['confirmado_por']} | {reg['fecha']} |")
    (trabajo / "ORDEN_DE_SUBIDA.md").write_text("\n".join(lineas) + "\n", encoding="utf8")
    print("ORDEN_DE_SUBIDA.md generado.")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("accion", choices=["generar", "estado", "confirmar", "orden"])
    ap.add_argument("archivo", nargs="?")
    ap.add_argument("--trabajo", required=True)
    ap.add_argument("--por", default="")
    ap.add_argument("--nota", default="")
    a = ap.parse_args()
    t = Path(a.trabajo).resolve()
    if a.accion == "generar":
        cmd_generar(t)
    elif a.accion == "estado":
        sys.exit(0 if cmd_estado(t) == 0 else 1)
    elif a.accion == "confirmar":
        if not a.archivo or not a.por.strip():
            sys.exit("Uso: confirmar ARCHIVO --por \"Nombre del tutor\"")
        cmd_confirmar(t, a.archivo, a.por.strip(), a.nota)
    else:
        sys.exit(cmd_orden(t))


if __name__ == "__main__":
    main()
