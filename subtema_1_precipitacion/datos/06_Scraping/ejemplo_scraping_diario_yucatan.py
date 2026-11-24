#!/usr/bin/env python3
"""
Ejemplo de extraccion: Diario de Yucatan (yucatan.com.mx) - notas sobre lluvias/inundaciones en Merida.

Estrategia respetuosa: NO se usa el buscador; se recorren los sitemaps XML que el propio sitio publica
en robots.txt (sitemap_index.xml -> post-sitemap.xml ... post-sitemapN.xml, ~5000 URLs cada uno, desde dic-2017)
y se filtran las URLs cuyo "slug" contiene palabras clave. La URL ya trae seccion y fecha:
  https://www.yucatan.com.mx/<seccion>/AAAA/MM/DD/<slug>.html
robots.txt (verificado 2026-10-01): User-agent: * solo prohibe /wp-admin/, /100-joyas/ y rutas de woocommerce.

Opcional: por cada URL se puede bajar la nota y leer <meta property="og:title"> / article:published_time.
El texto de las notas tiene derechos de autor: guardar solo metadatos (titulo, fecha, URL) y datos puntuales
(mm de lluvia, colonias afectadas) con cita; no redistribuir el texto completo.

Uso: python3 ejemplo_scraping_diario_yucatan.py [n_sitemaps]   (por defecto 2: los dos sitemaps mas recientes)
"""
import csv
import re
import sys
import time
import urllib.request

try:
    import requests  # opcional
except ImportError:
    requests = None

UA = "MeridaCiudadEsponja-UniProject/0.1 (proyecto universitario)"
PAUSA = 5
CLAVES = re.compile(r"lluvi|inunda|encharca|aguacero|tormenta|chubasco|precipitaci|huracan|ciclon|pozos-pluvial|onda-tropical|frente-frio", re.I)


def get(url):
    if requests:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=90)
        r.raise_for_status()
        return r.text
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read().decode("utf-8", "replace")


def main(n_sitemaps=2):
    idx = get("https://www.yucatan.com.mx/sitemap_index.xml")
    posts = [u for u in re.findall(r"<loc>(.*?)</loc>", idx) if "post-sitemap" in u]
    posts.sort(key=lambda u: int(re.search(r"post-sitemap(\d*)", u).group(1) or 1))
    filas = []
    for sm in posts[-n_sitemaps:]:
        time.sleep(PAUSA)
        xml = get(sm)
        for u in re.findall(r"<loc>(https://www\.yucatan\.com\.mx/[^<]+\.html)</loc>", xml):
            m = re.match(r"https://www\.yucatan\.com\.mx/([\w-]+)/(\d{4})/(\d{2})/(\d{2})/([^/]+)\.html", u)
            if not m or not CLAVES.search(m.group(5)):
                continue
            filas.append({
                "fecha": f"{m.group(2)}-{m.group(3)}-{m.group(4)}",
                "seccion": m.group(1),
                "menciona_merida_slug": int("merida" in m.group(5) or m.group(1) == "merida"),
                "slug": m.group(5),
                "url": u,
                "sitemap": sm.rsplit("/", 1)[-1],
            })
    filas.sort(key=lambda r: r["fecha"], reverse=True)
    with open("muestra_diario_yucatan_notas_lluvia.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["fecha", "seccion", "menciona_merida_slug", "slug", "url", "sitemap"])
        w.writeheader()
        w.writerows(filas)
    print(f"{len(filas)} notas con palabras clave de lluvia en {n_sitemaps} sitemap(s)")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 2)
