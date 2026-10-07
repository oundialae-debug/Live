"""Fotos de jugadores con licencia libre para las plantillas (jugador vs jugador). Corre en GitHub Actions
(el entorno de Claude no llega a Wikimedia). Entrada: fotos/pedidos/*.json {"jugadores": ["Kylian Mbappé", ...]}.
Busca la foto principal del artículo de la Wikipedia en inglés (en biografías de gente viva solo se admiten
fotos libres), comprueba la licencia en Commons (CC / dominio público) y guarda fotos/<slug>.jpg + <slug>.json
con autor y licencia para el crédito obligatorio. Si no hay foto libre, apunta el fallo y sigue.
También {"web": [{"buscar": "...", "slug": "...", "n": 8, "dias": 7, "debe": ["arteta"], "noticia": "Arteta"}]}
("noticia": primero la foto principal de las noticias de hoy con esa palabra en el titular): fotos recientes y grandes de toda la web
(Bing/DuckDuckGo) a fotos/candidatas/, sin mirar licencia (decisión del usuario 07/10)."""
import json, re, sys, unicodedata, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UA = {"User-Agent": "2yellow-bot/1.0 (https://github.com/oundialae-debug/live)"}


def get(url):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30))


def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "_", t).strip("_")


def foto(nombre):
    q = urllib.parse.urlencode({"action": "query", "format": "json", "redirects": 1, "prop": "pageimages",
                                "piprop": "name", "titles": nombre})
    pags = get(f"https://en.wikipedia.org/w/api.php?{q}")["query"]["pages"]
    archivo = next((p.get("pageimage") for p in pags.values() if p.get("pageimage")), None)
    if not archivo:
        q = urllib.parse.urlencode({"action": "query", "format": "json", "list": "search", "srlimit": 1,
                                    "srsearch": f"{nombre} footballer"})
        r = get(f"https://en.wikipedia.org/w/api.php?{q}")["query"]["search"]
        if r:
            return foto(r[0]["title"]) if r[0]["title"] != nombre else None
        return None
    q = urllib.parse.urlencode({"action": "query", "format": "json", "prop": "imageinfo", "iiprop": "url|extmetadata",
                                "iiurlwidth": 900, "titles": f"File:{archivo}"})
    info = next(iter(get(f"https://commons.wikimedia.org/w/api.php?{q}")["query"]["pages"].values()))["imageinfo"][0]
    meta = info.get("extmetadata", {})
    lic = re.sub("<[^>]+>", "", meta.get("LicenseShortName", {}).get("value", ""))
    autor = re.sub("<[^>]+>", "", meta.get("Artist", {}).get("value", "")).strip()
    if not re.search(r"CC|Public domain|PD", lic, re.I):
        print(f"[!] {nombre}: licencia no libre ({lic})"); return None
    return {"jugador": nombre, "archivo": archivo, "url": info["thumburl"], "autor": autor[:60], "licencia": lic,
            "credito": f"Photo: {autor[:40]}, {lic}"}


def commons(buscar, n=6, c_ancho=1600):
    """Varias fotos candidatas de Commons (para no repetir la misma foto de un jugador)."""
    q = urllib.parse.urlencode({"action": "query", "format": "json", "list": "search", "srnamespace": 6,
                                "srlimit": n * 2, "srsearch": buscar})
    out = []
    for r in get(f"https://commons.wikimedia.org/w/api.php?{q}")["query"]["search"]:
        t = r["title"]
        if not re.search(r"\.(jpe?g|png)$", t, re.I):
            continue
        q2 = urllib.parse.urlencode({"action": "query", "format": "json", "prop": "imageinfo", "iiprop": "url|extmetadata",
                                     "iiurlwidth": c_ancho, "titles": t})
        info = next(iter(get(f"https://commons.wikimedia.org/w/api.php?{q2}")["query"]["pages"].values()))["imageinfo"][0]
        meta = info.get("extmetadata", {})
        lic = re.sub("<[^>]+>", "", meta.get("LicenseShortName", {}).get("value", ""))
        autor = re.sub("<[^>]+>", "", meta.get("Artist", {}).get("value", "")).strip()
        if re.search(r"CC|Public domain|PD", lic, re.I):
            out.append({"archivo": t[5:], "url": info["thumburl"], "autor": autor[:60], "licencia": lic,
                        "credito": f"Photo: {autor[:40]}, {lic}"})
        if len(out) >= n:
            break
    return out


