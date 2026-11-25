"""Captura las series de 10 min de las estaciones automáticas de Yucatán del visor SIVEA (SMN/CONAGUA).

El visor público https://smn.conagua.gob.mx/tools/GUI/sivea_v3/sivea.php solo guarda ~90 días. Cada corrida
descarga la ventana de 90 días de cada estación de Yucatán y la FUSIONA con lo que ya se tenía, sin duplicar,
de modo que la serie crece con el tiempo. Hay que correrla al menos cada ~60 días para no perder registros.

Endpoints (los usa el propio visor público):
  php/getPrecipitacion.php?per=B24                    -> JSON con las estaciones activas
  php/getReporteEstacion.php?tipo=3&nombre_estacion=  -> CSV de 90 días cada ~10 min

Estaciones: todas las de estado «Yucatán» que lista el visor en ese momento (el 24-nov-2026: DZILAM, TANTAQUIN,
MERIDA, PROGRESO y VALLADOLID). «MERIDA» aparece en el visor, pero casi no transmite: la corrida del 24-nov-2026 trajo
2 registros en 90 días. La estación más cercana con serie continua es PROGRESO (~30 km).

Salidas en datos/06_Scraping/:
  smn_sivea_yucatan_10min.csv         serie acumulada (estacion, hora local y UTC, lluvia, temperatura, humedad)
  smn_sivea_estaciones.csv            metadatos y cobertura de cada estación
  smn_sivea_capturas.csv              bitácora: qué se bajó y cuántos registros eran nuevos

Cortesía: User-Agent identificable, 3 s entre peticiones (~15 peticiones por corrida), solo lectura.
Requisitos: pandas
Uso:        python scripts/scraping_smn_sivea.py
"""
import csv
import io
import json
import re
import time
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

import pandas as pd

BASE = "https://smn.conagua.gob.mx/tools/GUI/sivea_v3/"
UA = "MeridaCiudadEsponja-UniProject/0.1 (proyecto universitario; contacto: equipo del proyecto)"
HEADERS = {"User-Agent": UA, "Referer": BASE + "sivea.php"}
PAUSA = 3
OUT = Path(__file__).resolve().parent.parent / "datos" / "06_Scraping"
COLS = ["estacion", "fecha_local", "fecha_utc", "precipitacion_mm", "temperatura_c", "humedad_pct"]


def get(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read()


def estaciones_yucatan():
    data = json.loads(get(BASE + "php/getPrecipitacion.php?per=B24"))
    return sorted({(d["nombre_estacion"], d.get("tipoestacion", ""), d.get("municipio", "")) for d in data
                   if d.get("estado", "").startswith("Yuc")})


def numero(v):
    v = v.strip()
    return None if (v == "" or set(v) <= {"/"}) else float(v)


def serie_90d(nombre):
    q = urllib.parse.urlencode({"tipo": 3, "nombre_estacion": nombre})
    texto = get(BASE + "php/getReporteEstacion.php?" + q).decode("utf-8-sig")
    lineas = texto.splitlines()
    meta = {}
    for l in lineas:
        m = re.match(r"(Latitud|Longitud|Altitud|Municipio),(.*)", l)
        if m:
            meta[m.group(1)] = m.group(2).strip().strip('"')
    ini = next((i for i, l in enumerate(lineas) if l.startswith('"Fecha Local"')), None)
    if ini is None:
        return meta, []
    lector = csv.reader(io.StringIO("\n".join(lineas[ini:])))
    cab = next(lector)
    col = {re.sub(r"\s*\(.*", "", c).strip().lower(): i for i, c in enumerate(cab)}
    i_ll = next(i for c, i in col.items() if c.startswith("precipit"))
    i_t = next(i for c, i in col.items() if c.startswith("temperatura"))
    i_h = next(i for c, i in col.items() if c.startswith("humedad"))
    filas = []
    for r in lector:
        if len(r) <= max(i_ll, i_t, i_h) or not r[0].startswith("20"):
            continue
        filas.append([nombre, r[0], r[1], numero(r[i_ll]), numero(r[i_t]), numero(r[i_h])])
    return meta, filas


def main():
    OUT.mkdir(exist_ok=True)
    f_serie = OUT / "smn_sivea_yucatan_10min.csv"
    previa = pd.read_csv(f_serie, dtype={"estacion": str}) if f_serie.exists() else pd.DataFrame(columns=COLS)
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M")
    nuevas, bitacora, metas = [], [], {}
    est = estaciones_yucatan()
    print("estaciones de Yucatán en el visor:", [e[0] for e in est])
    for nombre, tipo, mun in est:
        time.sleep(PAUSA)
        meta, filas = serie_90d(nombre)
        df = pd.DataFrame(filas, columns=COLS)
        metas[nombre] = dict(estacion=nombre, tipo=tipo, municipio=meta.get("Municipio", mun), latitud=meta.get("Latitud"),
                             longitud=meta.get("Longitud"), altitud_m=meta.get("Altitud"))
        ya = set(previa[previa.estacion == nombre].fecha_utc)
        n_nuevos = int((~df.fecha_utc.isin(ya)).sum())
        bitacora.append(dict(captura=ahora, estacion=nombre, registros_descargados=len(df), registros_nuevos=n_nuevos,
                             desde_utc=df.fecha_utc.min() if len(df) else "", hasta_utc=df.fecha_utc.max() if len(df) else ""))
        nuevas.append(df)
        print(f"  {nombre:11} {len(df):6,} registros descargados, {n_nuevos:6,} nuevos")
    todo = pd.concat([previa] + nuevas, ignore_index=True)
    todo = todo.drop_duplicates(["estacion", "fecha_utc"], keep="last").sort_values(["estacion", "fecha_utc"])
    todo.to_csv(f_serie, index=False)

    # metadatos y cobertura
    filas_e = []
    for nombre, g in todo.groupby("estacion"):
        m = metas.get(nombre, dict(estacion=nombre))
        d = pd.to_datetime(g.fecha_utc)
        esperados = int((d.max() - d.min()).total_seconds() // 600) + 1
        m.update(registros=len(g), desde_utc=g.fecha_utc.min(), hasta_utc=g.fecha_utc.max(),
                 cobertura_pct=round(100 * len(g) / esperados, 1), dias_con_lluvia=int((g.groupby(g.fecha_local.str[:10]).precipitacion_mm.sum() > 0).sum()))
        filas_e.append(m)
    pd.DataFrame(filas_e).to_csv(OUT / "smn_sivea_estaciones.csv", index=False)

    f_bit = OUT / "smn_sivea_capturas.csv"
    previa_b = pd.read_csv(f_bit) if f_bit.exists() else pd.DataFrame()
    pd.concat([previa_b, pd.DataFrame(bitacora)], ignore_index=True).to_csv(f_bit, index=False)
    print(f"serie acumulada: {len(todo):,} registros -> {f_serie}")


if __name__ == "__main__":
    main()
