"""Noticias de fútbol -> vídeo -> publicación AUTOMÁTICA sin aprobación (usuario 11/10: "la noticia deja de ser noticia si se
publica tarde"). Lo lanza el workflow `noticias` cada hora justo después del escaneo (scripts/noticias.py).

  noticia_auto.py hay   -> $GITHUB_OUTPUT hay=si|no (barato, sin red: ¿está activo, hay clave de IA, hay tema grande nuevo y
                           no se ha llegado al máximo diario?)
  noticia_auto.py       -> IA (Groq/Cerebras/Mistral gratis, clave en secretos) evalúa los temas grandes; el primero que pasa
                           todos los filtros se dibuja (3 tarjetas con la foto del momento), se monta en vídeo con música y se
                           deja en redes/cola/ (TikTok + IG automático). enviar_cola.yml lo manda a Buffer.

Filtros (redes/noticias/config.json): >= `umbral` medios distintos; máx `max_dia` al día (1 por pasada); nunca el mismo tema en
48 h (descartes: 12 h); categorías sensibles (muerte, delito, lesión grave, política, juicios) NO se publican solas: quedan en
redes/noticias/revision.md para que las mire el usuario; toda cifra/nombre del texto debe salir en los titulares leídos (anti
invento); importancia y calidad >= 7 según la IA; cara visible en la zona segura (comprobar_caras); sin vocabulario de apuestas.
"modo": "publicar" (cola) | "seco" (hace todo menos encolar, para revisar el vídeo) | "off".
Pruebas sin red: NA_LLM_FILE=respuesta.json NA_FOTO=foto.jpg PP_GIT=0 PP_RED=0 python3 scripts/noticia_auto.py"""
import csv, html, json, os, re, shutil, subprocess, sys, tempfile, unicodedata, urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
import post_partido_live as pp                      # música, montaje, subida a git, URL raw
from titulares import VACIAS

ROOT = pp.ROOT
DIR, MAD = ROOT / "redes/noticias", ZoneInfo("Europe/Madrid")
CFG0 = {"modo": "publicar", "umbral": 8, "max_dia": 3, "min_importancia": 7, "min_calidad": 7,
        "descarte_horas": 12, "bloqueo_horas": 48, "seg_tarjeta": 3.2}
OK_CAT = {"result", "red_card", "transfer", "record", "manager", "award", "controversy", "squad", "other"}
SENSIBLE = re.compile(
    r"\b(dies|died|dead|death|killed|murder\w*|stabb\w*|shot dead|arrest\w*|police|rape\w*|abus\w+|assault\w*|cancer|tumou?r|"
    r"cardiac|heart attack|funeral|tragedy|tragic|suicide|war|bomb\w*|terror\w*|politic\w*|president|government|court|jail\w*|"
    r"prison|sentenced|fraud|tax evasion|racis\w+|"
    r"muere|muri[oó]|fallec\w+|muerte|detenid\w+|polic[ií]a|c[aá]rcel|juicio|denuncia\w*|cáncer|tragedia|guerra|gobierno|racis\w+|"
    r"morto|morte|arrestat\w+|tribunale|d[eé]c[eè]s|d[eé]c[eé]d\w+|arr[eê]t\w+|gestorben|verhaftet|"
    r"ruptur\w+|cruciate|ACL|broken|fractur\w+|surgery|operation|ligament|season-ending|rotura|cruzado|operado|"
    r"lesi[oó]n grave|infortunio)\b", re.I)
EXTRA_OK = {"LaLiga", "Clásico", "Clasico", "Premier", "League", "Serie", "Bundesliga", "Ligue", "Champions", "Europa", "UEFA", "FIFA"}


def cfg():
    try:
        return {**CFG0, **json.loads((DIR / "config.json").read_text())}
    except Exception:
        return dict(CFG0)


def ahora():
    return pp.ahora()


# ---------- registro de decisiones ----------

def decisiones():
    out = []
    try:
        for l in (DIR / "decisiones.jsonl").read_text(encoding="utf-8").splitlines():
            try:
                out.append(json.loads(l))
            except Exception:
                pass
    except FileNotFoundError:
        pass
    return out


