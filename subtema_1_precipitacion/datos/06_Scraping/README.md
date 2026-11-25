# 06_Scraping — datos obtenidos por scraping (C6)

Generado el 2026-11-24 por `scripts/generar_documentacion.py`. Responsable: Equipo 1 (Diego Loria, Rama Marin, José Ángel Pech).

Scripts en `scripts/`: `scraping_smn_sivea.py` (SIVEA/SMN), `scraping_procivy.py` (PROCIVY) y `scraping_diario_yucatan.py` (Diario de Yucatán). Se corren con `python scripts/<script>.py`; hacen peticiones espaciadas (3 a 5 s) con un User-Agent identificable y solo leen páginas públicas permitidas por su robots.txt. **El SIVEA solo guarda 90 días**: `scraping_smn_sivea.py` fusiona cada captura con la serie anterior, así que hay que correrlo al menos cada ~60 días; sin eso la serie queda como una foto de la ventana capturada. Controles y límites (incluido que la lluvia de Progreso en SIVEA no coincide con la serie diaria del SMN el 7-sep-2026): [`../REPORTE_CALIDAD.md`](../REPORTE_CALIDAD.md).

## Resumen de tablas

| Archivo | Fuente | Granularidad | Clave | Cobertura | Filas |
|---|---|---|---|---|---:|
| [`smn_sivea_yucatan_10min.csv`](smn_sivea_yucatan_10min.csv) | C6.1 | estación × 10 min | `estacion + fecha_utc` | 2026-08 – 2026-11 | 47,698 |
| [`smn_sivea_estaciones.csv`](smn_sivea_estaciones.csv) | C6.1 | estación | `estacion` | — | 5 |
| [`smn_sivea_capturas.csv`](smn_sivea_capturas.csv) | C6.1 | captura × estación | `captura + estacion` | 2026-11 – 2026-11 | 10 |
| [`procivy_boletines_2019_2026.csv`](procivy_boletines_2019_2026.csv) | C6.2 | boletín | `id_sistema + boletin` | 2019-05 – 2026-10 | 413 |
| [`procivy_sistemas_2019_2026.csv`](procivy_sistemas_2019_2026.csv) | C6.2 | sistema | `temporada + id_sistema` | 2019-05 – 2026-10 | 124 |
| [`diario_yucatan_notas_lluvia_2017_2026.csv`](diario_yucatan_notas_lluvia_2017_2026.csv) | C6.3 | nota | `url` | 2017-12 – 2026-11 | 6,589 |

## Cómo se relacionan
- `smn_sivea_estaciones.csv` y `smn_sivea_capturas.csv` describen la serie `smn_sivea_yucatan_10min.csv` y su procedencia.
- `procivy_sistemas_2019_2026.csv` resume `procivy_boletines_2019_2026.csv` (une por `temporada` + `id_sistema`) y suma los sistemas sin boletines.
- El Diario de Yucatán es una fuente secundaria: el CSV es un índice de enlaces, no un conteo de eventos.

## `smn_sivea_yucatan_10min.csv`
Serie acumulada de las estaciones automáticas de Yucatán del visor SIVEA (SMN). Cada corrida de `scraping_smn_sivea.py` agrega la ventana de 90 días sin duplicar. Celda vacía = sin dato. Ojo: el canal de lluvia puede traer 0.0 donde en realidad falta el dato (ver REPORTE_CALIDAD.md).

Fuente: C6.1 · Granularidad: estación × 10 min · Clave: `estacion + fecha_utc` · Cobertura: 2026-08 – 2026-11 · Filas: 47,698

| Columna | Tipo | Unidad | Descripción |
|---|---|---|---|
| `estacion` | texto |  | Estación (DZILAM, MERIDA, PROGRESO, TANTAQUIN, VALLADOLID) |
| `fecha_local` | fecha-hora | AAAA-MM-DD HH:MM:SS | Hora local |
| `fecha_utc` | fecha-hora | AAAA-MM-DD HH:MM:SS | Hora UTC |
| `precipitacion_mm` | decimal | mm/10 min | Lluvia del intervalo |
| `temperatura_c` | decimal | °C | Temperatura del aire |
| `humedad_pct` | decimal | % | Humedad relativa |

## `smn_sivea_estaciones.csv`
Metadatos y cobertura de cada estación en la serie acumulada. «MERIDA» casi no transmite (2 registros en 90 días).

Fuente: C6.1 · Granularidad: estación · Clave: `estacion` · Cobertura: — · Filas: 5

