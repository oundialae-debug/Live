"""Escaneo horario de noticias de fútbol (usuario 11/10: la noticia deja de serlo si se publica tarde).
Corre en GitHub Actions cada hora (workflow `noticias`, 08:30-23:30 Madrid). Guarda CADA noticia nueva con medio, titular,
URL y fechas en redes/noticias/AAAA-MM-DD.jsonl, SIN repetir: una noticia ya guardada (mismo titular normalizado o misma URL,
o un titular casi idéntico del mismo medio) no se vuelve a apuntar aunque siga en el RSS horas después.
Calcula los temas del día (nº de medios distintos en las últimas 36 h) en redes/noticias/temas.json.
Uso: noticias.py            -> escanea y guarda
     noticias.py ventana    -> escribe dentro=si|no en $GITHUB_OUTPUT (¿es hora de escanear en Madrid? 08:00-23:45)"""
import hashlib, json, os, re, sys, unicodedata, urllib.request, xml.etree.ElementTree as ET
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
from titulares import FEEDS, VACIAS, PAL          # los mismos ~34 medios que redes/fuentes.md

ROOT = Path(os.environ.get("LIVE_ROOT") or Path(__file__).resolve().parents[1])
DIR = ROOT / "redes/noticias"
MAD = ZoneInfo("Europe/Madrid")
GUARDA_DIAS = 14          # los ficheros diarios de más de 14 días se borran (el repo no crece sin fin)
TEMAS_HORAS = 36
ATOM = "{http://www.w3.org/2005/Atom}"


def norm(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", t)).strip()


def idn(t):
    return hashlib.sha1(norm(t).encode()).hexdigest()[:12]


def parecido(a, b):
    """Jaccard de palabras: titulares casi idénticos de un mismo medio (retoques de última hora)."""
    A, B = set(a.split()), set(b.split())
    return bool(A and B) and len(A & B) / len(A | B) >= 0.85


def leer(nombre, url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (2yellow noticias)"})
    raiz = ET.fromstring(urllib.request.urlopen(req, timeout=25).read())
    limite = datetime.now(timezone.utc) - timedelta(hours=TEMAS_HORAS)
    out = []
    for it in (list(raiz.iter("item")) or list(raiz.iter(ATOM + "entry")))[:40]:
        t = (it.findtext("title") or it.findtext(ATOM + "title") or "").strip()
        link = (it.findtext("link") or "").strip()
        if not link:
            a = it.find(ATOM + "link")
            link = a.get("href", "") if a is not None else ""
        f = it.findtext("pubDate") or it.findtext(ATOM + "updated") or it.findtext(ATOM + "published")
        pub = None
        try:
            if f:
                pub = parsedate_to_datetime(f) if "," in f else datetime.fromisoformat(f.replace("Z", "+00:00"))
                if pub.tzinfo is None:
                    pub = pub.replace(tzinfo=timezone.utc)
                if pub < limite:
                    continue
        except Exception:
            pub = None
        if nombre.startswith("Google News"):
            t = t.rsplit(" - ", 1)[0]
        if t:
            out.append({"medio": nombre, "titulo": re.sub(r"\s+", " ", t)[:240], "url": link,
                        "pub": pub.astimezone(timezone.utc).isoformat(timespec="minutes") if pub else ""})
    return out


def cargar(dias=GUARDA_DIAS):
    """Todo lo guardado en los últimos `dias` días: lista de dicts (cada uno con 'id', 'norm')."""
    items = []
    for p in sorted(DIR.glob("????-??-??.jsonl"))[-dias:]:
        for l in p.read_text(encoding="utf-8").splitlines():
            try:
                x = json.loads(l)
                x["norm"] = norm(x["titulo"])
                items.append(x)
            except Exception:
                pass
    return items


def escanear():
    DIR.mkdir(parents=True, exist_ok=True)
    ahora = datetime.now(timezone.utc)
    previos = cargar()
    ids = {x["id"] for x in previos}
    urls = {x["url"] for x in previos if x.get("url")}
    por_medio = defaultdict(list)
    for x in previos:
        if x["visto"] >= (ahora - timedelta(hours=48)).isoformat(timespec="minutes"):
            por_medio[x["medio"]].append(x["norm"])
    fallos = []

    def uno(kv):
        try:
            return kv[0], leer(*kv), None
        except Exception as ex:
            return kv[0], [], type(ex).__name__
    with ThreadPoolExecutor(8) as ex:
        res = list(ex.map(uno, FEEDS.items()))
    nuevas, leidas = [], 0
    for nombre, items, fallo in res:
        if fallo:
            fallos.append(f"{nombre} ({fallo})")
            continue
        leidas += 1
        for it in items:
            i, n = idn(it["titulo"]), norm(it["titulo"])
            if i in ids or (it["url"] and it["url"] in urls) or any(parecido(n, m) for m in por_medio[nombre]):
                continue                       # ya guardada: NO se repite
            ids.add(i); urls.add(it["url"]); por_medio[nombre].append(n)
            nuevas.append({"id": i, **it, "visto": ahora.isoformat(timespec="minutes")})
    if nuevas:
        f = DIR / f"{ahora.astimezone(MAD):%Y-%m-%d}.jsonl"
        with f.open("a", encoding="utf-8") as fh:
            for x in nuevas:
                fh.write(json.dumps(x, ensure_ascii=False) + "\n")
    # limpieza de ficheros viejos
    for p in sorted(DIR.glob("????-??-??.jsonl"))[:-GUARDA_DIAS]:
        p.unlink()
    temas(ahora)
    print(f"{leidas}/{len(FEEDS)} medios leídos, {len(nuevas)} noticias NUEVAS guardadas (de {sum(len(r[1]) for r in res)} vistas), "
          f"{len(fallos)} fallos: {fallos}")


def temas(ahora):
    """Temas (nombres propios) por nº de medios distintos en las últimas 36 h, con los titulares/URLs que los sostienen."""
    desde = (ahora - timedelta(hours=TEMAS_HORAS)).isoformat(timespec="minutes")
    medios, ej, primera = defaultdict(set), defaultdict(list), {}
    for x in cargar(3):
        if (x.get("pub") or x["visto"]) < desde:
            continue
        for p in set(PAL.findall(x["titulo"])):
            if p in VACIAS or (p.upper() == p and len(p) < 4):
                continue
            medios[p].add(x["medio"])
            ej[p].append({"medio": x["medio"], "titulo": x["titulo"], "url": x["url"], "pub": x.get("pub", "")})
            primera[p] = min(primera.get(p, x["visto"]), x["visto"])
    top = sorted(medios.items(), key=lambda kv: -len(kv[1]))[:30]
    out = {"generado": ahora.isoformat(timespec="minutes"),
           "temas": [{"tema": p, "medios": len(m), "lista_medios": sorted(m), "primera_vez": primera[p],
                      "titulares": ej[p][:12]} for p, m in top]}
    (DIR / "temas.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def ventana():
    """08:00-23:45 hora de Madrid. El cron va en UTC y cubre verano e invierno; aquí se descartan las pasadas fuera de hora."""
    t = datetime.now(MAD)
    dentro = (8, 0) <= (t.hour, t.minute) <= (23, 45) or os.environ.get("FORZAR") == "1"
    print(f"Madrid {t:%H:%M}: {'dentro' if dentro else 'fuera'} de la ventana 08:00-23:45")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"dentro={'si' if dentro else 'no'}\n")


if __name__ == "__main__":
    ventana() if sys.argv[1:2] == ["ventana"] else escanear()
