"""Procesa la lluvia cada 10 minutos de la ESMA «MERIDA» (abril a junio de 2022).

Origen: carpeta de Google Drive que el Organismo de Cuenca Península de Yucatán (CONAGUA) indicó en su
respuesta al folio 340009400252226 (carpeta «EMAs ESMAs / Yucatán», archivos MERIDA_2022_04/05/06.xlsb).
Los archivos son datos abiertos de estaciones automáticas del SMN; no traen datos personales.
Los .xlsb se bajan a mano (no se versionan) y esta script lee una carpeta local con ellos.

Se descartó el resto de la carpeta para Mérida: «MERIDA CONAGUA» de 2025 tiene 0 a 42 % de cobertura de
mayo a septiembre (abril 42 %); febrero y marzo de 2025 están completos pero son temporada seca. Ver
datos/05_Solicitudes_gobierno/seguimiento_folios.md.

Salidas en datos/05_Solicitudes_gobierno/:
  conagua_esma_merida_10min_2022.csv                  lluvia cada 10 min (hora local y UTC)
  conagua_esma_merida_intensidad_mensual_2022.csv     cobertura, máximos en 10 min / 1 h / 24 h y contraste con CLICOM
  conagua_esma_procedencia.csv                        archivo, SHA-256, tamaño, fecha de descarga

Requisitos: pandas, numpy, pyxlsb
Uso:        python scripts/procesar_esma_drive.py <carpeta con MERIDA_2022_0[456].xlsb>
"""
import calendar
import datetime as dt
import hashlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from pyxlsb import open_workbook

AQUI = Path(__file__).resolve().parent
OUT = AQUI.parent / "datos" / "05_Solicitudes_gobierno"
P7 = AQUI.parent / "datos" / "07_Datos_propios"
CARPETA = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else Path.cwd()
MESES = [4, 5, 6]
ANIO = 2022
URL_CARPETA = "https://drive.google.com/drive/folders/1qPdWl97Ub3w1jm3bUZ33W4Vt58fhSOgn"
BASE_EXCEL = dt.datetime(1899, 12, 30)


def leer(path):
    with open_workbook(str(path)) as wb, wb.get_sheet(wb.sheets[0]) as sh:
        filas = [[c.v for c in r] for r in sh.rows()]
    ir = next(i for i, h in enumerate(filas[0]) if isinstance(h, str) and h.lower().startswith("precip"))
    out = []
    for r in filas[1:]:
        if isinstance(r[0], float) and isinstance(r[1], float):
            loc = (BASE_EXCEL + dt.timedelta(days=r[0])).replace(microsecond=0)
            utc = (BASE_EXCEL + dt.timedelta(days=r[1])).replace(microsecond=0)
            # los registros traen unos segundos de desfase respecto al múltiplo de 10 min
            out.append((pd.Timestamp(loc).round("min"), pd.Timestamp(utc).round("min"), float(r[ir] or 0.0)))
    return out


def main():
    filas, proc = [], []
    for m in MESES:
        f = CARPETA / f"MERIDA_{ANIO}_{m:02d}.xlsb"
        b = f.read_bytes()
        proc.append(dict(archivo=f.name, fuente=URL_CARPETA, sha256=hashlib.sha256(b).hexdigest(), bytes=len(b),
                         fecha_descarga=dt.date.today().isoformat()))
        filas += leer(f)
    df = pd.DataFrame(filas, columns=["fecha_hora_local", "fecha_hora_utc", "precipitacion_mm"]).sort_values("fecha_hora_local")
    dup = int(df.fecha_hora_local.duplicated().sum())
    df = df.drop_duplicates("fecha_hora_local")
    desfase = (df.fecha_hora_local - df.fecha_hora_utc).dt.total_seconds().div(3600).round(2).unique().tolist()
    print(f"registros: {len(df):,} | duplicados descartados: {dup} | local - UTC (h): {desfase}")
    df.to_csv(OUT / "conagua_esma_merida_10min_2022.csv", index=False, date_format="%Y-%m-%d %H:%M")
    pd.DataFrame(proc).to_csv(OUT / "conagua_esma_procedencia.csv", index=False)

    # ---- resumen mensual y contraste con la serie diaria de CLICOM (31044 = Mérida OBS, el mismo sitio)
    clicom = pd.read_csv(P7 / "smn_precip_diaria.csv", dtype={"estacion": str}, parse_dates=["fecha"])
    clicom = clicom[clicom.estacion == "31044"].set_index("fecha")["precip_mm"]
    s = df.set_index("fecha_hora_local")["precipitacion_mm"]
    res = []
    for m in MESES:
        sm = s[(s.index.year == ANIO) & (s.index.month == m)]
        esperados = calendar.monthrange(ANIO, m)[1] * 144
        serie = sm.asfreq("10min")                      # huecos -> NaN
        w1 = serie.rolling(6, min_periods=6).sum()      # 1 h
        w24 = serie.rolling(144, min_periods=144).sum() # 24 h
        dia = sm.resample("D").sum()
        cl = clicom.reindex(dia.index).dropna()
        comp = dia.reindex(cl.index)
        corr = float(np.corrcoef(comp, cl)[0, 1]) if len(cl) > 5 and cl.std() > 0 and comp.std() > 0 else np.nan
        nota = ""
        if len(sm) / esperados < 0.95:
            nota = "cobertura menor al 95 %"
        if corr < 0.6 or abs(comp.sum() - cl.sum()) > 0.5 * max(cl.sum(), 1):
            nota = (nota + "; " if nota else "") + "difiere de CLICOM: usar con reserva"
        res.append(dict(
            mes=f"{ANIO}-{m:02d}", registros=len(sm), cobertura_pct=round(100 * len(sm) / esperados, 1),
            lluvia_total_mm=round(sm.sum(), 1), max_10min_mm=round(sm.max(), 1), max_10min_hora_local=sm.idxmax().strftime("%Y-%m-%d %H:%M"),
            max_1h_mm=round(w1.max(), 1), max_1h_inicio_local=(w1.idxmax() - pd.Timedelta(minutes=50)).strftime("%Y-%m-%d %H:%M"),
            max_24h_mm=round(w24.max(), 1), max_24h_termina_local=w24.idxmax().strftime("%Y-%m-%d %H:%M"),
            lluvia_clicom_31044_mm=round(cl.sum(), 1), correlacion_diaria_clicom=round(corr, 2), nota=nota))
    r = pd.DataFrame(res)
    r.to_csv(OUT / "conagua_esma_merida_intensidad_mensual_2022.csv", index=False)
    print(r[["mes", "registros", "cobertura_pct", "lluvia_total_mm", "max_10min_mm", "max_1h_mm", "max_24h_mm",
             "lluvia_clicom_31044_mm", "correlacion_diaria_clicom", "nota"]].to_string(index=False))


if __name__ == "__main__":
    main()
