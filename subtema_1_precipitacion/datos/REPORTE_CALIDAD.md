# Reporte de calidad — datos de lluvia (C7)

Generado el 2026-11-24 por `scripts/generar_documentacion.py`.

## Qué se detectó
Varias estaciones del SMN traían **0.0 mm durante meses completos**, también en plena temporada de lluvias. Ejemplo: FIUADY en junio de 2020 (el mes de la tormenta Cristóbal) marca 0.0 mm, mientras las demás estaciones urbanas registraron ~540 a 606 mm. Son faltantes codificados como cero. Tomarlos como datos válidos baja los totales anuales y los promedios.

## Regla aplicada (`scripts/procesar_datos.py`, función `limpiar_ceros_espurios`)
Un **mes completo** (≥80 % de sus días con dato) cuyo total es exactamente 0.0 mm se deja **sin dato** si:
1. cae entre junio y octubre (en Mérida no llueve 0 mm todo un mes de la temporada lluviosa), o
2. forma parte de una **racha de 3 o más meses seguidos** en 0.0 mm en la misma estación.

Los días de esos meses quedan vacíos en `smn_precip_diaria.csv` y de ahí se propagan a las tablas mensual, anual, de índices, Gumbel y tendencias.

## Registros descartados (conservados)
- **130 meses** en 6 estaciones, listados con su motivo en [`07_Datos_propios/meses_invalidados.csv`](07_Datos_propios/meses_invalidados.csv).
- Los datos originales no se modificaron: siguen en `07_Datos_propios/insumo_SMN_CONAGUA_estaciones/`.

| Estación | Nombre | Meses descartados | Días descartados |
|---|---|---:|---:|
| 31023 | PROGRESO (OBS) | 40 | 1,211 |
| 31036 | C.I.C.Y. | 0 | 0 |
| 31044 | MERIDA (OBS) | 31 | 949 |
| 31047 | FUERZA AEREA | 0 | 0 |
| 31057 | CONKAL | 6 | 181 |
| 31078 | F.I.U.A.D.Y. (PERIFERICO) | 36 | 1,097 |
| 31079 | MERIDA SANTIAGO | 0 | 0 |
| 31095 | COLONIA EMILIANO ZAPATA | 12 | 364 |
| 31097 | MERIDA (CONAGUA) | 5 | 153 |

Por motivo:

| Estación | Motivo | Meses |
|---|---|---:|
| 31023 | mes de jun-oct con 0.0 mm | 8 |
| 31023 | racha de 3 o más meses seguidos con 0.0 mm | 32 |
| 31044 | mes de jun-oct con 0.0 mm | 10 |
| 31044 | mes de jun-oct con 0.0 mm; racha de 3 o más meses seguidos con 0.0 mm | 9 |
| 31044 | racha de 3 o más meses seguidos con 0.0 mm | 12 |
| 31057 | mes de jun-oct con 0.0 mm | 2 |
| 31057 | racha de 3 o más meses seguidos con 0.0 mm | 4 |
| 31078 | mes de jun-oct con 0.0 mm | 2 |
| 31078 | mes de jun-oct con 0.0 mm; racha de 3 o más meses seguidos con 0.0 mm | 15 |
| 31078 | racha de 3 o más meses seguidos con 0.0 mm | 19 |
| 31095 | mes de jun-oct con 0.0 mm; racha de 3 o más meses seguidos con 0.0 mm | 6 |
| 31095 | racha de 3 o más meses seguidos con 0.0 mm | 6 |
| 31097 | mes de jun-oct con 0.0 mm | 2 |
| 31097 | racha de 3 o más meses seguidos con 0.0 mm | 3 |

## Efecto en la lluvia anual media 1991–2020 (mm/año)
Mismo cálculo (años con 12 meses válidos) con los datos originales y con los datos limpios.

| Estación | Nombre | Antes | Años | Después | Años | Coincide con el CSV publicado |
|---|---|---:|---:|---:|---:|---|
| 31023 | PROGRESO (OBS) | 630.5 | 21 | 630.5 | 21 | sí |
| 31036 | C.I.C.Y. | 1062.1 | 18 | 1062.1 | 18 | sí |
| 31044 | MERIDA (OBS) | 1086.9 | 19 | 1117.1 | 18 | sí |
| 31047 | FUERZA AEREA | 617.3 | 1 | 617.3 | 1 | sí |
| 31057 | CONKAL | 1133.9 | 23 | 1133.9 | 23 | sí |
| 31078 | F.I.U.A.D.Y. (PERIFERICO) | 939.2 | 13 | 1109.0 | 11 | sí |
| 31079 | MERIDA SANTIAGO | nan | 0 | nan | 0 | sí |
| 31095 | COLONIA EMILIANO ZAPATA | 1001.2 | 19 | 997.4 | 18 | sí |
| 31097 | MERIDA (CONAGUA) | 1063.3 | 25 | 1066.5 | 23 | sí |

