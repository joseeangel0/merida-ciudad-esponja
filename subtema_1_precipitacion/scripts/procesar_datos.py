"""
Procesa los registros diarios del SMN/CONAGUA para Mérida (subtema 1) y genera
los "datos propios" del equipo en datos/07_Datos_propios/:
  1. Series limpias (diaria, mensual, anual) y climatología 1991-2020
  2. Índices de lluvia extrema y periodos de retorno (Gumbel)
  3. Catálogo de eventos extraordinarios

Requisitos: pandas, numpy
Uso:        python scripts/procesar_datos.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent.parent / "datos"
SMN_DIR = next(BASE.rglob("*SMN_CONAGUA_estaciones")) / "diarios"
OUT = BASE / "07_Datos_propios"
OUT.mkdir(exist_ok=True)

UMBRAL_DIAS_MES = 0.80    # % mínimo de días con dato para aceptar un total mensual
UMBRAL_MESES_ANIO = 12    # meses válidos requeridos para aceptar un total anual
URBANAS = ["31044", "31097", "31078", "31036", "31095"]

# Eventos con nombre documentados por el SMN (reseñas de ciclones tropicales).
# Se asignan a un día si cae dentro de la ventana indicada.
EVENTOS_CONOCIDOS = [
    ("1988-09-13", "1988-09-16", "Huracán Gilberto"),
    ("1995-09-30", "1995-10-02", "Huracán Opal"),
    ("1995-10-10", "1995-10-12", "Huracán Roxanne"),
    ("2002-09-21", "2002-09-25", "Huracán Isidoro"),
    ("2020-06-01", "2020-06-06", "Tormenta tropical Cristóbal"),
    ("2020-10-02", "2020-10-04", "Tormenta tropical Gamma"),
    ("2020-10-06", "2020-10-08", "Huracán Delta"),
]


# ---------------------------------------------------------------- lectura SMN / CLICOM
def leer_smn(path):
    meta, filas = {}, []
    for linea in path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = linea.strip()
        if s[:4].isdigit() and s[4:5] == "-":
            partes = s.split()
            filas.append((partes[0], partes[1] if len(partes) > 1 else "NULO"))
        elif ":" in s and not filas:
            k, _, v = s.partition(":")
            meta[k.strip()] = v.strip().rstrip("°").strip()
    df = pd.DataFrame(filas, columns=["fecha", "precip_mm"])
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df["precip_mm"] = pd.to_numeric(df["precip_mm"], errors="coerce")
    return meta, df.dropna(subset=["fecha"])


def limpiar_ceros_espurios(df):
    """Convierte a NaN los días de meses cuyo 0.0 mm casi seguro es un faltante codificado.

    Un mes completo (>= UMBRAL_DIAS_MES de días con dato) con total 0.0 mm se considera
    sospechoso si:
      - cae en la temporada lluviosa (jun-oct; en Mérida nunca llueve 0 mm todo el mes), o
      - forma parte de una racha de >= 3 meses consecutivos en cero en la misma estación.
    Devuelve (df limpio, lista de meses 'YYYY-MM' invalidados).
    """
    d = df.set_index("fecha")["precip_mm"]
    tot = d.resample("MS").sum(min_count=1)
    n = d.resample("MS").count()
    completo = n >= UMBRAL_DIAS_MES * tot.index.days_in_month
    cero = completo & (tot == 0)
    sosp = cero & tot.index.month.isin(range(6, 11))

    idx = tot.index.year * 12 + tot.index.month
    corr, ini = 0, None
    for i, (flag, k) in enumerate(zip(cero.to_numpy(), idx)):
        if flag and corr and k == ult + 1:
            corr += 1
        elif flag:
            corr, ini = 1, i
        else:
            corr = 0
        ult = k
        if corr >= 3:
            sosp.iloc[ini:i + 1] = True
    meses = [t.strftime("%Y-%m") for t in tot.index[sosp.to_numpy()]]
    if meses:
        mask = df["fecha"].dt.strftime("%Y-%m").isin(meses)
        df = df.copy()
        df.loc[mask, "precip_mm"] = np.nan
    return df, meses


def agregar(df):
    """Diario -> mensual y anual con control de completitud."""
    d = df.set_index("fecha")["precip_mm"]
    m = pd.DataFrame({
        "precip_mm": d.resample("MS").sum(min_count=1),
        "dias_con_dato": d.resample("MS").count(),
        "max_diaria_mm": d.resample("MS").max(),
    })
    m["dias_mes"] = m.index.days_in_month
    m["completo"] = m["dias_con_dato"] >= UMBRAL_DIAS_MES * m["dias_mes"]
    m.loc[~m["completo"], "precip_mm"] = np.nan

    a = pd.DataFrame({
        "precip_mm": m["precip_mm"].resample("YS").sum(min_count=1),
        "meses_validos": m["completo"].resample("YS").sum(),
        "dias_lluvia_>=1mm": (d >= 1).resample("YS").sum(),
        "dias_>=50mm": (d >= 50).resample("YS").sum(),
        "dias_>=100mm": (d >= 100).resample("YS").sum(),
        "max_diaria_mm": d.resample("YS").max(),
    })
    a.loc[a["meses_validos"] < UMBRAL_MESES_ANIO, "precip_mm"] = np.nan
    m.index.name = a.index.name = "fecha"
    return m.reset_index(), a.reset_index()


catalogo, diarios, mensuales, anuales = [], [], [], []
for f in sorted(SMN_DIR.glob("dia*.txt")):
    meta, df = leer_smn(f)
    clave = meta.get("ESTACIÓN") or f.stem[3:]
    df, invalidados = limpiar_ceros_espurios(df)
    if invalidados:
        print(f"  {clave}: {len(invalidados)} meses con 0.0 mm sospechoso -> sin dato")
    validos = df.dropna(subset=["precip_mm"])
    catalogo.append({
        "clave": clave, "nombre": meta.get("NOMBRE"), "municipio": meta.get("MUNICIPIO"),
        "situacion": meta.get("SITUACIÓN"),
        "latitud": float(meta.get("LATITUD", "nan")), "longitud": float(meta.get("LONGITUD", "nan")),
        "altitud_msnm": meta.get("ALTITUD", "").replace("msnm", "").strip(),
        "inicio": validos["fecha"].min().date() if len(validos) else None,
        "fin": validos["fecha"].max().date() if len(validos) else None,
        "dias_con_dato": len(validos),
        "pct_completitud": round(100 * len(validos) / max(len(df), 1), 1),
    })
    df.insert(0, "estacion", clave)
    diarios.append(df)
    m, a = agregar(df.drop(columns="estacion"))
    m.insert(0, "estacion", clave)
    a.insert(0, "estacion", clave)
    mensuales.append(m)
    anuales.append(a)

cat = pd.DataFrame(catalogo)
smn_d = pd.concat(diarios)
smn_m = pd.concat(mensuales)
smn_a = pd.concat(anuales)
smn_a["anio"] = smn_a["fecha"].dt.year
smn_a = smn_a.drop(columns="fecha")

# ================================================================ 1. Series limpias y climatología
cat.to_csv(OUT / "smn_catalogo_estaciones.csv", index=False)
smn_d.to_csv(OUT / "smn_precip_diaria.csv", index=False, date_format="%Y-%m-%d")
smn_m.to_csv(OUT / "smn_precip_mensual.csv", index=False, date_format="%Y-%m")
smn_a.to_csv(OUT / "smn_precip_anual.csv", index=False)

m44 = smn_m[(smn_m.estacion == "31044") & smn_m.fecha.between("1991-01-01", "2020-12-31")].copy()
m44["mes"] = m44.fecha.dt.month
clim = m44.groupby("mes")["precip_mm"].agg(["mean", "median", "min", "max", "count"]).round(1)
clim.columns = ["promedio_mm", "mediana_mm", "minimo_mm", "maximo_mm", "anios_validos"]
clim.to_csv(OUT / "climatologia_mensual_31044_1991_2020.csv")

# Promedio anual 1991-2020 por estación urbana (para el mapa de puntos)
prom = (smn_a[smn_a.anio.between(1991, 2020)].groupby("estacion")["precip_mm"]
        .agg(precip_anual_media_mm="mean", anios_completos="count").round(1).reset_index())
prom = cat[["clave", "nombre", "latitud", "longitud"]].merge(prom, left_on="clave", right_on="estacion").drop(columns="estacion")
prom.to_csv(OUT / "promedio_anual_por_estacion_1991_2020.csv", index=False)

# ================================================================ 2. Índices extremos y periodos de retorno
indices = smn_a[smn_a.estacion.isin(URBANAS)][
    ["estacion", "anio", "precip_mm", "dias_lluvia_>=1mm", "dias_>=50mm", "dias_>=100mm", "max_diaria_mm", "meses_validos"]]
indices.to_csv(OUT / "indices_lluvia_extrema_por_anio.csv", index=False)

# Gumbel (método de momentos) sobre el máximo diario anual de años completos
filas = []
for est in ["31097", "31044"]:
    x = smn_a[(smn_a.estacion == est) & smn_a.precip_mm.notna()]["max_diaria_mm"].dropna()
    media, desv = x.mean(), x.std(ddof=1)
    alfa = desv * np.sqrt(6) / np.pi
    u = media - 0.5772 * alfa
    for T in [2, 5, 10, 25, 50, 100]:
        filas.append({"estacion": est, "periodo_retorno_anios": T,
                      "lluvia_24h_mm": round(u - alfa * np.log(-np.log(1 - 1 / T)), 1),
                      "anios_usados": len(x), "max_observado_mm": x.max()})
pd.DataFrame(filas).to_csv(OUT / "periodos_retorno_lluvia_24h.csv", index=False)

# Tendencia lineal 1961-2025 de la estación más completa
t = smn_a[(smn_a.estacion == "31097") & smn_a.anio.between(1961, 2025)]
tc = t.dropna(subset=["precip_mm"])
pd.DataFrame([{
    "estacion": "31097",
    "tendencia_precip_mm_por_decada": round(np.polyfit(tc.anio, tc.precip_mm, 1)[0] * 10, 1),
    "anios_completos": len(tc),
    "tendencia_dias_>=50mm_por_decada": round(np.polyfit(tc.anio, tc["dias_>=50mm"], 1)[0] * 10, 2),
}]).to_csv(OUT / "tendencias_31097.csv", index=False)

# ================================================================ 3. Catálogo de eventos extraordinarios
ev = smn_d[smn_d.estacion.isin(URBANAS) & (smn_d.precip_mm >= 100)].copy()
ev = ev.merge(cat[["clave", "nombre"]], left_on="estacion", right_on="clave").drop(columns="clave")
ev["evento_asociado"] = ""
for ini, fin, nombre in EVENTOS_CONOCIDOS:
    ev.loc[ev.fecha.between(ini, fin), "evento_asociado"] = nombre
ev = ev.sort_values("precip_mm", ascending=False)
ev.to_csv(OUT / "eventos_extraordinarios_>=100mm.csv", index=False, date_format="%Y-%m-%d")

print("Listo. Archivos en", OUT)
for f in sorted(OUT.glob("*.csv")):
    print(f"  {f.name:50s} {sum(1 for _ in open(f)) - 1:>8} filas")
