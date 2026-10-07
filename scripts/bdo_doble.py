# Balón de Oro en dos listas juntas (usuario 07/10). Datos: futbol-pipeline datos_formatos.balon_oro_doble().
# ZONA SEGURA: todo dentro de x 80-880, y 318-1540.
import base64, sys
from pathlib import Path
R = Path("/home/user/futbol-pipeline/redes/plantillas/recursos")
b = lambda p: base64.b64encode(Path(p).read_bytes()).decode()
AM, NO, GR = "#FFD21F", "#0A0C11", "#5C6476"
MERECE = [("Lamine Yamal", "Barcelona · Spain", 93), ("Michael Olise", "Bayern · France", 88), ("Ousmane Dembélé", "PSG · France", 87),
          ("Harry Kane", "Bayern · England", 86), ("Kylian Mbappé", "Real Madrid · France", 86)]
GANA = [("Lamine Yamal", "Barcelona · Spain", 95), ("Michael Olise", "Bayern · France", 89), ("Kylian Mbappé", "Real Madrid · France", 89),
        ("Harry Kane", "Bayern · England", 87), ("Ousmane Dembélé", "PSG · France", 87)]
def lista(titulo, como, filas, col):
    f = "".join(f'<div style="display:flex;align-items:center;gap:12px;padding:12px 0;border-bottom:2px solid #1E2330">'
                f'<div style="font-size:40px;font-weight:900;font-stretch:75%;width:24px;color:{col if i == 0 else GR}">{i + 1}</div>'
                f'<div style="flex:1;min-width:0"><div style="font-size:38px;font-weight:900;font-stretch:80%;white-space:nowrap">{n.split()[-1]}</div>'
                f'<div style="font-size:20px;color:#AEB5C4;white-space:nowrap">{e.split(" · ")[1]}</div></div>'
                f'<div style="width:56px;height:74px;border-radius:9px;background:{col if i == 0 else "#F1F3F8"};color:{NO};display:grid;'
                f'place-items:center;transform:rotate(-6deg);font-size:32px;font-weight:900;font-stretch:75%;margin-right:8px">{v}</div></div>'
                for i, (n, e, v) in enumerate(filas))
    return (f'<div style="flex:1;min-width:0"><div style="display:inline-block;background:{col};color:{NO};font-weight:900;font-size:26px;'
            f'letter-spacing:2px;padding:7px 14px;border-radius:9px">{titulo}</div>'
            f'<div style="font-size:21px;color:#C9CED9;margin:12px 0 6px;line-height:1.3;height:112px">{como}</div>{f}</div>')
h = f"""<style>@font-face{{font-family:A;src:url(data:font/woff2;base64,{b(R/'Archivo-latin.woff2')}) format('woff2');font-stretch:62% 125%;font-weight:100 900}}
*{{margin:0;padding:0;box-sizing:border-box}} body{{width:1080px;height:1920px;background:{NO};color:#F1F3F8;font-family:A,sans-serif;overflow:hidden;position:relative}}</style>
<div style="position:absolute;inset:-40px;background:url(data:image/jpeg;base64,{b('/home/user/Live/fotos/candidatas/bdo_trofeo.jpg')}) center 0%/cover no-repeat,#0A0C11;filter:blur(3px)"></div>
<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(10,12,17,.35) 0%,rgba(10,12,17,.55) 22%,rgba(10,12,17,.85) 42%,rgba(10,12,17,.92) 100%)"></div>
<div style="position:absolute;right:200px;top:1505px;font-size:18px;opacity:.7">Photo: Ank Kumar, CC BY-SA 4.0</div>
<div style="position:absolute;left:80px;right:200px;top:330px">
<div style="display:flex;justify-content:space-between;align-items:center"><img style="width:200px" src="data:image/png;base64,{b(R/'2yellow-logo-transparent-for-dark.png')}">
<div style="font-size:24px;letter-spacing:2px;color:#C9CED9">BALLON D'OR 2026</div></div>
<div style="font-size:66px;font-weight:900;font-stretch:80%;line-height:1;margin:24px 0 30px">Who <span style="color:{AM}">deserves</span> it vs<br>who will <span style="color:#7FD4FF">win</span> it</div>
<div style="display:flex;gap:36px">
{lista("DESERVES IT", "Performance by position, league + World Cup, adjusted for minutes (60%) · titles (35%) · fair play (5%)", MERECE, AM)}
{lista("WILL WIN IT", "Same score (70%) + popularity (30%): Wikipedia views in 5 languages", GANA, "#7FD4FF")}
</div>
<div style="font-size:50px;font-weight:900;font-stretch:80%;margin-top:34px">Which list is right?</div></div>"""
from playwright.sync_api import sync_playwright
out = sys.argv[1]
with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium"); pg = br.new_page(viewport={"width": 1080, "height": 1920})
    pg.set_content(h); pg.wait_for_timeout(300); pg.screenshot(path=out, quality=92, type="jpeg"); br.close()
print("ok", out)
