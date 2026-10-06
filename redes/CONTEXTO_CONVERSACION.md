# Contexto de la conversación que montó 2yellow (05-06/10/2026)

Resumen de todo lo hablado con el usuario en el chat que creó el sistema. Léelo entero antes de proponer o cambiar nada. Lo que aquí se dice "decidido" lo decidió el usuario.

## Quién es y cómo trabajar con él
- Cuenta: 2yellow (@2yellowdata) en TikTok e Instagram. Lema: "Football data, before and after the match". Contenido SIEMPRE en inglés; con el usuario, español y MUY breve (ahorra créditos).
- Quiere que Claude actúe como experto en contenido viral de fútbol, publique solo, gratis y con la mínima fricción para él. Objetivo final: INTERACCIÓN y seguidores.
- Escucha lo que pide: si pide "una prueba para ver", es una prueba que se le enseña, NO algo que automatizar ("Yo no te he dicho que organices nada"). No dar respuestas genéricas.
- No quiere tareas manuales pesadas (recopilar capturas cada semana = "demasiado trabajo").
- Ligas: las 5 grandes europeas; NUNCA Segunda División. Mientras no hay ligas (parón), Nations League. Las ligas vuelven el 9/10.
- Nada de vocabulario de apuestas en imágenes ni textos (bookies, odds, tips, picks de apuesta). Se quitó "Bookies" de la plantilla upset alert (TikTok dejaba en 0 vistas los posts con esa palabra). Pies con "Data, not betting advice. 18+" en los posts de datos.
- Nunca el mismo color para los dos equipos (06/10, Croacia-España ambos rojos: no se sabía qué Elo era de quién). Arreglado en `generar.py` (`separar()`).
- Los % de las imágenes son SOLO de nuestro modelo (`mod_*`), nunca mezcla con mercado.

## Rutina diaria (decidida)
- 2 mejores partidos del día → 6 plantillas de previo (la 6ª, borrosa, invita al perfil) → vídeo con música, publicado en la mejor hora del país, ≥4 h antes del saque y nunca a <20 min ni tras el final.
- Post-partido: 5 plantillas (post1,2,4,5,6) → vídeo → publicar ~30 min tras el final (tarea puntual a saque+2h00).
- Vídeo del día: pronósticos de ayer (resultado) + hoy (~09:30 Madrid).
- Música siempre (hip hop/trap/electro), rotando la biblioteca del repo (`musica/`, 20 pistas, `redes/biblioteca_musica.json`). Descripción en inglés + 5 hashtags SEO.
- Días sin partidos: no hay previos/post/vídeo, pero SÍ los 3 extras.
- Vídeos: GitHub Actions (`montar-video`); Higgs sandbox = plan B.

## Contenido extra (aprobado 05/10)
- 3 al día, TODOS los días: 2 memes + 1 dato curioso, sobre algo de las últimas 24-48 h. Mismo día, nunca pasarlos al siguiente.
- Formato: foto REAL de Wikimedia Commons + texto grande, estilo FotMob/Flashscore (el usuario rechazó las tarjetas de texto sobre negro: "¿has visto algo así en FotMob?"). 1 imagen por post por defecto; 2-3 si la idea lo pide.
- Reglas visuales: nunca tapar caras (se tapó la de Haaland/Kane al principio); logo 2yellow ARRIBA-IZQ; crédito de foto arriba-dcha (licencia CC BY-SA); NADA de "Source:"/webs en la imagen; zona segura y=150-1200 de 1350 (Instagram recorta casi a cuadrado; TikTok tapa la franja de abajo).
- Percepción: la foto debe ENCARNAR el chiste (si el chiste es de entrenadores de club esperando, cara de Mourinho/Guardiola con pánico, no Mbappé neutro).
- Segunda opinión: subagente Claude Sonnet como crítico de cada meme antes de programar.
- Publicación: Buffer en MODO RECORDATORIO (`schedulingType: "notification"`): al usuario le llega el aviso, abre TikTok/IG y publica él con música de la app (probado OK el 05/10). Motivo: Buffer/APIs no permiten música en fotos; Higgs TikTok solo con selección manual; se decidió mantener formato imagen/carrusel.
- Inspiración (solo aprender, NO crear plantillas nuevas ni copiar): Flashscore (emoji-arte, primera imagen gancho sin texto, pies de 4 palabras con juego de palabras) y Sofascore (publican ~17 min tras el final, jugador recortado + número gigante, 4 datos). FotMob creció en TikTok con memes/emoción, no con pantallazos de datos.
- Fuentes: Reddit, X y TikTok no se pueden leer desde aquí (bloqueados); el usuario no quiere scrapers que se salten bloqueos.
- LLMs gratuitos (Groq/Cerebras/Mistral, `futbol-pipeline/scripts/llm_gratis.py` → `preguntar()`): permiso del usuario 06/10 para usarlos SIEMPRE que haga falta (ideas, críticas, textos, análisis). Probado OK en esta sesión.
- 06/10: el usuario pidió analizar cuentas del sector y proponer mejoras a probar → resumen en `aprendizajes.md` ("Análisis del sector").

