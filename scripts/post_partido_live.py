#!/usr/bin/env python3
"""Post-partido AUTOMÁTICO (usuario 10/10): futbol-pipeline baja los datos, Live dibuja, monta y publica.

futbol-pipeline (post_partido.yml) deja, en cuanto termina cada uno de los 2 partidos grandes del día,
data/redes/post_partido/<match_id>.json con estado "datos_listos" (y la fila en data/historico_partidos.csv).
Este script corre dentro de enviar_cola.yml (cada 10 min), ANTES del paso "Enviar":
  hay   -> clon superficial y disperso de futbol-pipeline (solo las marcas, sin instalar nada) y
           ¿alguna "datos_listos" que no esté en redes/post_partido_hechos.json? -> GITHUB_OUTPUT hay=si/no
  (sin argumento) -> para cada una: `LIENZO=reel datos_clubes.py post` en el clon (5 tarjetas + la lista tapada,
           ZONA_ESTRICTA=1), vídeo como scripts/montar_video.py (2.8 s por tarjeta, pista menos usada de
           redes/biblioteca_musica.json, arranque del bandido de aprender.py), commit del MP4 en media/post_partido/,
           URL raw 200, y 2 JSON de cola (tiktok + instagram, hora = ahora+3 min, vídeo -> automático).
           El paso "Enviar" del mismo job los manda a Buffer. El registro impide repetir.
Pruebas sin red: scripts/prueba_post_partido_live.py."""
import csv, json, os, re, shutil, subprocess, sys, tempfile, time, unicodedata, urllib.parse, urllib.request, zlib
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(os.environ.get("LIVE_ROOT") or Path(__file__).resolve().parents[1])
MAD = ZoneInfo("Europe/Madrid")
FP_URL = os.environ.get("FP_URL", "https://github.com/oundialae-debug/futbol-pipeline.git")
FP_DIR = Path(os.environ.get("FP_DIR", "/tmp/futbol-pipeline"))
MARCAS = "data/redes/post_partido"
HECHOS = ROOT / "redes/post_partido_hechos.json"
COLA, MEDIA = ROOT / "redes/cola", ROOT / "media/post_partido"
BIB, CSV_PUB = ROOT / "redes/biblioteca_musica.json", ROOT / "redes/publicaciones.csv"
RAW = "https://raw.githubusercontent.com/oundialae-debug/live/main/"
SEG, FADE = 2.8, 0.5                     # PLAYBOOK: post-partido, 2.8 s por tarjeta
CADUCA = timedelta(hours=8)              # más de 8 h tras el saque: ya no se publica (se apunta "caducado")
MAX_INTENTOS = 3
EVITAR = {"electro"}                     # biblioteca: "hueco de 0.5 s en 6 s: evitar"
GIT = os.environ.get("PP_GIT", "1") == "1"
RED = os.environ.get("PP_RED", "1") == "1"
LIGA_TAG = {"Premier League": "#PremierLeague", "La Liga": "#LaLiga", "Serie A": "#SerieA",
            "Bundesliga": "#Bundesliga", "Ligue 1": "#Ligue1", "Champions League": "#UCL"}
PROHIBIDO = re.compile(r"\b(bet|bets|betting|odds|tip|tips|stake|bookie|wager|punt)\b", re.I)


def ahora():
    a = os.environ.get("AHORA")
    return datetime.fromisoformat(a).astimezone(timezone.utc) if a else datetime.now(timezone.utc)


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


# ---------- registro ----------

def leer_hechos():
    try:
        h = json.loads(HECHOS.read_text())
    except Exception:
        h = {}
    h.setdefault("partidos", {})
    h.setdefault("en_curso", {})
    return h


def guardar_hechos(h):
    HECHOS.write_text(json.dumps(h, ensure_ascii=False, indent=1, sort_keys=True) + "\n")


# ---------- futbol-pipeline ----------

