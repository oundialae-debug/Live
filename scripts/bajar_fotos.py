"""Fotos de jugadores con licencia libre para las plantillas (jugador vs jugador). Corre en GitHub Actions
(el entorno de Claude no llega a Wikimedia). Entrada: fotos/pedidos/*.json {"jugadores": ["Kylian Mbappé", ...]}.
Busca la foto principal del artículo de la Wikipedia en inglés (en biografías de gente viva solo se admiten
fotos libres), comprueba la licencia en Commons (CC / dominio público) y guarda fotos/<slug>.jpg + <slug>.json
con autor y licencia para el crédito obligatorio. Si no hay foto libre, apunta el fallo y sigue."""
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
