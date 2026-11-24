"""Genera la documentación reproducible de los datos del subtema 1.

Salidas (todas en datos/):
  07_Datos_propios/README.md                       Tablas, claves, cobertura y diccionario legible
  07_Datos_propios/diccionario_columnas.csv        Diccionario de columnas (máquina)
  07_Datos_propios/estaciones_claves_territoriales.csv   Estación -> municipio / AGEB (INEGI MG 2025)
  MANIFIESTO_FUENTES.csv                           Procedencia de las 27 fuentes
  MANIFIESTO_ARCHIVOS.csv                          Cada archivo: tamaño, SHA-256, fuente, ¿está en Git?
  REPORTE_CALIDAD.md                               Limpieza, registros descartados y efecto en los resultados

Requisitos: pandas, numpy, pyshp, pyproj (scripts/requirements.txt)
Uso:        python scripts/procesar_datos.py && python scripts/generar_documentacion.py
Los datos de partida deben existir (ZIP de INEGI, insumo SMN en 07_Datos_propios).
"""
import hashlib
import subprocess
import sys
import tempfile
import zipfile
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import warnings

import shapefile  # pyshp
from pyproj import CRS, Transformer

warnings.filterwarnings("ignore", category=UserWarning, module="shapefile")
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from fuentes import CATEGORIAS, FUENTES  # noqa: E402

DATOS = AQUI.parent / "datos"
P7 = DATOS / "07_Datos_propios"
HOY = date.today().isoformat()

RESPONSABLE = "Equipo 1 (Diego Loria, Rama Marin, José Ángel Pech)"  # todos los integrantes, por decisión del equipo

# Fecha en que se bajó cada fuente (no se usa la fecha del archivo: un clon de Git la cambia).
EXTRACCION = {f["id"]: "2026-10-01" for f in FUENTES}
EXTRACCION.update({"C5.1": "—", "C5.2": "—", "C5.3": "—", "C8.3": "2026-10-05",
                   "C7.1": HOY, "C7.2": HOY, "C7.3": HOY})
VERSION = {
    "C1.1": "Edición 2004–2006", "C1.2": "Edición 2023", "C1.3": "Marco Geoestadístico 2025",
    "C2.1": "Serie 1985–2023 (historico.datos.gob.mx)", "C2.2": "CENAPRED 2000–2023; CNPC 2018–2025",
    "C2.3": "Actualizado jun-2025", "C3.1": "Programas presupuestarios 2024–2025",
    "C3.2": "Boletín 2026-3", "C3.3": "Boletín 2025-10", "C4.1": "Capas del Atlas 2017 (WMS)",
    "C4.2": "Publicado 2018 (datos ≤2017)", "C4.3": "Publicado jun-2024", "C5.1": "—", "C5.2": "—",
    "C5.3": "—", "C6.1": "Muestra del 2026-10-01 (SIVEA guarda solo 90 días)", "C6.2": "Temporada 2020",
    "C6.3": "Sitemaps dic-2017 a oct-2026 (muestra de 170 notas)",
    "C7.1": f"Generado {HOY} con procesar_datos.py (datos SMN hasta 2026-09-25)",
    "C7.2": f"Generado {HOY}", "C7.3": f"Generado {HOY}",
    "C8.1": "MDT 5 m (2011–2017); MDT/MDS 1.5 m (edición 2025)", "C8.2": "CEM 4.0 (15 m)",
    "C8.3": "GEDI L2A v002; ICESat-2 ATL08 v007", "C9.1": "Release 2026-09-23.1",
    "C9.2": "Derivado de C8.1 + C9.1", "C9.3": "Base OSM 2026-07-15 (espejo Overpass)",
}

