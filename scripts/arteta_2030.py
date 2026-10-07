# Noticia del día 07/10: Arteta renueva con el Arsenal hasta 2030 (BBC, Sky, Guardian, Fox). Ángulo: 3 veces segundo,
# luego campeón. £20m al año (Daily Mail; £80m+ por 4 años, Mirror). Zona segura x 80-880, y 318-1540.
import base64, sys
from pathlib import Path
R = Path("/home/user/futbol-pipeline/redes/plantillas/recursos")
FOTO, POS = sys.argv[2], (sys.argv[3] if len(sys.argv) > 3 else "center 20%")
b = lambda p: base64.b64encode(Path(p).read_bytes()).decode()
AM, NO, RJ = "#FFD21F", "#0A0C11", "#EF0107"
LINEA = [("2019", "Arrives", "#C9CFDA"), ("2020", "FA Cup", "#F1F3F8"), ("2023", "2nd", "#8A93A6"), ("2024", "2nd", "#8A93A6"),
         ("2025", "2nd", "#8A93A6"), ("2026", "CHAMPIONS", AM)]
hitos = "".join(f'<div style="flex:1;text-align:center"><div style="width:22px;height:22px;border-radius:50%;margin:0 auto;background:{c};'
                f'box-shadow:0 0 0 5px {NO}"></div><div style="font-size:22px;font-weight:800;margin-top:10px;color:#AEB5C4">{a}</div>'
                f'<div style="font-size:{30 if t == "CHAMPIONS" else 26}px;font-weight:900;font-stretch:{70 if t == "CHAMPIONS" else 80}%;color:{c};margin-top:2px">{t}</div></div>'
                for a, t, c in LINEA)
mime = "webp" if FOTO.endswith("webp") else "png" if FOTO.endswith("png") else "jpeg"
h = f"""<style>@font-face{{font-family:A;src:url(data:font/woff2;base64,{b(R/'Archivo-latin.woff2')}) format('woff2');font-stretch:62% 125%;font-weight:100 900}}
*{{margin:0;padding:0;box-sizing:border-box}} body{{width:1080px;height:1920px;background:{NO};color:#F1F3F8;font-family:A,sans-serif;overflow:hidden;position:relative}}</style>
<div style="position:absolute;left:0;right:0;top:0;height:1150px;background:url(data:image/{mime};base64,{b(FOTO)}) {POS}/cover"></div>
<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(10,12,17,.55) 0%,rgba(10,12,17,.05) 22%,rgba(10,12,17,.2) 40%,rgba(10,12,17,.93) 54%,{NO} 62%)"></div>
<img style="position:absolute;left:80px;top:330px;width:200px" src="data:image/png;base64,{b(R/'2yellow-logo-transparent-for-dark.png')}">
<div style="position:absolute;left:80px;right:200px;top:340px;text-align:right;font-size:26px;font-weight:900;letter-spacing:2px;color:#fff;text-shadow:0 2px 10px #000">ARSENAL · UNTIL 2030</div>
<div style="position:absolute;left:80px;right:200px;top:860px">
<div style="font-size:70px;font-weight:900;font-stretch:76%;line-height:1">3 times second.<br>Then <span style="color:{AM}">champions</span>.</div>
<div style="font-size:26px;color:#C9CFDA;margin-top:14px;line-height:1.3">Arsenal reward Mikel Arteta with a new deal until 2030: about £20m a year, the best-paid boss in the Premier League.</div>
<div style="position:relative;margin-top:34px"><div style="position:absolute;left:8%;right:8%;top:10px;height:3px;background:linear-gradient(90deg,#3A4152,{RJ})"></div>
<div style="display:flex;position:relative">{hitos}</div></div>
<div style="display:flex;gap:10px;margin-top:30px">
<div style="flex:1;background:rgba(255,255,255,.06);border-radius:14px;padding:12px 16px"><div style="font-size:48px;font-weight:900;font-stretch:72%;color:{AM};line-height:1">22 yrs</div><div style="font-size:18px;font-weight:700;letter-spacing:1.5px;color:#C9CFDA;margin-top:4px">TITLE WAIT ENDED (2004)</div></div>
<div style="flex:1;background:rgba(255,255,255,.06);border-radius:14px;padding:12px 16px"><div style="font-size:48px;font-weight:900;font-stretch:72%;color:{AM};line-height:1">No. 1</div><div style="font-size:18px;font-weight:700;letter-spacing:1.5px;color:#C9CFDA;margin-top:4px">LONGEST-SERVING PL BOSS</div></div>
</div></div>"""
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium"); pg = br.new_page(viewport={"width": 1080, "height": 1920})
    pg.set_content(h); pg.wait_for_timeout(300); pg.screenshot(path=sys.argv[1], quality=92, type="jpeg"); br.close()
print("ok")