Además, la lluvia de 24 h con periodo de retorno de 100 años pasó de 209 a 214 mm en Mérida (OBS) y de 182 a 183 mm en Mérida (CONAGUA); los años usados en el ajuste bajaron de 44–55 a 36–52.

## Limitaciones
- La regla es una **heurística**: un mes realmente seco (0 mm) en la costa, por ejemplo en Progreso, podría descartarse sin ser un faltante. Por eso la lista completa está en `meses_invalidados.csv` para auditarla.
- Progreso (31023) y Conkal (31057) tienen meses descartados, pero no se usan en el dashboard (solo las 5 estaciones urbanas).
- Los años recientes (2026) están incompletos: no hay total anual, pero sí índices de los días disponibles.
- Los sectores del dashboard (Norte, Poniente, Oriente) son aproximados por coordenadas; **el Centro no tiene estación**.
- El cruce estación–AGEB (`estaciones_claves_territoriales.csv`) depende del datum de las coordenadas del SMN; una estación cerca del borde de una AGEB podría caer en la vecina.
- Los datos del SMN son preliminares y no se contrastaron contra otra red de medición.

## Respuestas de la PNT (C5): controles y límites
Procesadas con `scripts/procesar_pnt.py`; los controles salen de [`05_Solicitudes_gobierno/controles_calidad_pnt.csv`](05_Solicitudes_gobierno/controles_calidad_pnt.csv).

| Control | Resultado | Detalle |
|---|---|---|
| PROCIVY: eventos registrados | 18 | 2024-09-26 a 2026-10-08 (sin contar la fecha con error) |
| PROCIVY: fechas posteriores a la respuesta (no corregidas) | 1 | 10 JUL. 2027 |
| Drenaje: reportes en el XLS | 65448 | 2024-01-01 a 2026-10-05; sin fecha: 0 |
| Drenaje: reportes por trabajo programado | 31.4 % | sin coordenadas; no responden a la lluvia |
| Drenaje: solicitudes con coordenadas | 90.2 % | el campo trae solo una coma cuando no hay coordenadas |
| Drenaje: AGEB distintas con reportes | 514 | Marco Geoestadístico 2025 |
| Drenaje: solicitudes sin AGEB urbana o sin coordenadas | 10.4 % | quedan como SIN_* |
| Anexo PDF: líneas con folio / reportes únicos | 1,600 / 1,583 | 17 folios repetidos descartados; 2018-01-27 a 2022-12-24 |
| Anexo PDF: años cubiertos | 2018, 2019, 2020, 2021, 2022 | no hay registros de 2023 |
| Desagüe con litros, hoja 2024: filas y litros vs hoja TOTALES | coincide | 150 reportes y 4,570,000 L (oficial: 150 y 4,570,000 L) |
| Desagüe con litros, hoja 2025: filas y litros vs hoja TOTALES | coincide | 187 reportes y 4,678,000 L (oficial: 187 y 4,678,000 L) |
| Desagüe con litros, hoja 2026: filas y litros vs hoja TOTALES | coincide | 243 reportes y 7,474,000 L (oficial: 243 y 7,474,000 L) |
| Desagüe: hoja 30MAY-1JUNIO es un extracto de 2026 | sí | 41 reportes y 1,510,000 L; no se suma dos veces |
| Desagüe: filas con año distinto al de su hoja | 1 | se conservan con su fecha real |

Límites que conviene tener presentes:
- Los reportes de drenaje son **registros administrativos** del Ayuntamiento: miden la demanda atendida, no la superficie inundada, y dependen de que la gente llame.
- El 31 % de los reportes de 2024–2026 es trabajo programado del propio Ayuntamiento; no se relaciona con la lluvia y no tiene coordenadas. Para analizar lluvia contra afectaciones hay que filtrar `origen = solicitud`.
- No hay datos de 2023, y los de 2018–2022 (anexo PDF) y 2024–2026 (XLS) vienen de entregas distintas; no se pueden comparar sin cuidado.
- El Ayuntamiento declaró que **no existen** registros de pluviómetros municipales ni un listado de puntos de encharcamiento recurrente.
- PROCIVY solo entregó desde octubre de 2024 y sus fechas venían en texto libre; un registro con año 2027 se conservó sin corregir y se marcó.
- C5.1 (CONAGUA): la información existe pero aún no se recoge (CD con pago de derechos); no hay datos de esa respuesta en el repositorio.
- Los originales con datos personales no están en el repositorio; su huella SHA-256 está en `05_Solicitudes_gobierno/respuestas_pnt_procedencia.csv`.

## Procedencia
Cada fuente y archivo está en [`MANIFIESTO_FUENTES.csv`](MANIFIESTO_FUENTES.csv) y [`MANIFIESTO_ARCHIVOS.csv`](MANIFIESTO_ARCHIVOS.csv) (URL, versión, fecha de extracción, licencia, responsable, tamaño y SHA-256).
