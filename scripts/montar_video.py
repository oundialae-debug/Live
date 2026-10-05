#!/usr/bin/env python3
"""Monta un vídeo 1080x1920 con imágenes + música a partir de pedidos/<id>.json.
Pedido: {"id":"ukr_hun_2026-10-06","images":["media/a.jpg",...],"seconds":2.3,
         "audio":"musica/boom.mp3","out":"videos/ukr_hun_2026-10-06.mp4","fade":0.5}
La duración sale de nº imágenes x seconds. Quita el silencio inicial de la pista y normaliza si suena flojo."""
import json, re, subprocess, sys
from pathlib import Path

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)

def main(p):
    o = json.loads(Path(p).read_text())
    imgs, sec, fade = o["images"], float(o.get("seconds", 2.5)), float(o.get("fade", 0.5))
    dur = round(len(imgs) * sec, 2)
    out = Path(o.get("out") or f"videos/{o['id']}.mp4"); out.parent.mkdir(parents=True, exist_ok=True)
    vol = run(["ffmpeg", "-hide_banner", "-t", "5", "-i", o["audio"], "-af", "volumedetect", "-f", "null", "-"]).stderr
    m = re.search(r"mean_volume: (-?[\d.]+) dB", vol)
    flojo = bool(m) and float(m.group(1)) < -20
    af = "silenceremove=start_periods=1:start_threshold=-40dB:start_silence=0.05," + ("loudnorm=I=-14:TP=-1.5," if flojo else "")
    af += f"atrim=0:{dur},afade=t=out:st={max(dur - fade, 0)}:d={fade}"
    cmd = ["ffmpeg", "-v", "error", "-y"]
    for i in imgs:
        cmd += ["-loop", "1", "-t", str(sec), "-i", i]
    cmd += ["-i", o["audio"]]
    n = len(imgs)
    ins = "".join(f"[{k}:v]" for k in range(n))
    fc = f"{ins}concat=n={n}:v=1:a=0,scale=1080:1920,fps=30,format=yuv420p[v];[{n}:a]{af}[a]"
    cmd += ["-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "fast",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)]
    r = run(cmd)
    if r.returncode:
        print(r.stderr); sys.exit(1)
    print("OK", out, dur, "s", "(loudnorm)" if flojo else "")

if __name__ == "__main__":
    for p in sys.argv[1:]:
        main(p)
