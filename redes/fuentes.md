# 50 fuentes de fútbol para 2yellow

Creada el 07/10 a petición del usuario, después de que se escapara la despedida de Messi. Sirve para mirar **qué está comentando todo el mundo** antes de elegir tema, y luego darle nuestro ángulo con datos.

- El contenedor de Claude no abre estas webs. Las que tienen RSS (marcadas como `rss`) las lee `scripts/titulares.py` en GitHub Actions (workflow `tendencias`, 05:20 y 14:00 UTC) y escribe `redes/titulares.md`. Ese archivo trae los temas que se repiten en más medios, que son la noticia del día.
- Las redes sociales no tienen RSS: se consultan con WebSearch (`site:` o el nombre de la cuenta) o cuando el usuario manda capturas.

## Noticias generales (Inglaterra / internacional)
| # | Fuente | URL | Para qué |
|---|---|---|---|
| 1 | BBC Sport | bbc.com/sport/football · rss | Noticia seria del día, Premier, selecciones |
| 2 | The Guardian Football | theguardian.com/football · rss | Análisis, historias curiosas, columnas |
| 3 | Sky Sports Football | skysports.com/football · rss | Fichajes, Premier, ruedas de prensa |
| 4 | ESPN FC | espn.com/soccer · rss | Global, EE. UU., Latinoamérica |
| 5 | Goal | goal.com/en · rss | Rankings, listas, polémicas virales |
| 6 | The Athletic | nytimes.com/athletic/football | Exclusivas y datos de fondo (de pago) |
| 7 | talkSPORT | talksport.com/football · rss | Declaraciones polémicas, tono de debate |
| 8 | Daily Mail Sport | dailymail.co.uk/sport/football · rss | Lo más compartido y morboso |
| 9 | Mirror Football | mirror.co.uk/sport/football · rss | Virales, vida de jugadores |
| 10 | The Independent Football | independent.co.uk/sport/football · rss | Noticia del día |
| 11 | The Telegraph Football | telegraph.co.uk/football · rss | Exclusivas Inglaterra |
| 12 | 90min | 90min.com · rss | Listas y rankings virales |
| 13 | Planet Football | planetfootball.com · rss | Nostalgia, "where are they now", curiosidades |
| 14 | FourFourTwo | fourfourtwo.com · rss | Rankings históricos, listas |
| 15 | Football365 | football365.com · rss | Opinión y humor británico |
| 16 | Yahoo Sports Soccer | sports.yahoo.com/soccer · rss | Resúmenes rápidos de agencias |
| 17 | Google News "football" | news.google.com (búsqueda) · rss | Agregador: qué titula todo el mundo |

## España, Italia, Alemania, Francia, Portugal
| # | Fuente | URL | Para qué |
|---|---|---|---|
| 18 | Marca | marca.com · rss | Real Madrid, LaLiga, selección |
| 19 | AS | as.com · rss | Real Madrid, LaLiga, selección |
| 20 | Mundo Deportivo | mundodeportivo.com · rss | Barça, curiosidades |
| 21 | Sport | sport.es · rss | Barça, Lamine Yamal |
| 22 | Relevo | relevo.com | Historias largas, datos curiosos |
| 23 | Google News "fútbol" (España) | news.google.com (búsqueda) · rss | Agregador en español |
| 24 | La Gazzetta dello Sport | gazzetta.it · rss | Serie A |
| 25 | Football Italia | football-italia.net · rss | Serie A en inglés |
| 26 | Calciomercato | calciomercato.com · rss | Rumores de Serie A |
| 27 | Kicker | kicker.de · rss | Bundesliga |
| 28 | L'Équipe | lequipe.fr · rss | Ligue 1, Francia, Balón de Oro (lo organiza France Football) |
| 29 | Foot Mercato | footmercato.net · rss | Fichajes, Francia |
| 30 | Record | record.pt · rss | Portugal, Cristiano |

## Sudamérica (aquí se nos escapó Messi)
| # | Fuente | URL | Para qué |
|---|---|---|---|
| 31 | TN Deportivo | tn.com.ar/deportes · rss | Argentina, Messi (16 mil likes en Threads con la despedida) |
| 32 | Olé | ole.com.ar · rss | Argentina, Boca/River |
| 33 | Infobae Deportes | infobae.com/deportes · rss | Argentina y Latinoamérica |
| 34 | Google News "fútbol" (Argentina) | news.google.com (búsqueda) · rss | Agregador argentino |
| 35 | ge.globo | ge.globo.com · rss | Brasil |

## Datos y estadística
| # | Fuente | URL | Para qué |
|---|---|---|---|
| 36 | Opta Analyst | theanalyst.com | Récords y datos comprobados |
| 37 | FBref | fbref.com | Estadística por jugador, comprobar cifras |
| 38 | Transfermarkt | transfermarkt.com | Valores, partidos internacionales, historial |
| 39 | SofaScore | sofascore.com | Notas y datos del partido en directo |
| 40 | FotMob | fotmob.com | Notas, xG, alineaciones |

## Redes sociales (ideas virales; sin RSS, mirar con WebSearch)
| # | Fuente | Dónde | Para qué |
|---|---|---|---|
| 41 | r/soccer | reddit.com/r/soccer · rss (top del día) | Lo más votado del día: termómetro de viralidad |
| 42 | 433 | Instagram/TikTok @433 | Formato viral, memes, emoción |
| 43 | B/R Football | Instagram/TikTok @brfootball | Gráficos virales, comparativas |
| 44 | Fabrizio Romano | X/Instagram @fabrizioromano | Fichajes ("Here we go") |
| 45 | OptaJoe | X @OptaJoe | Datos-récord en una línea: idea de curioso |
| 46 | Squawka | X @Squawka | Comparativas de jugadores, datos virales |
| 47 | MadFootball | Threads/Instagram @madfootball_1 | Leyendas, nostalgia, emoción (lo mandó el usuario) |
| 48 | todonoticias (TN) | Threads @todonoticias | Argentina, momentos emotivos |
| 49 | ESPN FC | Instagram/TikTok @espnfc | Debates y polémicas |
| 50 | Troll Football / Footy Humour | Instagram/Facebook | Humor: qué meme funciona hoy |

## Cómo usarla cada día (tarea diaria y extras)
1. Leer `redes/titulares.md` y `redes/tendencias.md`: el tema que sale en más medios es la noticia del día.
2. Si es un momento emocional (despedida, récord, lesión grave, vuelta de una leyenda), es el post del día, aunque no haya dato raro.
3. Darle nuestro ángulo: un dato o contraste que se entienda en 1 segundo (p. ej. "Empezó con una roja, acabó con un gol").
4. Comprobar las cifras en 2 fuentes como mínimo (rigor), y respetar las reglas importantes (zona segura, fondo, nada repetido).