def apuntar(d):
    DIR.mkdir(parents=True, exist_ok=True)
    d = {"t": ahora().isoformat(timespec="minutes"), **d}
    with (DIR / "decisiones.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False) + "\n")


def bloqueados(c):
    """Temas (minúsculas) que no se vuelven a proponer: publicados/revisar/seco 48 h, descartados 12 h, y lo publicado a mano."""
    t, bloq = ahora(), set()
    for d in decisiones():
        h = c["descarte_horas"] if d.get("estado") == "descartar" else c["bloqueo_horas"]
        if datetime.fromisoformat(d["t"]) > t - timedelta(hours=h):
            bloq |= {x.lower() for x in d.get("temas", [])}
    try:
        desde = (t.astimezone(MAD) - timedelta(hours=48)).strftime("%Y-%m-%d")
        pub = ""
        for r in csv.reader((ROOT / "redes/publicaciones.csv").open(encoding="utf-8")):
            if r and r[0] >= desde:
                pub += " " + " ".join(r[1:3]).lower()
        return bloq, pub
    except Exception:
        return bloq, ""


def hoy_publicadas():
    hoy = ahora().astimezone(MAD).date()
    return sum(1 for d in decisiones() if d.get("estado") in ("publicado", "seco")
               and datetime.fromisoformat(d["t"]).astimezone(MAD).date() == hoy)


def candidatos(c):
    try:
        temas = json.loads((DIR / "temas.json").read_text())["temas"]
    except Exception:
        return []
    bloq, pub = bloqueados(c)
    return [x for x in temas if x["medios"] >= c["umbral"] and x["tema"].lower() not in bloq
            and x["tema"].lower() not in pub][:6]


def claves_ia():
    return [k for k in ("GROQ_API_KEY", "CEREBRAS_API_KEY", "MISTRAL_API_KEY") if os.environ.get(k)]


def hay():
    c, motivo = cfg(), ""
    if c["modo"] == "off":
        motivo = "modo off"
    elif not claves_ia() and not os.environ.get("NA_LLM_FILE"):
        motivo = "sin clave de IA (GROQ_API_KEY)"
    elif hoy_publicadas() >= c["max_dia"]:
        motivo = f"máximo diario ({c['max_dia']}) alcanzado"
    elif not candidatos(c):
        motivo = f"ningún tema nuevo con >= {c['umbral']} medios"
    print("hay=" + ("no: " + motivo if motivo else "si"))
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"hay={'no' if motivo else 'si'}\n")


# ---------- IA ----------

PROMPT = """You are the news editor of 2yellow (@2yellowdata), a football data account on TikTok/Instagram. Below are the biggest
football topics from the last hours (each topic = a proper noun that appears in many outlets) with the headlines that mention it.
Group topics that are the SAME story into one story. For each distinct story decide if it is worth a fast 3-card video.
RULES: use ONLY facts that appear in the headlines below (no outside knowledge, no guesses, every number and name in your text must
appear in the headlines). English, British spelling, neutral and factual tone, no betting words (odds, bet, tip, stake...).
Do not repeat any story listed in "already_done". Mark sensitive stories honestly with their category (death, crime, injury,
politics, legal) - they will NOT be published automatically.
Return ONLY JSON: {"stories":[{"topics":[candidate words that belong to this story],"key":"short-kebab-slug",
"category":"result|red_card|transfer|record|manager|award|controversy|squad|other|death|crime|injury|politics|legal",
"importance":1-10 (10 = everybody is talking about it, a casual fan must care),"quality":1-10 (is it a clear, visual, one-sentence story?),
"repeated":true|false,"reason":"one line",
"tag":"<=22 chars like RED CARD · LA LIGA","title":"<=7 words, punchy, no full stop","subtitle":"<=130 chars, what happened",
"facts":[{"figure":"<=8 chars taken from the headlines or empty","label":"<=30 chars"}] (0-3),
"next":"<=110 chars: what happens next / why it matters (only from the headlines)","question":"<=45 chars, engages the fans",
"post":"<=230 chars caption ending with the question","tiktok_title":"<=85 chars","hashtags":["#a","#b","#c","#d","#e"],
"photo_query":"how a fan would google the exact moment, e.g. 'Vinicius Saliba hair pull red card'"}]}
"""


