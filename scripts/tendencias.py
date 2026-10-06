"""Tendencias del día para 2yellow (usuario 06/10: "aprende a usar trends en fútbol, publicar según el momentum").
Corre en GitHub Actions (aquí no hay internet). Lee las búsquedas en tendencia de Google Trends (RSS público) en los
países de las 5 grandes + EE. UU., se queda con las de fútbol y escribe redes/tendencias.md para la tarea diaria."""
import re, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAISES = {"GB": "UK", "ES": "Spain", "IT": "Italy", "DE": "Germany", "FR": "France", "US": "USA"}
FUTBOL = re.compile(r"\b(football|soccer|f[uú]tbol|calcio|fu(ss|ß)ball|fc|cf|atletico|atlético|madrid|barcelona|barça|liverpool|"
                    r"arsenal|chelsea|tottenham|newcastle|man(chester)? (city|united|utd)|juventus|inter|milan|napoli|roma|lazio|bayern|"
                    r"dortmund|leverkusen|psg|marseille|lyon|monaco|ballon d.or|champions league|premier league|la ?liga|serie a|"
                    r"bundesliga|ligue 1|uefa|fifa|nations league|mbapp[eé]|yamal|haaland|kane|vin[ií]cius|bellingham|salah|messi|"
                    r"ronaldo|olise|demb[eé]l[eé]|cl[aá]sico|derby|derbi|national team|selecci[oó]n|world cup|mundial|strikers?|goalkeeper|midfielder)\b", re.I)
NO_FUTBOL = re.compile(r"\b(cricket|ipl|t20|odi|nfl|nba|mlb|nhl|rugby|tennis|f1|formula 1)\b", re.I)
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
            if FUTBOL.search(texto) and not NO_FUTBOL.search(texto):
                filas.append((pais, t, trafico, (noticias or [""])[0]))
    out = [f"# Tendencias de fútbol ({datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC, Google Trends)", "",
           "Generado por el workflow `tendencias`. Úsalo para elegir temas de memes, curiosos y jugador vs jugador.", "",
           "| País | Búsqueda | Tráfico | Titular |", "|---|---|---|---|"]
    out += [f"| {p} | {t} | {tr} | {n[:100]} |" for p, t, tr, n in filas] or ["| — | (nada de fútbol en tendencia) | | |"]
    (ROOT / "redes/tendencias.md").write_text("\n".join(out) + "\n")
    print(f"{len(filas)} tendencias de fútbol")


if __name__ == "__main__":
    main()
