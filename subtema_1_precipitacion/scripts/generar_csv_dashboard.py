"""Genera el CSV mensual de lluvia por estación para la pestaña «Lluvia» del dashboard.

Entrada : datos/07_Datos_propios/smn_precip_diaria.csv  (salida de procesar_datos.py)
          datos/07_Datos_propios/smn_catalogo_estaciones.csv
Salida  : datos/07_Datos_propios/dashboard_lluvia_mensual_por_estacion.csv
          dashboard/data.js  (mismos datos + índices anuales, eventos y periodos de retorno,
                              embebidos para que index.html funcione sin servidor)

Solo stdlib (sin pandas). Ejecutar DESPUÉS de procesar_datos.py, que ya deja en blanco
los meses con 0.0 mm sospechosos (faltantes codificados como cero).
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

DATOS = Path(__file__).resolve().parent.parent / "datos" / "07_Datos_propios"

# Estaciones urbanas operando. Sector APROXIMADO por coordenadas respecto al centro
# (20.9675, -89.6237). Los sectores del dashboard no tienen límites oficiales.
# El Centro no tiene estación propia: no se rellena.
SECTOR = {
    "31036": "Norte",     # C.I.C.Y.
    "31078": "Norte",     # F.I.U.A.D.Y. (Periférico)
    "31097": "Poniente",  # Mérida (CONAGUA)
    "31044": "Poniente",  # Mérida (OBS), suroeste
    "31095": "Oriente",   # Col. Emiliano Zapata
}
NOMBRE_CORTO = {
    "31036": "CICY",
    "31044": "Mérida (OBS)",
    "31078": "FIUADY (Periférico)",
    "31095": "Col. Emiliano Zapata",
    "31097": "Mérida (CONAGUA)",
}
UMBRAL_DIA_LLUVIA = 1.0     # mm: «día con lluvia»
UMBRAL_EVENTO_INTENSO = 50.0  # mm en 24 h
MIN_DIAS_CON_DATO = 25      # mes con menos días con dato => lluvia_mm vacío


def leer(nombre):
    with open(DATOS / nombre, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def num(x):
    return None if x in ("", None) else float(x)


def escribir_data_js(nombres, filas_mensuales):
    """Empaqueta los datos del dashboard en dashboard/data.js (window.DATOS)."""
    est = [{"clave": k, "nombre": NOMBRE_CORTO[k], "sector": SECTOR[k]} for k in sorted(SECTOR)]
    cat = {r["clave"]: r for r in leer("smn_catalogo_estaciones.csv")}
    for e in est:
        c = cat[e["clave"]]
        e.update(lat=float(c["latitud"]), lon=float(c["longitud"]),
                 inicio=c["inicio"][:4], fin=c["fin"][:4])
    prom = {r["clave"]: num(r["precip_anual_media_mm"])
            for r in leer("promedio_anual_por_estacion_1991_2020.csv")}
    for e in est:
        e["prom_1991_2020"] = prom.get(e["clave"])
    claves = set(SECTOR)
    anual = [[r["estacion"], int(r["anio"]), num(r["precip_mm"]), int(float(r["dias_>=50mm"])),
              int(float(r["dias_>=100mm"])), num(r["max_diaria_mm"])]
             for r in leer("indices_lluvia_extrema_por_anio.csv") if r["estacion"] in claves]
    eventos = [[r["estacion"], r["fecha"], num(r["precip_mm"]), r["evento_asociado"]]
               for r in leer("eventos_extraordinarios_>=100mm.csv") if r["estacion"] in claves]
    retorno = [[r["estacion"], int(r["periodo_retorno_anios"]), num(r["lluvia_24h_mm"]),
                num(r["max_observado_mm"]), int(r["anios_usados"])]
               for r in leer("periodos_retorno_lluvia_24h.csv")]
    datos = {
        "generado": __import__("datetime").date.today().isoformat(),
        "estaciones": est,
        # [clave, "YYYY-MM", lluvia_mm|null, dias_con_lluvia|null, eventos_intensos|null]
        "mensual": [[f[2], f[0][:7], num(f[4]), num(f[5]), num(f[6])] for f in filas_mensuales],
        # [clave, año, total_mm|null, dias>=50, dias>=100, max_24h_mm|null]
        "anual": anual,
        # [clave, fecha, mm, evento]
        "eventos": eventos,
        # [clave, T_años, lluvia_24h_mm, max_observado_mm, años_usados]
        "retorno": retorno,
    }
    out = DATOS.parent.parent / "dashboard" / "data.js"
    out.parent.mkdir(exist_ok=True)
    out.write_text("window.DATOS = " + json.dumps(datos, ensure_ascii=False, separators=(",", ":"))
                   + ";\n", encoding="utf-8")
    print(f"dashboard -> {out} ({out.stat().st_size // 1024} KB)")


def main():
    nombres = {}
    with open(DATOS / "smn_catalogo_estaciones.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            nombres[r["clave"]] = r["nombre"]

    # (estacion, "YYYY-MM") -> acumulados
    mes = defaultdict(lambda: {"dias": 0, "mm": 0.0, "lluvia": 0, "intensos": 0})
    with open(DATOS / "smn_precip_diaria.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            est = r["estacion"]
            if est not in SECTOR or r["precip_mm"] == "":
                continue
            v = float(r["precip_mm"])
            m = mes[(est, r["fecha"][:7])]
            m["dias"] += 1
            m["mm"] += v
            m["lluvia"] += v >= UMBRAL_DIA_LLUVIA
            m["intensos"] += v >= UMBRAL_EVENTO_INTENSO

    salida = DATOS / "dashboard_lluvia_mensual_por_estacion.csv"
    filas = []
    with open(salida, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["fecha", "sector", "estacion_clave", "estacion", "lluvia_mm",
                    "dias_con_lluvia", "eventos_intensos", "dias_con_dato", "nota"])
        for (est, ym), m in sorted(mes.items(), key=lambda kv: (kv[0][1], kv[0][0])):
            ok = m["dias"] >= MIN_DIAS_CON_DATO
            nota = "" if ok else "mes sin datos suficientes"
            fila = [f"{ym}-01", SECTOR[est], est, nombres.get(est, est),
                    round(m["mm"], 1) if ok else "",
                    m["lluvia"] if ok else "",
                    m["intensos"] if ok else "",
                    m["dias"], nota]
            w.writerow(fila)
            filas.append(fila)
    print(f"{len(mes)} filas -> {salida}")
    escribir_data_js(nombres, filas)


if __name__ == "__main__":
    main()
