# Reglas del Workspace y Contexto del Proyecto

## Contexto del Proyecto: "Mérida, Ciudad Esponja"
Este repositorio contiene el proyecto colaborativo para el sitio web de visualización sobre la lluvia y el agua en Mérida, Yucatán. El sitio cubre 9 subtemas; el entregable final del Equipo 1 es la carpeta `booklet/` (capítulo 04 del booklet, en D3).

El foco principal de este espacio de trabajo es el **Subtema 1: Precipitación y eventos de lluvia**, ubicado en `subtema_1_precipitacion/`.

- **Pregunta guía:** *¿Cómo se distribuye la lluvia en Mérida y cómo ha cambiado con el tiempo?*
- **Idioma del asistente y de los commits:** Siempre responder y redactar en **español**.

---

## Estructura del Repositorio
```text
booklet/                                             # ENTREGA FINAL del booklet: ficha.md, datos/ (CSV por escena) y graficas/ (D3)
Precipitación y eventos de lluvia en Mérida.pdf     # Documento resumen ejecutivo
subtema_1_precipitacion/
├── README.md                                        # Documentación del subtema
├── fuentes_subtema1_precipitacion.csv               # CSV exportado del catálogo de fuentes
├── catalogo_fuentes_precipitacion_merida.xlsx       # GENERADO: Catálogo de 27 fuentes en Excel
├── scripts/
│   ├── fuentes.py                                   # ÚNICA FUENTE DE VERDAD del catálogo (27 fuentes)
│   ├── procesar_datos.py                            # Procesa insumos SMN -> datos/07_Datos_propios/*.csv
│   ├── generar_entregables.py                       # Genera figuras + Excel + documento .tex
│   └── requirements.txt                             # Dependencias Python
├── documento/
│   ├── fuentes_precipitacion_merida.tex             # GENERADO: Fuente LaTeX
│   ├── fuentes_precipitacion_merida.pdf             # GENERADO: Documento final compilado
│   └── figuras/                                     # GENERADAS: Gráficas y mapas para el documento
└── datos/
    ├── 01_INEGI/                                    # Isoyetas, extremos climáticos y marco geoestadístico
    ├── 02_datos_gob_mx/                             # Series mensuales SMN y declaratorias CENAPRED/CNPC
    ├── 03_SIEGY/                                    # Boletines e indicadores presupuestales estatales
    ├── 04_GeoPortal_Merida/                         # Atlas de Riesgos, CC y PACMUN (PDFs)
    ├── 05_Solicitudes_gobierno/                     # PNT: solicitudes sugeridas y seguimiento de folios
    ├── 06_Scraping/                                 # Scripts de ejemplo (SMN SIVEA, PROCIVY, Diario de Yucatán)
    ├── 07_Datos_propios/                            # CSVs calculados listos para visualización
    ├── 08_LiDAR/                                    # Modelos de elevación INEGI (MDT, MDS, CEM)
    ├── 09_AR/                                       # Edificios centro Mérida (Overture, alturas INEGI, OSM)
    └── _excluidas_fuera_de_categorias/              # Fuentes internacionales no categorizadas (NOAA, ERA5, etc.)
```

---

## Reglas del Repositorio (No Negociables)

1. **Matriz 9 × 3 Estricta:**
   - Cada subtema utiliza exactamente **9 categorías** con **3 fuentes** cada una (27 fuentes en total):
     - **C1:** INEGI
     - **C2:** datos.gob.mx
     - **C3:** SIEGY
     - **C4:** GeoPortal / Ayuntamiento de Mérida
     - **C5:** Solicitudes de gobierno (PNT)
     - **C6:** Scraping
     - **C7:** Datos propios
     - **C8:** LiDAR
     - **C9:** AR (Realidad Aumentada)
   - **No se permiten fuentes complementarias** fuera de estas categorías. Si una fuente no encaja en la matriz, debe guardarse en `_excluidas_fuera_de_categorias/` y no incluirse en el catálogo oficial.

2. **Única Fuente de Verdad para Fuentes:**
   - La definición de las 27 fuentes reside **única y exclusivamente en `subtema_1_precipitacion/scripts/fuentes.py`**.
   - **Nunca editar a mano** el Excel (`catalogo_fuentes_precipitacion_merida.xlsx`), el LaTeX (`fuentes_precipitacion_merida.tex`) ni el PDF.
   - Si cambia `fuentes.py`, se deben regenerar los entregables ejecutando:
     ```bash
     cd subtema_1_precipitacion/scripts
     python procesar_datos.py
     python generar_entregables.py
     cd ../documento && tectonic fuentes_precipitacion_merida.tex
     ```

3. **Política de Control de Versiones (Git) y Datos Pesados:**
   - La carpeta `datos/` contiene insumos pesados (~580 MB: ZIPs de INEGI/LiDAR, rásteres, PDFs grandes).
   - **Excluidos de Git:** `.venv/`, `__pycache__/`, `.DS_Store`, `*.zip`, carpetas pesadas de `01_INEGI/`, rásteres de `08_LiDAR/`, `_excluidas_fuera_de_categorias/`, y PDFs pesados de `04_GeoPortal_Merida/`.
   - **Incluidos en Git:** Scripts, documentación (`.md`), CSVs ligeros (`07_Datos_propios`, scraping, muestras), GeoJSON de `09_AR`, el Excel generado y el PDF del documento.
   - **Límite de tamaño:** Si un archivo a comitear pesa **más de 50 MB**, consultar y pedir confirmación explícita al usuario antes de hacer el commit.

4. **Convención de Commits:**
   - Formato **Conventional Commits** en español con scope del subtema:
     - `feat(subtema1): ...`
     - `fix(subtema1): ...`
     - `docs(subtema1): ...`
     - `chore: ...`
     - `refactor(subtema1): ...`

---

## Estado Actual y Pendientes (al 05/10/2026)

### Solicitudes de Información PNT (Enviadas el 01/10/2026, recibidas el 02/10/2026)
- **C5.1 (CONAGUA / SMN):** Folio `340009400252326` — Lluvia cada 10 min EMA Mérida, metadatos y máximos. Límite: 30/10/2026 (con prórroga: 17/11/2026).
- **C5.2 (Ayuntamiento de Mérida):** Folio `1190579126000596` — Pluviómetros municipales y reportes encharcamiento Ayuntatel/Waze. Límite: 30/10/2026 (con prórroga: 17/11/2026).
- **C5.3 (PROCIVY / Sec. Gral. Gobierno):** Folio `1191217326000207` — Afectaciones y declaratorias desde 2000. Límite: 30/10/2026 (con prórroga: 17/11/2026).
- **Nota:** Folio erróneo `340009400252226` enviado a CONAGUA con texto municipal (esperar resolución por incompetencia antes del 07/10/2026).
- **Acción requerida antes del 09/10/2026:** Monitorear "Mi Historial" en la PNT por posibles solicitudes de aclaración.

### Pendientes Técnicos
1. Automatizar/programar scraping del SMN (las estaciones automáticas borran registros después de 90 días).
2. (Hecho) El prototipo HTML se eliminó; las escenas finales están en `booklet/graficas/` y se regeneran sus CSV con `scripts/generar_booklet_datos.py`.
