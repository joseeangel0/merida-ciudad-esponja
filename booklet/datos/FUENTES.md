# Fuentes de los CSV del booklet

Todos los CSV los genera `subtema_1_precipitacion/scripts/generar_booklet_datos.py` a partir de las tablas ya limpias del repositorio (sin escribir ningún valor a mano). UTF-8, coma como separador, fechas ISO, **celda vacía = sin dato**. Lluvia en milímetros.

El procedimiento completo de limpieza (meses con ceros falsos, completitud) está en `subtema_1_precipitacion/datos/REPORTE_CALIDAD.md`.

## `escena-1.csv` · normal climatológica mensual
- **Fuente original:** SMN/CONAGUA, estación 31044 MERIDA (OBS), registros diarios CLICOM. https://smn.conagua.gob.mx/es/climatologia/informacion-climatologica/informacion-estadistica-climatologica
- **Corte:** 25 de septiembre de 2026 (último dato del SMN procesado).
- **Cómo se calculó:** promedio, mediana y máximo de la lluvia mensual de cada mes del año entre 1991 y 2020, con los años que tienen el mes completo (columna `anios_validos`). Viene de `climatologia_mensual_31044_1991_2020.csv` (C7.1).

## `escena-2.csv` · días con 50 mm o más por año
- **Fuente original:** SMN/CONAGUA, estación 31097 MERIDA (CONAGUA), registros diarios CLICOM (misma URL).
- **Corte:** 25 de septiembre de 2026.
- **Cómo se calculó:** días del año con 50 mm o más en 24 horas (`indices_lluvia_extrema_por_anio.csv`, C7.2). `anio_completo = si` cuando el año tiene 12 meses válidos; si no, el conteo puede quedarse corto. `max_diaria_mm` y `fecha_max_diaria` son el día más lluvioso del año con dato válido. 2026 va hasta septiembre y por eso es incompleto.

## `escena-3.csv` · lluvia del día contra reportes de desagüe (un renglón por día)
- **Lluvia:** SMN/CONAGUA, estaciones urbanas 31036, 31044, 31078, 31095 y 31097 (CLICOM). `lluvia_mm` es el promedio de las estaciones con dato ese día; `estaciones_con_dato` dice cuántas entraron (se exigen al menos 4 de 5). Corte: 25-sep-2026.
- **Reportes:** Ayuntamiento de Mérida, respuesta a la solicitud de acceso a la información con folio 1190579126000596, Plataforma Nacional de Transparencia (https://www.plataformadetransparencia.org.mx/). Corte: 29-oct-2026. Solo reportes de «desagüe de calles inundadas» con `origen = solicitud` (sin trabajos programados). Los datos con nombres, teléfonos, direcciones y coordenadas de los solicitantes no se publican; aquí solo hay conteos por día.
- **Periodo:** desde el 1-ene-2024 (entrega de hoja de cálculo 2024–2026). No hay datos de 2023 y la entrega 2018–2022 (anexo en PDF) no se mezcla porque pudo contar distinto.
- **Supuesto:** un día sin filas de reportes cuenta como 0.
- **Cómo se usa en la gráfica:** D3 agrupa los días por lluvia (menos de 10, 10 a 25, 25 a 50 y 50 mm o más; cortes elegidos por el equipo) y calcula la mediana de lluvia y de reportes de cada grupo.

## `escena-4.csv` · el temporal de mayo y junio de 2026, día por día
- **Lluvia:** SMN/CONAGUA, estaciones 31036 (CICY), 31044 (Mérida OBS), 31078 (FIUADY Periférico), 31095 (Col. Emiliano Zapata) y 31097 (Mérida CONAGUA), del 26 de mayo al 10 de junio de 2026. Corte: 25-sep-2026.
- **Reportes:** la misma respuesta del Ayuntamiento (entrega 2024–2026), reportes de desagüe de calles inundadas por día; se repite en cada estación porque es un total de la ciudad (`reportes_desague_dia`).

## `cifras.csv` · las 3 cifras grandes
Cada fila trae valor, unidad, fuente, corte y cómo se calculó. Se pueden recalcular con `escena-1.csv` (75 %), `eventos_extraordinarios_>=100mm.csv` de `07_Datos_propios` (223 mm) y el CSV de reportes diarios de `05_Solicitudes_gobierno` (322 reportes).

## Licencia
Los datos pertenecen al SMN/CONAGUA y al Ayuntamiento de Mérida; se usan con fines académicos y cada uno conserva sus términos de uso.