def llm(candidatos_, hechos_):
    if os.environ.get("NA_LLM_FILE"):
        return json.loads(Path(os.environ["NA_LLM_FILE"]).read_text())
    entrada = {"candidates": [{"topic": x["tema"], "outlets": x["medios"],
                               "headlines": [f"{h['medio']}: {h['titulo']}" for h in x["titulares"][:8]]} for x in candidatos_],
               "already_done": hechos_}
    proveedores = [("GROQ_API_KEY", "https://api.groq.com/openai/v1/chat/completions", "openai/gpt-oss-120b"),
                   ("GROQ_API_KEY", "https://api.groq.com/openai/v1/chat/completions", "llama-3.3-70b-versatile"),
                   ("CEREBRAS_API_KEY", "https://api.cerebras.ai/v1/chat/completions", "gpt-oss-120b"),
                   ("MISTRAL_API_KEY", "https://api.mistral.ai/v1/chat/completions", "ministral-8b-latest")]
    for env, url, modelo in proveedores:
        if not os.environ.get(env):
            continue
        cuerpo = {"model": modelo, "temperature": 0.2, "max_tokens": 3500,
                  "messages": [{"role": "system", "content": PROMPT},
                               {"role": "user", "content": json.dumps(entrada, ensure_ascii=False)}]}
        for formato in (True, False):
            b = dict(cuerpo)
            if formato:
                b["response_format"] = {"type": "json_object"}
            try:
                rq = urllib.request.Request(url, json.dumps(b).encode(), {
                    "Content-Type": "application/json", "Authorization": "Bearer " + os.environ[env],
                    "User-Agent": "Mozilla/5.0 (2yellow noticias)"})        # sin User-Agent propio, 403
                txt = json.load(urllib.request.urlopen(rq, timeout=90))["choices"][0]["message"]["content"]
                return json.loads(txt[txt.index("{"): txt.rindex("}") + 1])
            except Exception as ex:
                print(f"[!] {modelo} {'json' if formato else 'texto'}: {type(ex).__name__} {str(ex)[:120]}")
    return None


# ---------- comprobaciones ----------

def sin_acentos(t):
    return unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()


def respaldado(h, titulares):
    """Anti-invento: toda cifra y todo nombre propio (no inicial de frase) del texto debe salir en los titulares leídos."""
    base = sin_acentos(" ".join(titulares))
    texto = " ".join([h.get("title", ""), h.get("subtitle", ""), h.get("next", ""), h.get("post", "")] +
                     [f"{f.get('figure', '')} {f.get('label', '')}" for f in h.get("facts", [])])
    texto = re.sub(r"#\w+", "", texto)
    malos = [n for n in re.findall(r"\d+(?:[.,:]\d+)*", texto) if sin_acentos(n) not in base]
    for m in re.finditer(r"(?<![.!?]\s)(?<!^)\b([A-ZÁÉÍÓÚÑ][\wáéíóúñü'’-]{3,})", texto):
        w = m.group(1)
        if w in VACIAS or w in EXTRA_OK or w.upper() == w:
            continue
        if sin_acentos(w.rstrip("'’s")) not in base:
            malos.append(w)
    return malos


def evaluar(h, c, titulares, bloq):
    """-> (estado, motivo). estado: publicar | descartar | revisar."""
    cat = h.get("category", "other")
    if h.get("repeated") or any(t.lower() in bloq for t in h.get("topics", [])):
        return "descartar", "repetida (ya publicada/decidida)"
    if cat not in OK_CAT:
        return "revisar", f"categoría sensible: {cat}"
    if SENSIBLE.search(" ".join(titulares)):
        return "revisar", "palabra sensible en los titulares: " + SENSIBLE.search(" ".join(titulares)).group(0)
    if int(h.get("importance", 0)) < c["min_importancia"]:
        return "descartar", f"importancia {h.get('importance')} < {c['min_importancia']}"
    if int(h.get("quality", 0)) < c["min_calidad"]:
        return "descartar", f"calidad {h.get('quality')} < {c['min_calidad']}"
    for k in ("title", "subtitle", "question", "post", "tiktok_title", "tag"):
        if not str(h.get(k, "")).strip():
            return "descartar", f"falta {k}"
    if pp.PROHIBIDO.search(json.dumps(h, ensure_ascii=False)):
        return "descartar", "vocabulario de apuestas"
    malos = respaldado(h, titulares)
    if malos:
        return "revisar", "datos que no salen en los titulares: " + ", ".join(sorted(set(malos))[:6])
    return "publicar", "ok"


