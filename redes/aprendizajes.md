# Aprendizajes (actualizar cada día con datos reales)
- 2026-10-05 (línea base, 30 días previos): 11 posts, 2.303 views, alcance 802, 9 reacciones, 4 comentarios, 0 shares, engagement 0,53 %. Se ve pero no se interactúa.
- Hipótesis a probar: pregunta final directa; música distinta por vídeo; hora previo (≥4 h antes); vídeo diario por la mañana.

## Análisis FotMob en TikTok (capturas del usuario, 05/10/2026; contenido de 2023-24, vistas actuales)
- Rango típico: 20K-500K; los grandes 1M-6.6M. Los peores (20-35K): demos de la app, capturas de pantalla de datos/alineaciones y entrevistas con logo. Los mejores: emoción + cultura futbolera + una frase.
- Formatos que repiten: (1) "POV/my rating" meme del rating (1.1M, 997K); (2) clip de jugador + 3-6 palabras en minúscula con bucle abierto ("when you realize" 6.6M, "define" 870K, "did you know" 433K, "life is about" 977K, "expectations" 450K); (3) estadística sorprendente con narrativa, no solo dato (France 14-0 Gibraltar 403K, "last time Arsenal beat Liverpool at Anfield" 1.2M, "Ajax in 2019" 806K); (4) mini-reacción de un jugador con una línea ("He's the goat" 450K); (5) comparaciones Haaland/Van Dijk (1.1M).
- Insight: texto muy corto en el primer frame, 1 idea, sin logo; repiten el mismo formato decenas de veces.
- Ideas a probar con el bandido (variable nueva `gancho`): stat_sorpresa (frase corta tipo "last time X beat Y at Z") vs pregunta vs slideshow actual; primera carta con 4-6 palabras. Cuidado: fotos de jugadores = derechos; usar camisetas/colores propios.

## Fuentes públicas (05/10/2026)
- Fanpage Karma (marcas, no solo fútbol): carrusel vs vídeo. Instagram: alcance +13%, engagement x1,5 (+51% interacciones) a favor del carrusel. TikTok: alcance +3% (igual), engagement +81% y likes +82% del carrusel, pero shares ~1/3 menos. => añadir variable `formato` (carrusel/vídeo) al bandido.
- Forbes (FotMob): su explosión en TikTok fue orgánica, ligada al Mundial 2022 y a usuarios compartiendo la app; no hay estrategia de contenido documentada. => los picos llegan con grandes torneos/eventos.
- OneFootball: contenido vertical deslizable tipo stories funciona sin instrucciones.
- 2026-10-06: sin métricas aún (todos <24 h). Hoy: diario 09:30, previos CRO-ESP 14:45 (primera=key) y ENG-CZE 16:45 (primera=pred). INCIDENTE: la 1ª tanda de montaje falló por carrera de pushes (dos pushes seguidos): hacer UN solo push de pedidos o esperar al workflow. INCIDENTE 2: el sistema denegó crear las tareas puntuales de post-partido (create_trigger) → no hay post-partido automático hoy; el usuario debe aprobarlo.
- 06/10: el vídeo del día salió de 3.6 s (bandido eligió 1.8 s por carta). Corregido: en daily el tiempo por carta es 3.5/4.5/5.5 s.

## Análisis del sector (06/10/2026, pedido del usuario; TikTok/IG no se pueden leer desde aquí → estudios públicos)
- Buffer (52M posts): en IG los reels dan +36% alcance y los carruseles +12% interacción y muchos más guardados. Reels = captar, carruseles = retener. Constancia: publicar 20+ semanas de 26 → ~4,5x interacción por post.
- TikTok photo mode: carrusel +31% interacción en cuentas <100K, +20-40% guardados, +10-25% comentarios; mismo alcance que vídeo. Ojo: el uso masivo de fotos ha bajado su rendimiento medio (vistas -23%).
- Caso cuenta de stats 0→100K en 90 días (blog de una herramienta, fiable a medias): 3 formatos repetidos sin parar: cara a cara jugador vs jugador, rankings y "carreras" temporada a temporada; de 1 a 3 vídeos/día.
- Equipe de France (3M en 6 meses): audios en tendencia + jugadores haciendo lo que les hace reconocibles.
- Mejoras propuestas al usuario (pendiente de su elección): (1) previo como CARRUSEL vs vídeo (variable `formato`); (2) formato nuevo cara a cara/ranking; (3) pregunta polarizante como primer comentario (`metadata.instagram.firstComment` de Buffer); (4) vídeos en modo recordatorio para poner audio en tendencia (a costa de trabajo del usuario); (5) primera carta con 4-6 palabras de gancho, sin datos.
Fuentes: buffer.com/resources/creator-growth-playbook, fanpagekarma.com/insights/carousel-vs-video-performance-tiktok-instagram, ttcalculator.net/learn/tiktok-photo-carousel-engagement, sambadigital.com (caso FFF), sociavault.com/blog/engagement-benchmarks-2026.
- 07/10 INCIDENTE: enviar-cola falló desde las 12:00 (no existía redes/cola/enviados/ en main: git no guarda carpetas vacías). Arreglado (mkdir + .gitkeep); el curioso de Kane de las 12:00 se reprogramó a las 19:30.
