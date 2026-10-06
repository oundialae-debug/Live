"""Cola de publicaciones: Buffer solo guarda lo de los próximos minutos (límite de programados del plan gratis).
Cada post es un JSON en redes/cola/ (ver redes/cola/LEEME.md). El workflow enviar-cola lo ejecuta cada 10 min:
lo que toca en <= VENTANA min se manda a Buffer con customScheduled a su hora (o ahora+3 min si va tarde),
se apunta en publicaciones.csv y se mueve a redes/cola/enviados/. Uso: python3 scripts/enviar_cola.py [--prueba]"""
import csv, json, os, sys, urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT, MAD = Path(__file__).resolve().parents[1], ZoneInfo("Europe/Madrid")
COLA, HECHOS, LOG = ROOT / "redes/cola", ROOT / "redes/cola/enviados", ROOT / "redes/publicaciones.csv"
CANAL = {"instagram": "6ac3c8166a5c39ccb620dd8a", "tiktok": "6ac3c8456a5c39ccb620dec4"}
VENTANA, CADUCA = 25, 120  # min: se manda si toca en <=25 min; si lleva >2 h de retraso, se descarta
Q = "mutation($i:CreatePostInput!){createPost(input:$i){__typename ... on PostActionSuccess{post{id}} ... on MutationError{message}}}"

def gql(q, v):
    rq = urllib.request.Request(os.environ.get("BUFFER_URL", "https://api.buffer.com"),
                                json.dumps({"query": q, "variables": v}).encode(),
                                {"Content-Type": "application/json", "Authorization": "Bearer " + os.environ["BUFFER_API_KEY"]})
    return json.load(urllib.request.urlopen(rq, timeout=60))

def entrada(x, due):
    video = "video" in x
    if x["red"] == "instagram":
        tipo = "reel" if video else ("carousel" if len(x.get("imagenes", [])) > 1 else "post")
        meta = {"instagram": {"type": tipo, "shouldShareToFeed": True}}
        # primer comentario: NO, Buffer lo reserva al plan de pago ("First comment requires a paid plan", 06/10)
    else:
        meta = {"tiktok": {"title": x.get("titulo", x["text"].split("\n")[0])[:90]}}
    assets = [{"video": {"url": x["video"]}}] if video else [{"image": {"url": u}} for u in x["imagenes"]]
    return {"channelId": CANAL[x["red"]], "text": x["text"], "assets": assets, "metadata": meta, "mode": "customScheduled",
            "dueAt": due.isoformat(timespec="seconds"),
            "schedulingType": "notification" if x.get("recordatorio", not video) else "automatic"}

def main(prueba=False):
    ahora = datetime.now(timezone.utc)
    for p in sorted(COLA.glob("*.json")):
        x = json.loads(p.read_text())
        hora = datetime.fromisoformat(x["hora"])
        if hora.tzinfo is None: hora = hora.replace(tzinfo=MAD)
        falta = (hora - ahora).total_seconds() / 60
        if falta > VENTANA: continue
        destino = HECHOS / p.name
        if falta < -CADUCA:
            print("CADUCADO", p.name); x["estado"] = "caducado"
            destino.write_text(json.dumps(x, ensure_ascii=False, indent=1)); p.unlink(); continue
        due = max(hora, ahora + timedelta(minutes=3))
        i = entrada(x, due)
        if prueba: print(p.name, json.dumps(i, ensure_ascii=False)[:300]); continue
        r = gql(Q, {"i": i}); print(p.name, json.dumps(r)[:200])
        d = (r.get("data") or {}).get("createPost") or {}
        if d.get("__typename") != "PostActionSuccess": continue  # se reintenta en la próxima pasada
        x.update(estado="enviado", buffer_id=d["post"]["id"], dueAt=i["dueAt"])
        destino.write_text(json.dumps(x, ensure_ascii=False, indent=1)); p.unlink()
        with open(LOG, "a", newline="") as f:
            csv.writer(f).writerow([due.astimezone(MAD).date(), x.get("tipo", ""), x.get("partido", ""), x["red"], x["buffer_id"],
                                    due.astimezone(MAD).strftime("%Y-%m-%dT%H:%M"), x.get("musica", ""), x.get("plantillas", ""),
                                    "", "", "", "", "", "", x.get("notas", "") + " [cola]", x.get("variante", "")])

if __name__ == "__main__":
    if "--comprobar" in sys.argv:  # solo lee la cuenta: confirma que la clave funciona
        r = gql("{account{organizations{name channelCount limits{scheduledPosts}}}}", {})
        print(json.dumps(r)[:400]); sys.exit(0 if (r.get("data") or {}).get("account") else 1)
    main("--prueba" in sys.argv)
