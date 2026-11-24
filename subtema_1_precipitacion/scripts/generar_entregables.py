"""
Genera los entregables del subtema 1 (9 categorías × 3 fuentes):
  - documento/figuras/*.pdf|png               (gráficas)
  - catalogo_fuentes_precipitacion_merida.xlsx
  - documento/fuentes_precipitacion_merida.tex

Requisitos: pandas, numpy, matplotlib, openpyxl, pyshp, pyproj
Uso:        cd scripts && python generar_entregables.py   (después de procesar_datos.py)
"""
import io
import zipfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shapefile
from matplotlib.colors import BoundaryNorm, ListedColormap
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from pyproj import CRS, Transformer

from fuentes import CATEGORIAS, FUENTES, VISUALIZACIONES

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "datos"
PROP = DATOS / "07_Datos_propios"
DOC = RAIZ / "documento"
FIG = DOC / "figuras"
FIG.mkdir(parents=True, exist_ok=True)
for f in FIG.glob("*"):
    f.unlink()

# Paleta de referencia (skill dataviz): categórica en orden fijo + rampa azul secuencial
AZUL, NARANJA = "#2a78d6", "#eb6834"
TINTA, TINTA2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
RAMPA_AZUL = ["#f0f6fe", "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

plt.rcParams.update({
    "font.family": "sans-serif", "font.size": 9, "axes.edgecolor": GRID, "axes.labelcolor": TINTA2,
    "xtick.color": TINTA2, "ytick.color": TINTA2, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "axes.titlesize": 10, "axes.titleweight": "bold", "axes.titlecolor": TINTA, "axes.titlelocation": "left",
})

clim = pd.read_csv(PROP / "climatologia_mensual_31044_1991_2020.csv")
anual = pd.read_csv(PROP / "smn_precip_anual.csv", dtype={"estacion": str})
mens = pd.read_csv(PROP / "smn_precip_mensual.csv", dtype={"estacion": str}, parse_dates=["fecha"])
cat = pd.read_csv(PROP / "smn_catalogo_estaciones.csv", dtype={"clave": str})
prom = pd.read_csv(PROP / "promedio_anual_por_estacion_1991_2020.csv", dtype={"clave": str})
retorno = pd.read_csv(PROP / "periodos_retorno_lluvia_24h.csv", dtype={"estacion": str})
eventos = pd.read_csv(PROP / "eventos_extraordinarios_>=100mm.csv", dtype={"estacion": str}).fillna("")
tend = pd.read_csv(PROP / "tendencias_31097.csv")
yuc = pd.read_csv(DATOS / "02_datos_gob_mx" / "conagua_smn_precipitacion_mensual_YUCATAN_y_NACIONAL_1985_2023.csv")
yuc = yuc[yuc.entidad.str.lower().str.startswith("yuc")]
decl = pd.read_csv(DATOS / "02_datos_gob_mx" / "cenapred_declaratorias_2000_2023_YUCATAN.csv", encoding="latin-1")
decl.columns = [c.encode("latin-1").decode("utf-8") if "Ã" in c else c for c in decl.columns]
for c in decl.select_dtypes(include=["object", "str"]):
    decl[c] = decl[c].map(lambda v: v.encode("latin-1").decode("utf-8") if isinstance(v, str) and "Ã" in v else v)
decl = decl[decl["Clave Municipio"] == 31050]
decl = decl[decl["Clasificación Fenómeno"].str.contains("Hidrometeorol")
            & ~decl["Tipo Fenómeno"].str.contains("Temperatura")]
decl = decl[["Fecha Inicio", "Fecha Fin", "Tipo Declaratoria", "Tipo Fenómeno", "Observaciones"]].copy()
decl["_f"] = pd.to_datetime(decl["Fecha Inicio"], dayfirst=True)
decl = decl.sort_values("_f").drop(columns="_f")


# =============================================================== FIGURAS
def guardar(fig, nombre):
    fig.tight_layout()
    fig.savefig(FIG / f"{nombre}.pdf")
    fig.savefig(FIG / f"{nombre}.png", dpi=180)
    plt.close(fig)


# V1 climatograma
fig, ax = plt.subplots(figsize=(6.4, 2.8))
ax.bar(MESES, clim.promedio_mm, color=AZUL, width=0.7)
for i, v in enumerate(clim.promedio_mm):
    if clim.mes[i] in (6, 9):
        ax.text(i, v + 4, f"{v:.0f}", ha="center", va="bottom", color=TINTA, fontsize=8)
ax.set_ylabel("mm")
ax.set_title("Lluvia promedio mensual — Mérida (OBS 31044), 1991–2020")
ax.grid(axis="x", visible=False)
guardar(fig, "v1_climatograma")

# V2 Mérida (31097) vs Yucatán (datos.gob.mx)
s97 = anual[anual.estacion == "31097"].set_index("anio")["precip_mm"].loc[1961:2025]
sy = yuc.set_index("anio")["anual"]
fig, ax = plt.subplots(figsize=(6.4, 3.0))
ax.plot(s97.index, s97.values, color=AZUL, lw=1.6, marker="o", ms=2.5, label="Mérida – estación SMN 31097 (C7.1)")
ax.plot(sy.index, sy.values, color=NARANJA, lw=1.6, marker="o", ms=2.5, label="Promedio de Yucatán – SMN vía datos.gob.mx (C2.1)")
ax.set_ylabel("mm/año")
ax.set_ylim(0, 2200)
ax.set_title("Precipitación anual: Mérida vs. Yucatán")
ax.legend(frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2)
ax.annotate("2020: 1,954 mm", xy=(2020, s97.get(2020)), xytext=(2001, 1900), fontsize=8, color=TINTA,
            arrowprops=dict(arrowstyle="-", color=TINTA2, lw=0.6))
guardar(fig, "v2_serie_anual")

# V3 heatmap mes x año (31097)
h = mens[mens.estacion == "31097"].copy()
h["anio"], h["mes"] = h.fecha.dt.year, h.fecha.dt.month
piv = h.pivot_table(index="mes", columns="anio", values="precip_mm").reindex(columns=range(1961, 2026))
fig, ax = plt.subplots(figsize=(6.6, 2.9))
cmap = ListedColormap(RAMPA_AZUL)
cmap.set_bad("#ffffff")
im = ax.pcolormesh(piv.columns, piv.index, np.ma.masked_invalid(piv.values), cmap=cmap,
                   norm=BoundaryNorm([0, 25, 50, 100, 150, 200, 300, 400, 700], cmap.N), edgecolors="white", linewidth=0.3)
ax.set_yticks(range(1, 13))
ax.set_yticklabels(MESES, fontsize=7)
ax.invert_yaxis()
ax.grid(False)
ax.set_title("Lluvia mensual (mm) — SMN 31097 Mérida, 1961–2025 (blanco = sin dato)")
cb = fig.colorbar(im, ax=ax, pad=0.01, fraction=0.03)
cb.ax.tick_params(labelsize=7)
cb.outline.set_visible(False)
guardar(fig, "v3_heatmap")

# V4 días >= 50 mm por año (31097, años completos)
a97 = anual[anual.estacion == "31097"].set_index("anio").loc[1961:2025]
d50 = a97["dias_>=50mm"].where(a97["precip_mm"].notna())
fig, ax = plt.subplots(figsize=(6.4, 2.5))
ax.bar(d50.index, d50.values, color=AZUL, width=0.75)
ax.set_title("Días con lluvia ≥ 50 mm por año — SMN 31097 Mérida (años completos)")
ax.set_ylabel("días")
ax.grid(axis="x", visible=False)
guardar(fig, "v4_dias_intensos")


# V5 mapa: municipio (Marco Geoestadístico) + isoyetas INEGI + estaciones
def leer_shp(zip_path, base, encoding="latin-1"):
    z = zipfile.ZipFile(zip_path)
    r = shapefile.Reader(shp=io.BytesIO(z.read(base + ".shp")), dbf=io.BytesIO(z.read(base + ".dbf")),
                         shx=io.BytesIO(z.read(base + ".shx")), encoding=encoding)
    t = Transformer.from_crs(CRS.from_wkt(z.read(base + ".prj").decode()), 4326, always_xy=True)
    return r, t


def partes(shape, t):
    idx = list(shape.parts) + [len(shape.points)]
    for a, b in zip(idx[:-1], idx[1:]):
        xs, ys = t.transform(*np.array(shape.points[a:b]).T)
        yield np.asarray(xs), np.asarray(ys)


BB = (-90.05, -89.30, 20.78, 21.36)
fig, ax = plt.subplots(figsize=(5.6, 4.6))
r, t = leer_shp(DATOS / "01_INEGI" / "mg2025_31_yucatan.zip", "conjunto_de_datos/31mun")
for sr in r.iterShapeRecords():
    if sr.record["CVE_MUN"] == "050":
        for xs, ys in partes(sr.shape, t):
            ax.fill(xs, ys, color="#f0efec", zorder=0)
            ax.plot(xs, ys, color=TINTA, lw=1.0)
r, t = leer_shp(DATOS / "01_INEGI" / "702825267544_s.zip", "precipitacionMediaAnual")
etiquetas = {}
for sr in r.iterShapeRecords():
    for xs, ys in partes(sr.shape, t):
        dentro = (xs > BB[0]) & (xs < BB[1]) & (ys > BB[2]) & (ys < BB[3])
        if not dentro.any():
            continue
        if sr.record["CLAVE"] == "H2O":
            ax.plot(xs, ys, color=TINTA2, lw=0.8)
            continue
        ax.plot(xs, ys, color=AZUL, lw=0.9, ls="--", alpha=0.8)
        sel = np.where((xs < BB[1] - 0.01) & (ys > BB[2] + 0.02) & (ys < BB[3] - 0.03))[0]
        if len(sel):
            k = sel[np.argmax(xs[sel])]
            v = sr.record["CLAVE"]
            if v not in etiquetas or xs[k] > etiquetas[v][0]:
                etiquetas[v] = (xs[k], ys[k])
for v, (x, y) in etiquetas.items():
    ax.text(x, y, f"{v} mm", fontsize=7, color=AZUL, ha="right", va="center",
            bbox=dict(fc="white", ec="none", pad=0.5))
p = prom[prom.anios_completos >= 10]
cmap2 = ListedColormap(RAMPA_AZUL[2:8])
sc = ax.scatter(p.longitud, p.latitud, c=p.precip_anual_media_mm, cmap=cmap2,
                norm=BoundaryNorm([600, 700, 800, 900, 1000, 1100, 1200], cmap2.N),
                s=70, edgecolors=TINTA, linewidths=0.8, zorder=5)
offs = {"31095": (7, -3), "31097": (-30, -3), "31044": (7, -4), "31036": (7, -4), "31078": (-24, 2), "31023": (7, -3), "31057": (7, -3)}
for _, s in p.iterrows():
    dx, dy = offs.get(s.clave, (7, 2))
    ax.annotate(f"{s.precip_anual_media_mm:,.0f}", (s.longitud, s.latitud), xytext=(dx, dy),
                textcoords="offset points", fontsize=7, color=TINTA, zorder=6)
ax.set_xlim(BB[0], BB[1])
ax.set_ylim(BB[2], BB[3])
ax.set_aspect("equal")
ax.grid(False)
ax.text(-89.62, 21.32, "Golfo de México", fontsize=8, color=TINTA2, ha="center", style="italic")
ax.set_title("Lluvia media anual (mm): estaciones SMN e isoyetas INEGI")
cb = fig.colorbar(sc, ax=ax, fraction=0.035, pad=0.02, label="mm/año (estaciones)")
cb.ax.tick_params(labelsize=7)
cb.outline.set_visible(False)
guardar(fig, "v5_mapa")

# V7 periodos de retorno
fig, ax = plt.subplots(figsize=(6.0, 2.8))
for est, col in [("31097", AZUL), ("31044", NARANJA)]:
    s = retorno[retorno.estacion == est]
    ax.plot(s.periodo_retorno_anios, s.lluvia_24h_mm, color=col, lw=1.8, marker="o", ms=4,
            label=f"SMN {est} ({int(s.anios_usados.iloc[0])} años)")
ax.axhline(215, color=TINTA2, lw=0.8, ls=":")
ax.text(2.1, 218, "Cristóbal, 4-jun-2020: 215 mm", fontsize=8, color=TINTA2, va="bottom")
ax.set_xscale("log")
ax.set_xticks([2, 5, 10, 25, 50, 100])
ax.set_xticklabels(["2", "5", "10", "25", "50", "100"])
ax.set_xlabel("Periodo de retorno (años)")
ax.set_ylabel("mm en 24 h")
ax.set_ylim(0, 250)
ax.set_title("Lluvia máxima en 24 h esperada según periodo de retorno (Gumbel)")
ax.legend(frameon=False, fontsize=8, loc="lower right")
guardar(fig, "v7_periodos_retorno")


# =============================================================== EXCEL
wb = Workbook()
HEAD = PatternFill("solid", fgColor="1C5CAB")
BOLD_W = Font(bold=True, color="FFFFFF")
WRAP = Alignment(wrap_text=True, vertical="top")
NOMBRE_CAT = {c: n for c, n, _ in CATEGORIAS}
CARPETA_CAT = {c: d for c, _, d in CATEGORIAS}


def hoja(ws, df, anchos=None, nota=None):
    fila0 = 3 if nota else 1
    if nota:
        ws.cell(1, 1, nota).font = Font(italic=True, color="52514E")
    for j, col in enumerate(df.columns, 1):
        c = ws.cell(fila0, j, str(col))
        c.fill, c.font, c.alignment = HEAD, BOLD_W, Alignment(wrap_text=True, vertical="center")
    for i, row in enumerate(df.itertuples(index=False), fila0 + 1):
        for j, v in enumerate(row, 1):
            if isinstance(v, float) and np.isnan(v):
                v = None
            c = ws.cell(i, j, v)
            c.alignment = WRAP
            if isinstance(v, str) and v.startswith("http"):
                c.hyperlink, c.font = v, Font(color="1C5CAB", underline="single")
    ws.freeze_panes = ws.cell(fila0 + 1, 3 if len(df.columns) > 3 else 2)
    ws.auto_filter.ref = f"A{fila0}:{get_column_letter(len(df.columns))}{fila0 + len(df)}"
    for j, col in enumerate(df.columns, 1):
        ws.column_dimensions[get_column_letter(j)].width = (anchos or {}).get(col, max(12, min(40, len(str(col)) + 4)))


fuentes = pd.DataFrame(FUENTES)
fuentes.insert(1, "categoria", fuentes.cat.map(NOMBRE_CAT))
fuentes["carpeta"] = "datos/" + fuentes.cat.map(CARPETA_CAT)
fuentes = fuentes.drop(columns="cat").rename(columns={
    "id": "ID", "categoria": "Categoría", "nombre": "Fuente", "institucion": "Institución", "mide": "Qué contiene",
    "periodo": "Periodo", "resolucion": "Resolución", "formato": "Formato", "acceso": "Acceso", "url": "URL",
    "confiabilidad": "Confiabilidad", "limitaciones": "Limitaciones", "uso": "Uso propuesto",
    "estado": "Estado", "archivos": "Archivos", "carpeta": "Carpeta"})
ws = wb.active
ws.title = "1_Fuentes_27"
hoja(ws, fuentes, {"Categoría": 22, "Fuente": 45, "Institución": 30, "Qué contiene": 40, "Limitaciones": 50,
                   "Uso propuesto": 45, "URL": 45, "Resolución": 28, "Periodo": 22, "Estado": 22, "Archivos": 40,
                   "Carpeta": 26, "Acceso": 24, "Formato": 20})

matriz = pd.DataFrame([{"Categoría": n, **{f"Fuente {k + 1}": f"{x['id']} · {x['nombre']}"
                                            for k, x in enumerate([f for f in FUENTES if f["cat"] == c])}}
                       for c, n, _ in CATEGORIAS])
hoja(wb.create_sheet("2_Matriz_9x3"), matriz, {"Categoría": 28, "Fuente 1": 50, "Fuente 2": 50, "Fuente 3": 50})

vis = pd.DataFrame(VISUALIZACIONES, columns=["ID", "Visualización", "Pregunta", "Fuentes", "Tipo", "Datos"])
hoja(wb.create_sheet("3_Visualizaciones"), vis, {"Visualización": 42, "Pregunta": 32, "Fuentes": 28, "Datos": 50})
hoja(wb.create_sheet("4_Estaciones_SMN"), cat, {"nombre": 28},
     nota="Estaciones climatológicas del SMN usadas como insumo de los datos propios (C7).")
hoja(wb.create_sheet("5_Climatologia_31044"), clim,
     nota="Lluvia mensual 1991–2020, estación 31044 Mérida (OBS). Solo meses con ≥80% de días con dato.")
hoja(wb.create_sheet("6_Periodos_retorno"), retorno,
     nota="Lluvia máxima esperada en 24 h (Gumbel, método de momentos) sobre el máximo diario anual de años completos.")
hoja(wb.create_sheet("7_Eventos_>=100mm"), eventos, {"nombre": 28, "evento_asociado": 30},
     nota="Días con ≥100 mm en estaciones urbanas (C7.3).")
hoja(wb.create_sheet("8_Declaratorias_Merida"), decl, {"Tipo Fenómeno": 22, "Observaciones": 70},
     nota="Declaratorias por fenómenos hidrometeorológicos (sin temperatura extrema) en el municipio de Mérida (31050). Fuente: CENAPRED vía datos.gob.mx (C2.2).")
inv = [{"carpeta": str(f.parent.relative_to(RAIZ)), "archivo": f.name, "tamano_MB": round(f.stat().st_size / 1e6, 2)}
       for f in sorted(DATOS.rglob("*")) if f.is_file() and not f.name.startswith(".")
       and "_excluidas" not in str(f) and "conagua_smn_precipitacion_mensual_estatal/" not in str(f)]
hoja(wb.create_sheet("9_Inventario_archivos"), pd.DataFrame(inv), {"carpeta": 50, "archivo": 55})
wb.save(RAIZ / "catalogo_fuentes_precipitacion_merida.xlsx")


# =============================================================== LATEX
def tex(s):
    s = str(s)
    for a, b in [("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"),
                 ("_", r"\_"), ("{", r"\{"), ("}", r"\}"), ("~", r"\textasciitilde{}"), ("^", r"\^{}"),
                 ("≥", r"$\geq$"), ("≤", r"$\leq$"), ("×", r"$\times$"), ("≈", r"$\approx$"), ("→", r"$\rightarrow$"),
                 ("−", r"$-$"), ("°", r"\textdegree{}")]:
        s = s.replace(a, b)
    return s


def url(u):
    return r"\url{" + u + "}" if u.startswith("http") else tex(u)


def ficha(f):
    archivos = "" if f["archivos"] == "—" else r" · {\small\nolinkurl{" + f["archivos"] + "}}"
    return rf"""
\begin{{ficha}}{{{f['id']} · {tex(f['nombre'])}}}
\begin{{tabularx}}{{\linewidth}}{{@{{}}>{{\leavevmode\color{{tinta2}}\bfseries\raggedright\arraybackslash}}p{{2.9cm}}X@{{}}}}
Institución & {tex(f['institucion'])} \\
Qué contiene & {tex(f['mide'])} \\
Periodo · resolución & {tex(f['periodo'])} · {tex(f['resolucion'])} \\
Formato · acceso & {tex(f['formato'])} · {tex(f['acceso'])} \\
Confiabilidad & {tex(f['confiabilidad'])} \\
Limitaciones & {tex(f['limitaciones'])} \\
Uso propuesto & {tex(f['uso'])} \\
Estado & {tex(f['estado'])}{archivos} \\
Enlace & {url(f['url'])} \\
\end{{tabularx}}
\end{{ficha}}"""


secciones_fichas = ""
for c, n, carpeta in CATEGORIAS:
    secciones_fichas += rf"\subsection{{{c} · {tex(n)}}}" + "\n" + \
        rf"{{\small\color{{tinta2}}Carpeta: \nolinkurl{{datos/{carpeta}/}}}}" + "\n" + \
        "".join(ficha(f) for f in FUENTES if f["cat"] == c) + "\n"


def corto(nombre):
    return nombre.split(" 1:1")[0].split(" (")[0].split(" –")[0].split(" —")[0].split(":")[0].rstrip(",")


matriz_rows = "\n".join(
    rf"\textbf{{{c} {tex(n)}}} & " + " & ".join(f"{f['id']} {tex(corto(f['nombre']))}" for f in FUENTES if f["cat"] == c) + r" \\ \midrule"
    for c, n, _ in CATEGORIAS)

estado_n = {k: sum(f["estado"].startswith(k) for f in FUENTES) for k in ["Descargado", "Generado", "Script", "Pendiente", "Documentado", "Parcial"]}
visrows = "\n".join(rf"{v[0]} & {tex(v[1])} & {tex(v[2])} & {tex(v[3])} \\" for v in VISUALIZACIONES)

ev = eventos[eventos.estacion.isin(["31044", "31097", "31036", "31095"])].drop_duplicates("fecha").head(12)
evrows = "\n".join(rf"{r.fecha} & {r.precip_mm:.1f} & {tex(r.nombre)} ({r.estacion}) & {tex(r.evento_asociado) or '—'} \\" for r in ev.itertuples())
declrows = "\n".join(
    rf"{r['Fecha Inicio']} & {tex(r['Tipo Declaratoria'])} & {tex(r['Tipo Fenómeno'])} & {tex(str(r['Observaciones']).strip())} \\"
    for _, r in decl.iterrows())
retrows = "\n".join(
    rf"{T} & " + " & ".join(f"{retorno[(retorno.estacion == e) & (retorno.periodo_retorno_anios == T)].lluvia_24h_mm.iloc[0]:.0f}" for e in ["31097", "31044"]) + r" \\"
    for T in [2, 5, 10, 25, 50, 100])
catrows = "\n".join(
    rf"{r.clave} & {tex(r.nombre)} & {tex(r.situacion.title())} & {r.inicio[:4]}–{r.fin[:4]} & {r.pct_completitud:.0f}\% \\"
    for r in cat[cat.municipio == "MÉRIDA"].itertuples())

clim_tot = clim.promedio_mm.sum()
pct_lluvias = 100 * clim[clim.mes.between(5, 10)].promedio_mm.sum() / clim_tot
r100 = retorno[retorno.periodo_retorno_anios == 100].lluvia_24h_mm
con_datos = estado_n["Descargado"] + estado_n["Generado"] + estado_n["Script"]

documento = rf"""\documentclass[11pt,a4paper]{{article}}
\usepackage[spanish,es-noshorthands]{{babel}}
\usepackage{{fontspec}}
\setmainfont{{texgyreheros}}[Extension=.otf,UprightFont=*-regular,BoldFont=*-bold,ItalicFont=*-italic,BoldItalicFont=*-bolditalic]
\usepackage[margin=2.2cm]{{geometry}}
\usepackage{{xcolor,graphicx,booktabs,tabularx,longtable,array,enumitem,titlesec,fancyhdr}}
\usepackage[most]{{tcolorbox}}
\usepackage[hidelinks]{{hyperref}}
\usepackage{{xurl}}
\definecolor{{azul}}{{HTML}}{{1C5CAB}}
\definecolor{{tinta2}}{{HTML}}{{52514E}}
\definecolor{{fondo}}{{HTML}}{{F3F7FC}}
\titleformat{{\section}}{{\Large\bfseries\color{{azul}}}}{{\thesection}}{{0.6em}}{{}}
\titleformat{{\subsection}}{{\large\bfseries}}{{\thesubsection}}{{0.6em}}{{}}
\newtcolorbox{{ficha}}[1]{{enhanced,colback=white,colframe=azul!35,boxrule=0.6pt,arc=2pt,
  title={{\bfseries #1}},coltitle=azul,colbacktitle=fondo,fonttitle=\normalsize,left=6pt,right=6pt,top=3pt,bottom=3pt}}
\newtcolorbox{{nota}}{{colback=fondo,colframe=fondo,arc=2pt,left=8pt,right=8pt}}
\setlength{{\parskip}}{{0.5em}}\setlength{{\parindent}}{{0pt}}
\renewcommand{{\arraystretch}}{{1.2}}
\pagestyle{{fancy}}\fancyhf{{}}\renewcommand{{\headrulewidth}}{{0pt}}
\fancyfoot[L]{{\small\color{{tinta2}}Mérida, Ciudad Esponja · Subtema 1}}\fancyfoot[R]{{\small\color{{tinta2}}\thepage}}

\begin{{document}}

{{\color{{azul}}\small\bfseries MÉRIDA CIUDAD ESPONJA}}\\[2pt]
{{\huge\bfseries Precipitación y eventos de lluvia en Mérida}}\\[4pt]
{{\large\color{{tinta2}} Catálogo de fuentes (9 categorías × 3 fuentes), datos y propuesta de visualización}}\\[6pt]
{{\small\color{{tinta2}} Subtema 1 · Versión 2 · 1 de octubre de 2026}}

\begin{{nota}}
\textbf{{Pregunta del subtema:}} ¿Cómo se distribuye la lluvia en Mérida y cómo ha cambiado con el tiempo?\\[3pt]
\textbf{{Entregables:}} este documento; el Excel \texttt{{catalogo\_fuentes\_precipitacion\_merida.xlsx}}; y la carpeta
\texttt{{datos/}}, organizada en una subcarpeta por categoría (\texttt{{01\_INEGI}} … \texttt{{09\_AR}}).
\end{{nota}}

\section{{Resumen}}

\begin{{itemize}}[leftmargin=1.2em,itemsep=2pt]
\item \textbf{{27 fuentes}} en las 9 categorías del proyecto, 3 por categoría. De ellas, {con_datos} ya tienen datos en la carpeta
  (descargados, generados por nosotros o con script y muestra de scraping), {estado_n['Parcial'] + estado_n['Documentado']} solo se pueden consultar en línea
  y {estado_n['Pendiente']} están pendientes (las 3 solicitudes de información, enviadas el 1 de octubre).
\item \textbf{{Cuánto llueve:}} unos \textbf{{{clim_tot:,.0f} mm al año}} en el centro de Mérida (estación 31044, promedio 1991–2020).
\item \textbf{{Cuándo llueve:}} el \textbf{{{pct_lluvias:.0f}\%}} cae de mayo a octubre, con picos en junio ({clim.promedio_mm[5]:.0f} mm)
  y septiembre ({clim.promedio_mm[8]:.0f} mm). Julio baja a {clim.promedio_mm[6]:.0f} mm (canícula).
\item \textbf{{Dónde llueve:}} más hacia el sur y el oriente, menos hacia la costa. Las isoyetas de INEGI van de 600 mm cerca de Progreso
  a 1,000 mm al sur, y las estaciones del SMN registran 630 mm en Progreso contra 1,000–1,130 mm en Mérida y Conkal.
\item \textbf{{Eventos extraordinarios:}} 2020 fue el año más lluvioso (1,954 mm en la estación 31097; 1,802 mm en el promedio de Yucatán).
  Cristóbal dejó 215 mm en un día (4-jun-2020). Mérida tuvo declaratorias oficiales por Isidoro (2002), Emily (2005), Dean (2007) y Gamma/Delta (2020).
\item \textbf{{¿Qué tan raro es?}} Según nuestro ajuste, una lluvia de unos {r100.min():.0f}–{r100.max():.0f} mm en 24 h se espera, en promedio, una vez cada 100 años.
  Cristóbal estuvo en ese rango.
\item \textbf{{¿Ha cambiado?}} El total anual no muestra una tendencia clara ({tend.iloc[0, 1]:+.1f} mm por década, 1961–2025). Los días con 50 mm o más
  fueron más frecuentes en 2020–2025, pero son pocos años para concluir.
\end{{itemize}}

\section{{Matriz de fuentes: 9 categorías × 3}}

{{\small
\begin{{longtable}}{{@{{}}>{{\raggedright\arraybackslash}}p{{2.9cm}}>{{\raggedright\arraybackslash}}p{{4.4cm}}>{{\raggedright\arraybackslash}}p{{4.4cm}}>{{\raggedright\arraybackslash}}p{{4.4cm}}@{{}}}}
\toprule
\textbf{{Categoría}} & \textbf{{Fuente 1}} & \textbf{{Fuente 2}} & \textbf{{Fuente 3}} \\ \midrule
\endhead
{matriz_rows}
\end{{longtable}}}}

\textbf{{Criterios de confiabilidad.}} \emph{{Alta}}: medición directa o publicación oficial con metodología documentada.
\emph{{Media-alta}}: oficial o científica, pero estimada, antigua o sin metadatos. \emph{{Media}}: registro administrativo,
fuente secundaria o con resolución gruesa para una ciudad.

\textbf{{Notas importantes}}
\begin{{itemize}}[leftmargin=1.2em,itemsep=1pt]
\item \textbf{{SIEGY}} ahora redirige a \texttt{{datos.yucatan.gob.mx}} y ya no publica capas ni anuarios. No tiene datos directos de lluvia;
  las 3 fuentes elegidas son de contexto.
\item \textbf{{LiDAR:}} el modelo de INEGI para Mérida se llama ``LiDAR'' en su portal, pero sus metadatos dicen que se hizo con
  imágenes de satélite (es fotogramétrico). El único LiDAR real sobre la ciudad son los satélites de la NASA (C8.3: GEDI e ICESat-2, ya descargados).
\item \textbf{{Datos del SMN:}} los registros diarios de estaciones (CLICOM) no están en datos.gob.mx. Los usamos como insumo de los
  \emph{{datos propios}} (C7) y están en \nolinkurl{{07_Datos_propios/insumo_SMN_CONAGUA_estaciones/}}.
\end{{itemize}}

\section{{Fichas de fuentes}}
{secciones_fichas}

\section{{Estaciones del SMN dentro del municipio}}
\begin{{tabularx}}{{\linewidth}}{{@{{}}lXlll@{{}}}}
\toprule
\textbf{{Clave}} & \textbf{{Nombre}} & \textbf{{Situación}} & \textbf{{Periodo}} & \textbf{{\% días con dato}} \\ \midrule
{catrows}
\bottomrule
\end{{tabularx}}

Recomendación: usar la \textbf{{31097}} para series largas (es la más completa) y la \textbf{{31044}} (observatorio, OMM 76644)
para la climatología. La 31078 (FIUADY) registra totales anormalmente bajos desde 2010.

\section{{Propuesta de visualizaciones}}

\begin{{tabularx}}{{\linewidth}}{{@{{}}lXXX@{{}}}}
\toprule
\textbf{{ID}} & \textbf{{Visualización}} & \textbf{{Pregunta}} & \textbf{{Fuentes}} \\ \midrule
{visrows}
\bottomrule
\end{{tabularx}}

Borradores estáticos con los datos ya descargados (las versiones interactivas se harán en el HTML):

\begin{{center}}
\includegraphics[width=0.9\linewidth]{{figuras/v1_climatograma.pdf}}\\[6pt]
\includegraphics[width=0.9\linewidth]{{figuras/v2_serie_anual.pdf}}
\end{{center}}
{{\small\color{{tinta2}} V2: Mérida suele llover más que el promedio de Yucatán, pero sube y baja en los mismos años. Los huecos son años incompletos.}}

\begin{{center}}
\includegraphics[width=0.93\linewidth]{{figuras/v3_heatmap.pdf}}\\[6pt]
\includegraphics[width=0.9\linewidth]{{figuras/v4_dias_intensos.pdf}}
\end{{center}}

\begin{{center}}
\includegraphics[width=0.78\linewidth]{{figuras/v5_mapa.pdf}}
\end{{center}}
{{\small\color{{tinta2}} V5: el área gris es el municipio de Mérida (Marco Geoestadístico INEGI). Las líneas punteadas son las isoyetas de INEGI.
Los círculos son las estaciones del SMN con al menos 10 años completos; el número junto a cada uno es su promedio anual en mm.}}

\begin{{center}}
\includegraphics[width=0.85\linewidth]{{figuras/v7_periodos_retorno.pdf}}
\end{{center}}

\section{{Eventos extraordinarios}}

\subsection{{Días más lluviosos (estaciones urbanas del SMN)}}
{{\small
\begin{{tabularx}}{{\linewidth}}{{@{{}}llXl@{{}}}}
\toprule
\textbf{{Fecha}} & \textbf{{mm/24 h}} & \textbf{{Estación}} & \textbf{{Evento asociado}} \\ \midrule
{evrows}
\bottomrule
\end{{tabularx}}}}

\subsection{{Declaratorias oficiales por lluvia o ciclón en el municipio de Mérida (CENAPRED, 2000–2023)}}
{{\small
\begin{{tabularx}}{{\linewidth}}{{@{{}}lllX@{{}}}}
\toprule
\textbf{{Inicio}} & \textbf{{Tipo}} & \textbf{{Fenómeno}} & \textbf{{Observaciones}} \\ \midrule
{declrows}
\bottomrule
\end{{tabularx}}}}

\subsection{{Lluvia esperada en 24 h por periodo de retorno (datos propios, C7.2)}}
\begin{{tabular}}{{@{{}}lrr@{{}}}}
\toprule
\textbf{{Periodo de retorno (años)}} & \textbf{{SMN 31097 (mm)}} & \textbf{{SMN 31044 (mm)}} \\ \midrule
{retrows}
\bottomrule
\end{{tabular}}

\section{{Advertencias metodológicas}}
\begin{{itemize}}[leftmargin=1.2em,itemsep=2pt]
\item \textbf{{Completitud:}} un mes cuenta solo si tiene al menos 80\% de días con dato, y un año solo si tiene los 12 meses válidos.
\item \textbf{{Estación ≠ ciudad:}} un pluviómetro mide un punto. En una tormenta, dos colonias pueden recibir cantidades muy distintas.
\item \textbf{{Intensidad:}} los datos diarios no muestran aguaceros cortos (por ejemplo, 60 mm en una hora), que son los que más inundan.
  Para eso sirven C5.1 (solicitud al SMN) y C6.1 (scraping periódico de las estaciones automáticas).
\item \textbf{{Periodos de retorno:}} son estimaciones con 36–52 años de datos; la incertidumbre crece mucho para 50 y 100 años.
\item \textbf{{Elevación:}} Mérida es muy plana (0–13 m en el centro); usar el modelo de INEGI con cuidado y validarlo con C8.3.
\end{{itemize}}

\section{{Pendientes}}
\begin{{enumerate}}[leftmargin=1.4em,itemsep=2pt]
\item Dar seguimiento a las 3 solicitudes de información (C5.1–C5.3), enviadas el 1 de octubre; vencen el 30 de octubre (con prórroga, el 17 de noviembre).
\item Programar el scraping del SMN (C6.1) para que corra cada semana y vaya acumulando la serie de intensidad.
\item Conectar \texttt{{07\_Datos\_propios/}} con el prototipo HTML.
\end{{enumerate}}

\end{{document}}
"""
(DOC / "fuentes_precipitacion_merida.tex").write_text(documento, encoding="utf-8")
print("Listo: figuras, Excel y .tex generados.")
