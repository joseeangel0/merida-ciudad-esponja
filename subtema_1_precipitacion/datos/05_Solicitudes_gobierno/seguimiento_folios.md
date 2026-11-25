# Seguimiento de solicitudes de información (PNT)

Enviadas el 01/10/2026 por la PNT (se tienen por recibidas el 02/10/2026). Respuestas recibidas del 26 al 30 de octubre de 2026.

| Fuente | Folio | Institución | Respuesta | Datos |
|---|---|---|---|---|
| C5.1 | **340009400252326** | CONAGUA / SMN | 30/10/2026. Tiene lluvia diaria y horaria del Observatorio de Mérida (76644) y de las estaciones «Mérida» y «Mérida CONAGUA», más metadatos. No cabe en la PNT: se entrega en CD ($13 MXN de derechos de reproducción, con cita en Ciudad de México), por SEPOMEX con costo o en USB. No calcularon los máximos de 1 h y 24 h | **No se recogerá** (decisión del equipo). Si se retoma, contacto: modulo.externo@conagua.gob.mx, tel. 55 5174 4000 ext. 1374 |
| C5.2 | **1190579126000596** | Ayuntamiento de Mérida | 27 a 29/10/2026. Pluviómetros municipales y puntos de encharcamiento recurrente: **inexistentes**. Reportes de drenaje y desagüe de calles: **entregados** (XLS, XLSX y PDF) | Procesados y anonimizados: `ayuntamiento_*.csv` |
| C5.3 | **1191217326000207** | Secretaría General de Gobierno (PROCIVY) | 28 a 30/10/2026. Solo desde octubre de 2024 (se pidió desde 2000): 18 fenómenos con su efecto en Mérida | Procesados: `procivy_eventos_2024_2026.csv` |
| (error) | 340009400252226 | CONAGUA | 30/10/2026. Era el folio con el texto dirigido al Ayuntamiento; CONAGUA no tiene esa información. El Organismo de Cuenca Península de Yucatán indica una carpeta de Google Drive con datos de sus estaciones | **Revisada el 24/11/2026: solo sirven 3 meses de 2022** (integrados como extra; ver abajo) |

## Notas
- Las cartas de respuesta (sin metadatos) están en [`respuestas/`](respuestas/). Los Excel y PDF del Ayuntamiento traen datos personales de los solicitantes (nombre, teléfono, dirección, coordenadas) y **no se publican**; su huella SHA-256 está en `respuestas_pnt_procedencia.csv`.
- Plazo para un recurso de revisión: 15 días hábiles desde la notificación de la respuesta (arts. 144 y 145 de la LGTAIP); las respuestas son de finales de octubre.

## Carpeta de Drive del Organismo de Cuenca (revisada el 24/11/2026)
Contiene archivos `.xlsb` mensuales de estaciones automáticas de Yucatán (EMA/ESMA) con lluvia cada 10 minutos, más `metadatos.csv` y `Aclaraciones.pdf`. Para Mérida hay «MERIDA CONAGUA» de febrero a septiembre de 2025 y «MERIDA» de abril a junio de 2022; **no hay archivos de Mérida de 2026**, así que no cubren el temporal de mayo-junio de 2026.

Se descargó y midió una muestra (`MERIDA CONAGUA_2025_07.xlsb`): la resolución sí es de 10 minutos, pero solo trae ~20 % de los registros del mes (≈6 horas por día; faltan unas 20 horas diarias) y suma **1.2 mm** frente a **87.8 mm** de la misma estación en la serie diaria del SMN (CLICOM). Los archivos de mayo a septiembre de 2025 pesan 10–42 KB frente a 124–145 KB de febrero y marzo, por lo que probablemente tienen el mismo problema. **Esos archivos de 2025 no se integraron.** Según `Aclaraciones.pdf`, los faltantes no se pueden reponer y la hora viene en UTC.

**Extra integrado:** los tres archivos de «MERIDA» (ESMA en el sitio del Observatorio) de abril a junio de 2022 sí están completos (99 a 100 % de los registros cada 10 minutos). Se procesaron con `scripts/procesar_esma_drive.py` a `conagua_esma_merida_10min_2022.csv` y `conagua_esma_merida_intensidad_mensual_2022.csv`. Junio de 2022 coincide con la serie diaria del SMN (164.0 mm contra 159.1 mm) y trae un máximo de 13.8 mm en 10 minutos y 40.2 mm en 1 hora (28 de junio); mayo de 2022 difiere de la serie diaria (34.6 mm contra 8.1 mm) y se usa con reserva.

Nota: en `metadatos.csv` las longitudes vienen sin el signo negativo (p. ej. 89.65 en lugar de −89.65).
