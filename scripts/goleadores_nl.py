# Curioso 07/10: Leo Walta (Finland) tiene los mismos goles que Lamine Yamal en la Nations League. Datos propios
# (futbol-pipeline data/selecciones, tras la jornada 4). ZONA SEGURA x 80-880, y 318-1540.
import base64, json, sys
from pathlib import Path
R = Path("/home/user/futbol-pipeline/redes/plantillas/recursos"); F = Path("/home/user/Live/fotos")
b = lambda p: base64.b64encode(Path(p).read_bytes()).decode()
AM, NO, GR = "#FFD21F", "#0A0C11", "#5C6476"
c1 = json.load(open(F / "leo_walta.json"))["credito"]; c2 = json.load(open(F / "candidatas/yamal_2.json"))["credito"]
cred = c1 if c1 == c2 else f"{c1} · {c2}"
TABLA = [("Harry Kane", "England", 6), ("Michael Olise", "France", 4), ("Lamine Yamal", "Spain", 4), ("Leo Walta", "Finland", 4),
         ("Troy Parrott", "Ireland", 4), ("Viktor Gyökeres", "Sweden", 4)]
filas = "".join(f'<div style="display:flex;align-items:center;gap:16px;padding:7px 0;border-bottom:2px solid #1E2330;'
                f'{"background:linear-gradient(90deg,rgba(255,210,31,.18),transparent);" if n in ("Leo Walta", "Lamine Yamal") else ""}">'
                f'<div style="flex:1;font-size:34px;font-weight:800">{n} <span style="font-size:22px;color:#AEB5C4;font-weight:600">{p}</span></div>'
                f'<div style="font-size:40px;font-weight:900;font-stretch:75%;color:{AM if g == 6 else "#F1F3F8"};margin-right:6px">{g}</div></div>'
                for n, p, g in TABLA)
foto = lambda f, pos: (f'<div style="flex:1;background:url(data:image/jpeg;base64,{b(f)}) {pos}/cover"></div>')
h = f"""<style>@font-face{{font-family:A;src:url(data:font/woff2;base64,{b(R/'Archivo-latin.woff2')}) format('woff2');font-stretch:62% 125%;font-weight:100 900}}
*{{margin:0;padding:0;box-sizing:border-box}} body{{width:1080px;height:1920px;background:{NO};color:#F1F3F8;font-family:A,sans-serif;overflow:hidden;position:relative}}</style>
<div style="position:absolute;left:0;right:0;top:0;height:1000px;display:flex;gap:6px">{foto(F/'leo_walta.jpg','center 15%')}{foto(F/'candidatas/yamal_2.jpg','center 10%')}</div>
<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(10,12,17,.55) 0%,rgba(10,12,17,.1) 22%,rgba(10,12,17,.15) 38%,rgba(10,12,17,.92) 52%,{NO} 62%)"></div>
<img style="position:absolute;left:80px;top:330px;width:200px" src="data:image/png;base64,{b(R/'2yellow-logo-transparent-for-dark.png')}">
<div style="position:absolute;left:80px;right:200px;top:345px;text-align:right;font-size:22px;letter-spacing:2px;color:#E6E9F0">NATIONS LEAGUE</div>
<div style="position:absolute;left:80px;right:200px;top:820px">
<div style="display:flex;justify-content:space-between;font-size:30px;font-weight:900;letter-spacing:2px"><span>LEO WALTA · FIN</span><span>YAMAL · ESP</span></div>
<div style="font-size:150px;font-weight:900;font-stretch:72%;line-height:1;text-align:center;margin-top:-10px"><span style="color:{AM}">4</span> = <span style="color:{AM}">4</span></div>
<div style="font-size:52px;font-weight:900;font-stretch:80%;line-height:1.05;margin-top:6px">Finland's Leo Walta has as many goals as Lamine Yamal.</div>
<div style="font-size:24px;color:#AEB5C4;margin:18px 0 6px;letter-spacing:1px">TOP SCORERS AFTER 4 GAMES</div>{filas}</div>
<div style="position:absolute;left:80px;right:200px;top:788px;text-align:right;font-size:16px;opacity:.7">{cred}</div>"""
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium"); pg = br.new_page(viewport={"width": 1080, "height": 1920})
    pg.set_content(h); pg.wait_for_timeout(300); pg.screenshot(path=sys.argv[1], quality=92, type="jpeg"); br.close()
print("ok")