# --------------------------------------------------------------------------- 1. claves territoriales
def claves_territoriales():
    cat = pd.read_csv(P7 / "smn_catalogo_estaciones.csv", dtype={"clave": str})
    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(DATOS / "01_INEGI" / "mg2025_31_yucatan.zip") as z:
            for n in z.namelist():
                if Path(n).stem in ("31a", "31mun"):
                    z.extract(n, tmp)
        base = Path(tmp) / "conjunto_de_datos"
        crs = CRS.from_wkt((base / "31a.prj").read_text())
        tr = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
        a = shapefile.Reader(str(base / "31a"), encoding="latin-1")
        m = shapefile.Reader(str(base / "31mun"), encoding="latin-1")
        campos_m = [f[0] for f in m.fields[1:]]
        nom_mun = {r[campos_m.index("CVE_MUN")]: r[campos_m.index("NOMGEO")] for r in m.records()}

        def dentro(shp, x, y):
            if not (shp.bbox[0] <= x <= shp.bbox[2] and shp.bbox[1] <= y <= shp.bbox[3]):
                return False
            pts, parts = shp.points, list(shp.parts) + [len(shp.points)]
            cruces = 0
            for i in range(len(parts) - 1):  # regla par-impar sobre todos los anillos (maneja huecos)
                ring = pts[parts[i]:parts[i + 1]]
                for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
                    if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                        cruces += 1
            return cruces % 2 == 1

        filas = []
        for r in cat.itertuples():
            x, y = tr.transform(r.longitud, r.latitud)
            fila = dict(clave=r.clave, nombre=r.nombre, latitud=r.latitud, longitud=r.longitud,
                        cve_ent="31", cve_mun="", nom_mun="", cve_loc="", cve_ageb="", cvegeo_ageb="",
                        ubicacion="fuera del Marco Geoestadístico de Yucatán")
            for sh, rec in zip(a.iterShapes(), a.iterRecords()):
                if dentro(sh, x, y):
                    d = dict(zip([f[0] for f in a.fields[1:]], rec))
                    fila.update(cve_mun=d["CVE_MUN"], nom_mun=nom_mun.get(d["CVE_MUN"], ""),
                                cve_loc=d["CVE_LOC"], cve_ageb=d["CVE_AGEB"], cvegeo_ageb=d["CVEGEO"],
                                ubicacion="AGEB urbana")
                    break
            else:
                for sh, rec in zip(m.iterShapes(), m.iterRecords()):
                    if dentro(sh, x, y):
                        d = dict(zip(campos_m, rec))
                        fila.update(cve_mun=d["CVE_MUN"], nom_mun=d["NOMGEO"],
                                    ubicacion="solo municipio (fuera de AGEB urbana)")
                        break
            filas.append(fila)
    df = pd.DataFrame(filas)
    df.to_csv(P7 / "estaciones_claves_territoriales.csv", index=False)
    return df