| Columna | Tipo | Unidad | Descripción |
|---|---|---|---|
| `estacion` | texto |  | Estación |
| `tipo` | texto |  | EMA o ESMA |
| `municipio` | texto |  | Municipio |
| `latitud` | decimal | grados | Latitud |
| `longitud` | decimal | grados | Longitud |
| `altitud_m` | entero | m | Altitud |
| `registros` | entero | registros | Registros acumulados |
| `desde_utc` | fecha-hora | AAAA-MM-DD HH:MM:SS | Primer registro |
| `hasta_utc` | fecha-hora | AAAA-MM-DD HH:MM:SS | Último registro |
| `cobertura_pct` | decimal | % | Registros entre los esperados cada 10 min en ese lapso |
| `dias_con_lluvia` | entero | días | Días locales con lluvia > 0 |

## `smn_sivea_capturas.csv`
Bitácora de cada corrida del scraper: cuántos registros se bajaron y cuántos eran nuevos.

Fuente: C6.1 · Granularidad: captura × estación · Clave: `captura + estacion` · Cobertura: 2026-11 – 2026-11 · Filas: 10

| Columna | Tipo | Unidad | Descripción |
|---|---|---|---|
| `captura` | fecha-hora | AAAA-MM-DD HH:MM | Cuándo se corrió |
| `estacion` | texto |  | Estación |
| `registros_descargados` | entero | registros | Registros de la ventana de 90 días |
| `registros_nuevos` | entero | registros | Los que no estaban ya en la serie |
| `desde_utc` | fecha-hora |  | Inicio de la ventana |
| `hasta_utc` | fecha-hora |  | Fin de la ventana |

## `procivy_boletines_2019_2026.csv`
Boletines de ciclones tropicales de PROCIVY (Protección Civil de Yucatán), temporadas 2019 a 2026. El resumen se recorta a 400 caracteres.

Fuente: C6.2 · Granularidad: boletín · Clave: `id_sistema + boletin` · Cobertura: 2019-05 – 2026-10 · Filas: 413

| Columna | Tipo | Unidad | Descripción |
|---|---|---|---|
| `temporada` | entero | AAAA | Temporada ciclónica |
| `id_sistema` | texto |  | Identificador del sistema en el sitio (NNAA) |
| `ciclon` | texto |  | Nombre del ciclón, o número si no tiene |
| `boletin` | texto |  | Clave del boletín |
| `fecha` | fecha | AAAA-MM-DD | Fecha del boletín |
| `hora` | texto | HH:MM | Hora local |
| `menciona_lluvia` | entero | 0/1 | El texto menciona lluvia |
| `dist_merida_km` | entero | km | Distancia a Mérida si el texto la da (solo unos cuantos boletines) |
| `resumen` | texto |  | Texto del boletín recortado a 400 caracteres |

## `procivy_sistemas_2019_2026.csv`
Todos los sistemas que lista PROCIVY por temporada. Los que no amenazaron a Yucatán figuran con `sin_boletines = 1` y 0 boletines.

Fuente: C6.2 · Granularidad: sistema · Clave: `temporada + id_sistema` · Cobertura: 2019-05 – 2026-10 · Filas: 124

| Columna | Tipo | Unidad | Descripción |
|---|---|---|---|
| `temporada` | entero | AAAA | Temporada |
| `id_sistema` | texto |  | Identificador |
| `ciclon` | texto |  | Nombre o número |
| `fecha_formacion` | fecha | AAAA-MM-DD | Fecha de formación |
| `sin_boletines` | entero | 0/1 | PROCIVY indica «No hay boletines» |
| `boletines` | entero | boletines | Boletines emitidos |
| `primer_boletin` | fecha | AAAA-MM-DD | Primer boletín |
| `ultimo_boletin` | fecha | AAAA-MM-DD | Último boletín |
| `dist_minima_merida_km` | decimal | km | Distancia mínima a Mérida mencionada en los boletines (vacío si ninguno la da) |
| `menciona_lluvia` | entero | 0/1 | Algún boletín menciona lluvia |

## `diario_yucatan_notas_lluvia_2017_2026.csv`
Notas del Diario de Yucatán cuyo enlace contiene palabras de lluvia (lluvia, inundación, tormenta, huracán…). Solo metadatos: no se copia el texto de las notas. Incluye notas de otras regiones y algunas que no son del clima; sirve como índice, no como conteo de eventos.

Fuente: C6.3 · Granularidad: nota · Clave: `url` · Cobertura: 2017-12 – 2026-11 · Filas: 6,589

| Columna | Tipo | Unidad | Descripción |
|---|---|---|---|
| `fecha` | fecha | AAAA-MM-DD | Fecha de la nota (sale de la URL) |
| `seccion` | texto |  | Sección (yucatan, merida, mexico, mundo…) |
| `menciona_merida_slug` | entero | 0/1 | El enlace menciona Mérida |
| `slug` | texto |  | Final del enlace |
| `url` | texto |  | Enlace a la nota |
| `sitemap` | texto |  | Sitemap de origen |