def clonar(completo=False):
    """Clon de futbol-pipeline main: disperso (solo las marcas) para mirar; completo para dibujar."""
    if not (FP_DIR / ".git").exists() and not (FP_DIR / MARCAS).exists():
        r = run(["git", "clone", "-q", "--depth", "1", "--filter=blob:none", "--sparse", FP_URL, str(FP_DIR)])
        if r.returncode:
            sys.exit("No se pudo clonar futbol-pipeline: " + r.stderr[-300:])
        # sin cone: con cone bajaría también los CSV sueltos de data/ (~160 MB) en cada pasada
        run(["git", "-C", str(FP_DIR), "sparse-checkout", "set", "--no-cone", f"/{MARCAS}/"])
    if completo and (FP_DIR / ".git").exists():
        r = run(["git", "-C", str(FP_DIR), "sparse-checkout", "disable"])
        if r.returncode:
            sys.exit("No se pudo completar el clon: " + r.stderr[-300:])


def pendientes():
    hechos = leer_hechos()["partidos"]
    out = []
    for p in sorted((FP_DIR / MARCAS).glob("*.json")):
        try:
            m = json.loads(p.read_text())
        except Exception:
            continue
        if m.get("estado") == "datos_listos" and str(m.get("match_id")) not in hechos:
            out.append(m)
    return out


def hay():
    clonar()
    pend = pendientes()
    for m in pend:
        print(f"Datos listos: {m['local']} {m.get('resultado', '')} {m['visitante']} ({m['fecha']})")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"hay={'si' if pend else 'no'}\n")
    print("hay =", "si" if pend else "no")
    return bool(pend)


def dibujar(m):
    """`datos_clubes.py post` en el clon -> PNG en orden (post1..post5 + post6 lista) y sus JSON."""
    carpeta = FP_DIR / "redes/plantillas/salida" / f"{m['fecha']}_{m['local']}_{m['visitante']}".replace(" ", "_")
    shutil.rmtree(carpeta, ignore_errors=True)
    env = {**os.environ, "LIENZO": "reel", "ZONA_ESTRICTA": "1"}
    r = run([sys.executable, "redes/plantillas/datos_clubes.py", "post", m["local"], m["visitante"], m["fecha"]],
            cwd=FP_DIR, env=env)
    print(r.stdout[-1500:])
    if r.returncode:
        raise RuntimeError("datos_clubes post: " + (r.stderr or r.stdout)[-600:])
    pngs = sorted(carpeta.glob("post*.png"))
    datos = {p.stem: json.loads(p.with_suffix(".json").read_text()) for p in pngs}
    if len(pngs) != 6:
        print(f"AVISO: {len(pngs)} tarjetas (se esperan 5 + la lista)")
    if len(pngs) < 5:
        raise RuntimeError(f"solo {len(pngs)} tarjetas")
    return pngs, datos


# ---------- vídeo ----------

def elegir_pista(mid):
    """La pista con menos usos de la biblioteca (empate: por match_id, para no repetir siempre la misma)."""
    b = json.loads(BIB.read_text())
    usos = {p["id"]: len(p.get("usos") or []) for p in b["pistas"]
            if p["id"] not in EVITAR and (p.get("dur") or 15) >= 15}       # las de 10 s se repetirían a media canción
    usos = {k: v for k, v in usos.items() if (ROOT / "musica" / f"{k}.mp3").exists()}
    return min(usos, key=lambda p: (usos[p], zlib.crc32(f"{p}{mid}".encode())))


def arranque():
    """s0/s1 del bandido (aprender.py elegir post), como los demás vídeos; si falla, s1 (como los post anteriores)."""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import aprender
        return aprender.elegir("post").get("arranque", "s1")
    except Exception as e:
        print("aprender.py no disponible:", type(e).__name__)
        return "s1"


