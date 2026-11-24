#!/usr/bin/env python3
"""
Ejemplo de extraccion: SMN/CONAGUA - visor SIVEA de Estaciones Meteorologicas Automaticas (EMA/ESMA).

Endpoints (API no documentada, usados por el propio visor publico
https://smn.conagua.gob.mx/tools/GUI/sivea_v3/sivea.php):
  - php/getPrecipitacion.php?per=B24      -> JSON: lluvia acumulada ultimas 24 h en todas las EMA activas
  - php/getReporteEstacion.php?tipo=N&nombre_estacion=ID
        tipo=1 (24 h), 2 (1 semana), 3 (90 dias) -> CSV cada 10 min (temp, lluvia, HR, presion, viento...)

Notas:
  - robots.txt de smn.conagua.gob.mx no existe (devuelve 404/500), no hay reglas de exclusion explicitas.
  - En la consulta del 2026-10-01 NO aparece una estacion "Merida" en el visor; las EMA de Yucatan activas
    eran PROGRESO (ESMA, ~30 km al norte), DZILAM, TANTAQUIN, VALLADOLID. Revisar periodicamente.
  - El visor solo guarda ~90 dias: para construir una serie hay que correr esto de forma periodica (cron).
  - Uso academico, peticiones espaciadas (>= 3 s), User-Agent identificable.

Uso: python3 ejemplo_scraping_smn_sivea.py   -> genera muestra_smn_sivea_yucatan_24h.csv y muestra_smn_sivea_progreso_10min.csv
"""
import csv
import io
import json
import time
import urllib.request

try:
    import requests  # opcional
except ImportError:
    requests = None

BASE = "https://smn.conagua.gob.mx/tools/GUI/sivea_v3/"
UA = "MeridaCiudadEsponja-UniProject/0.1 (proyecto universitario; contacto: equipo del proyecto)"
HEADERS = {"User-Agent": UA, "Referer": BASE + "sivea.php"}
PAUSA = 3  # segundos entre peticiones


def get(url):
    if requests:
        r = requests.get(url, headers=HEADERS, timeout=60)
        r.raise_for_status()
        return r.content
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def lluvia_24h_yucatan():
    data = json.loads(get(BASE + "php/getPrecipitacion.php?per=B24"))
    filas = [d for d in data if d.get("estado", "").startswith("Yuc")]
    campos = ["estacion_m", "nombre_estacion", "municipio", "estado", "organismo", "tipoestacion",
              "latitud", "longitud", "fecha_local", "fecha_utc", "precipitacion"]
    with open("muestra_smn_sivea_yucatan_24h.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        for d in filas:
            d["precipitacion"] = round(float(d["precipitacion"]), 1)
            w.writerow(d)
    print(f"Yucatan: {len(filas)} estaciones con lluvia 24 h")


def serie_10min(estacion="PROGRESO", tipo=2):
    raw = get(BASE + f"php/getReporteEstacion.php?tipo={tipo}&nombre_estacion={estacion}")
    texto = raw.decode("utf-8-sig")
    lineas = texto.splitlines()
    # el CSV trae un encabezado de metadatos; la tabla empieza en la linea con "Fecha Local"
    ini = next(i for i, l in enumerate(lineas) if l.startswith('"Fecha Local"'))
    lector = csv.reader(io.StringIO("\n".join(lineas[ini:])))
    cab = next(lector)
    with open(f"muestra_smn_sivea_{estacion.lower()}_10min.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["fecha_local", "fecha_utc", "precipitacion_mm", "temperatura_c", "humedad_pct"])
        n = 0
        for row in lector:
            if len(row) < 5:
                continue
            w.writerow([row[0], row[1], row[3], row[2], row[4]])
            n += 1
    print(f"{estacion}: {n} registros de 10 min ({cab[3]})")


if __name__ == "__main__":
    lluvia_24h_yucatan()
    time.sleep(PAUSA)
    serie_10min("PROGRESO", tipo=2)
