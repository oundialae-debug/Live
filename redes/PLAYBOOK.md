# 2yellow (@2yellowdata) — playbook diario de redes

Cuenta: TikTok + Instagram, contenido EN INGLÉS. Texto/hashtags: 5 hashtags, termina con "Data, not betting advice. 18+". Nada de vocabulario de apuestas en títulos (bookies, tips, odds).
Alcance: 5 grandes ligas europeas (NO Segunda). Nations League solo mientras no haya ligas.
Usuario: quiere respuestas MUY breves. Permiso permanente: se puede usar la API de Highlightly (si se agotan cuotas, webs externas). Sin partidos ese día = no se publica nada.

## Cada día (tarea "2yellow diario", ~07:46 Madrid)
1. MÉTRICAS: lee `publicaciones.csv`; para posts de >24 h sin métricas, `get_post includeMetrics:true` (Buffer) y rellena columnas. NO juzgues por un solo día: compara tendencias de varios días. **Los DOMINGOS** haz además la REVISIÓN SEMANAL: analiza toda la semana anterior (lun-dom) con `get_aggregated_post_metrics` y el CSV (por tipo de post, plantilla, pista, hora, liga, red) y escribe las conclusiones y los cambios decididos en `aprendizajes.md` bajo "Semana <fecha>". Actualiza `aprendizajes.md` (qué plantilla, música, hora, liga rinde más: views, likes, comentarios, shares, seguidores). Ajusta las reglas de abajo según los datos (tú decides). Cuenta de seguidores: `get_account`/`get_channel`.
2. PARTIDOS: del repo futbol-pipeline (datos en `data/` ; selecciones en `data/selecciones/`, ligas cuando empiecen; `registro_pronosticos.csv`). Elige los 2 mejores del día. Si no hay partidos → fin (no publicar nada).
3. PREVIO (por partido): generar con `python3 redes/plantillas/datos_selecciones.py pre <equipo> <fecha>` desde la raíz del repo (rama ccr-54cb5efb-9ua0d7; datos del disco; si faltan, API Highlightly o fuentes externas). Salen 6 PNG (pre1..pre6) en `redes/plantillas/salida/<fecha>_<local>_<visitante>/`.
   Publicar en la MEJOR hora del país de la liga, como mínimo 4 h antes del saque y nunca a menos de 20 min del saque. Usar `customScheduled` en Buffer (dueAt con offset; Buffer tarda ~5 min extra).
4. VÍDEO DEL DÍA: 2 tarjetas: ayer (`weekend_record`/post5) + hoy (`perfil_picks_hoy`; filtro cuota media ≥1.4, lo que más acierta el modelo). Publicar por la mañana (~09:30 Madrid).
5. POST-PARTIDO: al crear cada previo, crea una tarea puntual (`send_later`/create_trigger run_once) para saque+2h25 min (fin+30 min). Al ejecutarse: comprobar que acabó, actualizar datos, `datos_selecciones.py post <equipo> <fecha>` (5 PNG post1..post5), vídeo, `shareNow` en ambas redes.
6. REGISTRO: cada post publicado/programado → una fila en `publicaciones.csv` y commit+push a este repo (main).

## Montaje del vídeo — GitHub Actions (principal, nunca falla)
1. PNG → JPG (`ffmpeg -q:v 2`) a `media/` de este repo (oundialae-debug/live, público, rama main) con nombre único por día/partido.
2. Escribe `pedidos/<id>.json` (`{"id","images":["media/..jpg",...],"seconds","audio":"musica/<pista>.mp3","out":"videos/<id>.mp4"}`) y haz commit+push: se dispara el workflow `montar-video` (ffmpeg en GitHub, ~1 min) que genera `videos/<id>.mp4` (quita silencio inicial, normaliza si suena flojo, fade-out) y lo sube a main. Espera con `gh api repos/oundialae-debug/live/contents/videos/<id>.mp4` hasta que exista (haz `git pull`). Borra solos los vídeos de >14 días.
3. URL para Buffer: `https://raw.githubusercontent.com/oundialae-debug/live/main/videos/<id>.mp4` (probado: Buffer la acepta como `assets:[{video:{url}}]`).
4. Segundos por imagen: previo 6 tarjetas de 2.3 s en orden 2,3,4,5,1,6; post-partido 5 tarjetas de 2.8 s; diario 2 tarjetas de 4.5 s (duración total ≤ pista; pistas de 15 s).
5. Música: ya están en `musica/<id>.mp3` los 10 ids de `biblioteca_musica.json` (boom, rage, techno, mtrap, drill, electro, trapdark, phonk, anthem, techhouse). Pistas NUEVAS: generar en ElevenLabs, pedir URL fresca (`creative_get_flow_run_status`) y subir `descargas/<fecha>.json` con `{"files":{"nombre.mp3":"<url>"}}` + push: el workflow `bajar-musica` las descarga a `musica/` (el shell local no sale a internet; el runner de GitHub sí). Añádelas a `biblioteca_musica.json`. Si GitHub falla, plan B de Higgs.

## Plan B — Higgs (solo si GitHub falla o falta música)
`mcp__Higgs__media_upload` (video) → `sandbox_exec` (curl de JPG de raw.githubusercontent, pista con URL fresca de ElevenLabs, ffmpeg, PUT al upload_url con `-H "Content-Type: video/mp4" -H "If-None-Match: *"`) → `media_confirm` → URL CloudFront. Flujo ya probado.

