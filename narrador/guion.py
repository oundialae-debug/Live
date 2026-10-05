"""Convierte las escenas de un proyecto en el guion desbocado del personaje.

Entrada (escenas.json, lo escribe el proyecto que usa al personaje):
    {"titulo": "...", "escenas": [
        {"id": "s01", "objetivo_s": 60, "abre": true,
         "frases": ["France against Belgium!", "France win *sixty-four percent* of the time."]},
        ...]}
  - Lo que va entre *asteriscos* es el dato clave: se grita, se repite o se
    anuncia con suspense, y sale en pantalla como palabra suelta ("pop").
  - objetivo_s: duración deseada; si las frases no llegan, se rellena con
    muletillas del personaje.
  - Cualquier otro campo de la escena se ignora aquí (es para la web).

Salida (guion.json): por escena, los fragmentos con estilo, pausa, pop y
segundo estimado de inicio, y el SSML listo para Azure.
"""
import argparse
import json
import random
import re
import xml.sax.saxutils as saxutils

ENFASIS = re.compile(r"\*([^*]+)\*")


class Narrador:
    def __init__(self, personaje, semilla):
        self.p = personaje
        self.rnd = random.Random(semilla)
        self.usados = {}

    def elegir(self, clave):
        """Elemento al azar de una lista del personaje, sin repetir hasta agotarla."""
        lista = self.p[clave]
        pend = [x for x in lista if x not in self.usados.setdefault(clave, set())]
        if not pend:
            self.usados[clave] = set()
            pend = list(lista)
        x = self.rnd.choice(pend)
        self.usados[clave].add(x)
        return x

    def frag(self, texto, estilo="normal", pausa="fragmento", pop=None):
        p = self.p
        return {
            "texto": texto.strip(),
            "estilo": p["estilos"][estilo],
            "rate": self.rnd.choice(p["prosodia"]["rate"]),
            "pitch": self.rnd.choice(p["prosodia"]["pitch"]),
            "pausa_ms": self.rnd.choice(p["pausas_ms"][pausa]),
            "pop": pop,
            "suspense": pausa == "suspense",
        }

    def trocear(self, frase):
        """Una frase del proyecto -> fragmentos cortos con énfasis y suspense."""
        prob = self.p["probabilidades"]
        out = []
        if self.rnd.random() < prob["interjeccion"]:
            i = self.elegir("interjecciones")
            out.append(self.frag(i, pop=i.rstrip(".!").upper() if len(i) < 12 else None))
        if self.rnd.random() < prob["secreto"]:
            out.append(self.frag(self.elegir("secretos"), "secreto", "suspense"))
        if self.p.get("hd"):
            trozos = [frase]
        else:
            trozos = [t for t in re.split(r"(?<=[,;:—])\s+", frase) if t.strip()]
        for t in trozos:
            m = ENFASIS.search(t)
            if not m:
                out.append(self.frag(t))
                continue
            antes, clave, despues = t[:m.start()], m.group(1), t[m.end():]
            hay_suspense = self.rnd.random() < prob["suspense"]
            if hay_suspense and self.p.get("hd"):
                # Voz HD: el suspense va antes de la frase entera, sin partirla
                out.append(self.frag(self.elegir("suspense"), "secreto", "suspense"))
                out.append(self.frag(antes + clave + despues, pop=clave))
            elif hay_suspense:
                if antes.strip():
                    out.append(self.frag(antes, pausa="fragmento"))
                out.append(self.frag(self.elegir("suspense"), "secreto", "suspense"))
                out.append(self.frag(clave + "!", "enfasis", pop=clave))
                if despues.strip(" .,;:!?"):
                    out.append(self.frag(despues))
            else:
                out.append(self.frag(antes + clave + despues, pop=clave))
                if self.rnd.random() < prob["repetir_enfasis"]:
                    out.append(self.frag(clave.capitalize() + "!", "enfasis", pop=clave))
            if self.rnd.random() < 0.35:
                out.append(self.frag(self.elegir("reacciones"), "alegre"))
        out[-1]["pausa_ms"] = self.rnd.choice(self.p["pausas_ms"]["frase"])
        return out

    def duracion(self, frags):
        pps = self.p["palabras_por_segundo"]
        t = 0.0
        for f in frags:
            f["inicio_est_s"] = round(t, 2)
            rate = 1 + int(f["rate"].strip("%+")) / 100
            t += len(f["texto"].split()) / (pps * rate) + f["pausa_ms"] / 1000
        return t

    def escena(self, esc):
        # Grupos = una frase del proyecto cada uno; el relleno solo entra entre grupos,
        # nunca en mitad de una frase.
        grupos = []
        if not esc.get("abre") and self.rnd.random() < 0.7:
            grupos.append([self.frag(self.elegir("transiciones"), pausa="frase")])
        for frase in esc["frases"]:
            grupos.append(self.trocear(frase))
        plano = lambda: [f for g in grupos for f in g]
        objetivo = esc.get("objetivo_s", 0) * 0.92
        guarda = 0
        relleno = set()
        # Como mucho un relleno por cada tres frases: más suena a disco rayado.
        tope = max(1, len(esc["frases"]) // 3)
        while self.duracion(plano()) < objetivo and guarda < tope:
            guarda += 1
            # Nunca dos rellenos seguidos: solo huecos sin relleno a ningún lado.
            huecos = [i for i in range(1, len(grupos) + 1)
                      if id(grupos[i - 1]) not in relleno and (i == len(grupos) or id(grupos[i]) not in relleno)]
            if not huecos:
                break
            clave = self.rnd.choice(["rellenos", "rellenos", "reacciones"])
            g = [self.frag(self.elegir(clave), "alegre", "frase")]
            relleno.add(id(g))
            grupos.insert(self.rnd.choice(huecos), g)
        frags = plano()
        est = self.duracion(frags)
        return {"id": esc["id"], "fragmentos": frags, "estimado_s": round(est, 1),
                "ssml": ssml(frags, self.p)}


def ssml_hd(frags, p):
    """Voces DragonHD: texto corrido, la emoción la saca el modelo del propio texto.
    La pausa larga (suspense) se marca con puntos suspensivos."""
    partes = []
    for f in frags:
        t = f["texto"].replace("*", "").strip()
        if f.get("suspense") and not t.endswith(("...", "?", "!")):
            t = t.rstrip(".,;:") + "..."
        partes.append(t)
    texto = saxutils.escape(" ".join(partes))
    params = f' parameters="{p["parametros_hd"]}"' if p.get("parametros_hd") else ""
    return ('<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" '
            f'xml:lang="{p["idioma"]}"><voice name="{p["voz"]}"{params}>{texto}</voice></speak>')


def ssml(frags, p):
    if p.get("hd"):
        return ssml_hd(frags, p)
    partes = []
    for f in frags:
        texto = saxutils.escape(f["texto"].replace("*", ""))
        partes.append(f'<mstts:express-as style="{f["estilo"]}"><prosody rate="{f["rate"]}" pitch="{f["pitch"]}">'
                      f'{texto}</prosody></mstts:express-as><break time="{f["pausa_ms"]}ms"/>')
    return ('<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" '
            f'xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="{p["idioma"]}">'
            f'<voice name="{p["voz"]}">' + "".join(partes) + "</voice></speak>")


def generar(escenas, personaje, semilla=7):
    n = Narrador(personaje, semilla)
    salida = [n.escena(e) for e in escenas["escenas"]]
    return {"titulo": escenas.get("titulo", ""), "personaje": personaje["nombre"], "voz": personaje["voz"],
            "estimado_total_s": round(sum(e["estimado_s"] for e in salida), 1), "escenas": salida}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("escenas")
    ap.add_argument("--personaje", default="personajes/blitz.json")
    ap.add_argument("--salida", default="guion.json")
    ap.add_argument("--semilla", type=int, default=7)
    a = ap.parse_args()
    g = generar(json.load(open(a.escenas, encoding="utf-8")),
                json.load(open(a.personaje, encoding="utf-8")), a.semilla)
    json.dump(g, open(a.salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    caracteres = sum(len(f["texto"]) for e in g["escenas"] for f in e["fragmentos"])
    print(f"{len(g['escenas'])} escenas, ~{g['estimado_total_s'] / 60:.1f} min estimados, "
          f"{caracteres} caracteres de texto -> {a.salida}")


if __name__ == "__main__":
    main()
