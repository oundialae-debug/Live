#!/usr/bin/env python3
"""Prueba SIN RED de scripts/post_partido_live.py (sin git, sin Buffer, sin API).
Necesita un checkout de futbol-pipeline con sus datos (FP_REAL, por defecto ../futbol-pipeline) y playwright + ffmpeg.
Marcas falsas en una copia temporal:
  - 999000001 Real Madrid - Villarreal (datos reales del 10/10) "datos_listos"  -> se publica
  - 999000002 Borussia Dortmund - Werder Bremen (09/10) "datos_listos"          -> se publica
  - 1336420545 Real Madrid - Villarreal "datos_listos" (ya publicado a mano)     -> el registro lo impide
  - 1340476411 RB Leipzig - Frankfurt "abandonado"                              -> se ignora
  - 999000003 "datos_listos" de hace días                                       -> caducado, sin cola
Comprueba: 6 imágenes (5 + lista) dentro de x 80-880, y 318-1540; vídeo de 6 x 2.8 s; 2 JSON de cola (TikTok + IG)
con vídeo automático; y que una segunda pasada no repite nada.
Uso: python3 scripts/prueba_post_partido_live.py"""
import json, os, re, shutil, subprocess, sys, tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

LIVE = Path(__file__).resolve().parents[1]
FP_REAL = Path(os.environ.get("FP_REAL", LIVE.parent / "futbol-pipeline")).resolve()
ok = True


def check(c, txt):
    global ok
    print(("OK   " if c else "FALLO") + " " + txt)
    ok &= bool(c)


def marca(d, mid, local, vis, liga, fecha, saque, estado="datos_listos", res="1-0"):
    (d / f"{mid}.json").write_text(json.dumps({"match_id": mid, "local": local, "visitante": vis, "liga": liga,
                                               "fecha": fecha, "saque_utc": saque, "estado": estado, "resultado": res}))


def duracion(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True)
    return float(r.stdout.strip() or 0)