# --------------------------------------------------------------------------- 2. diccionario
G = "estación-día"; M = "estación-mes"; A = "estación-año"
TABLAS = [
    dict(archivo="smn_catalogo_estaciones.csv", fuente="C7.1", gran="estación", clave="clave",
         fecha=("inicio", "fin"), desc="Catálogo de las 9 estaciones del SMN en Mérida y alrededores, con su cobertura real.",
         cols=[("clave", "texto", "", "Clave de estación del SMN (CLICOM)"), ("nombre", "texto", "", "Nombre de la estación"),
               ("municipio", "texto", "", "Municipio según el SMN"), ("situacion", "texto", "", "OPERANDO o SUSPENDIDA"),
               ("latitud", "decimal", "grados", "Latitud (datum del SMN, ≈WGS84)"), ("longitud", "decimal", "grados", "Longitud"),
               ("altitud_msnm", "entero", "m", "Altitud sobre el nivel del mar"),
               ("inicio", "fecha", "", "Primer día con dato válido"), ("fin", "fecha", "", "Último día con dato válido"),
               ("dias_con_dato", "entero", "días", "Días con dato válido (tras la limpieza)"),
               ("pct_completitud", "decimal", "%", "Días con dato entre los días de inicio a fin")]),
    dict(archivo="smn_precip_diaria.csv", fuente="C7.1", gran=G, clave="estacion + fecha", fecha="fecha",
         desc="Lluvia diaria. Celda vacía = sin dato (nunca 0): incluye los meses descartados por la regla de ceros espurios.",
         cols=[("estacion", "texto", "", "Clave de estación"), ("fecha", "fecha", "AAAA-MM-DD", "Día"),
               ("precip_mm", "decimal", "mm/día", "Precipitación acumulada en 24 h; vacío = sin dato")]),
    dict(archivo="smn_precip_mensual.csv", fuente="C7.1", gran=M, clave="estacion + fecha", fecha="fecha",
         desc="Lluvia mensual con control de completitud (≥80 % de los días del mes).",
         cols=[("estacion", "texto", "", "Clave de estación"), ("fecha", "texto", "AAAA-MM", "Mes"),
               ("precip_mm", "decimal", "mm/mes", "Suma del mes; vacío si completo = False"),
               ("dias_con_dato", "entero", "días", "Días del mes con dato"), ("max_diaria_mm", "decimal", "mm", "Máximo diario del mes"),
               ("dias_mes", "entero", "días", "Días del mes"), ("completo", "booleano", "", "True si dias_con_dato ≥ 80 % de dias_mes")]),
    dict(archivo="smn_precip_anual.csv", fuente="C7.1", gran=A, clave="estacion + anio", fecha="anio",
         desc="Totales e índices anuales. El total solo existe en años con 12 meses válidos; los conteos de días usan los días válidos.",
         cols=[("estacion", "texto", "", "Clave de estación"), ("precip_mm", "decimal", "mm/año", "Suma anual; vacío si meses_validos < 12"),
               ("meses_validos", "entero", "meses", "Meses completos del año"),
               ("dias_lluvia_>=1mm", "entero", "días", "Días con ≥1 mm"), ("dias_>=50mm", "entero", "días", "Días con ≥50 mm"),
               ("dias_>=100mm", "entero", "días", "Días con ≥100 mm"), ("max_diaria_mm", "decimal", "mm", "Máximo diario del año (con los días válidos)"),
               ("anio", "entero", "AAAA", "Año")]),
    dict(archivo="indices_lluvia_extrema_por_anio.csv", fuente="C7.2", gran=A, clave="estacion + anio", fecha="anio",
         desc="Índices de lluvia extrema por año para las estaciones urbanas.",
         cols=[("estacion", "texto", "", "Clave de estación"), ("anio", "entero", "AAAA", "Año"),
               ("precip_mm", "decimal", "mm/año", "Total anual (vacío si el año no está completo)"),
               ("dias_lluvia_>=1mm", "entero", "días", "Días con ≥1 mm"), ("dias_>=50mm", "entero", "días", "Días con ≥50 mm"),
               ("dias_>=100mm", "entero", "días", "Días con ≥100 mm"), ("max_diaria_mm", "decimal", "mm", "Máximo diario del año"),
               ("meses_validos", "entero", "meses", "Meses completos del año")]),
    dict(archivo="periodos_retorno_lluvia_24h.csv", fuente="C7.2", gran="estación × periodo de retorno", clave="estacion + periodo_retorno_anios",
         fecha=None, desc="Lluvia esperada en 24 h por periodo de retorno (Gumbel por momentos sobre el máximo diario anual de años completos).",
         cols=[("estacion", "texto", "", "Clave de estación (solo 31097 y 31044 tienen serie suficiente)"),
               ("periodo_retorno_anios", "entero", "años", "Periodo de retorno T"),
               ("lluvia_24h_mm", "decimal", "mm", "Lluvia en 24 h esperada una vez cada T años"),
               ("anios_usados", "entero", "años", "Años completos usados en el ajuste"),
               ("max_observado_mm", "decimal", "mm", "Máximo diario observado en la serie")]),
    dict(archivo="tendencias_31097.csv", fuente="C7.2", gran="estación", clave="estacion", fecha=None,
         desc="Tendencia lineal de la estación Mérida (CONAGUA).",
         cols=[("estacion", "texto", "", "Clave de estación"), ("tendencia_precip_mm_por_decada", "decimal", "mm/década", "Pendiente del total anual"),
               ("anios_completos", "entero", "años", "Años completos usados"),
               ("tendencia_dias_>=50mm_por_decada", "decimal", "días/década", "Pendiente de los días con ≥50 mm")]),
    dict(archivo="climatologia_mensual_31044_1991_2020.csv", fuente="C7.1", gran="mes del año", clave="mes", fecha=None,
         desc="Climatología mensual 1991–2020 de Mérida (OBS).",
         cols=[("mes", "entero", "1–12", "Mes del año"), ("promedio_mm", "decimal", "mm", "Promedio mensual"),
               ("mediana_mm", "decimal", "mm", "Mediana mensual"), ("minimo_mm", "decimal", "mm", "Mínimo mensual"),
               ("maximo_mm", "decimal", "mm", "Máximo mensual"), ("anios_validos", "entero", "años", "Años con ese mes completo")]),
    dict(archivo="promedio_anual_por_estacion_1991_2020.csv", fuente="C7.1", gran="estación", clave="clave", fecha=None,
         desc="Lluvia anual media 1991–2020 por estación (para mapas).",
         cols=[("clave", "texto", "", "Clave de estación"), ("nombre", "texto", "", "Nombre"), ("latitud", "decimal", "grados", "Latitud"),
               ("longitud", "decimal", "grados", "Longitud"), ("precip_anual_media_mm", "decimal", "mm/año", "Media de los años completos 1991–2020"),
               ("anios_completos", "entero", "años", "Años completos usados")]),
    dict(archivo="eventos_extraordinarios_>=100mm.csv", fuente="C7.3", gran="evento (estación-día)", clave="estacion + fecha", fecha="fecha",
         desc="Días con ≥100 mm en 24 h en estaciones urbanas, con el ciclón asociado cuando aplica.",
         cols=[("estacion", "texto", "", "Clave de estación"), ("fecha", "fecha", "AAAA-MM-DD", "Día"),
               ("precip_mm", "decimal", "mm/24 h", "Lluvia del día"), ("nombre", "texto", "", "Nombre de la estación"),
               ("evento_asociado", "texto", "", "Ciclón de las reseñas del SMN cuando el día cae en su ventana; vacío si no hay")]),
    dict(archivo="dashboard_lluvia_mensual_por_estacion.csv", fuente="C7.1", gran=M, clave="estacion_clave + fecha", fecha="fecha",
         desc="Tabla para el dashboard: lluvia mensual de las 5 estaciones urbanas. Mes sin datos suficientes = celdas vacías.",
         cols=[("fecha", "fecha", "AAAA-MM-01", "Primer día del mes"), ("sector", "texto", "", "Norte, Poniente u Oriente (aproximado por coordenadas; el Centro no tiene estación)"),
               ("estacion_clave", "texto", "", "Clave de estación"), ("estacion", "texto", "", "Nombre de la estación"),
               ("lluvia_mm", "decimal", "mm/mes", "Suma del mes; vacío si no hay ≥25 días con dato"),
               ("dias_con_lluvia", "entero", "días", "Días con ≥1 mm"), ("eventos_intensos", "entero", "días", "Días con ≥50 mm en 24 h"),
               ("dias_con_dato", "entero", "días", "Días del mes con dato"), ("nota", "texto", "", "Motivo si el mes quedó vacío")]),
    dict(archivo="meses_invalidados.csv", fuente="C7.1", gran=M, clave="estacion + mes", fecha=None,
         desc="Meses descartados por la regla de ceros espurios (el original sigue en insumo_SMN_CONAGUA_estaciones/).",
         cols=[("estacion", "texto", "", "Clave de estación"), ("mes", "texto", "AAAA-MM", "Mes descartado"),
               ("dias_con_dato", "entero", "días", "Días que el original traía con dato (todos en 0.0)"),
               ("motivo", "texto", "", "Condición de la regla que se cumplió")]),
    dict(archivo="estaciones_claves_territoriales.csv", fuente="C7.1", gran="estación", clave="clave", fecha=None,
         desc="Clave territorial de cada estación según el Marco Geoestadístico 2025 de INEGI, para cruzar con otras tablas.",
         cols=[("clave", "texto", "", "Clave de estación"), ("nombre", "texto", "", "Nombre"), ("latitud", "decimal", "grados", "Latitud"),
               ("longitud", "decimal", "grados", "Longitud"), ("cve_ent", "texto", "", "Entidad (31 = Yucatán)"),
               ("cve_mun", "texto", "", "Municipio (050 = Mérida)"), ("nom_mun", "texto", "", "Nombre del municipio"),
               ("cve_loc", "texto", "", "Localidad (si cae en AGEB urbana)"), ("cve_ageb", "texto", "", "AGEB urbana"),
               ("cvegeo_ageb", "texto", "", "Clave geoestadística completa de la AGEB (13 dígitos)"),
               ("ubicacion", "texto", "", "Cómo se resolvió el cruce espacial")]),
]


