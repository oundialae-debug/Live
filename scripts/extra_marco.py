# Extras (memes/curioso) 1080x1920 con MARCO: todo dentro de x80-880, y318-1540 (assert) + fondo = misma foto difuminada/oscurecida.
# Corre en el sandbox de Higgs (internet, Pillow, Montserrat): python3 extra_marco.py jobs.json  (logo.png al lado; salida en ~/out + *_chk.jpg con la caja roja)
# jobs: [{"kind":"c|m","file":"<Archivo de Commons>","out":"x.jpg","hook":"<=34 car","focus":0.1,"big":"..","sub":"..","wy":[500,1000]}]  (kind c = curioso Kane 125, a medida)
import json, re, subprocess, urllib.parse, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
F="/usr/share/fonts/truetype/higgsfield/Montserrat-ExtraBold.ttf"
W,H=1080,1920; AM=(255,210,31); X0,X1,Y0,Y1=80,880,318,1540
UA="2yellow/1.0 (oundialae@gmail.com)"
def fp(f,w=1600):
    out=f"/home/user/c/{f}"; subprocess.run(["mkdir","-p","/home/user/c"])
    subprocess.run(["curl","-sL","-m","40","-A",UA,"-o",out,f"https://commons.wikimedia.org/wiki/Special:FilePath/{urllib.parse.quote(f)}?width={w}"],check=True); return out
def artist(f):
    r=subprocess.run(["curl","-sL","-m","25","-A",UA,"-G","https://commons.wikimedia.org/w/api.php","--data-urlencode","action=query","--data-urlencode","titles=File:"+f,"--data-urlencode","prop=imageinfo","--data-urlencode","iiprop=extmetadata","--data-urlencode","format=json"],capture_output=True,text=True).stdout
    p=list(json.loads(r)["query"]["pages"].values())[0]["imageinfo"][0]["extmetadata"]
    return f"Photo: {re.sub('<[^>]+>','',p['Artist']['value']).strip()}, {p['LicenseShortName']['value']}"
def wrap(d,t,f,w):
    L,c=[],""
    for x in t.split():
        s=(c+" "+x).strip()
        if d.textlength(s,font=f)<=w: c=s
        else: L.append(c); c=x
    return L+[c]
def card(photo,out,hook,cred,focus,body,wy=(520,1090)):
    im0=Image.open(photo).convert("RGB")
    r=max(W/im0.width,H/im0.height); bg=im0.resize((int(im0.width*r)+1,int(im0.height*r)+1))
    bg=bg.crop(((bg.width-W)//2,0,(bg.width-W)//2+W,H)).filter(ImageFilter.GaussianBlur(22))
    bg=Image.blend(bg,Image.new("RGB",(W,H),(8,10,16)),0.62).convert("RGBA")
    d=ImageDraw.Draw(bg); boxes=[]
    def T(xy,t,f,fill,anchor="la",stroke=0):
        xy=(xy[0]+((stroke+14) if anchor[0]=="l" else 0),xy[1])
        bb=d.textbbox(xy,t,font=f,anchor=anchor,stroke_width=stroke); boxes.append((bb,t))
        d.text(xy,t,font=f,fill=fill,anchor=anchor,stroke_width=stroke,stroke_fill="black")
    lg=Image.open("/home/user/logo.png").convert("RGBA"); lw=230; lg=lg.resize((lw,int(lg.height*lw/lg.width))); bg.alpha_composite(lg,(X0,Y0+14)); boxes.append(((X0,Y0+14,X0+lw,Y0+14+lg.height),"logo"))
    f=ImageFont.truetype(F,34); ly=Y0+110
    for l in wrap(d,hook,f,X1-X0-30): T((X0,ly),l,f,"white"); ly+=52
    wy0,wy1=wy; ww,wh=X1-X0,wy1-wy0
    r=ww/im0.width; ph=im0.resize((ww,int(im0.height*r))); top=int((ph.height-wh)*focus); ph=ph.crop((0,top,ww,top+wh))
    m=Image.new("L",(ww,wh),0); ImageDraw.Draw(m).rounded_rectangle((0,0,ww,wh),radius=28,fill=255)
    bg.paste(ph,(X0,wy0),m); boxes.append(((X0,wy0,X1,wy1),"photo"))
    T((X1-12,wy1-14),cred,ImageFont.truetype(F,20),(255,255,255,235),anchor="rd",stroke=2)
    body(d,T,wy1)
    for bb,t in boxes: assert bb[0]>=X0-1 and bb[2]<=X1+1 and bb[1]>=Y0 and bb[3]<=Y1,(t,bb)
    bg.convert("RGB").save(out,quality=90)
    chk=bg.convert("RGB"); ImageDraw.Draw(chk).rectangle((X0,Y0,X1,Y1),outline=(255,0,0),width=4); chk.resize((540,960)).save(out.replace(".jpg","_chk.jpg"),quality=70)
def meme(big,sub):
    def b(d,T,y):
        f=ImageFont.truetype(F,58); y+=30
        for l in wrap(d,big,f,X1-X0-34): T((X0,y),l,f,"white",stroke=5); y+=74
        f2=ImageFont.truetype(F,32); y+=14
        for l in wrap(d,sub,f2,X1-X0-34): T((X0,y),l,f2,AM); y+=44
    return b
def curioso(d,T,y):
    y+=18; T((X0,y),"125",ImageFont.truetype(F,200),AM); y+=215
    T((X0,y),"Level with Shilton.",ImageFont.truetype(F,62),"white",stroke=4); y+=88
    fl=ImageFont.truetype(F,24); fr=ImageFont.truetype(F,30)
    for a,bb in [("CAPS","125 · joint England record"),("GOALS","91 · England all-time top"),("LAST NIGHT","2 goals + 1 assist v Czechia")]:
        d.line((X0,y,X1,y),fill=(255,255,255,70),width=2); y+=14; T((X0,y+4),a,fl,AM); T((X0+250,y),bb,fr,"white"); y+=52
for j in json.load(open(sys.argv[1])):
    p=fp(j["file"]); c=artist(j["file"])
    card(p,"/home/user/out/"+j["out"],j["hook"],c,j["focus"],curioso if j["kind"]=="c" else meme(j["big"],j["sub"]),wy=tuple(j.get("wy",(520,1090))))
