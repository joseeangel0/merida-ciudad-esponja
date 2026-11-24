# Subtema 1 — Precipitación y eventos de lluvia en Mérida

Pregunta: **¿Cómo se distribuye la lluvia en Mérida y cómo ha cambiado con el tiempo?**

| Entregable | Archivo |
|---|---|
| Documento: matriz 9×3, fichas, hallazgos y visualizaciones | `documento/fuentes_precipitacion_merida.pdf` (fuente LaTeX: `.tex`) |
| Catálogo de las 27 fuentes y tablas resumen | `catalogo_fuentes_precipitacion_merida.xlsx` |
| Datos, una carpeta por categoría | `datos/01_INEGI` … `datos/09_AR` |

## Las 9 categorías (3 fuentes cada una)
| Carpeta | Contenido |
|---|---|
| `01_INEGI` | Isoyetas, índices de extremos climáticos y Marco Geoestadístico de Yucatán |
| `02_datos_gob_mx` | Lluvia mensual estatal del SMN, declaratorias de CENAPRED y catálogo de estaciones de CONAGUA |
| `03_SIEGY` | Indicadores y boletines de datos.yucatan.gob.mx. SIEGY ya no publica datos de lluvia |
| `04_GeoPortal_Merida` | Atlas de Riesgos, estudio de cambio climático y PACMUN. Las capas del Geoportal solo se pueden ver en el visor |
| `05_Solicitudes_gobierno` | `solicitudes_sugeridas.md`: 3 solicitudes de información listas para enviar en la PNT |
| `06_Scraping` | 3 scripts de ejemplo (SMN SIVEA, PROCIVY, Diario de Yucatán), cada uno con su CSV de muestra |
| `07_Datos_propios` | Tablas calculadas por el equipo (CSV listos para el HTML) a partir de `insumo_SMN_CONAGUA_estaciones/` |
| `08_LiDAR` | MDT/MDS de INEGI (5 m y 1.5 m) y CEM 15 m. Ver `README.md`: el "LiDAR" de INEGI para Mérida es fotogramétrico |
| `09_AR` | Edificios del centro: Overture, alturas calculadas con INEGI y OSM |
| `_excluidas_fuera_de_categorias` | Fuentes internacionales retiradas del catálogo (NOAA, CHIRPS, ERA5, NASA POWER, IBTrACS y otras) |

## Regenerar todo
```bash
python3 -m venv .venv && .venv/bin/pip install -r scripts/requirements.txt
.venv/bin/python scripts/procesar_datos.py                       # SMN -> datos/07_Datos_propios/
cd scripts && ../.venv/bin/python generar_entregables.py         # figuras + Excel + .tex
cd ../documento && tectonic fuentes_precipitacion_merida.tex     # .tex -> PDF
```
Para agregar o editar una fuente, modifica `scripts/fuentes.py`; de ahí salen el Excel y el PDF.

## Pendientes
1. Enviar las 3 solicitudes de información (`datos/05_Solicitudes_gobierno/solicitudes_sugeridas.md`).
2. Programar el scraping del SMN para que corra cada semana (las estaciones automáticas solo guardan 90 días).
3. Opcional: crear una cuenta en NASA Earthdata para descargar GEDI/ICESat-2 (único LiDAR real sobre Mérida).
4. Conectar `datos/07_Datos_propios/` con `merida_ciudad_esponja_prototipo.html`.
