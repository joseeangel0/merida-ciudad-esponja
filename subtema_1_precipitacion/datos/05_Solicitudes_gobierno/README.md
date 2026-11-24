# 05_Solicitudes_gobierno — respuestas de la PNT (C5), limpias y anonimizadas

Generado el 2026-11-24 por `scripts/generar_documentacion.py`. Responsable: Equipo 1 (Diego Loria, Rama Marin, José Ángel Pech).

Fuente: respuestas a las solicitudes de acceso a la información enviadas el 01-oct-2026 por la PNT a CONAGUA (C5.1), el Ayuntamiento de Mérida (C5.2) y PROCIVY (C5.3). Procesamiento: `scripts/procesar_pnt.py`. En `respuestas/` están las cartas oficiales (sin metadatos). **Los Excel y PDF originales del Ayuntamiento traen nombre, teléfono, dirección y coordenadas de los solicitantes y NO se publican**: aquí solo hay conteos por día, por mes y AGEB, y por colonia. Su huella SHA-256 está en `respuestas_pnt_procedencia.csv`. C5.1 (CONAGUA) respondió que tiene los datos pero solo los entrega en un CD con pago de derechos de reproducción; el equipo decidió no recogerlos. Controles y límites: [`../REPORTE_CALIDAD.md`](../REPORTE_CALIDAD.md).

## Resumen de tablas

| Archivo | Fuente | Granularidad | Clave | Cobertura | Filas |
|---|---|---|---|---|---:|
| [`procivy_eventos_2024_2026.csv`](procivy_eventos_2024_2026.csv) | C5.3 | evento | `fecha_inicio + fenomeno` | 2024-09 – 2027-07 | 18 |
| [`ayuntamiento_reportes_drenaje_dia.csv`](ayuntamiento_reportes_drenaje_dia.csv) | C5.2 | día × departamento × servicio × procedencia | `fecha_solicitud + departamento + servicio + procedencia` | 2024-01 – 2026-10 | 19,232 |
| [`ayuntamiento_reportes_drenaje_ageb_mes.csv`](ayuntamiento_reportes_drenaje_ageb_mes.csv) | C5.2 | mes × AGEB × servicio × origen | `mes + cvegeo_ageb + servicio + origen` | 2024-01 – 2026-10 | 20,641 |
| [`ayuntamiento_desague_calles_historico_dia.csv`](ayuntamiento_desague_calles_historico_dia.csv) | C5.2 | día × zona | `fecha_solicitud + zona` | 2018-01 – 2022-12 | 236 |
| [`ayuntamiento_desague_calles_litros_colonia_dia.csv`](ayuntamiento_desague_calles_litros_colonia_dia.csv) | C5.2 | día × colonia | `fecha + colonia` | 2024-09 – 2026-09 | 408 |
| [`respuestas_pnt_procedencia.csv`](respuestas_pnt_procedencia.csv) | C5 | archivo | `archivo` | — | 11 |
| [`controles_calidad_pnt.csv`](controles_calidad_pnt.csv) | C5 | control | `control` | — | 14 |

## Cómo se relacionan
- `ayuntamiento_reportes_drenaje_dia.csv` y `ayuntamiento_reportes_drenaje_ageb_mes.csv` vienen del mismo XLS (2024–oct-2026); la primera conserva el canal de llegada y la segunda la ubicación por AGEB.
- `origen = trabajo_programado` son programas del propio Ayuntamiento (sin coordenadas ni relación con la lluvia); para ligar reportes con lluvia hay que usar `origen = solicitud`.
- `ayuntamiento_desague_calles_historico_dia.csv` (2018–2022, anexo PDF) y los reportes de 2024–2026 son fuentes distintas con un hueco en 2023: no se deben unir sin tenerlo presente.
- `cvegeo_ageb` se une con `estaciones_claves_territoriales.csv` de `07_Datos_propios` para relacionar reportes con la lluvia de la estación más cercana.

## `procivy_eventos_2024_2026.csv`
Fenómenos meteorológicos que afectaron Mérida según PROCIVY. Las fechas venían como texto libre; se conserva el original. Un registro trae año 2027 (probable error de captura; no se corrigió).

Fuente: C5.3 · Granularidad: evento · Clave: `fecha_inicio + fenomeno` · Cobertura: 2024-09 – 2027-07 · Filas: 18

| Columna | Tipo | Unidad | Descripción |
|---|---|---|---|
| `fecha_texto_original` | texto |  | Fecha tal como la entregó PROCIVY |
| `fecha_inicio` | fecha | AAAA-MM-DD | Primer día del evento (interpretado) |
| `fecha_fin` | fecha | AAAA-MM-DD | Último día del evento (interpretado) |
| `fenomeno` | texto |  | Fenómeno meteorológico |
| `alerta_siat` | texto |  | Alerta del Sistema de Alerta Temprana para Ciclones Tropicales |
| `efectos` | texto |  | Efecto del fenómeno (lluvia moderada, fuerte, intensa…) |
| `afectaciones_merida` | texto |  | Afectaciones en Mérida |
| `viviendas_afectadas` | texto |  | Viviendas afectadas (texto original) |
| `personas_afectadas` | texto |  | Personas o familias afectadas (texto original) |
| `refugios_activados` | texto |  | Refugios activados (texto original) |
| `lamina_lluvia` | texto |  | Lámina de lluvia: remite al SMN, sin cifra |
| `declaratorias` | texto |  | Declaratorias de emergencia o desastre |
| `nota` | texto |  | Advertencia sobre el registro, si la hay |

