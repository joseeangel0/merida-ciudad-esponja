# 07_Datos_propios — tablas calculadas por el equipo (C7)

Generado el 2026-11-24 por `scripts/generar_documentacion.py`. Responsable: Equipo 1 (Diego Loria, Rama Marin, José Ángel Pech).

Insumo: registros diarios del SMN/CONAGUA (CLICOM) en `insumo_SMN_CONAGUA_estaciones/`. Procesamiento: `scripts/procesar_datos.py` (limpieza, agregación, Gumbel) y `scripts/generar_csv_dashboard.py`. Codificación UTF-8, separador coma, fechas ISO. **Celda vacía = sin dato (nunca 0 mm).** La limpieza y los registros descartados están en [`../REPORTE_CALIDAD.md`](../REPORTE_CALIDAD.md).

## Resumen de tablas

| Archivo | Fuente | Granularidad | Clave | Cobertura | Filas | Estaciones |
|---|---|---|---|---|---:|---:|
| [`smn_catalogo_estaciones.csv`](smn_catalogo_estaciones.csv) | C7.1 | estación | `clave` | 1951–2026 | 9 | 9 |
| [`smn_precip_diaria.csv`](smn_precip_diaria.csv) | C7.1 | estación-día | `estacion + fecha` | 1951-01 – 2026-09 | 115,430 | 9 |
| [`smn_precip_mensual.csv`](smn_precip_mensual.csv) | C7.1 | estación-mes | `estacion + fecha` | 1951-01 – 2026-09 | 4,444 | 9 |
| [`smn_precip_anual.csv`](smn_precip_anual.csv) | C7.1 | estación-año | `estacion + anio` | 1951 – 2026 | 374 | 9 |
| [`indices_lluvia_extrema_por_anio.csv`](indices_lluvia_extrema_por_anio.csv) | C7.2 | estación-año | `estacion + anio` | 1951 – 2026 | 239 | 5 |
| [`periodos_retorno_lluvia_24h.csv`](periodos_retorno_lluvia_24h.csv) | C7.2 | estación × periodo de retorno | `estacion + periodo_retorno_anios` | — | 12 | 2 |
| [`tendencias_31097.csv`](tendencias_31097.csv) | C7.2 | estación | `estacion` | — | 1 | 1 |
| [`climatologia_mensual_31044_1991_2020.csv`](climatologia_mensual_31044_1991_2020.csv) | C7.1 | mes del año | `mes` | — | 12 | — |
| [`promedio_anual_por_estacion_1991_2020.csv`](promedio_anual_por_estacion_1991_2020.csv) | C7.1 | estación | `clave` | — | 8 | 8 |
| [`eventos_extraordinarios_>=100mm.csv`](eventos_extraordinarios_>=100mm.csv) | C7.3 | evento (estación-día) | `estacion + fecha` | 1954-08 – 2026-06 | 76 | 5 |
| [`dashboard_lluvia_mensual_por_estacion.csv`](dashboard_lluvia_mensual_por_estacion.csv) | C7.1 | estación-mes | `estacion_clave + fecha` | 1951-01 – 2026-09 | 2,329 | 5 |
| [`meses_invalidados.csv`](meses_invalidados.csv) | C7.1 | estación-mes | `estacion + mes` | — | 130 | 6 |
| [`estaciones_claves_territoriales.csv`](estaciones_claves_territoriales.csv) | C7.1 | estación | `clave` | — | 9 | 9 |

## Cómo se relacionan
- La clave de cruce entre casi todas las tablas es la **clave de estación SMN** (`estacion`, `clave` o `estacion_clave`).
- `estaciones_claves_territoriales.csv` une cada estación con el municipio y la AGEB del INEGI (`cvegeo_ageb`) para cruzar con otras fuentes territoriales.
- Unidades: lluvia en **mm**; coordenadas en grados decimales (≈WGS84); fechas en formato ISO.

## `smn_catalogo_estaciones.csv`
Catálogo de las 9 estaciones del SMN en Mérida y alrededores, con su cobertura real.

Fuente: C7.1 · Granularidad: estación · Clave: `clave` · Cobertura: 1951–2026 · Filas: 9

| Columna | Tipo | Unidad | Descripción |
|---|---|---|---|
| `clave` | texto |  | Clave de estación del SMN (CLICOM) |
| `nombre` | texto |  | Nombre de la estación |
| `municipio` | texto |  | Municipio según el SMN |
| `situacion` | texto |  | OPERANDO o SUSPENDIDA |
| `latitud` | decimal | grados | Latitud (datum del SMN, ≈WGS84) |
| `longitud` | decimal | grados | Longitud |
| `altitud_msnm` | entero | m | Altitud sobre el nivel del mar |
| `inicio` | fecha |  | Primer día con dato válido |
| `fin` | fecha |  | Último día con dato válido |
| `dias_con_dato` | entero | días | Días con dato válido (tras la limpieza) |
| `pct_completitud` | decimal | % | Días con dato entre los días de inicio a fin |

