"""Sintetiza con Azure Speech cada escena de guion.json -> <carpeta>/<id>.mp3.

Usa Batch Synthesis (un trabajo con todas las escenas), que admite las voces
HD (DragonHD), igual que Text-to-audiobook. Necesita AZURE_SPEECH_KEY y
AZURE_SPEECH_REGION. Escribe en el guion la ruta y la duración real de cada
audio (mp3 de bitrate fijo).
"""
import argparse
import io
import json
import os
import sys
import time
import uuid
import zipfile

import requests

FORMATO = "audio-24khz-48kbitrate-mono-mp3"
BITS_POR_S = 48000
API_VERSION = "2024-04-01"


def sintetizar_lote(ssmls, key, region):
    """Un trabajo de Batch Synthesis con un SSML por escena -> lista de mp3 en el mismo orden."""
    base = f"https://{region}.api.cognitive.microsoft.com/texttospeech/batchsyntheses"
    sid = f"narrador-{uuid.uuid4().hex[:12]}"
    url = f"{base}/{sid}?api-version={API_VERSION}"
    h = {"Ocp-Apim-Subscription-Key": key}
    body = {"description": sid, "inputKind": "SSML", "inputs": [{"content": x} for x in ssmls],
            "properties": {"outputFormat": FORMATO, "concatenateResult": False, "decompressOutputFiles": False}}
    r = requests.put(url, headers={**h, "Content-Type": "application/json"}, json=body, timeout=30)
    if r.status_code not in (200, 201, 202):
        sys.exit(f"ERROR al crear el trabajo: HTTP {r.status_code}\n{r.text[:2000]}")
    inicio = time.time()
    while time.time() - inicio < 2400:
        d = requests.get(url, headers=h, timeout=30).json()
        print("  estado:", d.get("status"))
        if d.get("status") == "Succeeded":
            z = zipfile.ZipFile(io.BytesIO(requests.get(d["outputs"]["result"], timeout=300).content))
            mp3s = sorted(n for n in z.namelist() if n.lower().endswith(".mp3"))
            if len(mp3s) != len(ssmls):
                sys.exit(f"ERROR: {len(mp3s)} audios para {len(ssmls)} escenas: {z.namelist()}")
            return [z.read(n) for n in mp3s]
        if d.get("status") == "Failed":
            sys.exit(f"El trabajo falló: {d}")
        time.sleep(10)
    sys.exit("Timeout esperando a Azure.")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("guion")
    ap.add_argument("--carpeta", default="audio")
    a = ap.parse_args()
    key, region = os.environ["AZURE_SPEECH_KEY"], os.environ["AZURE_SPEECH_REGION"]
    g = json.load(open(a.guion, encoding="utf-8"))
    os.makedirs(a.carpeta, exist_ok=True)
    total = 0.0
    for e, mp3 in zip(g["escenas"], sintetizar_lote([e["ssml"] for e in g["escenas"]], key, region)):
        ruta = os.path.join(a.carpeta, f"{e['id']}.mp3")
        open(ruta, "wb").write(mp3)
        e["audio"] = f"{e['id']}.mp3"
        e["duracion_s"] = round(len(mp3) * 8 / BITS_POR_S, 2)
        total += e["duracion_s"]
        print(f"{e['id']}: {e['duracion_s']:.1f}s (estimado {e['estimado_s']:.1f}s)")
    g["duracion_total_s"] = round(total, 1)
    json.dump(g, open(a.guion, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"Total: {total / 60:.1f} min en {len(g['escenas'])} audios")


if __name__ == "__main__":
    main()
