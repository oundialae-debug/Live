"""Alertas de noticias grandes sin cubrir (usuario 11/10: la roja a Vinicius fue noticia mundial y no publicamos).
Lee redes/titulares.md (lo genera titulares.py cada 2 h en horario laboral europeo) y compara los temas que salen en
muchos medios con lo publicado en las últimas 48 h (redes/publicaciones.csv). Escribe redes/alertas.md."""
import csv, re
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UMBRAL = 7  # nº de medios distintos para considerarla noticia grande
filas = []
for l in (ROOT / "redes/titulares.md").read_text().splitlines():
    p = [x.strip() for x in l.strip().strip("|").split("|")]
    if len(p) >= 4 and p[1].isdigit():
        filas.append((p[0], int(p[1]), p[3]))
desde = (datetime.now(timezone.utc) + timedelta(hours=2) - timedelta(hours=48)).strftime("%Y-%m-%d")
pub = ""
try:
    for r in csv.reader((ROOT / "redes/publicaciones.csv").open(encoding="utf-8")):
        if r and r[0] >= desde:
            pub += " " + " ".join(r[1:3]).lower() + " " + (r[-2] if len(r) > 2 else "").lower()
except Exception:
    pass
sin, con = [], []
for tema, n, ej in filas:
    if n < UMBRAL:
        continue
    (con if tema.lower() in pub else sin).append((tema, n, ej))
ahora = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
out = [f"# Alertas de noticias ({ahora})", "",
       f"Temas en >= {UMBRAL} medios. La rutina diaria y cualquier sesión deben mirar esto ANTES de elegir tema (regla 6: la noticia que todos comentan va primero).", "",
       "## Grandes SIN publicar en las últimas 48 h (hacer post si pasa el listón: nada repetido, foto del momento)", ""]
out += [f"- **{t}** ({n} medios): {e}" for t, n, e in sin] or ["- (ninguna)"]
out += ["", "## Grandes ya cubiertas", ""] + ([f"- {t} ({n}): {e}" for t, n, e in con] or ["- (ninguna)"])
(ROOT / "redes/alertas.md").write_text("\n".join(out) + "\n")
print(f"alertas: {len(sin)} sin cubrir, {len(con)} cubiertas")
