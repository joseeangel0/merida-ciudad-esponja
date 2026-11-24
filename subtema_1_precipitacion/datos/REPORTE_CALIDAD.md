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

## Procedencia
Cada fuente y archivo está en [`MANIFIESTO_FUENTES.csv`](MANIFIESTO_FUENTES.csv) y [`MANIFIESTO_ARCHIVOS.csv`](MANIFIESTO_ARCHIVOS.csv) (URL, versión, fecha de extracción, licencia, responsable, tamaño y SHA-256).
