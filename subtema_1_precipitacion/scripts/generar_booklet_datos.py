"""Genera los CSV finales del booklet (una tabla por escena + las 3 cifras del capítulo).

Entrada : datos/07_Datos_propios/*.csv   (salida de procesar_datos.py)
          datos/05_Solicitudes_gobierno/*.csv   (salida de procesar_pnt.py)
Salida  : <raíz del repo>/booklet/datos/escena-1.csv ... escena-4.csv, cifras.csv

Solo stdlib. Ejecutar DESPUÉS de procesar_datos.py y procesar_pnt.py. No se escribe ningún valor
a mano: todo sale de los CSV de entrada. Los CSV usan columnas en español, minúsculas y con guion bajo.
"""
import csv
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean

RAIZ = Path(__file__).resolve().parents[2]
D = RAIZ / "subtema_1_precipitacion" / "datos"
P7, P5 = D / "07_Datos_propios", D / "05_Solicitudes_gobierno"
SALIDA = RAIZ / "booklet" / "datos"

ESTACIONES_URBANAS = {  # clave SMN -> nombre corto (las 5 estaciones urbanas operando)
    "31036": "CICY",
    "31044": "Mérida (OBS)",
    "31078": "FIUADY (Periférico)",
    "31095": "Col. Emiliano Zapata",
    "31097": "Mérida (CONAGUA)",
}
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
SERVICIO_DESAGUE = "DESAGÜE DE CALLES INUNDADAS"
ESCENA3_INICIO = "2024-01-01"      # inicio de la entrega 2024-2026 del Ayuntamiento
MIN_ESTACIONES = 4                 # estaciones con dato para promediar la lluvia de un día
ESCENA4_INICIO, ESCENA4_FIN = "2026-05-26", "2026-06-10"
ESTACION_SERIE_LARGA = "31097"                            # Mérida (CONAGUA), 1961-2026


