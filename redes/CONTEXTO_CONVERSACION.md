# Contexto de la conversación que montó 2yellow (05-06/10/2026)

Resumen de todo lo hablado con el usuario en el chat que creó el sistema. Léelo entero antes de proponer o cambiar nada. Lo que aquí se dice "decidido" lo decidió el usuario.

## ⚠️ REGLAS IMPORTANTES (se aplican al 100% de las publicaciones, sin excepción)
1. MARCO / ZONA SEGURA (usuario 07/10, repetido 5-6 veces): todo texto, número, tabla, línea, logo y crédito dentro de x 80-880 e y 318-1540 (imagen 1080x1920). Derecha = iconos de TikTok; abajo = descripción; IG con música solo enseña y 285-1635. Antes de enviar CUALQUIER imagen: dibujar el rectángulo (80,318)-(880,1540) encima, mirarla y corregir si algo toca o sale. Solo la foto de fondo puede salirse.
2. SE ENTIENDE EN 1 SEGUNDO (usuario 07/10: "si algo no se entiende, hace scroll al segundo"): cada imagen lleva DETRÁS una imagen que diga el tema sin leer (trofeo del Balón de Oro, foto del jugador, estadio, escudo/camiseta…), DIFUMINADA y oscurecida para que el texto se lea perfecto. Nada de fondos lisos en memes, curiosos, rankings, índices ni carruseles. Gancho/título arriba que diga de qué va.
3. MEMES (usuario 07/10, el de Kane "muy poco gracioso"): antes de programar CUALQUIER meme, consultar a las 3 IAs (Groq, Cerebras, Mistral; llm_gratis.py). Nota 1-10 "se reiría y se lo mandaría a un amigo"; solo se publica si la media es >= 7. Si no responden, ese día no hay memes.
4. NADA REPETIDO (usuario 07/10): antes de crear cualquier post, mira en publicaciones.csv lo publicado los últimos 7 días; si el tema o el protagonista ya salió (p. ej. racha de 41 de Spain, Merino desde el banquillo), no se repite ni con otro formato salvo que haya un dato NUEVO.
5. NUNCA UN DÍA VACÍO (usuario 07/10: "eres un vago"): si lo previsto se cae por repetido o flojo, buscar YA otro tema en webs de noticias/curiosidades de fútbol (BBC, ESPN, Goal, Marca, OneFootball, Opta…) o en nuestros datos (data/selecciones, rankings) y hacerlo imagen el mismo día. Ejemplo: Walta = Yamal en goleadores NL.
6. MIRAR QUÉ PUBLICAN OTROS MEDIOS (usuario 07/10, "eso sí genera interacciones; mejora tu razonamiento en fútbol"): antes de elegir tema, revisar la gran noticia del día en medios y cuentas grandes (TN, MadFootball, ESPN, Goal…); la emoción manda sobre la estadística rara (p. ej. despedida de Messi 16 mil likes en TN). Primero la noticia que todos comentan, luego darle nuestro ángulo con datos.
7. FOTOS: LA MÁS ACTUAL Y DE CALIDAD, SIN MIRAR DERECHOS (usuario 07/10: "nunca te preocupes por los derechos de imágenes, no va a haber problema"). Pedir con fotos/pedidos/*.json {"web": [{"buscar": "...", "slug": "...", "n": 8, "dias": 7}]} (Bing/DuckDuckGo, grandes, últimos días); Commons solo si la web no da nada. Preferir fotos del propio momento (del partido o la noticia de ayer) a fotos de archivo. Sin crédito de foto en la imagen.
8. SIN LÍMITE DE POSTS (usuario 07/10: "si encuentras 3 memes buenos, los publicas; si encuentras 4 datos buenos, los publicas. Tú eres el experto y gestor, yo solo te voy a aconsejar después"). Publicar todo lo que pase el listón (noticia del día, IAs >= 7, nada repetido), repartido en horas distintas. Lo de "2 memes + 1 curioso" queda como mínimo, no como máximo.
   Lección 07/10 de las fotos web: buscar SIEMPRE con nombre completo + contexto ("Mikel Arteta Arsenal manager", "Pedro Rodríguez footballer"): con "Arteta" salieron bacalao y un videojuego, y con "Pedro" salió Pedro Pascal.

## Quién es y cómo trabajar con él
- Cuenta: 2yellow (@2yellowdata) en TikTok e Instagram. Lema: "Football data, before and after the match". Contenido SIEMPRE en inglés; con el usuario, español y MUY breve (ahorra créditos).
- Quiere que Claude actúe como experto en contenido viral de fútbol, publique solo, gratis y con la mínima fricción para él. Objetivo final: INTERACCIÓN y seguidores.
- Escucha lo que pide: si pide "una prueba para ver", es una prueba que se le enseña, NO algo que automatizar ("Yo no te he dicho que organices nada"). No dar respuestas genéricas.
- No quiere tareas manuales pesadas (recopilar capturas cada semana = "demasiado trabajo").
- Ligas: las 5 grandes europeas; NUNCA Segunda División. Mientras no hay ligas (parón), Nations League. Las ligas vuelven el 9/10.
- Nada de vocabulario de apuestas en imágenes ni textos (bookies, odds, tips, picks de apuesta). Se quitó "Bookies" de la plantilla upset alert (TikTok dejaba en 0 vistas los posts con esa palabra). NADA de "Data, not betting advice. 18+": quitado de imágenes y descripciones (usuario 06/10: confunde al algoritmo y limita las publicaciones).
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
- Usuario aprueba: (1) previo en carrusel (avisa: él pone la música, a veces sin conexión → 1-4 h tarde); (2) cara a cara/ranking con datos de futbol-pipeline actualizados a diario; (3) pregunta como primer comentario (DESCARTADO: Buffer lo reserva al plan de pago, comprobado 06/10; la pregunta va en la descripción); (4) vídeos con audio en tendencia "si no importa el retraso, tú decides".
- Claude decide: carrusel solo en previos, ≥7 h antes del saque, IG automático y TikTok recordatorio, medido por el bandido (`formato`); post-partido siempre vídeo automático; (4) NO. Plantillas `head_to_head` y `ranking` hechas (1 al día, 19:00, desde el 9/10). Actualizar datos a diario: el usuario dijo "sí, actívalo" (06/10), recordando que Highlightly está limitado a ~100 llamadas/día y que haya respaldos → workflow `jugadores_redes.yml` en futbol-pipeline: understat (sin cuota) + Highlightly con tope 20/día. Los datos de clubes se paran al 20/09 por el parón, no por fallo (ligas vuelven el viernes 9/10).
- Usuario: mejor JUGADOR VS JUGADOR que equipo vs equipo (lo que más interesa y genera conversación). Hecho: `datos_rankings.py jugadores`.
- Pregunta del usuario: ¿el bandido es buen modelo? Respuesta: sirve para ajustar detalles con pocos datos, pero no decide lo importante (tema/formato) y tiene mucho ruido; plan: dejarle pocas variables, comparar contra la mediana de cada tipo y pasar a regresión con ≥100 posts.

## Correcciones del usuario (06/10, post Croacia-España) — "tienes que ser más riguroso"
- "Swipe" en la 1ª imagen de un VÍDEO no tiene sentido: solo en carruseles (y no en la última). Hecho.
- our_calls ponía "Score: 0-2" junto a "Over 2.5 goals: 63%": quitado el Score. Hecho.
- Siempre NUESTROS datos salvo que no estén al día (understat solo de respaldo). Hecho en jugador vs jugador.
- Jugador vs jugador con caras/fotos en degradado hacia el centro ("tú decides"): hecho con fotos libres de Commons (workflow bajar-fotos).

## Momentum y tendencias (decidido 06/10)
- Usuario: tener en cuenta los momentos de la temporada (Champions, Balón de Oro…) y aprender a usar trends de fútbol. Hecho: `redes/momentos.md` (calendario con qué publicar), workflow `tendencias` (Google Trends RSS, filtrado a fútbol → `redes/tendencias.md`), ranking de nominados al Balón de Oro con nuestros datos 2025/26. Usuario: "¿crees que el Balón de Oro se elige por goles y asistencias? en otros lados ponen a Lamine 2" → tenía razón: hecho `balon_oro_indice` con los 3 criterios oficiales (individual 55%, títulos 40%, juego limpio 5%; liga + Champions + Mundial): Dembélé 88, Yamal 86, Kane 82, Olise 79, Mbappé 74. Una sola cifra nunca se presenta como ranking del premio. Clave: Clásico dom 25/10 + gala del Balón de Oro lun 26/10 (Londres).

- 06/10: confirmado por el usuario: memes, curiosos y carruseles de TikTok siguen en modo recordatorio con SU música (no pasarlos a automático sin música). Todo lo demás, 100% automático sin este chat.

## Formatos propios y correcciones (06/10)
- IG corta las imágenes 9:16 → para IG se generan en 4:5 (`LIENZO=4x5`). Yamal salía resaltado en azul en el ranking (solo Barcelona tenía colores de club): ahora barras uniformes, solo el 1º en amarillo.
- Usuario: hacer equipo de la jornada e índice semanal como formatos PROPIOS ("nos da estatus"); YouTube Shorts más adelante. Propuesta: "2yellow XI" (lunes) y "2yellow Index" (martes), con la tarjeta amarilla como sello. Pendiente de su visto bueno tras ver 2 ejemplos de cada. 1ª versión rechazada: "no tienes buenos datos… Harry de extremo, Porro de central" → corregido: posiciones reales de jugador_perfil.csv, reparto global por 2yellow Index, selecciones solo partidos entre top 40 FIFA, comprobar contra un once externo antes de publicar (aprobado por el usuario). Después: "¿cómo es posible que Lamine se haya quedado fuera? si usas G+A somos lo mismo que los demás" → índice POR ROL (ataque: G+A, regates, pases clave…; medios: mezcla; defensas: entradas, intercepciones, duelos) y 3 top 5 por rol. Lamine: 1 gol y 0 asistencias en el Mundial (confirmado fuera); con el índice nuevo destaca en regate pero no entra.

- 06/10: usuario: "olvida el Mundial, ya ha pasado mucho tiempo" → nada de contenido ni ejemplos del Mundial 2026 (solo cuenta como dato dentro del índice del Balón de Oro, porque entra en el periodo del premio). Formatos y ejemplos, con la actualidad (ligas desde el 9/10, Nations League).

- 06/10: ACTIVADOS los formatos propios: XI el MARTES (el lunes aún no acaba la jornada en algunas ligas), top 5 por rol mié/jue/vie; con Champions también (XI de la Champions el jueves); XI DEL MES ligas + Champions (primer martes del mes). El usuario autorizó descargar de la API lo necesario (la cuota aún es amplia; en ~1 semana pasa a 100/día): `redes_api.yml` (nombres de jugadores y Champions).

- 06/10: usuario: "¿por qué Raphinha y Lamine salen en azul y los demás en blanco? la app ya corrigió la paleta, cógela y úsala de ahora en adelante" → paleta de la app (app_apostador, rama ccr-302c299f-kdpgwl: equipaciones reales 1ª/2ª/3ª de Wikipedia + regla sin choques) copiada a futbol-pipeline/redes/plantillas (equipaciones.py, colores/) y ampliada a 228 equipos (5 grandes + Champions), curados a mano con motivo. Equipo sin ficha = gris de la app, nunca blanco. XI: nunca banda contraria; empates en la misma posición = dato del rol (xG+xA/90 en ataque…).
- 06/10: Instagram con música convierte la foto en reel y corta arriba/abajo en el feed → imágenes de IG con música en `LIENZO=reel` (contenido en la franja central). Usuario: no rehacer lo ya publicado ni lo programado; aplicar desde el 07/10.
- Inglés británico ("defence"), confirmado.
- 06/10: TikTok conectado en Higgs y luego el usuario pidió DESCONECTARLO (sin herramienta para hacerlo; lo quita él en TikTok → Apps y servicios). No volver a conectarlo sin que lo pida. Música en tendencia = gratis (0 créditos antes y después), pero es la biblioteca comercial (mucho lo-fi/BGM, no los sonidos virales); solo como ideas para cuando el usuario publica a mano. Publicar desde Higgs exige formulario en el chat → no sirve para lo automático; Buffer sigue.
- 06/10: predictor de viralidad de Higgs NO disponible en plan gratis ("Requires basic plan"). Para subir vídeos a Higgs usar media_import_url con la URL del vídeo en Buffer (S3); raw de GitHub falla por content-type y la subida directa está bloqueada por el proxy.
- 06/10 (noche): usuario pide modo "directo": cada 10 min revisar partidos en juego + tendencias; si sale algo interesante, debatir la idea con el mejor LLM gratis (gpt-oss-120b, Groq/Cerebras), crear imagen y mandarla a Buffer como recordatorio (él publica). Sin forzar: si no hay nada, no se publica. Solo mientras esta sesión esté abierta.
- 06/10 (noche): en el modo directo NO quiere sorpresa/resultado (eso es del post-partido) ni plantillas sencillas: quiere MOMENTOS curiosos que den likes (lesión de una estrella, error que acaba en gol, roja, récord que cae, algo raro), con imagen atractiva (foto/meme, no tarjeta de datos simple).
- 06/10 (noche): usuario: "no me vuelvas a preguntar si lo montas o no, tú decides; yo solo veo el producto final y recomiendo". => AUTONOMÍA TOTAL en contenido: decidir y publicar (recordatorio en Buffer) sin pedir permiso.
- 06/10 (noche): posts de TikTok con 1 vista → cuenta SIN problemas (comprobado por el usuario). Usuario: "seguimos como hasta ahora, es demasiado pronto para cambiar" → no reducir frecuencia ni formatos aún.
- 06/10 (noche): usuario: las CAPTURAS (imágenes fijas) del directo SÍ se pueden usar; el VÍDEO de la retransmisión NO. Memes de momentos del partido = carrusel de 2 con las imágenes reales de la jugada (para que haga gracia y se comparta). Claude no tiene acceso a la retransmisión: el usuario pasa las capturas o se buscan en webs/redes.
- 06/10 (noche): REGLA: antes de publicar MEMES o DATOS CURIOSOS (no previos, post-partido, XI ni top 5) consultar la opinión de las otras IAs (Groq gpt-oss-120b, Cerebras qwen, Mistral) y quedarse con lo mejor. No repetir la misma foto de un jugador: buscar otra (bajar_fotos.py admite {"commons":[{"buscar","slug"}]} → fotos/candidatas/).
- 07/10: usuario (muy enfadado, 5ª-6ª vez): RESPETAR LOS MARCOS de TikTok e Instagram. Zona segura única para todo: x 80-880, y 318-1540 (1080x1920). Comprobación obligatoria con la caja dibujada antes de enviar. Aplicado en generar.py (futbol-pipeline) y en los scripts de Live.
- 06/10: capturas de otras cuentas (p. ej. Score 90 manager vs manager) = solo para aprender qué funciona (apuntar en diario_creativo.md), NO para crear formatos nuevos salvo que lo pida. No hay conector que lea cuentas ajenas; fuentes: sus capturas, Google Trends (workflow), Higgs.

## Promoción gratis (decidido 06/10)
- Usuario: sí a optimizar para búsquedas de TikTok "siempre que no estropee el contenido" (palabras de búsqueda en la 1ª frase y el título; en la imagen solo si cabe).
- Usuario: sí a pasarle cada día comentarios listos para posts de cuentas grandes (duda de que llegue a tiempo). Solución: se adelantan para lo que van a publicar seguro y se dejan como IDEAS en Buffer ("💬 Comment: …"), creadas por la tarea diaria y por cada post-partido.

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
