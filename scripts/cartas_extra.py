#!/usr/bin/env python3
"""Genera las cartas de MEMES y DATOS CURIOSOS (1080x1350 JPG) a partir de un JSON.
  python3 scripts/cartas_extra.py pedido.json
Pedido: {"id":"2026-10-06_meme1","cards":[{"kind":"meme|fact","kicker":"POV","text":"...","sub":"...","big":"0-7","source":"englandfootball.com"}]}
Salida: media/<id>_1.jpg, _2.jpg ... (sin vocabulario de apuestas, sin fotos con derechos)."""
import html, json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
AM, NO = "#FFD21F", "#0A0C11"
def card(c, i, n):
    e = lambda t: html.escape(t or "")
    fact = c.get("kind") == "fact"
    big = f'<div class="big">{e(c["big"])}</div>' if c.get("big") else ""
    sub = f'<div class="sub">{e(c["sub"])}</div>' if c.get("sub") else ""
    src = f'<div class="src">Source: {e(c["source"])}</div>' if c.get("source") else ""
    dots = "".join(f'<i class="{"on" if k == i else ""}"></i>' for k in range(n)) if n > 1 else ""
    swipe = '<div class="sw">swipe ›</div>' if n > 1 and i < n - 1 else ""
    return f"""<html><body style="margin:0"><style>
*{{box-sizing:border-box}} body{{width:1080px;height:1350px;background:{NO};color:#F1F3F8;font-family:'Arial Black','DejaVu Sans',Arial,sans-serif;position:relative;overflow:hidden}}
.bar{{position:absolute;left:0;top:0;width:100%;height:18px;background:{AM}}}
.k{{position:absolute;left:80px;top:110px;font-size:40px;letter-spacing:6px;color:{AM};text-transform:uppercase}}
.main{{position:absolute;left:80px;right:80px;top:200px;bottom:240px;display:flex;flex-direction:column;justify-content:center;gap:34px}}
.big{{font-size:260px;line-height:1;color:{AM}}}
.t{{font-size:{70 if fact else 84}px;line-height:1.12;font-weight:900;text-transform:{'none' if fact else 'none'}}}
.sub{{font-size:44px;line-height:1.25;color:#AEB5C4;font-family:Arial,sans-serif;font-weight:700}}
.src{{position:absolute;left:80px;bottom:150px;font-size:30px;color:#6B7385;font-family:Arial,sans-serif}}
.h{{position:absolute;left:80px;bottom:80px;font-size:36px;color:{AM}}}
.sw{{position:absolute;right:80px;bottom:80px;font-size:36px;color:#AEB5C4}}
.d{{position:absolute;left:50%;bottom:92px;transform:translateX(-50%);display:flex;gap:12px}}
.d i{{width:14px;height:14px;border-radius:7px;background:#2A3040}} .d i.on{{background:{AM}}}
</style><div class="bar"></div><div class="k">{e(c.get("kicker") or ("Did you know" if fact else ""))}</div>
<div class="main">{big}<div class="t">{e(c["text"])}</div>{sub}</div>{src}
<div class="h">@2yellowdata</div><div class="d">{dots}</div>{swipe}</body></html>"""
def main(p):
    o = json.loads(Path(p).read_text()); n = len(o["cards"]); Path("media").mkdir(exist_ok=True)
    with sync_playwright() as pw:
        exe = Path("/opt/pw-browsers/chromium")
        b = pw.chromium.launch(executable_path=str(exe)) if exe.exists() else pw.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        for i, c in enumerate(o["cards"]):
            pg.set_content(card(c, i, n)); pg.wait_for_timeout(150)
            out = f"media/{o['id']}_{i+1}.jpg"; pg.screenshot(path=out, type="jpeg", quality=90); print("OK", out)
        b.close()
if __name__ == "__main__": main(sys.argv[1])