## Publicación (Buffer)
- Instagram: `metadata.instagram {type:"reel", shouldShareToFeed:true}`. TikTok: `metadata.tiktok {title}`. Canales: IG 6ac3c8166a5c39ccb620dd8a, TikTok 6ac3c8456a5c39ccb620dec4. Posts publicados NO se pueden borrar desde Buffer. Borradores (`saveToDraft`) sí.
- El shell local no sale a internet salvo GitHub (gh/git). ElevenLabs: URLs frescas con `creative_get_flow_run_status(flow, session)`; música nueva con `creative_generate_in_flow` (node music, eleven_music_v2_5, 15 s, sin voz, ~0,09 $, máx. ~6 seguidas).

## Reglas aprendidas
- Hoy 05/10: Buffer ya publicó test; los posts tardan ~5 min en pasar de "sending" a "sent".
- Los previos nunca a <20 min del saque ni tras el final.
- Último 30 días antes de empezar: 11 posts, 2.303 views, 0,53 % engagement, 0 shares → pedir interacción (pregunta final) y gancho con dato en el primer segundo.

## MODELO DE APRENDIZAJE (obligatorio desde 2026-10-05)
- ANTES de montar cada vídeo: `python3 scripts/aprender.py elegir pre|post|daily` → JSON con la variante (primera carta, segundos por carta `seg`, música `arranque` s0/s1 → `audio_delay` 0/1 en el pedido, `hook` de la descripción: dato/pregunta/reto, antelación `ante` en h, pista `musica`). Úsala tal cual (explora al principio, luego explota lo que mejor rinde). Si no puedes ejecutarlo, elige al azar entre opciones poco probadas.
- Primera carta: pred=pre1, upset=pre2, key=pre5, goals=pre3; el resto va detrás en el orden habitual y pre6 (lista) siempre última. Post y daily: ignora `primera`.
- Guarda la cadena `variante` en la columna `variante` de `publicaciones.csv` (una fila por red).
- Con métricas (>24 h): rellena columnas y ejecuta `python3 scripts/aprender.py aprender` (actualiza `redes/modelo_estado.json`, imprime medias por opción). Los domingos copia ese informe a `aprendizajes.md`. Cada ~2 semanas añade variables nuevas en `BRAZOS` si ves algo que probar (sticker, texto de portada, duración…).
- MIGRACIÓN DEL MODELO: cuando `publicaciones.csv` tenga ≥100 observaciones con métricas, sustituye el bandido por una regresión bayesiana/ridge sobre la recompensa (efectos principales + interacciones música×primera carta, hora×liga, red) y contexto (liga, día, red). Mantén el mismo registro y las mismas columnas; compara ambos en `aprendizajes.md` antes de cambiar.

## CONTENIDO EXTRA DIARIO: 2 memes + 1 dato curioso (desde 2026-10-05; se suma a todo lo anterior)
Pedido del usuario: cada día, además de previos/post-partido/vídeo del día, 3 posts por red SIN datos del modelo, estilo carrusel de imágenes (inspirado en FotMob: lo que mejor les rindió fueron memes/emoción, no pantallazos de datos):
- MEME 1 y MEME 2: carrusel de 2-3 cartas (el nº lo decide `aprender.py elegir meme`, variable `cartas`). Una idea por carta, texto muy corto, gancho en la 1ª. Mezcla ingenio propio con formatos que circulan (POV, "me: / also me:", expectativa vs realidad), siempre en inglés, humor futbolero reconocible. Los 2 memes del día con formatos distintos.
- DATO CURIOSO: 1 sola imagen (carta `fact`, número grande + frase). Sácalo de fuentes REALES recientes (WebSearch/WebFetch: webs de federaciones, UEFA, FBref/Opta Analyst, prensa); verifica el dato en la fuente antes de publicar y pon `source` en la carta. Si no puedes verificarlo, no lo publiques y usa otro. (Reddit y X están bloqueados desde aquí: no insistas.)
- Reglas: sin vocabulario de apuestas; sin fotos con derechos ni capturas de películas/series/memes ajenos (nada de plantillas con imágenes de terceros); sin ataques a personas reales ni burlas a lesionados; no inventes citas de personas reales. Vale texto + colores de la marca. Fotos solo de Wikimedia Commons (CC BY-SA, atribución en la descripción) y solo cuando esté montado ese flujo.
- Generar: JSON `{"id":"<fecha>_meme1","cards":[{"kind":"meme|fact","kicker","text","sub","big","source"}]}` → `python3 scripts/cartas_extra.py pedido.json` (en el repo Live; deja JPG 1080x1350 en `media/<id>_N.jpg`) → push → URLs raw.
- Publicar en Buffer con imágenes (no vídeo): `assets` = varias `image` (carrusel) o una. IG: `metadata.instagram {type:"post", shouldShareToFeed:true}`; TikTok: `metadata.tiktok {title}` (modo foto). Hora Madrid: la que dé `aprender.py elegir meme|curioso` (variable `hora`: 12/17/21), `customScheduled`; evita pisar un previo a la misma hora (mueve 30 min).
- Descripción en inglés + 5 hashtags SEO; el meme no necesita "Data, not betting advice" pero el curioso sí lleva la fuente.
- Registro: `publicaciones.csv` con tipo `meme` o `curioso`, `variante` con `hook=`, `cartas=`, `hora=`. En la revisión semanal compara meme vs curioso vs previos/post por vistas, interacciones y seguidores, y reparte la frecuencia según resultados.
- Primera semana: pon los 3 posts en BORRADOR cada día? NO — publica directo, pero cuéntale al usuario el contenido en su resumen para que pueda objetar el humor.
