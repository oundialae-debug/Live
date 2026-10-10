# Cola de publicaciones (Buffer solo ve lo de los próximos minutos)
Un JSON por post y red. El workflow `enviar-cola` (cada 10 min) lo manda a Buffer ~25 min antes de su hora, a esa hora exacta (o ahora+3 min si GitHub va tarde; >2 h tarde = caducado). Luego queda en `enviados/` y en `publicaciones.csv` (notas "[cola]").
```json
{"red": "tiktok", "hora": "2026-10-07T12:00:00+02:00", "tipo": "meme", "partido": "tema",
 "text": "Texto + 5 hashtags", "titulo": "TikTok ≤90 car.", "imagenes": ["https://...jpg"],
 "variante": "hook=...;hora=12", "notas": ""}
```
- Imágenes (meme/curioso) → modo recordatorio (`notification`). Con `"video": "https://raw.githubusercontent.com/.../videos/x.mp4"` → automático (previos). Se puede forzar con `"recordatorio": true|false`.
- URL de imagen: CloudFront de Higgs o `https://raw.githubusercontent.com/oundialae-debug/live/main/media/<x>.jpg`.
- CARRUSEL (previo con `formato=carrusel`): `"imagenes": [6 URLs en orden]`. En IG va automático (`"recordatorio": false`, sale como carrusel sin música); en TikTok, recordatorio (el usuario pone la música, puede salir 1-4 h tarde) → la hora del carrusel debe ser ≥7 h antes del saque.
- Primer comentario: NO disponible (Buffer lo reserva al plan de pago). La pregunta va al final de la descripción.
- POST-PARTIDO AUTOMÁTICO (10/10): `scripts/post_partido_live.py` (paso previo de `enviar-cola`) escribe aquí `<fecha>_post_<partido>_{tiktok,instagram}.json` con `"video"` (automático) a ahora+3 min en cuanto futbol-pipeline marca el partido "datos_listos"; el mismo run los manda. No repite: `redes/post_partido_hechos.json`. Prueba sin red: `scripts/prueba_post_partido_live.py`.