def cobertura(t):
    df = pd.read_csv(P7 / t["archivo"], dtype=str)
    est = next((c for c in ("estacion", "clave", "estacion_clave") if c in df.columns), None)
    n_est = df[est].nunique() if est else None
    f = t["fecha"]
    if isinstance(f, tuple):
        per = f"{df[f[0]].min()[:4]}–{df[f[1]].max()[:4]}"
    elif f:
        s = df[f].dropna()
        per = f"{s.min()[:7] if len(s.iloc[0]) > 4 else s.min()} – {s.max()[:7] if len(s.iloc[0]) > 4 else s.max()}"
    else:
        per = "—"
    return len(df), n_est, per


def documentar_tablas():
    filas, md = [], []
    for t in TABLAS:
        n, ne, per = cobertura(t)
        t["_n"], t["_ne"], t["_per"] = n, ne, per
        for c in t["cols"]:
            filas.append(dict(tabla=t["archivo"], columna=c[0], tipo=c[1], unidad=c[2], descripcion=c[3]))
        # verificar que el diccionario coincide con el archivo
        real = list(pd.read_csv(P7 / t["archivo"], nrows=0).columns)
        if real != [c[0] for c in t["cols"]]:
            sys.exit(f"El diccionario de {t['archivo']} no coincide con sus columnas: {real}")
    pd.DataFrame(filas).to_csv(P7 / "diccionario_columnas.csv", index=False)

    L = [f"# 07_Datos_propios — tablas calculadas por el equipo (C7)\n",
         f"Generado el {HOY} por `scripts/generar_documentacion.py`. Responsable: {RESPONSABLE}.\n",
         "Insumo: registros diarios del SMN/CONAGUA (CLICOM) en `insumo_SMN_CONAGUA_estaciones/`. "
         "Procesamiento: `scripts/procesar_datos.py` (limpieza, agregación, Gumbel) y `scripts/generar_csv_dashboard.py`. "
         "Codificación UTF-8, separador coma, fechas ISO. **Celda vacía = sin dato (nunca 0 mm).** "
         "La limpieza y los registros descartados están en [`../REPORTE_CALIDAD.md`](../REPORTE_CALIDAD.md).\n",
         "## Resumen de tablas\n",
         "| Archivo | Fuente | Granularidad | Clave | Cobertura | Filas | Estaciones |",
         "|---|---|---|---|---|---:|---:|"]
    for t in TABLAS:
        L.append(f"| [`{t['archivo']}`]({t['archivo']}) | {t['fuente']} | {t['gran']} | `{t['clave']}` | {t['_per']} | {t['_n']:,} | {t['_ne'] if t['_ne'] is not None else '—'} |")
    L += ["", "## Cómo se relacionan",
          "- La clave de cruce entre casi todas las tablas es la **clave de estación SMN** (`estacion`, `clave` o `estacion_clave`).",
          "- `estaciones_claves_territoriales.csv` une cada estación con el municipio y la AGEB del INEGI (`cvegeo_ageb`) para cruzar con otras fuentes territoriales.",
          "- Unidades: lluvia en **mm**; coordenadas en grados decimales (≈WGS84); fechas en formato ISO.", ""]
    for t in TABLAS:
        L += [f"## `{t['archivo']}`", f"{t['desc']}", "",
              f"Fuente: {t['fuente']} · Granularidad: {t['gran']} · Clave: `{t['clave']}` · Cobertura: {t['_per']} · Filas: {t['_n']:,}", "",
              "| Columna | Tipo | Unidad | Descripción |", "|---|---|---|---|"]
        L += [f"| `{c[0]}` | {c[1]} | {c[2]} | {c[3]} |" for c in t["cols"]]
        L.append("")
    (P7 / "README.md").write_text("\n".join(L), encoding="utf-8")