## `ayuntamiento_reportes_drenaje_dia.csv`
Reportes de drenaje del Ayuntamiento (Dirección de Servicios Públicos), agregados por día. Sin nombres, direcciones ni coordenadas.

Fuente: C5.2 · Granularidad: día × departamento × servicio × procedencia · Clave: `fecha_solicitud + departamento + servicio + procedencia` · Cobertura: 2024-01 – 2026-10 · Filas: 19,232

| Columna | Tipo | Unidad | Descripción |
|---|---|---|---|
| `fecha_solicitud` | fecha | AAAA-MM-DD | Día en que se recibió el reporte |
| `departamento` | texto |  | Drenaje Poniente u Oriente |
| `servicio` | texto |  | Tipo de servicio solicitado |
| `procedencia` | texto |  | Canal por el que llegó (Ayuntatel, app, internet, trabajos programados…) |
| `origen` | texto |  | trabajo_programado (programas del propio Ayuntamiento) o solicitud (todo lo demás) |
| `reportes` | entero | reportes | Reportes recibidos ese día |
| `atendidos` | entero | reportes | De ellos, con estado Atendida |
| `dias_atencion_mediana` | decimal | días | Mediana de días entre solicitud y atención (vacío si no hay fecha de atención) |

## `ayuntamiento_reportes_drenaje_ageb_mes.csv`
Reportes de drenaje por AGEB urbana (INEGI MG 2025) y mes. La AGEB se obtuvo de las coordenadas del reporte, que no se publican.

Fuente: C5.2 · Granularidad: mes × AGEB × servicio × origen · Clave: `mes + cvegeo_ageb + servicio + origen` · Cobertura: 2024-01 – 2026-10 · Filas: 20,641

| Columna | Tipo | Unidad | Descripción |
|---|---|---|---|
| `mes` | texto | AAAA-MM | Mes de la solicitud |
| `cvegeo_ageb` | texto |  | Clave de la AGEB urbana (13 caracteres); SIN_COORDENADAS_VALIDAS o SIN_AGEB_URBANA si no se pudo ubicar |
| `servicio` | texto |  | Tipo de servicio |
| `origen` | texto |  | trabajo_programado o solicitud |
| `reportes` | entero | reportes | Reportes del mes en esa AGEB |

## `ayuntamiento_desague_calles_historico_dia.csv`
Reportes de desagüe de calles inundadas de 2018 a 2022 (anexo PDF del Ayuntamiento), agregados por día. No hay datos de 2023.

Fuente: C5.2 · Granularidad: día × zona · Clave: `fecha_solicitud + zona` · Cobertura: 2018-01 – 2022-12 · Filas: 236

| Columna | Tipo | Unidad | Descripción |
|---|---|---|---|
| `fecha_solicitud` | fecha | AAAA-MM-DD | Día de la solicitud |
| `zona` | texto |  | Poniente u Oriente |
| `reportes` | entero | reportes | Reportes ese día |
| `dias_atencion_mediana` | decimal | días | Mediana de días hasta la atención |

## `ayuntamiento_desague_calles_litros_colonia_dia.csv`
Desagües de calles inundadas de 2024 a 2026 con los litros desalojados (Departamento de Drenaje), por día de atención y colonia.

Fuente: C5.2 · Granularidad: día × colonia · Clave: `fecha + colonia` · Cobertura: 2024-09 – 2026-09 · Filas: 408

| Columna | Tipo | Unidad | Descripción |
|---|---|---|---|
| `fecha` | fecha | AAAA-MM-DD | Día de atención (o de solicitud si no hay) |
| `colonia` | texto |  | Colonia o fraccionamiento (normalizado) |
| `servicios` | entero | servicios | Desagües realizados |
| `litros` | entero | litros | Agua desalojada |

## `respuestas_pnt_procedencia.csv`
Cartas de respuesta publicadas y huella (SHA-256) de los originales que no se publican por traer datos personales.

Fuente: C5 · Granularidad: archivo · Clave: `archivo` · Cobertura: — · Filas: 11

| Columna | Tipo | Unidad | Descripción |
|---|---|---|---|
| `archivo` | texto |  | Archivo |
| `en_git` | texto |  | Si está en el repositorio y, si no, por qué |
| `sha256_original` | texto |  | SHA-256 del archivo recibido |
| `sha256_publicado` | texto |  | SHA-256 de la copia publicada (sin metadatos) |
| `bytes_publicado` | entero | bytes | Tamaño de la copia publicada |

## `controles_calidad_pnt.csv`
Controles medidos al procesar las respuestas de la PNT (totales, coincidencias con las cifras oficiales, duplicados).

Fuente: C5 · Granularidad: control · Clave: `control` · Cobertura: — · Filas: 14

| Columna | Tipo | Unidad | Descripción |
|---|---|---|---|
| `control` | texto |  | Qué se verificó |
| `valor` | texto |  | Resultado |
| `detalle` | texto |  | Detalle |
