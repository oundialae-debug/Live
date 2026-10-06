# Directo 06/10: Merino sale del banquillo y empata en Croatia. Carta con foto + cronología de goles desde el banquillo.
import base64, sys
from pathlib import Path
R = Path("/home/user/futbol-pipeline/redes/plantillas/recursos"); F = Path("/home/user/Live/fotos")
b = lambda p: base64.b64encode(Path(p).read_bytes()).decode()
AM, NO = "#FFD21F", "#0A0C11"
cred = sys.argv[1]; out = sys.argv[2]; pos = sys.argv[3] if len(sys.argv) > 3 else "center 15%"
filas = [("EURO '24 QF", "v Germany", "119' winner"), ("WC '26 LAST 16", "v Portugal", "91' winner"),
         ("WC '26 QF", "v Belgium", "115 secs after coming on"), ("TONIGHT", "v Croatia", "on at half-time · 1-1")]
fl = "".join(f'<div style="display:flex;align-items:baseline;gap:18px;padding:14px 0;border-bottom:2px solid rgba(255,255,255,.14)">'
             f'<span style="width:270px;font-size:30px;font-weight:900;letter-spacing:2px;color:{AM if i == 3 else "#C9CEDA"}">{a}</span>'
             f'<span style="flex:1;font-size:40px;font-weight:800">{c}<span style="opacity:.6;font-weight:600"> {bb}</span></span></div>'
             for i, (a, bb, c) in enumerate(filas))
h = f"""<style>@font-face{{font-family:A;src:url(data:font/woff2;base64,{b(R/'Archivo-latin.woff2')}) format('woff2');font-stretch:62% 125%;font-weight:100 900}}
*{{margin:0;padding:0;box-sizing:border-box}} body{{width:1080px;height:1920px;background:{NO};color:#F1F3F8;font-family:A,sans-serif;overflow:hidden;position:relative}}</style>
<div style="position:absolute;inset:0;background:url(data:image/jpeg;base64,{b(F/'mikel_merino.jpg')}) {pos}/cover"></div>
<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(10,12,17,.5) 0%,rgba(10,12,17,0) 25%,rgba(10,12,17,0) 38%,rgba(10,12,17,.93) 58%,{NO} 100%)"></div>
<img style="position:absolute;left:80px;top:330px;width:230px" src="data:image/png;base64,{b(R/'2yellow-logo-transparent-for-dark.png')}">
<div style="position:absolute;right:40px;top:340px;font-size:20px;opacity:.75">{cred}</div>
<div style="position:absolute;left:80px;right:80px;top:960px">
<div style="font-size:120px;font-weight:900;font-stretch:78%;line-height:.95">Bring on Merino.<br><span style="color:{AM}">Again.</span></div>
<div style="margin-top:26px">{fl}</div></div>"""
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium"); pg = br.new_page(viewport={"width": 1080, "height": 1920})
    pg.set_content(h); pg.wait_for_timeout(300); pg.screenshot(path=out, quality=92, type="jpeg"); br.close()
print("ok", out)
