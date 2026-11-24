#!/usr/bin/env python3
"""
Ejemplo de extraccion: Coordinacion Estatal de Proteccion Civil de Yucatan (PROCIVY)
"Boletin de ciclones tropicales" (Sistema de Alerta Temprana).

Estructura HTML (verificada 2026-10-01):
  - https://www.yucatan.gob.mx/procivy/boletines.php?t=AAAA      -> lista de sistemas de la temporada (links boletines.php?id=NNAA)
  - https://www.yucatan.gob.mx/procivy/boletines.php?id=NNAA     -> lista de boletines del sistema (links boletin.php?id=K&id_sistema=NNAA)
  - https://www.yucatan.gob.mx/procivy/boletin.php?id=K&id_sistema=NNAA -> boletin: fecha, hora, alerta, posicion, distancia, pronostico
robots.txt de www.yucatan.gob.mx: solo prohibe /paneladminweb/ y /4dm1n/  -> /procivy/ permitido.

Sirve para fechar eventos extraordinarios (ciclones que trajeron lluvia a Merida) y cruzarlos con series de lluvia.
Uso: python3 ejemplo_scraping_procivy.py [anio]  (por defecto 2020; solo baja los 3 primeros sistemas como muestra)
"""
import csv
import html
import re
import sys
import time
import urllib.request

try:
    import requests  # opcional
except ImportError:
    requests = None

BASE = "https://www.yucatan.gob.mx/procivy/"
UA = "MeridaCiudadEsponja-UniProject/0.1 (proyecto universitario)"
PAUSA = 3


def get(url):
    if requests:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=60)
        r.raise_for_status()
        return r.text
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def texto(h):
    h = re.sub(r"<script.*?</script>|<style.*?</style>", " ", h, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h))).strip()


def main(anio="2020", max_sistemas=3):
    idx = get(f"{BASE}boletines.php?t={anio}")
    sistemas = sorted(set(re.findall(r'href="boletines\.php\?id=(\d+)"', idx)))
    filas = []
    for sid in sistemas[:max_sistemas]:
        time.sleep(PAUSA)
        t = texto(get(f"{BASE}boletines.php?id={sid}"))
        nombre = re.search(r"Ciclón:\s*(.+?)\s+Temporada", t)
        # Cada boletin aparece como "XX/NNAA/K dd/Mes/AAAA - HH:MM hrs. <texto>"
        for m in re.finditer(r"([A-Z]{1,3}/\d{4}/\d+)\s+(\d{2}/\w{3}/\d{4})\s*-\s*(\d{1,2}:\d{2})\s*hrs\.\s*(.*?)(?=[A-Z]{1,3}/\d{4}/\d+\s+\d{2}/\w{3}/\d{4}|https://www\.yucatan\.gob\.mx|$)", t):
            resumen = m.group(4).strip()
            dist = re.search(r"(\d+)\s*km al [\w-]+ de Mérida", resumen)
            filas.append({
                "id_sistema": sid,
                "ciclon": nombre.group(1) if nombre else "",
                "boletin": m.group(1),
                "fecha": m.group(2),
                "hora": m.group(3),
                "menciona_lluvia": int(bool(re.search(r"lluvi", resumen, re.I))),
                "dist_merida_km": dist.group(1) if dist else "",
                "resumen": resumen[:400],
            })
    out = f"muestra_procivy_boletines_{anio}.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0].keys()) if filas else ["id_sistema"])
        w.writeheader()
        w.writerows(filas)
    print(f"{len(sistemas)} sistemas en {anio}; {len(filas)} boletines guardados en {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "2020")
