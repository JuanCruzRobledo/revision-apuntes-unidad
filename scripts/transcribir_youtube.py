#!/usr/bin/env python3
"""Baja transcripciones de YouTube SIN insistir si YouTube bloquea la IP.

Uso: python transcribir_youtube.py SALIDA_DIR ID_O_URL [ID_O_URL ...] [--pausa 20] [--idiomas es,es-419,en]

Regla (lección aprendida): YouTube bloquea la IP si se piden muchas transcripciones seguidas. Por eso hay pausa entre
pedidos y, ante el PRIMER bloqueo, el script se detiene y lo informa. NO reintentar en ráfaga ni usar proxies para esquivarlo:
los videos que queden sin transcripción se cubren con los guiones o la transcripción manual que pegue el tutor.
"""
import re
import sys
import time
from pathlib import Path


def video_id(s):
    m = re.search(r"(?:v=|youtu\.be/|embed/)([\w-]{11})", s)
    return m.group(1) if m else s.strip()


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        print(__doc__); return 2
    pausa = float(args[args.index("--pausa") + 1]) if "--pausa" in args else 20
    idiomas = args[args.index("--idiomas") + 1].split(",") if "--idiomas" in args else ["es", "es-419", "es-AR", "en"]
    pos = [a for i, a in enumerate(args) if not a.startswith("--") and (i == 0 or not args[i - 1].startswith("--"))]
    out = Path(pos[0]); out.mkdir(parents=True, exist_ok=True)
    ids = [video_id(x) for x in pos[1:]]
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        print("Falta youtube-transcript-api: pip install youtube-transcript-api (o trabajar con los guiones)."); return 1
    api = YouTubeTranscriptApi()
    ok, sin = [], []
    for k, vid in enumerate(ids):
        destino = out / f"{vid}.txt"
        if destino.exists():
            ok.append(vid); continue
        if k:
            time.sleep(pausa)
        try:
            tr = api.fetch(vid, languages=idiomas)
            destino.write_text(" ".join(s.text for s in tr), encoding="utf-8"); ok.append(vid)
            print(f"OK    {vid}")
        except Exception as e:
            nombre = type(e).__name__
            print(f"FALLA {vid}: {nombre}")
            sin.append(vid)
            if "Block" in nombre:
                restantes = ids[k + 1:]
                print("\nYouTube bloqueó la IP. SE DETIENE: no se insiste ni se usan proxies.")
                sin += restantes
                break
    print(f"\nTranscripciones listas: {len(ok)}. Sin transcripción: {len(sin)} -> {sin}")
    if sin:
        print("Para esos videos usar los guiones, o pedirle al tutor que pegue la transcripción (Mostrar transcripción en YouTube).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