# ---------- foto y tarjetas ----------

def caras_suaves(ruta):
    """Como comprobar_caras.caras pero acepta caras pequeñas de la foto original (>= 30 px): en la tarjeta final se recortan y
    amplían, y ahí comprobar_caras.py (>= 90 px, dentro de la zona segura) es el que decide."""
    import cv2
    img = cv2.imread(ruta); h0, w0 = img.shape[:2]
    det = cv2.FaceDetectorYN.create(str(Path(__file__).with_name("modelos") / "yunet.onnx"), "", (w0, h0), 0.5, 0.3, 5000)
    _, res = det.detect(img)
    return [tuple(int(v) for v in r[:4]) for r in (res if res is not None else []) if r[2] >= 30]


def buscar_foto(h, tmp):
    """Descarga candidatas y devuelve (ruta, caras) de la mejor: grande, con cara(s) claras. NA_FOTO = foto local de prueba."""
    from PIL import Image
    if os.environ.get("NA_FOTO"):
        rutas = [os.environ["NA_FOTO"]]
    else:
        import bajar_fotos
        claves = [t for t in h.get("topics", []) if len(t) > 3] or None
        cand = bajar_fotos.web(h["photo_query"], n=8, dias=2, debe=claves, grande=True)
        if len(cand) < 4:
            cand += bajar_fotos.web(h["photo_query"], n=8, dias=2, debe=claves, grande=False)
        rutas = []
        for i, f in enumerate(cand[:24]):
            try:
                d = urllib.request.urlopen(urllib.request.Request(f["url"], headers=bajar_fotos.UA_WEB), timeout=20).read()
                if not 60_000 <= len(d) <= 15_000_000:
                    continue
                p = Path(tmp) / f"c{i}.img"
                p.write_bytes(d); rutas.append(str(p))
            except Exception:
                pass
    mejores = []
    for r in rutas:
        try:
            W, H = Image.open(r).size
            if W < 900 or H < 600 or not 0.9 <= W / H <= 2.6:
                continue
            Image.open(r).convert("RGB").save(r + ".jpg", quality=93)
            cs = caras_suaves(r + ".jpg")
            cs = sorted(cs, key=lambda b: -b[2])[:2]
            if cs and cs[0][2] >= W * 0.025:
                mejores.append((cs[0][2] * 1.0 / W, r + ".jpg", cs, (W, H)))
        except Exception as ex:
            print("foto descartada:", type(ex).__name__)
    mejores.sort(reverse=True)
    return mejores


def recorte(cs, W, H, ancho_extra=1.0):
    x0 = min(c[0] for c in cs); y0 = min(c[1] for c in cs)
    x1 = max(c[0] + c[2] for c in cs); y1 = max(c[1] + c[3] for c in cs)
    uw, uh = x1 - x0, y1 - y0
    cw = max(2.6 * uw, 2.6 * uh * 4 / 3, min(W, H * 4 / 3) * 0.3) * ancho_extra
    cw = min(cw, W, H * 4 / 3)
    ch = cw * 3 / 4
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + 0.06 * ch
    ox = min(max(cx - cw / 2, 0), W - cw); oy = min(max(cy - ch / 2, 0), H - ch)
    return [int(ox), int(oy), int(cw), int(ch)]


def tarjeta(spec, out):
    """noticia_marco.py; si el texto pasa de y=1540 baja el tamaño del titular y repite."""
    hs = 80 if len(re.sub("<.*?>", "", spec["headline"])) <= 26 else 68 if len(spec["headline"]) <= 40 else 58
    for _ in range(4):
        spec["hsize"] = hs
        sp = out + ".json"
        Path(sp).write_text(json.dumps(spec, ensure_ascii=False))
        r = subprocess.run([sys.executable, str(ROOT / "scripts/noticia_marco.py"), sp, out], capture_output=True, text=True)
        m = re.search(r"bottom=\s*([\d.]+)", r.stdout)
        if r.returncode == 0 and m and float(m.group(1)) <= 1540:
            return True
        print("tarjeta: se sale de la zona segura o falló", (m.group(1) if m else r.stderr[-200:]), "-> titular más pequeño")
        hs -= 8
    return False


