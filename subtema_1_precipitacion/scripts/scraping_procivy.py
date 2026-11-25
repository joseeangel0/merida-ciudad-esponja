"""Boletines de ciclones tropicales de PROCIVY (Protección Civil de Yucatán), temporadas 2019 a 2026.

Fuente: https://www.yucatan.gob.mx/procivy/boletines.php?t=AAAA (lista de sistemas) y
        https://www.yucatan.gob.mx/procivy/boletines.php?id=NNAA (todos los boletines de un sistema).
robots.txt de www.yucatan.gob.mx: solo prohíbe /paneladminweb/ y /4dm1n/ (verificado el 24-nov-2026).
Cortesía: User-Agent identificable y 3 s entre peticiones (~130 peticiones en total).

Salidas en datos/06_Scraping/:
  procivy_boletines_2019_2026.csv   un renglón por boletín (fecha, hora, distancia a Mérida si la menciona, resumen)
  procivy_sistemas_2019_2026.csv    un renglón por sistema listado (ciclón, formación, nº de boletines —0 si PROCIVY no emitió— y distancia mínima a Mérida)

Sirve para fechar ciclones y cruzarlos con la lluvia y los reportes de drenaje. Los resúmenes son boletines
oficiales; se guardan recortados a 400 caracteres.
Uso: python scripts/scraping_procivy.py [anio_inicial] [anio_final]
"""
import html
import re
import sys
import time
import urllib.request
from pathlib import Path

import pandas as pd

BASE = "https://www.yucatan.gob.mx/procivy/"
UA = "MeridaCiudadEsponja-UniProject/0.1 (proyecto universitario)"
PAUSA = 3
OUT = Path(__file__).resolve().parent.parent / "datos" / "06_Scraping"
MESES_LARGOS = {"enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
                "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12}
MESES = {"Ene": 1, "Feb": 2, "Mar": 3, "Abr": 4, "May": 5, "Jun": 6, "Jul": 7, "Ago": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dic": 12}


def get(url):
    for intento in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:  # reintento simple
            if intento == 2:
                raise
            time.sleep(10)


def texto(h):
    h = re.sub(r"<script.*?</script>|<style.*?</style>", " ", h, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h))).strip()


def fecha_iso(f):
    d, m, a = f.split("/")
    return f"{a}-{MESES.get(m[:3].capitalize(), 0):02d}-{d}"


def main(a0=2019, a1=2026):
    filas, info = [], []
    for anio in range(a0, a1 + 1):
        time.sleep(PAUSA)
        sistemas = sorted(set(re.findall(r'href="boletines\.php\?id=(\d+)"', get(f"{BASE}boletines.php?t={anio}"))))
        print(f"{anio}: {len(sistemas)} sistemas")
        for sid in sistemas:
            time.sleep(PAUSA)
            t = texto(get(f"{BASE}boletines.php?id={sid}"))
            for _ in range(3):                      # a veces el sitio responde una página incompleta
                if "Ciclón:" in t and "Temporada" in t:
                    break
                time.sleep(PAUSA * 2)
                t = texto(get(f"{BASE}boletines.php?id={sid}"))
            else:
                print(f"AVISO: el sistema {sid} ({anio}) no trae encabezado; revisar")
            nombre = re.search(r"Ciclón:\s*(.+?)\s+Temporada", t)
            form = re.search(r"Fecha de formación:\s*\w+,\s*(\d{1,2}) de (\w+) de (\d{4})", t)
            info.append(dict(temporada=anio, id_sistema=sid, ciclon=nombre.group(1) if nombre else "",
                             fecha_formacion=f"{form.group(3)}-{MESES_LARGOS[form.group(2).lower()]:02d}-{int(form.group(1)):02d}" if form else "",
                             sin_boletines=int("No hay boletines" in t)))
            for m in re.finditer(r"([A-Z]{1,3}/\d{4}/\d+)\s+(\d{2}/\w{3}/\d{4})\s*-\s*(\d{1,2}:\d{2})\s*hrs\.\s*(.*?)(?=[A-Z]{1,3}/\d{4}/\d+\s+\d{2}/\w{3}/\d{4}|https://www\.yucatan\.gob\.mx|$)", t):
                resumen = m.group(4).strip()
                dist = re.search(r"(\d+)\s*km al [\w-]+ de Mérida", resumen)
                filas.append(dict(temporada=anio, id_sistema=sid, ciclon=nombre.group(1) if nombre else "", boletin=m.group(1),
                                  fecha=fecha_iso(m.group(2)), hora=m.group(3), menciona_lluvia=int(bool(re.search(r"lluvi", resumen, re.I))),
                                  dist_merida_km=dist.group(1) if dist else "", resumen=resumen[:400]))
    df = pd.DataFrame(filas).drop_duplicates(["id_sistema", "boletin"]).sort_values(["fecha", "hora"])
    df.to_csv(OUT / "procivy_boletines_2019_2026.csv", index=False)
    d = df.assign(dist=pd.to_numeric(df.dist_merida_km, errors="coerce"))
    agg = (d.groupby(["temporada", "id_sistema"])
           .agg(boletines=("boletin", "size"), primer_boletin=("fecha", "min"), ultimo_boletin=("fecha", "max"),
                dist_minima_merida_km=("dist", "min"), menciona_lluvia=("menciona_lluvia", "max")).reset_index())
    sis = pd.DataFrame(info).merge(agg, on=["temporada", "id_sistema"], how="left")
    sis["boletines"] = sis["boletines"].fillna(0).astype(int)
    sis.to_csv(OUT / "procivy_sistemas_2019_2026.csv", index=False)
    print(f"{len(df):,} boletines de {int((sis.boletines > 0).sum())} sistemas con boletines; {len(sis)} sistemas listados ({df.fecha.min()} a {df.fecha.max()})")


if __name__ == "__main__":
    main(*(int(x) for x in sys.argv[1:3]))
