#!/usr/bin/env python3
"""Modelo de aprendizaje de 2yellow: bandido Thompson (Beta) por variable.
  python3 scripts/aprender.py elegir pre|post|daily   -> JSON con la variante a usar (explora/explota solo)
  python3 scripts/aprender.py aprender                -> relee publicaciones.csv, actualiza redes/modelo_estado.json e imprime informe
Cada fila del CSV con métricas y columna `variante` ("primera=pred;seg=2.3;arranque=s0;hook=dato;ante=4;musica=hh03") es una observación.
Recompensa 0-1 = 0.5*min(1,interacciones/vistas/0.05) + 0.5*min(1,vistas/(2*mediana de vistas)). Interacciones = likes+2*coment+3*shares+3*guardados+10*seguidores."""
import csv, json, random, statistics, sys
from pathlib import Path
R = Path(__file__).resolve().parent.parent / "redes"
CSV, EST, BIB = R / "publicaciones.csv", R / "modelo_estado.json", R / "biblioteca_musica.json"
BRAZOS = {  # variable -> opciones (musica sale de la biblioteca)
    "primera": ["pred", "upset", "key", "goals"],  # qué carta va primero en el previo (solo pre)
    "seg": ["1.8", "2.3", "2.8"],                  # segundos por carta
    "arranque": ["s0", "s1"],                      # música desde el seg 0 o desde el 1
    "hook": ["dato", "pregunta", "reto"],          # estilo de la primera frase de la descripción
    "ante": ["4", "5", "6"],                       # horas de antelación del previo (solo pre)
    "cartas": ["2", "3"],                          # nº de cartas del carrusel meme (solo meme)
    "hora": ["12", "17", "21"],                    # hora Madrid de los posts extra (meme/curioso)
}
SOLO_PRE = {"primera", "ante"}
SOLO_MEME, SOLO_EXTRA = {"cartas"}, {"cartas", "hora"}  # meme/curioso: solo hook, cartas (meme) y hora; sin música ni seg
def musica(): return [t["id"] for t in json.loads(BIB.read_text())["pistas"]]
def f(x):
    try: return float(x)
    except: return 0.0
def leer():
    filas = [r for r in csv.DictReader(open(CSV)) if r.get("variante") and r.get("views")]
    med = statistics.median([f(r["views"]) for r in filas]) if filas else 1
    obs = []
    for r in filas:
        v = max(f(r["views"]), 1)
        inter = f(r["likes"]) + 2*f(r["comentarios"]) + 3*f(r["shares"]) + 3*f(r["guardados"]) + 10*f(r["seguidores_nuevos"])
        rew = 0.5*min(1, inter/v/0.05) + 0.5*min(1, v/max(2*med, 1))
        obs.append((r["tipo"], dict(kv.split("=") for kv in r["variante"].split(";")), rew))
    return obs
def posterior(obs):
    est = {}
    for tipo, var, rew in obs:
        for k, val in var.items():
            e = est.setdefault(k, {}).setdefault(val, [1.0, 1.0, 0])  # Beta(1,1)
            e[0] += rew; e[1] += 1 - rew; e[2] += 1
    return est
def elegir(tipo):
    est = posterior(leer()); out = {}
    for k, ops in {**BRAZOS, "musica": musica()}.items():
        if tipo != "pre" and k in SOLO_PRE: continue
        if tipo in ("meme", "curioso"):
            if k not in ("hook", "hora") and not (k == "cartas" and tipo == "meme"): continue
        elif k in SOLO_EXTRA: continue
        if tipo == "daily" and k == "seg": ops = ["3.5", "4.5", "5.5"]  # 2 cartas con mucho texto: 1.8 s no da para leer (06/10 salió un vídeo de 3.6 s)
        e = est.get(k, {})
        # primero se prueba cada opción al menos 2 veces; luego Thompson
        pocas = [o for o in ops if e.get(o, [0, 0, 0])[2] < 2]
        if pocas: out[k] = random.choice(pocas)
        else: out[k] = max(ops, key=lambda o: random.betavariate(e[o][0], e[o][1]))
    out["variante"] = ";".join(f"{k}={v}" for k, v in out.items())
    return out
def informe():
    obs = leer(); est = posterior(obs); EST.write_text(json.dumps(est, indent=1))
    print(f"{len(obs)} observaciones")
    for k, d in est.items():
        print(f"\n{k}:")
        for o, (a, b, n) in sorted(d.items(), key=lambda x: -x[1][0]/(x[1][0]+x[1][1])):
            print(f"  {o:10s} n={n:<3d} media={a/(a+b):.2f}")
if __name__ == "__main__":
    c = sys.argv[1] if len(sys.argv) > 1 else "aprender"
    if c == "elegir": print(json.dumps(elegir(sys.argv[2] if len(sys.argv) > 2 else "pre")))
    else: informe()