## `smn_precip_diaria.csv`
Lluvia diaria. Celda vacía = sin dato (nunca 0): incluye los meses descartados por la regla de ceros espurios.

Fuente: C7.1 · Granularidad: estación-día · Clave: `estacion + fecha` · Cobertura: 1951-01 – 2026-09 · Filas: 115,430

| Columna | Tipo | Unidad | Descripción |
|---|---|---|---|
| `estacion` | texto |  | Clave de estación |
| `fecha` | fecha | AAAA-MM-DD | Día |
| `precip_mm` | decimal | mm/día | Precipitación acumulada en 24 h; vacío = sin dato |

## `smn_precip_mensual.csv`
Lluvia mensual con control de completitud (≥80 % de los días del mes).

Fuente: C7.1 · Granularidad: estación-mes · Clave: `estacion + fecha` · Cobertura: 1951-01 – 2026-09 · Filas: 4,444

| Columna | Tipo | Unidad | Descripción |
|---|---|---|---|
| `estacion` | texto |  | Clave de estación |
| `fecha` | texto | AAAA-MM | Mes |
| `precip_mm` | decimal | mm/mes | Suma del mes; vacío si completo = False |
| `dias_con_dato` | entero | días | Días del mes con dato |
| `max_diaria_mm` | decimal | mm | Máximo diario del mes |
| `dias_mes` | entero | días | Días del mes |
| `completo` | booleano |  | True si dias_con_dato ≥ 80 % de dias_mes |

## `smn_precip_anual.csv`
Totales e índices anuales. El total solo existe en años con 12 meses válidos; los conteos de días usan los días válidos.

Fuente: C7.1 · Granularidad: estación-año · Clave: `estacion + anio` · Cobertura: 1951 – 2026 · Filas: 374

| Columna | Tipo | Unidad | Descripción |
|---|---|---|---|
| `estacion` | texto |  | Clave de estación |
| `precip_mm` | decimal | mm/año | Suma anual; vacío si meses_validos < 12 |
| `meses_validos` | entero | meses | Meses completos del año |
| `dias_lluvia_>=1mm` | entero | días | Días con ≥1 mm |
| `dias_>=50mm` | entero | días | Días con ≥50 mm |
| `dias_>=100mm` | entero | días | Días con ≥100 mm |
| `max_diaria_mm` | decimal | mm | Máximo diario del año (con los días válidos) |
| `anio` | entero | AAAA | Año |

## `indices_lluvia_extrema_por_anio.csv`
Índices de lluvia extrema por año para las estaciones urbanas.

Fuente: C7.2 · Granularidad: estación-año · Clave: `estacion + anio` · Cobertura: 1951 – 2026 · Filas: 239

| Columna | Tipo | Unidad | Descripción |
|---|---|---|---|
| `estacion` | texto |  | Clave de estación |
| `anio` | entero | AAAA | Año |
| `precip_mm` | decimal | mm/año | Total anual (vacío si el año no está completo) |
| `dias_lluvia_>=1mm` | entero | días | Días con ≥1 mm |
| `dias_>=50mm` | entero | días | Días con ≥50 mm |
| `dias_>=100mm` | entero | días | Días con ≥100 mm |
| `max_diaria_mm` | decimal | mm | Máximo diario del año |
| `meses_validos` | entero | meses | Meses completos del año |

## `periodos_retorno_lluvia_24h.csv`
Lluvia esperada en 24 h por periodo de retorno (Gumbel por momentos sobre el máximo diario anual de años completos).

Fuente: C7.2 · Granularidad: estación × periodo de retorno · Clave: `estacion + periodo_retorno_anios` · Cobertura: — · Filas: 12

| Columna | Tipo | Unidad | Descripción |
|---|---|---|---|
| `estacion` | texto |  | Clave de estación (solo 31097 y 31044 tienen serie suficiente) |
| `periodo_retorno_anios` | entero | años | Periodo de retorno T |
| `lluvia_24h_mm` | decimal | mm | Lluvia en 24 h esperada una vez cada T años |
| `anios_usados` | entero | años | Años completos usados en el ajuste |
| `max_observado_mm` | decimal | mm | Máximo diario observado en la serie |

## `tendencias_31097.csv`
Tendencia lineal de la estación Mérida (CONAGUA).

Fuente: C7.2 · Granularidad: estación · Clave: `estacion` · Cobertura: — · Filas: 1

| Columna | Tipo | Unidad | Descripción |
|---|---|---|---|
| `estacion` | texto |  | Clave de estación |
| `tendencia_precip_mm_por_decada` | decimal | mm/década | Pendiente del total anual |
| `anios_completos` | entero | años | Años completos usados |
| `tendencia_dias_>=50mm_por_decada` | decimal | días/década | Pendiente de los días con ≥50 mm |

## `climatologia_mensual_31044_1991_2020.csv`
Climatología mensual 1991–2020 de Mérida (OBS).