def dibujar(h, tmp):
    """3 tarjetas 1080x1920 con la foto del momento. Devuelve rutas o None (y el motivo)."""
    esc = lambda s: html.escape(str(s))
    cands = buscar_foto(h, tmp)
    if not cands:
        return None, "sin foto buena con cara visible"
    hechos = [f for f in h.get("facts", []) if str(f.get("label", "")).strip()][:3]
    celdas = [[esc(f.get("figure") or "•"), esc(f["label"]).upper()] for f in hechos]
    for _, ruta, cs, (W, H) in cands[:3]:
        textos = [
            {"headline": esc(h["title"]).upper(), "sub": esc(h["subtitle"]), "celdas": [], "pregunta": "", "ancho": 1.0},
            {"headline": "WHAT WE KNOW", "sub": esc(" · ".join(f["label"] for f in hechos) or h["subtitle"]), "celdas": celdas, "pregunta": "", "ancho": 1.35},
            {"headline": "WHAT NEXT", "sub": esc(h.get("next", "")), "celdas": [], "pregunta": esc(h["question"]), "ancho": 1.15},
        ]
        rutas, ok = [], True
        for i, t in enumerate(textos, 1):
            out = str(Path(tmp) / f"n{i}.jpg")
            bien = False
            for k in (1.0, 0.8, 0.65):                   # si la cara sale pequeña/tapada, recorte más cerrado
                spec = {"foto": ruta, "crop": recorte(cs, W, H, t["ancho"] * k), "tag": esc(h["tag"]).upper(),
                        "headline": t["headline"], "sub": t["sub"], "celdas": t["celdas"], "pregunta": t["pregunta"]}
                if tarjeta(spec, out) and subprocess.run([sys.executable, str(ROOT / "scripts/comprobar_caras.py"), out, "1"],
                                                         capture_output=True).returncode == 0:
                    bien = True; break
            if not bien:
                print("cara no visible/segura en la tarjeta", i); ok = False; break
            rutas.append(out)
        if ok:
            return rutas, ruta
    return None, "ninguna foto pasó la comprobación de caras / zona segura"


# ---------- vídeo y cola ----------

def montar(rutas, pista, retraso, out, seg):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import montar_video
    with tempfile.TemporaryDirectory() as t:
        pedido = Path(t) / "p.json"
        pedido.write_text(json.dumps({"id": out.stem, "images": rutas, "seconds": seg, "audio": str(ROOT / "musica" / f"{pista}.mp3"),
                                      "out": str(out), "fade": pp.FADE, "audio_delay": retraso, "loop_audio": True}))
        montar_video.main(pedido)


def revision(h, estado, motivo, titulares):
    f = DIR / "revision.md"
    if not f.exists():
        f.write_text("# Noticias que NO se publicaron solas (miradlas a mano)\n\n")
    with f.open("a", encoding="utf-8") as fh:
        fh.write(f"## {ahora().astimezone(MAD):%d/%m %H:%M} · {h.get('title', h.get('key'))} · {estado}\n- Motivo: {motivo}\n"
                 f"- Temas: {', '.join(h.get('topics', []))}\n" + "".join(f"- {t}\n" for t in titulares[:5]) + "\n")