UA_WEB = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
          "Accept-Language": "en-GB,en;q=0.9"}


def web(buscar, n=8, dias=7, debe=None):
    """Fotos de toda la web (usuario 07/10: "nunca te preocupes por los derechos; busca la imagen más actual y de
    calidad"). Junta Bing Imágenes (grandes; primero de los últimos `dias`, luego sin fecha) y DuckDuckGo, y se queda
    solo con las que llevan en el título o en la URL alguna palabra de `debe` (por defecto, las palabras con mayúscula
    de la búsqueda): sin ese filtro Bing devuelve basura (con "Arteta" salió Cairo, Illinois)."""
    out = []
    for qft in (f"+filterui:imagesize-large+filterui:age-lt{dias * 1440}", "+filterui:imagesize-large"):
        try:
            q = urllib.parse.urlencode({"q": buscar, "first": 1, "count": 80, "qft": qft})
            html = urllib.request.urlopen(urllib.request.Request(f"https://www.bing.com/images/async?{q}", headers=UA_WEB), timeout=30).read().decode("utf-8", "ignore")
            for m in re.finditer(r'm="(\{[^"]+\})"', html):
                try:
                    d = json.loads(m.group(1).replace("&quot;", '"').replace("&amp;", "&"))
                    out.append({"url": d["murl"], "titulo": d.get("t", ""), "pagina": d.get("purl", ""), "fuente": "bing"})
                except Exception:
                    pass
        except Exception as ex:
            print(f"[!] bing {buscar}: {ex}")
    try:
        pag = urllib.request.urlopen(urllib.request.Request("https://duckduckgo.com/?" + urllib.parse.urlencode({"q": buscar, "iax": "images", "ia": "images"}), headers=UA_WEB), timeout=30).read().decode("utf-8", "ignore")
        vqd = re.search(r"vqd=['\"]?([\d-]+)", pag).group(1)
        per = "Day" if dias <= 1 else "Week" if dias <= 7 else "Month"
        for f in (f"time:{per},size:Large,,,,", "size:Large,,,,"):
            q = urllib.parse.urlencode({"l": "wt-wt", "o": "json", "q": buscar, "vqd": vqd, "f": f, "p": "1"})
            for r in get_web(f"https://duckduckgo.com/i.js?{q}").get("results", []):
                out.append({"url": r["image"], "titulo": r.get("title", ""), "pagina": r.get("url", ""), "fuente": "ddg"})
    except Exception as ex:
        print(f"[!] ddg {buscar}: {ex}")
    claves = [slug(w) for w in (debe or [w for w in buscar.split() if w[:1].isupper() and len(w) > 3])]
    vistos, buenos = set(), []
    for f in out:
        texto = slug(f"{f['titulo']} {f['pagina']} {f['url']}")
        if f["url"] in vistos or not f["url"].startswith("http") or (claves and not any(c in texto for c in claves)):
            continue
        vistos.add(f["url"]); buenos.append(f)
    print(f"web {buscar}: {len(out)} resultados, {len(buenos)} con {claves}")
    return buenos[: n * 3]