Fuente: C7.1 · Granularidad: mes del año · Clave: `mes` · Cobertura: — · Filas: 12

| Columna | Tipo | Unidad | Descripción |
|---|---|---|---|
| `mes` | entero | 1–12 | Mes del año |
| `promedio_mm` | decimal | mm | Promedio mensual |
| `mediana_mm` | decimal | mm | Mediana mensual |
| `minimo_mm` | decimal | mm | Mínimo mensual |
| `maximo_mm` | decimal | mm | Máximo mensual |
| `anios_validos` | entero | años | Años con ese mes completo |

## `promedio_anual_por_estacion_1991_2020.csv`
Lluvia anual media 1991–2020 por estación (para mapas).

Fuente: C7.1 · Granularidad: estación · Clave: `clave` · Cobertura: — · Filas: 8

| Columna | Tipo | Unidad | Descripción |
|---|---|---|---|
| `clave` | texto |  | Clave de estación |
| `nombre` | texto |  | Nombre |
| `latitud` | decimal | grados | Latitud |
| `longitud` | decimal | grados | Longitud |
| `precip_anual_media_mm` | decimal | mm/año | Media de los años completos 1991–2020 |
| `anios_completos` | entero | años | Años completos usados |

## `eventos_extraordinarios_>=100mm.csv`
Días con ≥100 mm en 24 h en estaciones urbanas, con el ciclón asociado cuando aplica.

Fuente: C7.3 · Granularidad: evento (estación-día) · Clave: `estacion + fecha` · Cobertura: 1954-08 – 2026-06 · Filas: 76

| Columna | Tipo | Unidad | Descripción |
|---|---|---|---|
| `estacion` | texto |  | Clave de estación |
| `fecha` | fecha | AAAA-MM-DD | Día |
| `precip_mm` | decimal | mm/24 h | Lluvia del día |
| `nombre` | texto |  | Nombre de la estación |
| `evento_asociado` | texto |  | Ciclón de las reseñas del SMN cuando el día cae en su ventana; vacío si no hay |

## `dashboard_lluvia_mensual_por_estacion.csv`
Tabla para el dashboard: lluvia mensual de las 5 estaciones urbanas. Mes sin datos suficientes = celdas vacías.

Fuente: C7.1 · Granularidad: estación-mes · Clave: `estacion_clave + fecha` · Cobertura: 1951-01 – 2026-09 · Filas: 2,329

| Columna | Tipo | Unidad | Descripción |
|---|---|---|---|
| `fecha` | fecha | AAAA-MM-01 | Primer día del mes |
| `sector` | texto |  | Norte, Poniente u Oriente (aproximado por coordenadas; el Centro no tiene estación) |
| `estacion_clave` | texto |  | Clave de estación |
| `estacion` | texto |  | Nombre de la estación |
| `lluvia_mm` | decimal | mm/mes | Suma del mes; vacío si no hay ≥25 días con dato |
| `dias_con_lluvia` | entero | días | Días con ≥1 mm |
| `eventos_intensos` | entero | días | Días con ≥50 mm en 24 h |
| `dias_con_dato` | entero | días | Días del mes con dato |
| `nota` | texto |  | Motivo si el mes quedó vacío |

## `meses_invalidados.csv`
Meses descartados por la regla de ceros espurios (el original sigue en insumo_SMN_CONAGUA_estaciones/).

Fuente: C7.1 · Granularidad: estación-mes · Clave: `estacion + mes` · Cobertura: — · Filas: 130

| Columna | Tipo | Unidad | Descripción |
|---|---|---|---|
| `estacion` | texto |  | Clave de estación |
| `mes` | texto | AAAA-MM | Mes descartado |
| `dias_con_dato` | entero | días | Días que el original traía con dato (todos en 0.0) |
| `motivo` | texto |  | Condición de la regla que se cumplió |

## `estaciones_claves_territoriales.csv`
Clave territorial de cada estación según el Marco Geoestadístico 2025 de INEGI, para cruzar con otras tablas.

Fuente: C7.1 · Granularidad: estación · Clave: `clave` · Cobertura: — · Filas: 9

| Columna | Tipo | Unidad | Descripción |
|---|---|---|---|
| `clave` | texto |  | Clave de estación |
| `nombre` | texto |  | Nombre |
| `latitud` | decimal | grados | Latitud |
| `longitud` | decimal | grados | Longitud |
| `cve_ent` | texto |  | Entidad (31 = Yucatán) |
| `cve_mun` | texto |  | Municipio (050 = Mérida) |
| `nom_mun` | texto |  | Nombre del municipio |
| `cve_loc` | texto |  | Localidad (si cae en AGEB urbana) |
| `cve_ageb` | texto |  | AGEB urbana |
| `cvegeo_ageb` | texto |  | Clave geoestadística completa de la AGEB (13 dígitos) |
| `ubicacion` | texto |  | Cómo se resolvió el cruce espacial |