# --------------------------------------------------------------------------- 3. manifiestos
REGLAS = [  # (subcadena en la ruta relativa a datos/, fuente) — la primera que coincida
    ("702825267544", "C1.1"), ("889463860136", "C1.2"), ("mg2025_31", "C1.3"),
    ("conagua_sih", "C2.3"), ("conagua_smn", "C2.1"), ("cenapred", "C2.2"), ("declaratorias", "C2.2"),
    ("SIEGY_indicadores", "C3.1"), ("Boletin_2026_03", "C3.2"), ("Boletin_2025_10", "C3.3"),
    ("Atlas_Riesgos", "C4.2"), ("Estudio_Riesgos", "C4.3"), ("PACMUN", "(apoyo de C4)"),
    ("05_Solicitudes", "C5"), ("sivea", "C6.1"), ("procivy", "C6.2"), ("diario_yucatan", "C6.3"),
    ("insumo_SMN", "C7.1"), ("indices_lluvia", "C7.2"), ("periodos_retorno", "C7.2"), ("tendencias", "C7.2"),
    ("eventos_extra", "C7.3"), ("07_Datos_propios", "C7.1"),
    ("MDT_5m", "C8.1"), ("MDT_1_5m", "C8.1"), ("MDS_1_5m", "C8.1"), ("indice_cartas", "C8.1"),
    ("CEM", "C8.2"), ("NASA_GEDI", "C8.3"),
    ("con_altura_inegi", "C9.2"), ("overture", "C9.1"), ("osm_", "C9.3"),
]
OMITIR = {".DS_Store", ".gitkeep", "MANIFIESTO_ARCHIVOS.csv", "MANIFIESTO_FUENTES.csv", "REPORTE_CALIDAD.md"}


