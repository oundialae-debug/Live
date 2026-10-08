# Curioso 07/10: Messi se despide de Argentina (6/10, 3-0 a Benin en el Monumental). Empezó con una roja en su
# debut (2005, Hungría, a los ~43 s de entrar) y acaba con gol. Datos de prensa (ESPN, beIN, Yahoo, CBS). Zona x 80-880, y 318-1540.
import base64, sys
from pathlib import Path
R = Path("/home/user/futbol-pipeline/redes/plantillas/recursos"); F = Path("/home/user/Live/fotos/candidatas")
b = lambda p: base64.b64encode(Path(p).read_bytes()).decode()
AM, NO, RO = "#FFD21F", "#0A0C11", "#E5383B"
cred = "Photos: Wikimedia Commons (CC BY-SA 3.0) · Hossein Zohrevand (CC BY 4.0)"
DATOS = [("208", "CAPS"), ("126", "GOALS"), ("21", "YEARS"), ("1", "WORLD CUP"), ("2", "COPA AMÉRICA"), ("85,000", "AT THE MONUMENTAL")]
celdas = "".join(f'<div style="background:rgba(255,255,255,.06);border-radius:14px;padding:12px 16px">'
                 f'<div style="font-size:56px;font-weight:900;font-stretch:72%;line-height:1;color:{AM}">{n}</div>'
                 f'<div style="font-size:19px;font-weight:700;letter-spacing:1.5px;color:#C9CFDA;margin-top:4px">{t}</div></div>' for n, t in DATOS)
foto = lambda f, pos: f'<div style="flex:1;background:url(data:image/{'webp' if str(f).endswith('webp') else 'jpeg'};base64,{b(f)}) {pos}/cover"></div>'
h = f"""<style>@font-face{{font-family:A;src:url(data:font/woff2;base64,{b(R/'Archivo-latin.woff2')}) format('woff2');font-stretch:62% 125%;font-weight:100 900}}
*{{margin:0;padding:0;box-sizing:border-box}} body{{width:1080px;height:1920px;background:{NO};color:#F1F3F8;font-family:A,sans-serif;overflow:hidden;position:relative}}</style>
<div style="position:absolute;left:0;right:0;top:0;height:1100px;display:flex;gap:6px">{foto(F/'messi_arg_1.jpg','center 12%')}{foto(F/'messi_adios_web_1.webp','46% center')}</div>
<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(10,12,17,.55) 0%,rgba(10,12,17,.1) 22%,rgba(10,12,17,.15) 40%,rgba(10,12,17,.92) 54%,{NO} 62%)"></div>
<img style="position:absolute;left:80px;top:330px;width:200px" src="data:image/png;base64,{b(R/'2yellow-logo-transparent-for-dark.png')}">
<div style="position:absolute;left:80px;right:200px;top:340px;text-align:right;font-size:26px;font-weight:900;letter-spacing:2px;color:#fff;text-shadow:0 2px 10px #000,0 0 4px #000">THE LAST TANGO</div>
<div style="position:absolute;left:80px;right:200px;top:880px">
<div style="display:flex;justify-content:space-between;font-size:26px;font-weight:900;letter-spacing:1.5px">
<span>2005 · FIRST GAME</span><span>2026 · LAST GAME</span></div>
<div style="display:flex;justify-content:space-between;align-items:center;margin-top:8px">
<div style="width:62px;height:86px;background:{RO};border-radius:8px;transform:rotate(-8deg);box-shadow:0 6px 18px rgba(0,0,0,.5)"></div>
<div style="font-size:28px;font-weight:800;color:#C9CFDA;text-align:center">vs Hungary&nbsp;&nbsp;→&nbsp;&nbsp;3-0 vs Benin</div>
<div style="font-size:78px;line-height:1">⚽</div></div>
<div style="font-size:60px;font-weight:900;font-stretch:78%;line-height:1.02;margin-top:18px">It started with a <span style="color:{RO}">red card</span>.<br>It ended with a <span style="color:{AM}">goal</span>.</div>
<div style="font-size:24px;color:#AEB5C4;margin-top:12px;line-height:1.3">Sent off on his debut, less than a minute after coming on.<br>Scored in his farewell, his 126th for Argentina.</div>
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-top:22px">{celdas}</div></div>"""
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium"); pg = br.new_page(viewport={"width": 1080, "height": 1920})
    pg.set_content(h); pg.wait_for_timeout(300); pg.screenshot(path=sys.argv[1], quality=92, type="jpeg"); br.close()
print("ok")
