# 2yellow (@2yellowdata) — playbook diario de redes

Cuenta: TikTok + Instagram, contenido EN INGLÉS. Texto/hashtags: 5 hashtags, termina con "Data, not betting advice. 18+". Nada de vocabulario de apuestas en títulos (bookies, tips, odds).
Alcance: 5 grandes ligas europeas (NO Segunda). Nations League solo mientras no haya ligas.
Usuario: quiere respuestas MUY breves. Permiso permanente: se puede usar la API de Highlightly (si se agotan cuotas, webs externas). Sin partidos ese día = no se publica nada.

## Cada día (tarea "2yellow diario", ~07:46 Madrid)
1. MÉTRICAS: lee `publicaciones.csv`; para posts de >24 h sin métricas, `get_post includeMetrics:true` (Buffer) y rellena columnas. Actualiza `aprendizajes.md` (qué plantilla, música, hora, liga rinde más: views, likes, comentarios, shares, seguidores). Ajusta las reglas de abajo según los datos (tú decides). Cuenta de seguidores: `get_account`/`get_channel`.
2. PARTIDOS: del repo futbol-pipeline (datos en `data/` ; selecciones en `data/selecciones/`, ligas cuando empiecen; `registro_pronosticos.csv`). Elige los 2 mejores del día. Si no hay partidos → fin (no publicar nada).
3. PREVIO (por partido): generar con `python3 redes/plantillas/datos_selecciones.py pre <equipo> <fecha>` desde la raíz del repo (rama ccr-54cb5efb-9ua0d7; datos del disco; si faltan, API Highlightly o fuentes externas). Salen 6 PNG (pre1..pre6) en `redes/plantillas/salida/<fecha>_<local>_<visitante>/`.
   Publicar en la MEJOR hora del país de la liga, como mínimo 4 h antes del saque y nunca a menos de 20 min del saque. Usar `customScheduled` en Buffer (dueAt con offset; Buffer tarda ~5 min extra).
4. VÍDEO DEL DÍA: 2 tarjetas: ayer (`weekend_record`/post5) + hoy (`perfil_picks_hoy`; filtro cuota media ≥1.4, lo que más acierta el modelo). Publicar por la mañana (~09:30 Madrid).
5. POST-PARTIDO: al crear cada previo, crea una tarea puntual (`send_later`/create_trigger run_once) para saque+2h25 min (fin+30 min). Al ejecutarse: comprobar que acabó, actualizar datos, `datos_selecciones.py post <equipo> <fecha>` (5 PNG post1..post5), vídeo, `shareNow` en ambas redes.
6. REGISTRO: cada post publicado/programado → una fila en `publicaciones.csv` y commit+push a este repo (main).

## Montaje del vídeo (probado)
- PNG → JPG (`ffmpeg -q:v 2`), copiar a `media/` de ESTE repo (oundialae-debug/live, público) y push. Buffer/Higgs leen `https://raw.githubusercontent.com/oundialae-debug/live/main/media/<f>.jpg`.
- Entorno shell local NO sale a internet (solo GitHub vía gh/git). `mcp__Higgs__sandbox_exec` SÍ (ffmpeg, curl).
- Flujo: `media_upload` (type video, content_type video/mp4) → `sandbox_exec` en UN solo comando: curl de los JPG y de la pista (URL fresca de ElevenLabs), ffmpeg, `curl -X PUT -H "Content-Type: video/mp4" -H "If-None-Match: *" --data-binary @out.mp4 '<upload_url>'` → `media_confirm` → URL CloudFront en Buffer.
- ffmpeg: previo = 6 tarjetas de 2.3 s en orden 2,3,4,5,1,6 (pista 13.8 s); post = 5 tarjetas 2.8 s; diario = 2 tarjetas 4.5 s. `concat` + `scale=1080:1920,fps=30,format=yuv420p`, audio `atrim` + `afade` out 0.5 s; quitar silencio inicial con `silenceremove=start_periods=1:start_threshold=-40dB`; si el volumen medio < -20 dB aplicar `loudnorm`. libx264 + aac, +faststart.
- Instagram: `metadata.instagram {type:"reel", shouldShareToFeed:true}`. TikTok: `metadata.tiktok {title}`. Buffer canales: IG 6ac3c8166a5c39ccb620dd8a, TikTok 6ac3c8456a5c39ccb620dec4. Los posts publicados NO se pueden borrar desde Buffer.
- Música: rotar pistas de `biblioteca_musica.json` y anotar la usada en el CSV para comparar. URLs frescas: `creative_get_flow_run_status` (flow + session_id). Si faltan pistas: `creative_generate_in_flow` (node music, eleven_music_v2_5, 15 s, hip hop/trap/electro, sin voz, ~0,09 $ cada una; máx. ~6 peticiones seguidas por límite).

## Reglas aprendidas
- Hoy 05/10: Buffer ya publicó test; los posts tardan ~5 min en pasar de "sending" a "sent".
- Los previos nunca a <20 min del saque ni tras el final.
- Último 30 días antes de empezar: 11 posts, 2.303 views, 0,53 % engagement, 0 shares → pedir interacción (pregunta final) y gancho con dato en el primer segundo.
