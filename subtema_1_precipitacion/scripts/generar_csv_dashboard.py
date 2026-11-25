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


P5 = DATOS.parent / "05_Solicitudes_gobierno"


def leer(nombre, carpeta=None):
    with open((carpeta or DATOS) / nombre, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def datos_pnt():
    """Series de reportes de drenaje (C5.2) y eventos de PROCIVY (C5.3) para el dashboard."""
    mes_anexo, mes_xls, mes_total = defaultdict(int), defaultdict(int), defaultdict(int)
    dia_des, dia_tot = defaultdict(int), defaultdict(int)
    for r in leer("ayuntamiento_desague_calles_historico_dia.csv", P5):
        mes_anexo[r["fecha_solicitud"][:7]] += int(r["reportes"])
    for r in leer("ayuntamiento_reportes_drenaje_dia.csv", P5):
        if r["origen"] != "solicitud":     # el trabajo programado no responde a la lluvia
            continue
        n, f = int(r["reportes"]), r["fecha_solicitud"]
        mes_total[f[:7]] += n
        dia_tot[f] += n
        if r["servicio"].startswith("DESAGÜE DE CALLES INUNDADAS"):
            mes_xls[f[:7]] += n
            dia_des[f] += n
    ini, fin = "2026-05-18", "2026-06-08"
    dias = sorted({f for f in dia_tot if ini <= f <= fin})
    lluvia = [[r["estacion"], r["fecha"], num(r["precip_mm"])] for r in leer("smn_precip_diaria.csv")
              if r["estacion"] in SECTOR and ini <= r["fecha"] <= fin]
    procivy = [[r["fecha_texto_original"], r["fecha_inicio"], r["fenomeno"], r["alerta_siat"], r["efectos"],
                r["afectaciones_merida"], r["personas_afectadas"], r["declaratorias"], r["nota"]]
               for r in leer("procivy_eventos_2024_2026.csv", P5)]
    dia_ev = "2022-06-28"   # día con la máxima lluvia en 1 h de la ESMA «MERIDA»
    esma = {"mensual": [[r["mes"], int(r["registros"]), num(r["cobertura_pct"]), num(r["lluvia_total_mm"]), num(r["max_10min_mm"]),
                         num(r["max_1h_mm"]), num(r["max_24h_mm"]), num(r["lluvia_clicom_31044_mm"]), num(r["correlacion_diaria_clicom"]), r["nota"]]
                        for r in leer("conagua_esma_merida_intensidad_mensual_2022.csv", P5)],
            "dia": dia_ev,
            "tormenta": [[r["fecha_hora_local"][11:], num(r["precipitacion_mm"])] for r in leer("conagua_esma_merida_10min_2022.csv", P5)
                         if r["fecha_hora_local"].startswith(dia_ev)]}
    return {
        "esma2022": esma,
        "reportes_mes": {"anexo": sorted(mes_anexo.items()), "xls_desague": sorted(mes_xls.items()),
                         "xls_total": sorted(mes_total.items())},
        "evento": {"dias": dias, "desague": [dia_des.get(d, 0) for d in dias], "total": [dia_tot.get(d, 0) for d in dias],
                   "lluvia": lluvia},
        "procivy": procivy,
    }


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
        **datos_pnt(),
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
