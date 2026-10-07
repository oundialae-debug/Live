import base64, sys
from pathlib import Path
R = Path("/home/user/futbol-pipeline/redes/plantillas/recursos"); F = Path("/home/user/Live/fotos")
b = lambda p: base64.b64encode(Path(p).read_bytes()).decode()
AM, RO, NO, VE = "#FFD21F", "#FF3B3B", "#0A0C11", "#2BD67B"
modo = sys.argv[1]  # perdio | empate
MARCADOR = sys.argv[2] if len(sys.argv) > 2 else "Croatia 1-0 Spain"
CSS = f"""@font-face{{font-family:A;src:url(data:font/woff2;base64,{b(R/'Archivo-latin.woff2')}) format('woff2');font-stretch:62% 125%;font-weight:100 900}}
*{{margin:0;padding:0;box-sizing:border-box}} body{{width:1080px;height:1920px;background:{NO};color:#F1F3F8;font-family:A,sans-serif;overflow:hidden;position:relative}}
.logo{{position:absolute;left:80px;top:330px;width:230px}} .cred{{position:absolute;right:200px;top:340px;font-size:20px;opacity:.75}}"""
logo = f'<img class="logo" src="data:image/png;base64,{b(R/"2yellow-logo-transparent-for-dark.png")}">'
def s1():
    hook = ("40 unbeaten.<br><span style='color:%s'>Ended in Croatia.</span>" % RO) if modo == "perdio" else ("41.<br><span style='color:%s'>And counting.</span>" % AM)
    sub = {"perdio": "Spain's world-record run is over.", "empate": "Spain survive Croatia. The record lives.",
           "gana": "From the bench to the record books: Merino x2."}[modo]
    return f"""<style>{CSS}</style><div style="position:absolute;inset:0;background:url(data:image/jpeg;base64,{b(F/('candidatas/merino_3.jpg' if modo == 'gana' else 'unai_simon.jpg'))}) center 20%/cover"></div>
<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(10,12,17,.55) 0%,rgba(10,12,17,0) 28%,rgba(10,12,17,0) 45%,rgba(10,12,17,.92) 72%,{NO} 100%)"></div>
{logo}<div class="cred">Photo: Bryan Berlin, CC BY-SA 4.0</div>
<div style="position:absolute;left:80px;right:200px;top:1130px">
<div style="font-size:132px;font-weight:900;font-stretch:78%;line-height:.95;letter-spacing:-2px">{hook}</div>
<div style="font-size:46px;font-weight:700;margin-top:30px;opacity:.92">{sub}</div></div>"""
def s2():
    fin = (f'<div class="row"><span>Tonight</span><b style="color:{RO}">{MARCADOR}</b></div>' if modo == "perdio"
           else f'<div class="row"><span>Tonight</span><b style="color:{VE if modo == "gana" else AM}">{MARCADOR}</b></div>')
    w, d, l = {"perdio": (31, 9, 0), "empate": (31, 10, 0), "gana": (32, 9, 0)}[modo]
    return f"""<style>{CSS} .row{{display:flex;justify-content:space-between;font-size:44px;padding:22px 0;border-bottom:2px solid #1E2330}} .row span{{opacity:.7}}
.box{{flex:1;border-radius:22px;padding:26px 0;text-align:center;font-weight:900;font-size:110px;font-stretch:80%;color:{NO}}} .box small{{display:block;font-size:34px;font-weight:800}}</style>
{logo}<div style="position:absolute;left:80px;right:200px;top:470px">
<div style="display:inline-block;background:{AM};color:{NO};font-weight:900;font-size:36px;letter-spacing:4px;padding:10px 22px;border-radius:10px">THE RUN</div>
<div style="font-size:300px;font-weight:900;font-stretch:75%;line-height:.9;margin-top:24px;color:{AM}">{40 if modo == 'perdio' else 41}</div>
<div style="font-size:52px;font-weight:800;margin:-6px 0 34px">games unbeaten. A men's international record.</div>
<div style="display:flex;gap:18px;margin-bottom:30px"><div class="box" style="background:{VE}">{w}<small>WON</small></div>
<div class="box" style="background:#C9CEDA">{d}<small>DRAWN</small></div><div class="box" style="background:{RO if l else '#3A4152'};color:{'#0A0C11' if l else '#F1F3F8'}">{l}<small>LOST</small></div></div>
<div class="row"><span>Started after</span><b>Colombia 1-0 Spain, Mar 2024</b></div>
<div class="row"><span>Trophies</span><b>Euro 2024 · World Cup 2026</b></div>
<div class="row"><span>Old record</span><b>Italy, 37 (2018-21)</b></div>{fin}</div>"""
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium"); pg = br.new_page(viewport={"width":1080,"height":1920})
    for n, h in (("1", s1()), ("2", s2())):
        pg.set_content(h); pg.wait_for_timeout(300); pg.screenshot(path=f"/tmp/claude-0/directo/racha_{modo}_{n}.jpg", quality=92, type="jpeg")
    br.close()
print("ok")
