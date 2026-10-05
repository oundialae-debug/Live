"""Sintetiza con Azure Speech cada escena de guion.json -> <carpeta>/<id>.mp3.

Usa la API en tiempo real (una petición por escena, hasta 10 min de audio
cada una). Necesita AZURE_SPEECH_KEY y AZURE_SPEECH_REGION. Escribe en el
guion la ruta y la duración real de cada audio (mp3 de bitrate fijo).
"""
import argparse
import json
import os
import sys
import time

import requests

FORMATO = "audio-24khz-48kbitrate-mono-mp3"
BITS_POR_S = 48000


def sintetizar(ssml, key, region):
    url = f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1"
    h = {"Ocp-Apim-Subscription-Key": key, "Content-Type": "application/ssml+xml",
         "X-Microsoft-OutputFormat": FORMATO, "User-Agent": "narrador-live"}
    for intento in range(5):
        r = requests.post(url, headers=h, data=ssml.encode("utf-8"), timeout=120)
        if r.status_code == 200 and r.content:
            return r.content
        if r.status_code in (429, 500, 502, 503):
            espera = int(r.headers.get("Retry-After", 5 * 2 ** intento))
            print(f"  HTTP {r.status_code}, reintento en {espera}s")
            time.sleep(espera)
            continue
        sys.exit(f"ERROR HTTP {r.status_code}: {r.text[:1000]}")
    sys.exit("ERROR: Azure no respondió tras 5 intentos")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("guion")
    ap.add_argument("--carpeta", default="audio")
    a = ap.parse_args()
    key, region = os.environ["AZURE_SPEECH_KEY"], os.environ["AZURE_SPEECH_REGION"]
    g = json.load(open(a.guion, encoding="utf-8"))
    os.makedirs(a.carpeta, exist_ok=True)
    total = 0.0
    for e in g["escenas"]:
        mp3 = sintetizar(e["ssml"], key, region)
        ruta = os.path.join(a.carpeta, f"{e['id']}.mp3")
        open(ruta, "wb").write(mp3)
        e["audio"] = f"{e['id']}.mp3"
        e["duracion_s"] = round(len(mp3) * 8 / BITS_POR_S, 2)
        total += e["duracion_s"]
        print(f"{e['id']}: {e['duracion_s']:.1f}s (estimado {e['estimado_s']:.1f}s)")
        time.sleep(1)
    g["duracion_total_s"] = round(total, 1)
    json.dump(g, open(a.guion, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"Total: {total / 60:.1f} min en {len(g['escenas'])} audios")


if __name__ == "__main__":
    main()
