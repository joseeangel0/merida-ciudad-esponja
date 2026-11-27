# Mérida, Ciudad Esponja

Proyecto colaborativo de visualización sobre la lluvia y el agua en Mérida, Yucatán (9 subtemas). Este repositorio contiene el **Subtema 1: Precipitación y eventos de lluvia** (Equipo 1).

> **Pregunta guía:** ¿Cómo se distribuye la lluvia en Mérida y cómo ha cambiado con el tiempo?

## Equipo

**Equipo 1** · Diego Loria · Rama Marin · José Ángel Pech

## Qué hay aquí

| Qué | Dónde |
|---|---|
| **Booklet (entrega final)**: ficha, CSV por escena y 4 escenas en D3 | [`booklet/`](booklet/) · capítulo completo en `booklet/graficas/capitulo.html` |
| **Dashboard interactivo** (lluvia por estación, ciclo anual, extremos, periodos de retorno, mapa) | [`subtema_1_precipitacion/dashboard/`](subtema_1_precipitacion/dashboard/) · publicado en https://joseeangel0.github.io/merida-ciudad-esponja/ |
| **Catálogo de 27 fuentes** (matriz 9 categorías × 3) | [`subtema_1_precipitacion/catalogo_fuentes_precipitacion_merida.xlsx`](subtema_1_precipitacion/catalogo_fuentes_precipitacion_merida.xlsx) y [`fuentes_subtema1_precipitacion.csv`](subtema_1_precipitacion/fuentes_subtema1_precipitacion.csv) |
| **Documento de fuentes** (fichas, hallazgos, visualizaciones) | [`subtema_1_precipitacion/documento/fuentes_precipitacion_merida.pdf`](subtema_1_precipitacion/documento/fuentes_precipitacion_merida.pdf) |
| **Datos**, una carpeta por categoría | [`subtema_1_precipitacion/datos/`](subtema_1_precipitacion/datos/) |
| **Scripts** (procesamiento y generación de entregables) | [`subtema_1_precipitacion/scripts/`](subtema_1_precipitacion/scripts/) |

Detalle del subtema, cómo regenerarlo todo y pendientes: [`subtema_1_precipitacion/README.md`](subtema_1_precipitacion/README.md).

## Estado de las fuentes (24/11/2026)

| Categoría | Estado |
|---|---|
| C1 INEGI (3) | Descargadas (los ZIP pesados no están en Git) |
| C2 datos.gob.mx (3) | Completas |
| C3 SIEGY (3) | C3.1 y C3.2 completas; **C3.3 parcial** (solo el boletín en PDF; el tablero Power BI no se puede descargar) |
| C4 GeoPortal / Ayuntamiento (3) | C4.2 y C4.3 descargadas (PDF pesados fuera de Git); **C4.1 solo consulta en línea** (visor WMS) |
| C5 Solicitudes PNT (3) | **Las tres respondieron (26 a 30-oct-2026).** C5.2 (Ayuntamiento) y C5.3 (PROCIVY) procesadas y anonimizadas; **C5.1 (CONAGUA)**: la lluvia horaria completa está en un CD de $13 MXN que no se recogió; como extra hay lluvia cada 10 minutos de abril a junio de 2022 (carpeta de Drive del Organismo de Cuenca) |
| C6 Scraping (3) | **Datos reales capturados el 24-nov-2026:** SIVEA (SMN, 90 días de 5 estaciones de Yucatán), boletines de PROCIVY 2019–2026 e índice de notas del Diario. El SIVEA hay que seguir capturándolo (solo guarda 90 días) y su lluvia de Progreso no coincide con la serie diaria del SMN el 7-sep-2026; «MERIDA» casi no transmite |
| C7 Datos propios (3) | Completas (series, índices extremos, periodos de retorno, eventos ≥100 mm) |
| C8 LiDAR (3) | C8.1 y C8.2 descargadas; C8.3 (NASA GEDI/ICESat-2) descargada y recortada a Mérida (única fuente LiDAR real del catálogo) |
| C9 AR (3) | Completas (edificios de Overture, alturas derivadas, OSM) |