def publicar(h, c, titulares):
    clave = re.sub(r"[^a-z0-9-]+", "-", h.get("key", "noticia").lower()).strip("-")[:50] or "noticia"
    nombre = f"{ahora().astimezone(MAD):%Y-%m-%d_%H%M}_{clave}"
    with tempfile.TemporaryDirectory() as tmp:
        rutas, info = dibujar(h, tmp)
        if not rutas:
            apuntar({"estado": "revisar", "temas": h["topics"], "clave": clave, "motivo": info})
            revision(h, "revisar", info, titulares)
            return "sin_foto"
        pista = pp.elegir_pista(clave)
        arr = pp.arranque()
        video = ROOT / "media/noticias" / f"{nombre}.mp4"
        video.parent.mkdir(parents=True, exist_ok=True)
        montar(rutas, pista, 1 if arr == "s1" else 0, video, c["seg_tarjeta"])
        shutil.copy(rutas[0], video.with_suffix(".jpg"))                 # portada para mirarla
    url = pp.RAW + "media/noticias/" + nombre + ".mp4"
    hora = (ahora() + timedelta(minutes=3)).astimezone(MAD)
    texto = h["post"].strip() + "\n" + " ".join(h["hashtags"][:5])
    if c["modo"] != "publicar":
        pp.subir([video, video.with_suffix(".jpg")], f"noticia (seco): {clave} [skip ci]")
        apuntar({"estado": "seco", "temas": h["topics"], "clave": clave, "video": url, "texto": texto})
        return "seco"
    if not (pp.subir([video, video.with_suffix(".jpg")], f"noticia: vídeo {clave} [skip ci]") and pp.url_ok(url)):
        apuntar({"estado": "revisar", "temas": h["topics"], "clave": clave, "motivo": "no se pudo subir el vídeo"})
        return "error_subida"
    cola = []
    for red in ("tiktok", "instagram"):
        x = {"red": red, "hora": hora.isoformat(timespec="seconds"), "tipo": "noticia", "partido": h["title"][:80],
             "text": texto, "video": url, "recordatorio": False, "musica": pista,
             "variante": f"seg={c['seg_tarjeta']};arranque={arr};hook=pregunta;musica={pista};formato=auto_noticia;hora={hora:%H}",
             "notas": "noticia automática (IA + reglas): " + "; ".join(titulares[:2])[:200]}
        if red == "tiktok":
            x["titulo"] = h["tiktok_title"][:90]
        p = pp.COLA / f"{hora:%Y%m%d}_noticia_{clave}_{red}.json"
        p.write_text(json.dumps(x, ensure_ascii=False, indent=1)); cola.append(p)
    b = json.loads(pp.BIB.read_text())
    for tr in b["pistas"]:
        if tr["id"] == pista:
            tr.setdefault("usos", []).append(f"noticia {clave} {hora:%Y-%m-%d}")
    pp.BIB.write_text(json.dumps(b, ensure_ascii=False, indent=1))
    apuntar({"estado": "publicado", "temas": h["topics"], "clave": clave, "video": url})
    pp.subir([*cola, pp.BIB, DIR / "decisiones.jsonl"], f"noticia: {clave} a la cola (TikTok + IG) [skip ci]")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write("publicado=si\n")
    return "en_cola"


def main():
    c = cfg()
    cands = candidatos(c)
    bloq, _ = bloqueados(c)
    if not cands or c["modo"] == "off" or hoy_publicadas() >= c["max_dia"]:
        return print("nada que hacer")
    hechos = [{"key": d.get("clave", ""), "topics": d.get("temas", [])} for d in decisiones()
              if datetime.fromisoformat(d["t"]) > ahora() - timedelta(hours=48) and d.get("estado") != "descartar"]
    r = llm(cands, hechos)
    if not r or not isinstance(r.get("stories"), list):
        return print("la IA no respondió: se reintenta la próxima hora (nada apuntado)")
    por_tema = {x["tema"].lower(): x for x in cands}
    hecho = False
    for h in sorted(r["stories"], key=lambda s: -int(s.get("importance", 0))):
        tits = [f"{t['medio']}: {t['titulo']}" for tm in h.get("topics", []) for t in por_tema.get(tm.lower(), {}).get("titulares", [])]
        if not tits:
            continue
        h["topics"] = [t for t in h.get("topics", []) if t.lower() in por_tema]
        estado, motivo = evaluar(h, c, tits, bloq)
        print(f"{h.get('key')}: {estado} ({motivo})")
        if estado != "publicar":
            apuntar({"estado": estado, "temas": h["topics"], "clave": h.get("key", ""), "motivo": motivo})
            if estado == "revisar":
                revision(h, estado, motivo, tits)
            continue
        if hecho or hoy_publicadas() >= c["max_dia"]:
            continue                                        # una por pasada: la siguiente se evalúa la próxima hora
        print("->", publicar(h, c, tits))
        hecho = True
    pp.subir([DIR / "decisiones.jsonl", DIR / "revision.md"] if (DIR / "revision.md").exists() else [DIR / "decisiones.jsonl"],
             "noticias: decisiones [skip ci]")


if __name__ == "__main__":
    hay() if sys.argv[1:2] == ["hay"] else main()
