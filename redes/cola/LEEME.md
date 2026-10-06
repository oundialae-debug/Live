# Cola de publicaciones (Buffer solo ve lo de los próximos minutos)
Un JSON por post y red. El workflow `enviar-cola` (cada 10 min) lo manda a Buffer ~25 min antes de su hora, a esa hora exacta (o ahora+3 min si GitHub va tarde; >2 h tarde = caducado). Luego queda en `enviados/` y en `publicaciones.csv` (notas "[cola]").
```json
{"red": "tiktok", "hora": "2026-10-07T12:00:00+02:00", "tipo": "meme", "partido": "tema",
 "text": "Texto + 5 hashtags", "titulo": "TikTok ≤90 car.", "imagenes": ["https://...jpg"],
 "variante": "hook=...;hora=12", "notas": ""}
```
- Imágenes (meme/curioso) → modo recordatorio (`notification`). Con `"video": "https://raw.githubusercontent.com/.../videos/x.mp4"` → automático (previos). Se puede forzar con `"recordatorio": true|false`.
- URL de imagen: CloudFront de Higgs o `https://raw.githubusercontent.com/oundialae-debug/live/main/media/<x>.jpg`.