def leer(carpeta, nombre):
    with open(carpeta / nombre, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def escribir(nombre, columnas, filas):
    SALIDA.mkdir(parents=True, exist_ok=True)
    with open(SALIDA / nombre, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(columnas)
        w.writerows(filas)
    print(f"  {nombre}: {len(filas)} filas")


def num(x):
    """Número sin ceros de más ('' se queda vacío = sin dato)."""
    return "" if x in ("", None) else f"{float(x):g}"


def escena1():
    """Ciclo anual: normal climatológica 1991-2020 de Mérida (OBS)."""
    filas = []
    for r in leer(P7, "climatologia_mensual_31044_1991_2020.csv"):
        m = int(r["mes"])
        filas.append([m, MESES[m - 1], r["promedio_mm"], r["mediana_mm"], r["maximo_mm"], r["anios_validos"]])
    escribir("escena-1.csv", ["mes", "nombre_mes", "promedio_mm", "mediana_mm", "maximo_mm", "anios_validos"], filas)
    return filas


def escena2():
    """Días con 50 mm o más por año en Mérida (CONAGUA), con marca de año completo."""
    diaria_max = {}
    for r in leer(P7, "smn_precip_diaria.csv"):
        if r["estacion"] != ESTACION_SERIE_LARGA or r["precip_mm"] == "":
            continue
        a = r["fecha"][:4]
        v = float(r["precip_mm"])
        if a not in diaria_max or v > diaria_max[a][0]:
            diaria_max[a] = (v, r["fecha"])
    filas = []
    for r in leer(P7, "indices_lluvia_extrema_por_anio.csv"):
        if r["estacion"] != ESTACION_SERIE_LARGA:
            continue
        a = r["anio"]
        completo = "si" if int(r["meses_validos"]) == 12 else "no"
        mx, fmx = diaria_max.get(a, ("", ""))
        filas.append([a, r["dias_>=50mm"], r["meses_validos"], completo, num(mx), fmx])
    escribir("escena-2.csv", ["anio", "dias_50mm_o_mas", "meses_validos", "anio_completo", "max_diaria_mm", "fecha_max_diaria"], filas)
    return filas


def escena3():
    """¿Cuánto aguanta la esponja? Lluvia diaria (promedio de las estaciones urbanas) contra reportes de desagüe del día.

    Solo días de la entrega 2024-2026 del Ayuntamiento (hoja de cálculo), con al menos 4 de las 5 estaciones con dato.
    """
    lluvia = defaultdict(list)
    for r in leer(P7, "smn_precip_diaria.csv"):
        if r["estacion"] in ESTACIONES_URBANAS and r["precip_mm"] != "" and r["fecha"] >= ESCENA3_INICIO:
            lluvia[r["fecha"]].append(float(r["precip_mm"]))
    rep = Counter()
    for r in leer(P5, "ayuntamiento_reportes_drenaje_dia.csv"):
        if r["origen"] == "solicitud" and r["servicio"] == SERVICIO_DESAGUE:
            rep[r["fecha_solicitud"]] += int(r["reportes"])
    filas = [[f, f"{mean(v):.1f}", len(v), rep.get(f, 0)] for f, v in sorted(lluvia.items()) if len(v) >= MIN_ESTACIONES]
    escribir("escena-3.csv", ["fecha", "lluvia_mm", "estaciones_con_dato", "reportes_desague"], filas)
    return filas


def escena4():
    """El temporal de mayo-junio de 2026 día por día: lluvia por estación y reportes de desagüe."""
    rep = Counter()
    for r in leer(P5, "ayuntamiento_reportes_drenaje_dia.csv"):
        if r["origen"] == "solicitud" and r["servicio"] == SERVICIO_DESAGUE:
            rep[r["fecha_solicitud"]] += int(r["reportes"])
    filas = []
    for r in leer(P7, "smn_precip_diaria.csv"):
        if r["estacion"] in ESTACIONES_URBANAS and ESCENA4_INICIO <= r["fecha"] <= ESCENA4_FIN:
            filas.append([r["fecha"], r["estacion"], ESTACIONES_URBANAS[r["estacion"]],
                          num(r["precip_mm"]), rep.get(r["fecha"], 0)])
    filas.sort(key=lambda f: (f[0], f[1]))
    escribir("escena-4.csv", ["fecha", "estacion_clave", "estacion", "lluvia_mm", "reportes_desague_dia"], filas)
    return filas


def cifras(e1, e3):
    """Las 3 cifras grandes del capítulo, con unidad, fuente y fecha de corte."""
    prom = [float(f[2]) for f in e1]
    jun_oct = sum(prom[5:10]) / sum(prom) * 100
    ev = max(leer(P7, "eventos_extraordinarios_>=100mm.csv"), key=lambda r: float(r["precip_mm"]))
    por_dia = Counter()
    for r in leer(P5, "ayuntamiento_reportes_drenaje_dia.csv"):
        if r["origen"] == "solicitud" and r["servicio"] == SERVICIO_DESAGUE:
            por_dia[r["fecha_solicitud"]] += int(r["reportes"])
    f_rep, n_rep = max(por_dia.items(), key=lambda kv: kv[1])
    filas = [
        ["lluvia_junio_octubre", f"{jun_oct:.0f}", "% de la lluvia anual", "SMN/CONAGUA, estación 31044 Mérida (OBS), CLICOM",
         "2026-09-25", "Suma de los promedios mensuales 1991-2020 de junio a octubre entre la suma de los 12 meses (escena-1.csv)"],
        ["maxima_lluvia_24h", f"{float(ev['precip_mm']):.0f}", "mm en un día",
         f"SMN/CONAGUA, estación {ev['estacion']} {ev['nombre']}, CLICOM", "2026-09-25",
         f"Máximo diario de las 5 estaciones urbanas ({ev['fecha']}, {ev['evento_asociado']}); eventos_extraordinarios_>=100mm.csv"],
        ["maximo_reportes_dia", str(n_rep), "reportes de calles inundadas en un día", "Ayuntamiento de Mérida, respuesta al folio 1190579126000596 (PNT)",
         "2026-10-29", f"Día con más reportes de desagüe de calles inundadas en 2024-2026 ({f_rep}); solo origen = solicitud"],
    ]
    escribir("cifras.csv", ["cifra", "valor", "unidad", "fuente", "fecha_corte", "calculo"], filas)


if __name__ == "__main__":
    print(f"Escribiendo en {SALIDA}")
    e1 = escena1()
    escena2()
    e3 = escena3()
    escena4()
    cifras(e1, e3)