def noticia(buscar, n=6):
    """Foto principal (og:image) de las noticias de hoy cuyo titular contiene `buscar` en los RSS de scripts/titulares.py
    (BBC, Guardian, Sky, Marca...). Es la foto más actual y de calidad: la que eligió el propio medio."""
    sys.path.insert(0, str(ROOT / "scripts"))
    from titulares import FEEDS
    import xml.etree.ElementTree as ET
    clave, out = slug(buscar), []
    for medio, url in FEEDS.items():
        if medio.startswith("Google News") or medio.startswith("r/"):
            continue
        try:
            raiz = ET.fromstring(urllib.request.urlopen(urllib.request.Request(url, headers=UA_WEB), timeout=20).read())
        except Exception:
            continue
        for it in list(raiz.iter("item"))[:40]:
            t, enlace = it.findtext("title") or "", (it.findtext("link") or "").strip()
            if clave not in slug(t) or not enlace.startswith("http"):
                continue
            try:
                html = urllib.request.urlopen(urllib.request.Request(enlace, headers=UA_WEB), timeout=20).read().decode("utf-8", "ignore")
                m = re.search(r'<meta[^>]+(?:property|name)=["\']og:image["\'][^>]+content=["\']([^"\']+)', html) or \
                    re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\']og:image', html)
                if m:
                    out.append({"url": m.group(1).replace("&amp;", "&"), "titulo": t, "pagina": enlace, "fuente": medio})
            except Exception:
                pass
            if len(out) >= n * 2:
                return out
    return out


def get_web(url):
    h = dict(UA_WEB, Referer="https://duckduckgo.com/")
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=30))


def main():
    hechos = 0
    for ped in sorted((ROOT / "fotos/pedidos").glob("*.json")):
        for c in json.loads(ped.read_text()).get("commons", []):  # {"buscar": "...", "slug": "..."} -> fotos/candidatas/
            try:
                for i, f in enumerate(commons(c["buscar"], c.get("n", 6), c.get("ancho", 1600)), 1):
                    d = ROOT / "fotos/candidatas"; d.mkdir(parents=True, exist_ok=True)
                    (d / f"{c['slug']}_{i}.jpg").write_bytes(urllib.request.urlopen(urllib.request.Request(f["url"], headers=UA), timeout=60).read())
                    (d / f"{c['slug']}_{i}.json").write_text(json.dumps(f, ensure_ascii=False, indent=1)); hechos += 1
            except Exception as ex:
                print(f"[!] {c}: {ex}")
    for ped in sorted((ROOT / "fotos/pedidos").glob("*.json")):
        for c in json.loads(ped.read_text()).get("web", []):  # {"buscar": "...", "slug": "...", "n": 8, "dias": 7} -> fotos/candidatas/
            d = ROOT / "fotos/candidatas"; d.mkdir(parents=True, exist_ok=True); i = 0
            cands = noticia(c["noticia"], c.get("n", 8)) if c.get("noticia") else []
            print(f"noticias con {c.get('noticia')}: {len(cands)}")
            for f in cands + web(c["buscar"], c.get("n", 8), c.get("dias", 7), c.get("debe")):
                try:
                    r = urllib.request.urlopen(urllib.request.Request(f["url"], headers=UA_WEB), timeout=30)
                    datos = r.read()
                    if "image" not in r.headers.get("Content-Type", "image") or len(datos) < 60_000:
                        continue  # no es imagen o es pequeña (mala calidad)
                except Exception:
                    continue
                i += 1; ext = "png" if datos[:4] == b"\x89PNG" else "webp" if datos[8:12] == b"WEBP" else "jpg"
                (d / f"{c['slug']}_{i}.{ext}").write_bytes(datos)
                (d / f"{c['slug']}_{i}.json").write_text(json.dumps(dict(f, credito=""), ensure_ascii=False, indent=1)); hechos += 1
                if i >= c.get("n", 8):
                    break
            print(f"web {c['buscar']}: {i} fotos")
    for ped in sorted((ROOT / "fotos/pedidos").glob("*.json")):
        for n in json.loads(ped.read_text()).get("jugadores", []):
            try:
                f = foto(n)
            except Exception as ex:
                print(f"[!] {n}: {ex}"); f = None
            if not f:
                continue
            s = slug(n)
            req = urllib.request.Request(f["url"], headers=UA)
            (ROOT / f"fotos/{s}.jpg").write_bytes(urllib.request.urlopen(req, timeout=60).read())
            (ROOT / f"fotos/{s}.json").write_text(json.dumps(f, ensure_ascii=False, indent=1))
            print(f"OK {n} -> fotos/{s}.jpg ({f['credito']})"); hechos += 1
        ped.unlink()
    print(f"{hechos} fotos")


if __name__ == "__main__":
    main()