> **Los «LiDAR» de INEGI para Mérida (C8.1) son fotogramétricos**, no un vuelo LiDAR. Ver [`datos/08_LiDAR/README.md`](subtema_1_precipitacion/datos/08_LiDAR/README.md).

## Documentación de los datos

| Qué | Archivo |
|---|---|
| Diccionario de columnas, clave, granularidad, cobertura y unidades de cada tabla | [`datos/07_Datos_propios/README.md`](subtema_1_precipitacion/datos/07_Datos_propios/README.md) y [`diccionario_columnas.csv`](subtema_1_precipitacion/datos/07_Datos_propios/diccionario_columnas.csv) |
| Procedencia de las 27 fuentes (URL, versión, fecha de extracción, licencia, responsable) | [`datos/MANIFIESTO_FUENTES.csv`](subtema_1_precipitacion/datos/MANIFIESTO_FUENTES.csv) |
| Cada archivo con tamaño, SHA-256 y si está en Git | [`datos/MANIFIESTO_ARCHIVOS.csv`](subtema_1_precipitacion/datos/MANIFIESTO_ARCHIVOS.csv) |
| Reporte de calidad y registros descartados | [`datos/REPORTE_CALIDAD.md`](subtema_1_precipitacion/datos/REPORTE_CALIDAD.md), [`meses_invalidados.csv`](subtema_1_precipitacion/datos/07_Datos_propios/meses_invalidados.csv) |
| Respuestas de la PNT: tablas limpias y anonimizadas, cartas oficiales y controles de calidad | [`datos/05_Solicitudes_gobierno/README.md`](subtema_1_precipitacion/datos/05_Solicitudes_gobierno/README.md) |
| Clave territorial (municipio y AGEB del INEGI) de cada estación | [`estaciones_claves_territoriales.csv`](subtema_1_precipitacion/datos/07_Datos_propios/estaciones_claves_territoriales.csv) |

## Calidad de datos: ceros que eran faltantes

Algunas estaciones del SMN reportan **0.0 mm durante meses completos de la temporada de lluvias** (por ejemplo, FIUADY en junio de 2020, cuando las demás estaciones registraron ~580 mm). Son faltantes codificados como cero. [`procesar_datos.py`](subtema_1_precipitacion/scripts/procesar_datos.py) los deja **sin dato** cuando un mes completo suma 0.0 mm y cae entre junio y octubre, o forma una racha de 3 o más meses seguidos en cero. Esto subió, por ejemplo, el promedio anual 1991–2020 de FIUADY de 939 a 1,109 mm.

Los sectores del dashboard (Norte, Poniente, Oriente) son aproximados por coordenadas; **el Centro no tiene estación**.

## Datos pesados fuera de Git

No se versionan los ZIP de INEGI, los rásteres y modelos de elevación de `08_LiDAR/`, los PDF grandes del Ayuntamiento ni los HDF5 de NASA. Se obtienen de las URL del [catálogo](subtema_1_precipitacion/fuentes_subtema1_precipitacion.csv).

## Reglas del repositorio

Ver [`AGENTS.md`](AGENTS.md): matriz 9×3 estricta, `scripts/fuentes.py` como única fuente de verdad del catálogo (el Excel, el LaTeX y el PDF se **generan**, no se editan a mano) y commits en español con formato Conventional Commits.

## Licencia y fuentes

**Privacidad:** los Excel y PDF de reportes del Ayuntamiento traen nombre, teléfono y dirección de ciudadanos y **no se publican**; solo se incluyen conteos por día, mes, AGEB y colonia.

Los datos pertenecen a sus instituciones (INEGI, SMN/CONAGUA, CENAPRED, Gobierno de Yucatán, Ayuntamiento de Mérida, Overture Maps, OpenStreetMap, NASA); cada uno conserva sus términos de uso, indicados en el catálogo. Edificios de Overture y OSM: licencia ODbL.
