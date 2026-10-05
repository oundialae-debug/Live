# narrador-live

Personajes ficticios (IA) que narran directos con voz de Azure. El proyecto que lo usa
pone los datos y este repo pone la forma de hablar.

## Cómo funciona

1. El proyecto escribe un `escenas.json`: escenas con frases en inglés. El dato clave va
   entre `*asteriscos*` (ver `ejemplos/escenas.json`).
2. `narrador/guion.py` convierte cada escena en un guion desbocado: trocea frases, mete
   interjecciones, grita o repite el dato clave, lo anuncia con suspense, susurra
   "secretos" y rellena hasta la duración pedida (`objetivo_s`). Cada fragmento lleva su
   estilo de Azure (`excited`, `shouting`, `whispering`, `cheerful`), velocidad, tono,
   pausa y la palabra que la web hace saltar en pantalla (`pop`).
3. `narrador/voz.py` sintetiza un mp3 por escena con la API de Azure Speech en tiempo
   real y apunta la duración real en el guion.

```
python3 narrador/guion.py escenas.json --personaje personajes/blitz.json --salida guion.json
AZURE_SPEECH_KEY=... AZURE_SPEECH_REGION=... python3 narrador/voz.py guion.json --carpeta audio
```

Otra `--semilla` da otro guion con los mismos datos.

## Personajes

- `personajes/blitz.json`: **Blitz**, una tarjeta amarilla parlante obsesionada con los
  números. Voz `en-US-DavisNeural`. Para crear otro, copia el JSON y cambia la voz, los
  estilos y las listas de muletillas.

## Desde otro repo

`.github/workflows/narrar.yml` se lanza a mano con la URL pública de un `escenas.json`, o
se llama como workflow reutilizable. Necesita los secretos `AZURE_SPEECH_KEY` y
`AZURE_SPEECH_REGION` en el repo que lo ejecuta. Deja `guion.json` y los mp3 en el
artefacto `narracion`.

Primer uso: directo de TikTok de la Nations League (`futbol-pipeline/web/live/`).
