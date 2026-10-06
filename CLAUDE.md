# Live

Personajes de IA que narran directos. El proyecto pone `escenas.json` (frases con el dato clave entre *asteriscos*); `narrador/guion.py` lo vuelve guion desbocado con SSML de Azure; `narrador/voz.py` hace un mp3 por escena (API en tiempo real, secretos `AZURE_SPEECH_KEY`/`AZURE_SPEECH_REGION`). Personajes en `personajes/*.json`.

## Notas compartidas
- 2026-10-05: creado para el directo de TikTok de futbol-pipeline (Blitz, en-US-DavisNeural). Repo Live. Hasta tener secretos aquí, la voz se generó con una copia en Text-to-audiobook (rama ccr-2cc251b2-00l5rc, `narrar-live.yml`).
- 2026-10-05: DavisNeural con estilos y frases troceadas sonaba muy robótica (queja del usuario). Ahora Andrew DragonHD por Batch Synthesis, frases enteras, máx. un relleno por cada 3 frases.

## Redes 2yellow (@2yellowdata, TikTok + Instagram) — LEER PRIMERO si el chat va de redes
Todo el sistema de publicación automática vive en este repo. Antes de tocar nada lee, en este orden:
0. `redes/CONTEXTO_CONVERSACION.md` — resumen de la conversación que creó todo (preferencias, decisiones, rechazos, incidentes). PRIMERO.
1. `redes/PLAYBOOK.md` — manual completo (previos, post-partido, vídeo del día, memes/curiosos en modo recordatorio, anti-retraso, Buffer, canales).
2. `redes/diario_creativo.md` — lo aprendido de memes y percepción (reglas del usuario).
3. `redes/aprendizajes.md` y `redes/publicaciones.csv` — métricas, incidentes y registro de cada post.
4. `scripts/aprender.py` (bandido que elige variantes), `scripts/montar_video.py` + workflow `montar-video`, `scripts/foto_meme.py` (memes con foto de Commons, sandbox de Higgs).
Tareas programadas: "2yellow diario" (07:46 Madrid, trig_016KxjMVXAwtFVbDiYKTeJKG) crea los previos, el vídeo del día, los 3 extras y las tareas puntuales de post-partido. Datos y plantillas: repo oundialae-debug/futbol-pipeline (`redes/plantillas/`, respeta su CLAUDE.md). Usuario: respuestas muy breves en español; contenido en inglés; sin vocabulario de apuestas.
- Mantén al día redes/CONTEXTO_CONVERSACION.md con cada decisión nueva del usuario.
