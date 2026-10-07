"""Titulares de fútbol de ~30 medios por RSS (redes/fuentes.md) para no perder la noticia del día (usuario 07/10: se
escapó la despedida de Messi). Corre en GitHub Actions (aquí no hay internet). Escribe redes/titulares.md con:
1) los temas (nombres propios) que salen en más medios distintos -> la noticia del día; 2) los titulares por medio."""
import re, urllib.request, xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GN = "https://news.google.com/rss/search?q={q}+when:1d&hl={hl}&gl={gl}&ceid={gl}:{ce}"
FEEDS = {
    "BBC": "https://feeds.bbci.co.uk/sport/football/rss.xml",
    "Guardian": "https://www.theguardian.com/football/rss",
    "Sky Sports": "https://www.skysports.com/rss/12040",
    "ESPN": "https://www.espn.com/espn/rss/soccer/news",
    "Goal": "https://www.goal.com/feeds/en/news",
    "talkSPORT": "https://talksport.com/football/feed/",
    "Daily Mail": "https://www.dailymail.co.uk/sport/football/index.rss",
    "Mirror": "https://www.mirror.co.uk/sport/football/?service=rss",
    "Independent": "https://www.independent.co.uk/sport/football/rss",
    "Telegraph": "https://www.telegraph.co.uk/football/rss.xml",
    "90min": "https://www.90min.com/posts.rss",
    "Planet Football": "https://www.planetfootball.com/feed",
    "FourFourTwo": "https://www.fourfourtwo.com/feeds.xml",
    "Football365": "https://www.football365.com/feed",
    "Yahoo": "https://sports.yahoo.com/soccer/rss/",
    "Google News EN": GN.format(q="football", hl="en-GB", gl="GB", ce="en"),
    "Marca": "https://e00-marca.uecdn.es/rss/futbol/portada.xml",
    "AS": "https://feeds.as.com/mrss-s/pages/as/site/as.com/section/futbol/portada/",
    "Mundo Deportivo": "https://www.mundodeportivo.com/feed/rss/futbol",
    "Sport": "https://www.sport.es/es/rss/futbol/rss.xml",
    "Google News ES": GN.format(q="f%C3%BAtbol", hl="es", gl="ES", ce="es"),
    "Gazzetta": "https://www.gazzetta.it/rss/calcio.xml",
    "Football Italia": "https://football-italia.net/feed/",
    "Calciomercato": "https://www.calciomercato.com/feed",
    "Kicker": "https://newsfeed.kicker.de/news/fussball",
    "L'Equipe": "https://dwh.lequipe.fr/api/edito/rss?path=/Football/",
    "Foot Mercato": "https://www.footmercato.net/flux-rss",
    "Record": "https://www.record.pt/rss",
    "TN": "https://tn.com.ar/rss/deportes/",
    "Ole": "https://www.ole.com.ar/rss/ultimas-noticias/",
    "Infobae": "https://www.infobae.com/arc/outboundfeeds/rss/category/deportes/",
    "Google News AR": GN.format(q="f%C3%BAtbol", hl="es-419", gl="AR", ce="es-419"),
    "ge.globo": "https://ge.globo.com/rss/ge/futebol/",
    "r/soccer (top día)": "https://www.reddit.com/r/soccer/top/.rss?t=day",
}
# Palabras con mayúscula que no son tema (artículos, días, meses, medios...).
VACIAS = set("""The A An And Of In On At To For With From By Is Are Was Be As After Before Over Into vs Vs How Why What Who When Where
This That It His Her Their He She They We You I My Our New Live Watch Report Video Photos Gallery Exclusive Breaking Update Updates
El La Los Las Un Una Del De En Con Por Para Que Qué Cómo Su Sus Al Lo Le Il Lo Gli Di Da Der Die Das Und Le Les Des Du Et Au Aux
Monday Tuesday Wednesday Thursday Friday Saturday Sunday January February March April May June July August September October November December
Lunes Martes Miércoles Jueves Viernes Sábado Domingo Octubre Football Fútbol Futbol Soccer Calcio News Noticias League Liga Cup Copa
Premier Champions Nations World Mundial Serie Bundesliga Ligue United City Real FC CF Club Sport Sports Fans Fan Coach Manager Player Players
BBC ESPN Goal Marca AS Sky Mail Mirror Telegraph Guardian Independent Reddit Here Here's Not But If So Just More Most Can Will Could""".split())
PAL = re.compile(r"\b([A-ZÁÉÍÓÚÑÜÖÄ][\wÁÉÍÓÚÑÜÖÄáéíóúñüöäçã'’\-]{2,})\b")


def leer(nombre, url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (2yellow titulares)"})
    raiz = ET.fromstring(urllib.request.urlopen(req, timeout=25).read())
    limite = datetime.now(timezone.utc) - timedelta(hours=36)
    out = []
    items = list(raiz.iter("item")) or list(raiz.iter("{http://www.w3.org/2005/Atom}entry"))
    for it in items[:40]:
        t = (it.findtext("title") or it.findtext("{http://www.w3.org/2005/Atom}title") or "").strip()
        f = it.findtext("pubDate") or it.findtext("{http://www.w3.org/2005/Atom}updated")
        try:
            d = parsedate_to_datetime(f) if f and "," in f else datetime.fromisoformat(f.replace("Z", "+00:00")) if f else None
            if d and d.tzinfo and d < limite:
                continue
        except Exception:
            pass
        if nombre.startswith("Google News"):
            t = t.rsplit(" - ", 1)[0]
        if t:
            out.append(t)
    return out


def main():
    por_medio, fallos = {}, []
    for nombre, url in FEEDS.items():
        try:
            por_medio[nombre] = leer(nombre, url)
        except Exception as ex:
            fallos.append(f"{nombre} ({type(ex).__name__})")
    medios = defaultdict(set); ejemplo = {}
    for nombre, tits in por_medio.items():
        for t in tits:
            for p in set(PAL.findall(t)):
                if p in VACIAS or p.upper() == p and len(p) < 4:
                    continue
                medios[p].add(nombre); ejemplo.setdefault(p, t)
    top = sorted(medios.items(), key=lambda kv: -len(kv[1]))[:25]
    ahora = datetime.now(timezone.utc)
    out = [f"# Titulares de fútbol ({ahora:%Y-%m-%d %H:%M} UTC, últimas 36 h)", "",
           f"Generado por `scripts/titulares.py` (workflow `tendencias`). Leídos {len(por_medio)} de {len(FEEDS)} medios; fuentes en `redes/fuentes.md`.", "",
           "## Temas que salen en más medios (la noticia del día está arriba)", "", "| Tema | Nº medios | Medios | Ejemplo |", "|---|---|---|---|"]
    out += [f"| {p} | {len(m)} | {', '.join(sorted(m))[:80]} | {ejemplo[p][:110]} |" for p, m in top]
    out += ["", "## Titulares por medio", ""]
    for nombre, tits in por_medio.items():
        out.append(f"**{nombre}** ({len(tits)})")
        out += [f"- {t[:140]}" for t in tits[:12]]
        out.append("")
    if fallos:
        out += ["Fallaron: " + ", ".join(fallos)]
    (ROOT / "redes/titulares.md").write_text("\n".join(out) + "\n")
    print(f"{len(por_medio)} medios leídos, {len(fallos)} fallos: {fallos}")


if __name__ == "__main__":
    main()
