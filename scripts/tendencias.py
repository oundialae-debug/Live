"""Tendencias del día para 2yellow (usuario 06/10: "aprende a usar trends en fútbol, publicar según el momentum").
Corre en GitHub Actions (aquí no hay internet). Lee las búsquedas en tendencia de Google Trends (RSS público) en los
países de las 5 grandes + EE. UU., se queda con las de fútbol y escribe redes/tendencias.md para la tarea diaria."""
import re, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAISES = {"GB": "UK", "ES": "Spain", "IT": "Italy", "DE": "Germany", "FR": "France", "US": "USA"}
FUTBOL = re.compile(r"\b(vs|v|fc|cf|ac|sc|united|city|real|atletico|atlético|madrid|barcelona|barça|liverpool|arsenal|chelsea|"
                    r"tottenham|newcastle|juventus|inter|milan|napoli|roma|lazio|bayern|dortmund|leverkusen|psg|marseille|lyon|"
                    r"monaco|ballon|champions|premier|liga|serie a|bundesliga|ligue|uefa|fifa|mbapp|yamal|haaland|kane|vinicius|"
                    r"bellingham|salah|messi|ronaldo|olise|dembele|dembélé|nations league|world cup|transfer|fichaje|derby|derbi|"
                    r"clasico|clásico|goal|gol|penalty|var|coach|manager|entrenador)\b", re.I)
NS = {"ht": "https://trends.google.com/trending/rss"}


def main():
    filas = []
    for geo, pais in PAISES.items():
        try:
            req = urllib.request.Request(f"https://trends.google.com/trending/rss?geo={geo}", headers={"User-Agent": "Mozilla/5.0"})
            raiz = ET.fromstring(urllib.request.urlopen(req, timeout=30).read())
        except Exception as ex:
            print(geo, "falló:", ex); continue
        for it in raiz.iter("item"):
            t = it.findtext("title") or ""
            trafico = it.findtext("ht:approx_traffic", default="", namespaces=NS)
            noticias = [n.findtext("ht:news_item_title", default="", namespaces=NS) for n in it.findall("ht:news_item", NS)]
            texto = " ".join([t] + noticias)
            if FUTBOL.search(texto):
                filas.append((pais, t, trafico, (noticias or [""])[0]))
    out = [f"# Tendencias de fútbol ({datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC, Google Trends)", "",
           "Generado por el workflow `tendencias`. Úsalo para elegir temas de memes, curiosos y jugador vs jugador.", "",
           "| País | Búsqueda | Tráfico | Titular |", "|---|---|---|---|"]
    out += [f"| {p} | {t} | {tr} | {n[:100]} |" for p, t, tr, n in filas] or ["| — | (nada de fútbol en tendencia) | | |"]
    (ROOT / "redes/tendencias.md").write_text("\n".join(out) + "\n")
    print(f"{len(filas)} tendencias de fútbol")


if __name__ == "__main__":
    main()
