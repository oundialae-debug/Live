# Meme rápido con foto (directo): python3 meme_foto.py foto.jpg salida.jpg "texto pequeño" "texto grande" "crédito" ["center 15%"]
import base64, sys
from pathlib import Path
R = Path("/home/user/futbol-pipeline/redes/plantillas/recursos")
b = lambda p: base64.b64encode(Path(p).read_bytes()).decode()
foto, out, peq, grande, cred = sys.argv[1:6]; pos = sys.argv[6] if len(sys.argv) > 6 else "center 15%"
h = f"""<style>@font-face{{font-family:A;src:url(data:font/woff2;base64,{b(R/'Archivo-latin.woff2')}) format('woff2');font-stretch:62% 125%;font-weight:100 900}}
*{{margin:0;padding:0;box-sizing:border-box}} body{{width:1080px;height:1920px;background:#0A0C11;color:#F1F3F8;font-family:A,sans-serif;overflow:hidden;position:relative}}</style>
<div style="position:absolute;inset:0;background:url(data:image/jpeg;base64,{b(foto)}) {pos}/cover"></div>
<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(10,12,17,.5) 0%,rgba(10,12,17,0) 25%,rgba(10,12,17,0) 48%,rgba(10,12,17,.9) 68%,#0A0C11 100%)"></div>
<img style="position:absolute;left:80px;top:330px;width:230px" src="data:image/png;base64,{b(R/'2yellow-logo-transparent-for-dark.png')}">
<div style="position:absolute;right:40px;top:340px;font-size:20px;opacity:.75">{cred}</div>
<div style="position:absolute;left:80px;right:80px;top:1170px">
<div style="font-size:50px;font-weight:700;opacity:.9">{peq}</div>
<div style="font-size:112px;font-weight:900;font-stretch:78%;line-height:.98;margin-top:14px">{grande}</div></div>"""
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium"); pg = br.new_page(viewport={"width": 1080, "height": 1920})
    pg.set_content(h); pg.wait_for_timeout(300); pg.screenshot(path=out, quality=92, type="jpeg"); br.close()
print("ok", out)