def fuente_de(ruta):
    for sub, f in REGLAS:
        if sub.lower() in ruta.lower():
            return f
    return "—"


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def manifiestos():
    cat = {c[0]: c[1] for c in CATEGORIAS}
    pd.DataFrame([dict(
        id=f["id"], categoria=cat[f["cat"]], fuente=f["nombre"], institucion=f["institucion"], url=f["url"],
        acceso_licencia=f["acceso"], version_edicion=VERSION[f["id"]], fecha_extraccion=EXTRACCION[f["id"]],
        formato=f["formato"], estado=f["estado"], responsable=RESPONSABLE) for f in FUENTES]
    ).to_csv(DATOS / "MANIFIESTO_FUENTES.csv", index=False)

    raiz = DATOS.parent.parent
    sal = subprocess.run(["git", "-C", str(raiz), "ls-files", "-z", "-c", "-o", "--exclude-standard"],
                         capture_output=True, text=True, check=True).stdout
    en_git = {x for x in sal.split("\0") if x}
    filas = []
    for p in sorted(DATOS.rglob("*")):
        rel = p.relative_to(DATOS).as_posix()
        if not p.is_file() or p.name in OMITIR or rel.startswith("_excluidas") or "__pycache__" in rel:
            continue
        filas.append(dict(ruta=rel, fuente=fuente_de(rel), tamano_bytes=p.stat().st_size, sha256=sha256(p),
                          en_git="si" if p.relative_to(raiz).as_posix() in en_git else "no"))
    pd.DataFrame(filas).to_csv(DATOS / "MANIFIESTO_ARCHIVOS.csv", index=False)
    return len(filas)