## Aprendizaje
- Bandido Thompson en `scripts/aprender.py` (variables: primera carta, seg/carta, arranque música s0/s1, hook, antelación, cartas, hora, música). Migrar a regresión bayesiana/ridge con ≥100 observaciones. Recompensa: interacciones/vistas y vistas vs mediana.
- No juzgar por un solo día; revisión semanal los DOMINGOS (semana lun-dom) en `aprendizajes.md`.
- Claude debe apuntar en `diario_creativo.md` qué memes funcionan y qué ajusta.

## Incidentes y arreglos
- 05/10: GitHub Actions no asignó runner ~15 min (avería general) → post-partido 25 min tarde. Arreglo: regla ANTI-RETRASO (si un workflow sigue en cola a los 3 min, datos de webs públicas y vídeo en Higgs). El usuario: "que no vuelva a pasar".
- 05/10: títulos de TikTok >90 caracteres fallan en Buffer.
- 06/10: la tarea diaria no creó el post-partido de Croacia-España (creado a mano), pasó 2 extras al día siguiente (corregido) y el vídeo del día salió de 3,6 s (ahora 3.5-5.5 s por carta en daily).
- Buffer plan gratuito: límite de posts programados a la vez; los publicados no se pueden borrar por API.

## Cola de publicación (decidido 06/10)
- El usuario: "no entiendo por qué hay que programar tanto". Decidido: memes/curiosos (y previos) se guardan en GitHub (`redes/cola/`) y el workflow `enviar-cola` los manda a Buffer pocos minutos antes de su hora (recordatorio para memes). Así Buffer solo tiene lo inminente y no se choca con el límite de programados. Clave `BUFFER_API_KEY` puesta y comprobada el 06/10: cola ACTIVA. La clave tiene todos los permisos (incl. insights y engagements); el usuario pide usarla con cabeza para analizar y conseguir más interacción y seguidores.

## Mejoras decididas (06/10, tras análisis del sector)
- Usuario aprueba: (1) previo en carrusel (avisa: él pone la música, a veces sin conexión → 1-4 h tarde); (2) cara a cara/ranking con datos de futbol-pipeline actualizados a diario; (3) pregunta como primer comentario; (4) vídeos con audio en tendencia "si no importa el retraso, tú decides".
- Claude decide: carrusel solo en previos, ≥7 h antes del saque, IG automático y TikTok recordatorio, medido por el bandido (`formato`); post-partido siempre vídeo automático; (4) NO. Plantillas `head_to_head` y `ranking` hechas (1 al día, 19:00, desde el 9/10). Actualizar datos a diario: el usuario dijo "sí, actívalo" (06/10), recordando que Highlightly está limitado a ~100 llamadas/día y que haya respaldos → workflow `jugadores_redes.yml` en futbol-pipeline: understat (sin cuota) + Highlightly con tope 20/día. Los datos de clubes se paran al 20/09 por el parón, no por fallo (ligas vuelven el viernes 9/10).
- Usuario: mejor JUGADOR VS JUGADOR que equipo vs equipo (lo que más interesa y genera conversación). Hecho: `datos_rankings.py jugadores`.
- Pregunta del usuario: ¿el bandido es buen modelo? Respuesta: sirve para ajustar detalles con pocos datos, pero no decide lo importante (tema/formato) y tiene mucho ruido; plan: dejarle pocas variables, comparar contra la mediana de cada tipo y pasar a regresión con ≥100 posts.

## Respaldo
- Workflow `redes_backup.yml` en futbol-pipeline (apagado): solo se activa si el usuario deja de tener Claude Pro (variable BACKUP_REDES=on + secreto BUFFER_API_KEY). Ver `futbol-pipeline/redes/backup/LEEME.md`. "De momento seguimos contigo".

## IDs útiles
- Buffer: IG 6ac3c8166a5c39ccb620dd8a, TikTok 6ac3c8456a5c39ccb620dec4.
- Tarea diaria: trig_016KxjMVXAwtFVbDiYKTeJKG (07:46 Madrid, crea tareas puntuales de post-partido).
- Música nueva: ElevenLabs flow Ftqxo4JAh1rF75G1yPf8 → `descargas/*.json` → workflow `bajar-musica`.
- Datos: `futbol-pipeline` → `redes/plantillas/datos_selecciones.py pre|post|hoy|perfil`; workflow `nations_league_ciclo.yml` (API Highlightly permitida para las tareas de redes; en el resto del proyecto, regla de su CLAUDE.md: pedir sí explícito).

## Pendiente
- Tras 2-3 días, valorar memes sin música vs con música del usuario; comparar extras vs previos/post en la revisión del domingo.
- Comprobar que las métricas de posts publicados a mano (recordatorio) llegan a Buffer; si no, usar métricas agregadas del canal.
- Clubes en plantillas cuando vuelvan las ligas (9/10+).
