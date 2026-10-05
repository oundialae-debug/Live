# Carta con foto real + texto (memes y datos curiosos). Corre en el sandbox de Higgs (Pillow + fuentes).
# Uso: python3 foto_meme.py pedido.json  ->  pedido: [{"foto":"x.jpg","out":"m.jpg","kind":"meme|fact","y0":0,
#   "text":"...", "big":"3", "sub":"...", "cred":"Photo: Autor, CC BY-SA 4.0"}]
# y0 = desplazamiento vertical del recorte (sube/baja la foto para que la cara quede ARRIBA y libre).
import json, sys
from PIL import Image, ImageDraw, ImageFont
F = "/usr/share/fonts/truetype/higgsfield/Montserrat-ExtraBold.ttf"
W, H = 1080, 1350; AM = (255, 210, 31, 255)

def base(src, y0):
    im = Image.open(src).convert("RGB"); r = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1))
    x0 = (im.width - W) // 2; y0 = max(0, min(y0, im.height - H)); im = im.crop((x0, y0, x0 + W, y0 + H))
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    for y in range(H - 760, H):
        d.line([(0, y), (W, y)], fill=(0, 0, 0, int(215 * ((y - (H - 760)) / 760) ** 0.8)))
    return Image.alpha_composite(im.convert("RGBA"), g)

def wrap(d, t, f, w):
    L, c = [], ""
    for x in t.split():
        s = (c + " " + x).strip()
        if d.textlength(s, font=f) <= w: c = s
        else: L.append(c); c = x
    return L + [c]

def foot(d, cred):
    s = ImageFont.truetype(F, 24); d.text((30, H - 48), cred, font=s, fill=(255, 255, 255, 210))
    a = "@2yellowdata"; d.text((W - 30 - d.textlength(a, font=s), H - 48), a, font=s, fill=AM)

def carta(p):
    im = base(p["foto"], p.get("y0", 0)); d = ImageDraw.Draw(im)
    if p.get("kind", "meme") == "meme":
        f = ImageFont.truetype(F, 68); L = wrap(d, p["text"], f, W - 140); y = H - 120 - len(L) * 86
        for l in L:
            d.text(((W - d.textlength(l, font=f)) / 2, y), l, font=f, fill="white", stroke_width=6, stroke_fill="black"); y += 86
    else:  # fact: "DID YOU KNOW" + número grande + frase + sub (SIN fuente ni web)
        d.text((70, 560), p.get("kicker", "DID YOU KNOW"), font=ImageFont.truetype(F, 34), fill=AM)
        d.text((70, 590), p["big"], font=ImageFont.truetype(F, 230), fill=AM)
        f = ImageFont.truetype(F, 52); y = 860
        for l in wrap(d, p["text"], f, W - 140):
            d.text((70, y), l, font=f, fill="white", stroke_width=4, stroke_fill="black"); y += 64
        if p.get("sub"):
            d.text((70, y + 14), p["sub"], font=ImageFont.truetype(F, 34), fill=(200, 205, 215, 255))
    foot(d, p["cred"]); im.convert("RGB").save(p["out"], quality=88)

for p in json.load(open(sys.argv[1])): carta(p)
