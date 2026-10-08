# Noticia 07/10: Pedro se retira (Yahoo, AS, Football Italia); despedida en el Spotify Camp Nou. Dato: en 2009 fue el
# primer jugador en marcar en 6 competiciones en un año (FC Barcelona, Fox). Zona segura x 80-880, y 318-1540.
import base64, sys
from pathlib import Path
R = Path("/home/user/futbol-pipeline/redes/plantillas/recursos")
FOTO, POS = sys.argv[2], (sys.argv[3] if len(sys.argv) > 3 else "center 20%")
b = lambda p: base64.b64encode(Path(p).read_bytes()).decode()
AM, NO = "#FFD21F", "#0A0C11"
COPAS = [("1", "WORLD CUP"), ("1", "EURO"), ("3", "CHAMPIONS LEAGUE"), ("1", "EUROPA LEAGUE"), ("2", "CLUB WORLD CUP"),
         ("5", "LA LIGA"), ("1", "PREMIER LEAGUE"), ("1", "FA CUP"), ("6", "COMPETITIONS SCORED IN, 2009")]
celdas = "".join(f'<div style="background:rgba(255,255,255,.06);border-radius:14px;padding:10px 14px">'
                 f'<div style="font-size:50px;font-weight:900;font-stretch:72%;line-height:1;color:{AM}">{n}{"×" if n != "6" and n != "1" else ""}</div>'
                 f'<div style="font-size:17px;font-weight:700;letter-spacing:1.2px;color:#C9CFDA;margin-top:4px">{t}</div></div>' for n, t in COPAS)
mime = "webp" if FOTO.endswith("webp") else "png" if FOTO.endswith("png") else "jpeg"
h = f"""<style>@font-face{{font-family:A;src:url(data:font/woff2;base64,{b(R/'Archivo-latin.woff2')}) format('woff2');font-stretch:62% 125%;font-weight:100 900}}
*{{margin:0;padding:0;box-sizing:border-box}} body{{width:1080px;height:1920px;background:{NO};color:#F1F3F8;font-family:A,sans-serif;overflow:hidden;position:relative}}</style>
<div style="position:absolute;left:0;right:0;top:0;height:1250px;background:url(data:image/{mime};base64,{b(FOTO)}) {POS}/cover"></div>
<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(10,12,17,.55) 0%,rgba(10,12,17,.05) 22%,rgba(10,12,17,.2) 44%,rgba(10,12,17,.93) 56%,{NO} 64%)"></div>
<img style="position:absolute;left:80px;top:330px;width:200px" src="data:image/png;base64,{b(R/'2yellow-logo-transparent-for-dark.png')}">
<div style="position:absolute;left:80px;right:200px;top:340px;text-align:right;font-size:26px;font-weight:900;letter-spacing:2px;color:#fff;text-shadow:0 2px 10px #000">PEDRO RETIRES</div>
<div style="position:absolute;left:80px;right:200px;top:910px">
<div style="font-size:78px;font-weight:900;font-stretch:76%;line-height:1">He won <span style="color:{AM}">everything</span>.</div>
<div style="font-size:25px;color:#C9CFDA;margin-top:14px;line-height:1.3">Barça, Chelsea, Lazio and Spain. In 2009 he became the first player ever to score in six different competitions in one year.</div>
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-top:24px">{celdas}</div>
<div style="font-size:22px;color:#AEB5C4;margin-top:16px">Farewell at the Spotify Camp Nou.</div></div>"""
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium"); pg = br.new_page(viewport={"width": 1080, "height": 1920})
    pg.set_content(h); pg.wait_for_timeout(300); pg.screenshot(path=sys.argv[1], quality=92, type="jpeg"); br.close()
print("ok")
