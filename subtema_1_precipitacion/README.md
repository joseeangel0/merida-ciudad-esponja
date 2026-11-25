# Subtema 1 — Precipitación y eventos de lluvia en Mérida

Pregunta: **¿Cómo se distribuye la lluvia en Mérida y cómo ha cambiado con el tiempo?**

| Entregable | Archivo |
|---|---|
| Documento: matriz 9×3, fichas, hallazgos y visualizaciones | `documento/fuentes_precipitacion_merida.pdf` (fuente LaTeX: `.tex`) |
| Catálogo de las 27 fuentes y tablas resumen | `catalogo_fuentes_precipitacion_merida.xlsx` |
| Dashboard interactivo (HTML, sin servidor) | `dashboard/index.html` |
| Documentación de datos: diccionario, manifiestos de procedencia y reporte de calidad | `datos/07_Datos_propios/README.md`, `datos/MANIFIESTO_*.csv`, `datos/REPORTE_CALIDAD.md` |
| Datos, una carpeta por categoría | `datos/01_INEGI` … `datos/09_AR` |

## Las 9 categorías (3 fuentes cada una)
| Carpeta | Contenido |
|---|---|
| `01_INEGI` | Isoyetas, índices de extremos climáticos y Marco Geoestadístico de Yucatán |
| `02_datos_gob_mx` | Lluvia mensual estatal del SMN, declaratorias de CENAPRED y catálogo de estaciones de CONAGUA |
| `03_SIEGY` | Indicadores y boletines de datos.yucatan.gob.mx. SIEGY ya no publica datos de lluvia |
| `04_GeoPortal_Merida` | Atlas de Riesgos, estudio de cambio climático y PACMUN. Las capas del Geoportal solo se pueden ver en el visor |
| `05_Solicitudes_gobierno` | `solicitudes_sugeridas.md`: 3 solicitudes de información listas para enviar en la PNT |
| `06_Scraping` | Datos capturados por scraping: SIVEA (SMN), boletines de PROCIVY 2019–2026 e índice de notas del Diario de Yucatán. Scripts en `scripts/scraping_*.py` |
| `07_Datos_propios` | Tablas calculadas por el equipo (CSV listos para el HTML) a partir de `insumo_SMN_CONAGUA_estaciones/` |
| `08_LiDAR` | MDT/MDS de INEGI (5 m y 1.5 m) y CEM 15 m. Ver `README.md`: el "LiDAR" de INEGI para Mérida es fotogramétrico |
| `09_AR` | Edificios del centro: Overture, alturas calculadas con INEGI y OSM |
| `_excluidas_fuera_de_categorias` | Fuentes internacionales retiradas del catálogo (NOAA, CHIRPS, ERA5, NASA POWER, IBTrACS y otras) |

## Regenerar todo
```bash
python3 -m venv .venv && .venv/bin/pip install -r scripts/requirements.txt
.venv/bin/python scripts/procesar_datos.py                       # SMN -> datos/07_Datos_propios/ (ceros espurios -> sin dato)
.venv/bin/python scripts/scraping_smn_sivea.py                  # captura el SIVEA (SMN) y la fusiona con lo anterior; repetir cada ~60 días
.venv/bin/python scripts/scraping_procivy.py                    # boletines de PROCIVY 2019–2026 (~7 min)
.venv/bin/python scripts/scraping_diario_yucatan.py             # índice de notas del Diario (~10 min)
.venv/bin/python scripts/procesar_pnt.py <carpeta con los ZIP de la PNT>  # respuestas PNT -> datos/05_Solicitudes_gobierno/ (anonimiza)
.venv/bin/python scripts/procesar_esma_drive.py <carpeta con MERIDA_2022_0[456].xlsb>  # extra: lluvia cada 10 min (Drive del Organismo de Cuenca)
.venv/bin/python scripts/generar_csv_dashboard.py                # CSV mensual + dashboard/data.js
.venv/bin/python scripts/generar_documentacion.py                # diccionario, manifiestos, claves AGEB y reporte de calidad
.venv/bin/python scripts/descargar_nasa_lidar.py               # NASA GEDI/ICESat-2 -> datos/08_LiDAR/NASA_GEDI_ICESat2/ (cuenta Earthdata)
cd scripts && ../.venv/bin/python generar_entregables.py         # figuras + Excel + .tex
cd ../documento && tectonic fuentes_precipitacion_merida.tex     # .tex -> PDF
```
Para agregar o editar una fuente, modifica `scripts/fuentes.py`; de ahí salen el Excel y el PDF.

## Pendientes
1. **C5.1 (CONAGUA):** la lluvia diaria y horaria completa de las estaciones de Mérida está en un CD de $13 MXN (Ciudad de México, con cita) que el equipo decidió no recoger. Como extra hay lluvia cada 10 minutos de abril a junio de 2022 (ESMA «MERIDA», carpeta de Drive que indicó el Organismo de Cuenca); los archivos de 2025 y 2026 no sirven. Es la única lluvia por intensidad que tenemos.
2. **Seguir capturando el SIVEA:** `scripts/scraping_smn_sivea.py` fusiona cada captura con la serie anterior, pero el visor solo guarda 90 días; hay que correrlo al menos cada ~60 días. Sin eso, la serie queda como una foto del 27-ago al 24-nov-2026.
3. Tablero de Power BI de C3.3 y capas del Geoportal de Mérida (C4.1): solo se pueden consultar en línea.
4. Los reportes de drenaje del Ayuntamiento no incluyen 2023.