def montar(pngs, pista, retraso, out):
    """Igual que scripts/montar_video.py (se le pasa un pedido temporal)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import montar_video
    with tempfile.TemporaryDirectory() as t:
        pedido = Path(t) / "pedido.json"
        pedido.write_text(json.dumps({"id": out.stem, "images": [str(p) for p in pngs], "seconds": SEG,
                                      "audio": str(ROOT / "musica" / f"{pista}.mp3"), "out": str(out),
                                      "fade": FADE, "audio_delay": retraso, "loop_audio": True}))
        montar_video.main(pedido)


# ---------- texto ----------

def etiqueta(n):
    n = unicodedata.normalize("NFKD", n).encode("ascii", "ignore").decode()
    return "#" + re.sub(r"[^A-Za-z0-9]", "", n)


def slug(n):
    n = unicodedata.normalize("NFKD", n).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "_", n).strip("_")


def texto(m, datos):
    """Resultado + gancho de xG (o la cifra del partido) + pregunta + 5 hashtags. Sin vocabulario de apuestas."""
    plant = {d.get("template"): d for d in datos.values()}
    d0 = next(d for d in datos.values() if d.get("home") and d.get("score"))
    a, b = d0["home"]["short"], d0["away"]["short"]
    gh, ga = d0["score"]
    res = f"{a} {gh}-{ga} {b}"
    if "deserved" in plant:
        xh, xa = plant["deserved"]["xg"]
        if abs(xh - xa) < 0.3:
            hook = f"Expected goals: {xh:.1f} vs {xa:.1f}, almost level."
        else:
            hook = f"Expected goals: {xh:.1f} vs {xa:.1f}, {a if xh > xa else b} created more."
        pregunta = "Did the better team win?"
    elif "stat_of_match" in plant:
        s = plant["stat_of_match"]
        hook = f'{s["number"]} ' + re.sub(r"<[^>]+>", "", s["text"])
        pregunta = s.get("question", "Fair result?")
    else:
        hook, pregunta = "Full-time numbers inside.", "Fair result?"
    tags = ["#football", LIGA_TAG.get(m.get("liga"), "#soccer"), etiqueta(a), etiqueta(b), "#fulltime"]
    cuerpo = f"{res}\n{hook} {pregunta}\n\n{' '.join(tags)}"
    titulo = f"{res} | {hook}"[:90]
    if PROHIBIDO.search(cuerpo) or PROHIBIDO.search(titulo):
        raise RuntimeError("vocabulario de apuestas en el texto: " + cuerpo)
    return cuerpo, titulo


# ---------- git / URL ----------

def git(*a):
    return run(["git", "-C", str(ROOT), *a])


def subir(rutas, msg):
    if not GIT:
        print("[sin git]", msg)
        return True
    git("add", *[str(p) for p in rutas])
    if git("diff", "--cached", "--quiet").returncode == 0:
        return True
    c = git("commit", "-q", "-m", msg)
    if c.returncode:
        print(c.stdout, c.stderr)
        return False
    for i in range(6):
        p = git("pull", "--rebase", "-q", "--autostash", "origin", "main")
        if p.returncode == 0 and git("push", "-q", "origin", "HEAD:main").returncode == 0:
            print("Subido:", msg)
            return True
        print("Reintento push", i + 1, (p.stderr or "")[-200:])
        time.sleep(5 + 5 * i)
    return False


def url_ok(u, espera=180):
    if not RED:
        return True
    fin = time.time() + espera
    while time.time() < fin:
        try:
            with urllib.request.urlopen(urllib.request.Request(u, method="HEAD"), timeout=20) as r:
                if r.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(10)
    return False


# ---------- un partido ----------

def procesar(m, t):
    """Registro: "partidos" = ya resueltos (no se vuelven a mirar); "en_curso" = música elegida, intentos, último error."""
    mid = str(m["match_id"])
    hechos = leer_hechos()
    cur = hechos.setdefault("en_curso", {}).setdefault(mid, {})
    base = {"partido": f"{m['local']}-{m['visitante']}", "fecha": m["fecha"], "resultado": m.get("resultado", "")}

    def cerrar(estado, msg, rutas=(), **extra):
        hechos["en_curso"].pop(mid, None)
        hechos["partidos"][mid] = {**base, **{k: v for k, v in cur.items() if k != "error" or estado == "error"},
                                   "estado": estado, "hora": t.isoformat(timespec="seconds"), **extra}
        guardar_hechos(hechos)
        return subir([*rutas, HECHOS], msg)

    if t > datetime.fromisoformat(m["saque_utc"]) + CADUCA:
        cerrar("caducado", f"post-partido: {base['partido']} caducado, sin publicar [skip ci]")
        return "caducado"
    nombre = f"{m['fecha']}_{slug(m['local'])}_{slug(m['visitante'])}"
    video = MEDIA / f"{nombre}.mp4"
    url = RAW + urllib.parse.quote(video.relative_to(ROOT).as_posix())
    try:
        pngs, datos = dibujar(m)                      # también si el vídeo ya está: el texto sale de los JSON
        cuerpo, titulo = texto(m, datos)
        if not video.exists():
            cur.setdefault("musica", elegir_pista(mid))
            cur.setdefault("arranque", arranque())
            cur["tarjetas"] = len(pngs)
            MEDIA.mkdir(parents=True, exist_ok=True)
            montar(pngs, cur["musica"], 1 if cur["arranque"] == "s1" else 0, video)
            guardar_hechos(hechos)
            if not subir([video, HECHOS], f"post-partido: vídeo {base['partido']} [skip ci]"):
                return "error_push"
    except (Exception, SystemExit) as e:
        cur["intentos"] = cur.get("intentos", 0) + 1
        cur["error"] = f"{type(e).__name__}: {e}"[:400]
        print("ERROR", mid, cur["error"])
        if cur["intentos"] >= MAX_INTENTOS:
            cerrar("error", f"post-partido: {base['partido']} error, sin publicar [skip ci]")
        else:
            guardar_hechos(hechos)
            subir([HECHOS], f"post-partido: {base['partido']} error {cur['intentos']}/{MAX_INTENTOS} [skip ci]")
        return "error"
    if not url_ok(url):
        print("La URL raw del vídeo aún no da 200: se reintenta en la siguiente pasada")
        return "url_no_lista"
    pista = cur.get("musica", "")
    hora = (max(t, datetime.now(timezone.utc)) + timedelta(minutes=3)).astimezone(MAD)
    variante = f"seg={SEG};arranque={cur.get('arranque', 's1')};hook=dato;musica={pista};formato=auto_post"
    COLA.mkdir(parents=True, exist_ok=True)
    colas = []
    for red in ("tiktok", "instagram"):
        x = {"red": red, "hora": hora.isoformat(timespec="seconds"), "tipo": "post", "partido": base["partido"],
             "text": cuerpo, "video": url, "recordatorio": False, "musica": pista, "variante": variante,
             "notas": f"post-partido automático (futbol-pipeline {mid}, {cur.get('tarjetas', len(pngs))} tarjetas)"}
        if red == "tiktok":
            x["titulo"] = titulo
        p = COLA / f"{hora:%Y%m%d}_post_{nombre}_{red}.json"
        p.write_text(json.dumps(x, ensure_ascii=False, indent=1))
        colas.append(p)
    b = json.loads(BIB.read_text())                  # rotación de música: la pista suma un uso
    for tr in b["pistas"]:
        if tr["id"] == pista:
            tr.setdefault("usos", []).append(f"post {base['partido']} {m['fecha']}")
    BIB.write_text(json.dumps(b, ensure_ascii=False, indent=1))
    if not cerrar("en_cola", f"post-partido: {base['partido']} a la cola (TikTok + IG) [skip ci]", [*colas, BIB],
                  video=url, publicar=hora.isoformat(timespec="seconds")):
        return "error_push"
    return "en_cola"


def main():
    clonar(completo=True)
    t = ahora()
    out = {}
    for m in pendientes():
        out[str(m["match_id"])] = procesar(m, t)
        print(m["local"], "-", m["visitante"], "->", out[str(m["match_id"])])
    return out


if __name__ == "__main__":
    if sys.argv[1:2] == ["hay"]:
        hay()
    else:
        main()