# --------------------------------------------------------------------------- 4. reporte de calidad
def leer_smn_dia(path):
    filas = []
    for linea in path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = linea.strip()
        if s[:4].isdigit() and s[4:5] == "-":
            p = s.split()
            filas.append((p[0], p[1] if len(p) > 1 else "NULO"))
    d = pd.DataFrame(filas, columns=["fecha", "v"])
    d["fecha"] = pd.to_datetime(d["fecha"], errors="coerce")
    d["v"] = pd.to_numeric(d["v"], errors="coerce")
    return d.dropna(subset=["fecha"]).set_index("fecha")["v"]


def promedio_1991_2020(d):
    """Misma regla que procesar_datos.agregar: mes completo >=80 % días; año válido con 12 meses."""
    tot = d.resample("MS").sum(min_count=1)
    ok = d.resample("MS").count() >= 0.8 * tot.index.days_in_month
    tot = tot.where(ok)
    anual = tot.resample("YS").sum(min_count=1).where(ok.resample("YS").sum() >= 12)
    a = anual[(anual.index.year >= 1991) & (anual.index.year <= 2020)].dropna()
    return (round(a.mean(), 1) if len(a) else np.nan), len(a)


def reporte():
    inv = pd.read_csv(P7 / "meses_invalidados.csv", dtype={"estacion": str})
    cat = pd.read_csv(P7 / "smn_catalogo_estaciones.csv", dtype={"clave": str}).set_index("clave")
    diar = pd.read_csv(P7 / "smn_precip_diaria.csv", dtype={"estacion": str}, parse_dates=["fecha"])
    prom_d = pd.read_csv(P7 / "promedio_anual_por_estacion_1991_2020.csv", dtype={"clave": str}).set_index("clave")
    filas = []
    for clave in sorted(cat.index):
        crudo = leer_smn_dia(P7 / "insumo_SMN_CONAGUA_estaciones" / "diarios" / f"dia{clave}.txt")
        limpio = diar[diar.estacion == clave].set_index("fecha")["precip_mm"]
        a0, n0 = promedio_1991_2020(crudo)
        a1, n1 = promedio_1991_2020(limpio)
        despues = prom_d["precip_anual_media_mm"].get(clave, np.nan)
        coincide = "sí" if (np.isnan(a1) and np.isnan(despues)) or abs(a1 - despues) < 0.15 else f"NO ({despues})"
        filas.append(dict(clave=clave, nombre=cat.loc[clave, "nombre"], meses=int((inv.estacion == clave).sum()),
                          dias=int(crudo.notna().sum() - limpio.notna().sum()), a0=a0, n0=n0, a1=a1, n1=n1, ok=coincide))
    T = pd.DataFrame(filas)
    por_motivo = inv.groupby(["estacion", "motivo"]).size().reset_index(name="n")

    L = [f"# Reporte de calidad — datos de lluvia (C7)\n", f"Generado el {HOY} por `scripts/generar_documentacion.py`.\n",
         "## Qué se detectó",
         "Varias estaciones del SMN traían **0.0 mm durante meses completos**, también en plena temporada de lluvias. "
         "Ejemplo: FIUADY en junio de 2020 (el mes de la tormenta Cristóbal) marca 0.0 mm, mientras las demás estaciones urbanas registraron ~540 a 606 mm. "
         "Son faltantes codificados como cero. Tomarlos como datos válidos baja los totales anuales y los promedios.\n",
         "## Regla aplicada (`scripts/procesar_datos.py`, función `limpiar_ceros_espurios`)",
         "Un **mes completo** (≥80 % de sus días con dato) cuyo total es exactamente 0.0 mm se deja **sin dato** si:",
         "1. cae entre junio y octubre (en Mérida no llueve 0 mm todo un mes de la temporada lluviosa), o",
         "2. forma parte de una **racha de 3 o más meses seguidos** en 0.0 mm en la misma estación.\n",
         "Los días de esos meses quedan vacíos en `smn_precip_diaria.csv` y de ahí se propagan a las tablas mensual, anual, de índices, Gumbel y tendencias.\n",
         "## Registros descartados (conservados)",
         f"- **{len(inv)} meses** en {inv.estacion.nunique()} estaciones, listados con su motivo en [`07_Datos_propios/meses_invalidados.csv`](07_Datos_propios/meses_invalidados.csv).",
         "- Los datos originales no se modificaron: siguen en `07_Datos_propios/insumo_SMN_CONAGUA_estaciones/`.\n",
         "| Estación | Nombre | Meses descartados | Días descartados |", "|---|---|---:|---:|"]
    L += [f"| {r.clave} | {r.nombre} | {r.meses} | {r.dias:,} |" for r in T.itertuples()]
    L += ["", "Por motivo:", "", "| Estación | Motivo | Meses |", "|---|---|---:|"]
    L += [f"| {r.estacion} | {r.motivo} | {r.n} |" for r in por_motivo.itertuples()]
    L += ["", "## Efecto en la lluvia anual media 1991–2020 (mm/año)",
          "Mismo cálculo (años con 12 meses válidos) con los datos originales y con los datos limpios.\n",
          "| Estación | Nombre | Antes | Años | Después | Años | Coincide con el CSV publicado |", "|---|---|---:|---:|---:|---:|---|"]
    L += [f"| {r.clave} | {r.nombre} | {r.a0} | {r.n0} | {r.a1} | {r.n1} | {r.ok} |" for r in T.itertuples()]
    L += ["", "Además, la lluvia de 24 h con periodo de retorno de 100 años pasó de 209 a 214 mm en Mérida (OBS) y de 182 a 183 mm en Mérida (CONAGUA); "
          "los años usados en el ajuste bajaron de 44–55 a 36–52.\n",
          "## Limitaciones",
          "- La regla es una **heurística**: un mes realmente seco (0 mm) en la costa, por ejemplo en Progreso, podría descartarse sin ser un faltante. Por eso la lista completa está en `meses_invalidados.csv` para auditarla.",
          "- Progreso (31023) y Conkal (31057) tienen meses descartados, pero no se usan en el dashboard (solo las 5 estaciones urbanas).",
          "- Los años recientes (2026) están incompletos: no hay total anual, pero sí índices de los días disponibles.",
          "- Los sectores del dashboard (Norte, Poniente, Oriente) son aproximados por coordenadas; **el Centro no tiene estación**.",
          "- El cruce estación–AGEB (`estaciones_claves_territoriales.csv`) depende del datum de las coordenadas del SMN; una estación cerca del borde de una AGEB podría caer en la vecina.",
          "- Los datos del SMN son preliminares y no se contrastaron contra otra red de medición.\n",
          "## Procedencia",
          "Cada fuente y archivo está en [`MANIFIESTO_FUENTES.csv`](MANIFIESTO_FUENTES.csv) y [`MANIFIESTO_ARCHIVOS.csv`](MANIFIESTO_ARCHIVOS.csv) "
          "(URL, versión, fecha de extracción, licencia, responsable, tamaño y SHA-256).\n"]
    (DATOS / "REPORTE_CALIDAD.md").write_text("\n".join(L), encoding="utf-8")
    print(T[["clave", "meses", "a0", "a1", "ok"]].to_string(index=False))


if __name__ == "__main__":
    k = claves_territoriales()
    print(k[["clave", "cve_mun", "nom_mun", "cvegeo_ageb", "ubicacion"]].to_string(index=False))
    documentar_tablas()
    n = manifiestos()
    print(f"manifiesto de archivos: {n}")
    reporte()