with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    live, fp = tmp / "live", tmp / "fp"
    (live / "redes/cola").mkdir(parents=True)
    for f in ("redes/biblioteca_musica.json", "redes/publicaciones.csv", "redes/post_partido_hechos.json"):
        shutil.copy(LIVE / f, live / f)
    shutil.copytree(LIVE / "musica", live / "musica")
    marcas = fp / "data/redes/post_partido"
    marcas.mkdir(parents=True)
    (fp / "redes").symlink_to(FP_REAL / "redes")        # datos_clubes.py lee los datos del checkout real (git show origin/main)
    marca(marcas, 999000001, "Real Madrid", "Villarreal", "La Liga", "2026-10-10", "2026-10-10T19:00:00+00:00")
    marca(marcas, 999000002, "Borussia Dortmund", "Werder Bremen", "Bundesliga", "2026-10-09", "2026-10-09T18:30:00+00:00", res="2-2")
    marca(marcas, 1336420545, "Real Madrid", "Villarreal", "La Liga", "2026-10-10", "2026-10-10T19:00:00+00:00")
    marca(marcas, 1340476411, "RB Leipzig", "Eintracht Frankfurt", "Bundesliga", "2026-10-10", "2026-10-10T16:30:00+00:00", "abandonado")
    marca(marcas, 999000003, "Malaga", "Espanyol", "La Liga", "2026-10-09", "2026-10-09T19:00:00+00:00", res="1-1")
    # 999000002 (Dortmund, 09/10) también estaría caducado a esta hora: se le pone el saque "de hoy" para la prueba
    m2 = json.loads((marcas / "999000002.json").read_text())
    m2["saque_utc"] = "2026-10-10T18:30:00+00:00"
    (marcas / "999000002.json").write_text(json.dumps(m2))

    env = {**os.environ, "LIVE_ROOT": str(live), "FP_DIR": str(fp), "PP_GIT": "0", "PP_RED": "0",
           "AHORA": "2026-10-10T21:00:00+00:00"}

    def correr(*a):
        r = subprocess.run([sys.executable, str(LIVE / "scripts/post_partido_live.py"), *a], env=env,
                           capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr

    gh = tmp / "gh_out"
    env["GITHUB_OUTPUT"] = str(gh)
    c, txt = correr("hay")
    check(c == 0 and "hay=si" in gh.read_text(), "hay: hay marcas datos_listos pendientes")
    c, txt = correr()
    print(txt[-1500:] if c else "\n".join(l for l in txt.splitlines() if "->" in l))
    check(c == 0, "la pasada termina sin error")
    h = json.loads((live / "redes/post_partido_hechos.json").read_text())["partidos"]
    check(h["999000001"]["estado"] == "en_cola" and h["999000002"]["estado"] == "en_cola", "los dos nuevos, en cola")
    check(h["999000003"]["estado"] == "caducado", "el de hace días: caducado")
    check(h["1336420545"]["estado"] == "publicado_manual" and h["1340476411"]["estado"] == "abandonado",
          "Real Madrid-Villarreal (manual) y Leipzig (abandonado) intactos")

    for mid, carpeta, slug in ((999000001, "2026-10-10_Real_Madrid_Villarreal", "2026-10-10_Real_Madrid_Villarreal"),
                               (999000002, "2026-10-09_Borussia_Dortmund_Werder_Bremen", "2026-10-09_Borussia_Dortmund_Werder_Bremen")):
        pngs = sorted((FP_REAL / "redes/plantillas/salida" / carpeta).glob("post*.png"))
        check(len(pngs) == 6 and pngs[-1].name == "post6_lista.png", f"{mid}: 6 imágenes ({', '.join(p.stem for p in pngs)})")
        v = live / "media/post_partido" / f"{slug}.mp4"
        check(v.exists() and abs(duracion(v) - 16.8) < 0.3, f"{mid}: vídeo {duracion(v) if v.exists() else 0:.1f} s (6 x 2.8)")
        colas = sorted((live / "redes/cola").glob(f"*_post_{slug}_*.json"))
        check([json.loads(p.read_text())["red"] for p in colas] == ["instagram", "tiktok"], f"{mid}: 2 JSON de cola")
        for p in colas:
            x = json.loads(p.read_text())
            hora = datetime.fromisoformat(x["hora"])
            t = x["text"]
            check(x["video"] == f"https://raw.githubusercontent.com/oundialae-debug/live/main/media/post_partido/{slug}.mp4"
                  and x["tipo"] == "post" and x["recordatorio"] is False and "musica=" in x["variante"]
                  and abs((hora - max(datetime(2026, 10, 10, 21, 0, tzinfo=timezone.utc), datetime.now(timezone.utc))
                           - timedelta(minutes=3)).total_seconds()) < 300     # ahora + 3 min
                  and len(re.findall(r"#\w+", t)) == 5 and "?" in t and "xG" not in ""
                  and not re.search(r"\b(bet|betting|odds|tip|tips)\b|not betting advice", t, re.I)
                  and "firstComment" not in x and ("titulo" in x) == (x["red"] == "tiktok"),
                  f"{p.name}: {t.splitlines()[0]} | {t.splitlines()[1]}")
        sys.path.insert(0, str(LIVE / "scripts"))
        import enviar_cola
        e = enviar_cola.entrada(json.loads(colas[0].read_text()), datetime.now(timezone.utc) + timedelta(minutes=3))
        check(e["schedulingType"] == "automatic" and e["metadata"]["instagram"]["type"] == "reel",
              "enviar_cola: IG reel automático")

    # zona segura, con las imágenes ya dibujadas: se vuelve a medir con generar.py
    sys.path.insert(0, str(FP_REAL / "redes/plantillas"))
    os.environ["LIENZO"] = "reel"
    import generar as G
    trab = []
    for carpeta in ("2026-10-10_Real_Madrid_Villarreal", "2026-10-09_Borussia_Dortmund_Werder_Bremen"):
        for j in sorted((FP_REAL / "redes/plantillas/salida" / carpeta).glob("post*.json")):
            trab.append((json.loads(j.read_text()), tmp / f"{carpeta}_{j.stem}.png"))
    G.renderizar(trab)
    check(len(trab) == 12 and not G.FUERA, f"zona segura x 80-880, y 318-1540: {len(G.FUERA)} fuera {G.FUERA[:3]}")

    n_cola = len(list((live / "redes/cola").glob("*.json")))
    gh.write_text("")
    c, _ = correr("hay")
    check("hay=no" in gh.read_text(), "segunda pasada: nada pendiente")
    c, txt = correr()
    check(c == 0 and len(list((live / "redes/cola").glob("*.json"))) == n_cola, "segunda pasada: no repite (misma cola)")

print("\nTODO BIEN" if ok else "\nHAY FALLOS")
sys.exit(0 if ok else 1)
