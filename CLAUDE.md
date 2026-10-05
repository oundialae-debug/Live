# Live

Personajes de IA que narran directos. El proyecto pone `escenas.json` (frases con el dato clave entre *asteriscos*); `narrador/guion.py` lo vuelve guion desbocado con SSML de Azure; `narrador/voz.py` hace un mp3 por escena (API en tiempo real, secretos `AZURE_SPEECH_KEY`/`AZURE_SPEECH_REGION`). Personajes en `personajes/*.json`.

## Notas compartidas
- 2026-10-05: creado para el directo de TikTok de futbol-pipeline (Blitz, en-US-DavisNeural). Repo Live. Hasta tener secretos aquí, la voz se generó con una copia en Text-to-audiobook (rama ccr-2cc251b2-00l5rc, `narrar-live.yml`).
