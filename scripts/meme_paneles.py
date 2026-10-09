# Meme de paneles (formato "texto / foto" apilado), todo dentro de la zona segura x 80-880, y 318-1540, con la cara de
# cada foto visible (comprobar con scripts/comprobar_caras.py). Fondo: la primera foto difuminada y oscurecida.
# Uso: python3 scripts/meme_paneles.py salida.jpg '[{"texto": "...", "foto": "ruta", "pos": "center 30%", "alto": 480}, ...]'
import base64, json, sys
from pathlib import Path
R = Path("/home/user/futbol-pipeline/redes/plantillas/recursos")
b = lambda p: base64.b64encode(Path(p).read_bytes()).decode()
mime = lambda f: "webp" if str(f).endswith("webp") else "png" if str(f).endswith("png") else "jpeg"
paneles = json.loads(sys.argv[2])
url = lambda f: f"data:image/{mime(f)};base64,{b(f)}"
bloques = "".join(
    (f'<div style="font-size:{p.get("tam", 44)}px;font-weight:900;font-stretch:82%;line-height:1.08;margin:{"0" if i == 0 else "18px"} 0 12px">{p["texto"]}</div>' if p.get("texto") else "")
    + (f'<div style="height:{p.get("alto", 480)}px;border-radius:18px;background:url({url(p["foto"])}) {p.get("pos", "center 30%")}/cover;box-shadow:0 10px 30px rgba(0,0,0,.5)"></div>' if p.get("foto") else "")
    for i, p in enumerate(paneles))
fondo = next(p["foto"] for p in paneles if p.get("foto"))
h = f"""<style>@font-face{{font-family:A;src:url(data:font/woff2;base64,{b(R/'Archivo-latin.woff2')}) format('woff2');font-stretch:62% 125%;font-weight:100 900}}
*{{margin:0;padding:0;box-sizing:border-box}} body{{width:1080px;height:1920px;background:#0A0C11;color:#fff;font-family:A,sans-serif;overflow:hidden;position:relative}}</style>
<div style="position:absolute;inset:-40px;background:url({url(fondo)}) center/cover;filter:blur(28px) brightness(.35)"></div>
<div style="position:absolute;left:80px;right:200px;top:340px">{bloques}</div>
<img style="position:absolute;left:80px;top:1478px;width:170px" src="data:image/png;base64,{b(R/'2yellow-logo-transparent-for-dark.png')}">"""
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium"); pg = br.new_page(viewport={"width": 1080, "height": 1920})
    pg.set_content(h); pg.wait_for_timeout(300)
    alto = pg.evaluate("document.querySelector('body > div:nth-of-type(2)').getBoundingClientRect().bottom")
    assert alto <= 1465, f"el contenido baja hasta y={alto}: recorta textos o fotos"
    pg.screenshot(path=sys.argv[1], quality=92, type="jpeg"); br.close()
print("ok")
