"""Imagen de noticia/curioso 1080x1920 con zona segura (x80-880, y318-1540) y cara visible (y 400-900).
Uso: python3 scripts/noticia_marco.py spec.json out.jpg
spec: {foto, crop:[x0,y0,w,h] (aspecto 4:3), tag, headline (html), sub, celdas:[[num,txt],..], pregunta}
Fondo = la misma foto difuminada y oscurecida. Sin crédito de foto (usuario 07/10)."""
import base64, io, json, sys
from pathlib import Path
from PIL import Image
RES = Path("/home/claude/futbol-pipeline/redes/plantillas/recursos")
spec = json.load(open(sys.argv[1])); out = sys.argv[2]
b64 = lambda p: base64.b64encode(Path(p).read_bytes()).decode()
im = Image.open(spec["foto"]).convert("RGB")
x0, y0, w, h = spec["crop"]
panel = im.crop((x0, y0, x0 + w, y0 + h)).resize((800, 600), Image.LANCZOS)
buf = io.BytesIO(); panel.save(buf, "JPEG", quality=93)
pan = base64.b64encode(buf.getvalue()).decode()
bg = im.copy(); bg.thumbnail((1400, 1400)); buf2 = io.BytesIO(); bg.save(buf2, "JPEG", quality=85)
bgb = base64.b64encode(buf2.getvalue()).decode()
AM, NO = "#FFD21F", "#0A0C11"
cel = spec.get("celdas", [])
cols = max(1, len(cel))
celdas = "".join(f'<div style="background:rgba(255,255,255,.09);border-radius:14px;padding:12px 14px">'
    f'<div style="font-size:58px;font-weight:900;font-stretch:72%;line-height:1;color:{AM}">{n}</div>'
    f'<div style="font-size:19px;font-weight:700;letter-spacing:1.2px;color:#D5DAE4;margin-top:5px;line-height:1.15">{t}</div></div>' for n, t in cel)
h_ = f"""<style>@font-face{{font-family:A;src:url(data:font/woff2;base64,{b64(RES/'Archivo-latin.woff2')}) format('woff2');font-stretch:62% 125%;font-weight:100 900}}
*{{margin:0;padding:0;box-sizing:border-box}} body{{width:1080px;height:1920px;background:{NO};color:#F1F3F8;font-family:A,sans-serif;overflow:hidden;position:relative}}</style>
<div style="position:absolute;inset:-60px;background:url(data:image/jpeg;base64,{bgb}) center/cover;filter:blur(26px) brightness(.38) saturate(1.1)"></div>
<div style="position:absolute;inset:0;background:rgba(10,12,17,.35)"></div>
<img style="position:absolute;left:80px;top:334px;height:46px" src="data:image/png;base64,{b64(RES/'2yellow-logo-transparent-for-dark.png')}">
<div style="position:absolute;left:300px;right:200px;top:342px;text-align:right;font-size:27px;font-weight:900;letter-spacing:2px;color:#fff;text-shadow:0 2px 10px #000">{spec['tag']}</div>
<div style="position:absolute;left:80px;top:402px;width:800px;height:600px;border-radius:26px;overflow:hidden;box-shadow:0 10px 40px rgba(0,0,0,.55)">
 <div style="position:absolute;inset:0;background:url(data:image/jpeg;base64,{pan}) center/100% 100%"></div>
 <div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(10,12,17,0) 68%,rgba(10,12,17,.8) 100%)"></div></div>
<div style="position:absolute;left:80px;width:800px;top:1020px">
 <div style="font-size:{spec.get('hsize',80)}px;font-weight:900;font-stretch:78%;line-height:1.02;text-shadow:0 3px 14px #000">{spec['headline']}</div>
 <div style="font-size:28px;color:#C4CAD8;margin-top:16px;line-height:1.3">{spec['sub']}</div>
 <div style="display:grid;grid-template-columns:repeat({cols},1fr);gap:10px;margin-top:22px">{celdas}</div>
 <div style="font-size:40px;font-weight:900;font-stretch:80%;color:{AM};margin-top:26px;line-height:1.1">{spec['pregunta']}</div>
</div>"""
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium"); pg = br.new_page(viewport={"width": 1080, "height": 1920})
    pg.set_content(h_); pg.wait_for_timeout(400)
    # medir el bloque de texto: el último elemento no debe pasar de y=1540
    bottom = pg.evaluate("(()=>{const e=document.querySelectorAll('div');let m=0;e.forEach(x=>{const r=x.getBoundingClientRect();if(r.width<900&&r.height>0&&r.bottom<1919)m=Math.max(m,r.bottom)});return m})()")
    pg.screenshot(path=out, quality=93, type="jpeg"); br.close()
print("ok; bottom=", bottom)
