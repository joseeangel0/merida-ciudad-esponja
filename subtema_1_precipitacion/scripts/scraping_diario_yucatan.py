"""Notas del Diario de Yucatán sobre lluvia e inundaciones (solo metadatos), de dic-2017 a la fecha.

Estrategia respetuosa: NO se usa el buscador ni se bajan las notas. Se leen los sitemaps XML que el propio sitio
publica en robots.txt (sitemap_index.xml -> post-sitemap.xml ... post-sitemapN.xml, ~5,000 URLs cada uno) y se
filtran las URLs cuyo «slug» contiene palabras clave de lluvia. La URL ya trae sección y fecha:
  https://www.yucatan.com.mx/<seccion>/AAAA/MM/DD/<slug>.html
robots.txt (verificado el 24-nov-2026) solo prohíbe /wp-admin/ (salvo admin-ajax) y rutas de WooCommerce.
Los textos de las notas tienen derechos de autor: aquí solo se guarda fecha, sección, slug y URL; no se redistribuye
el contenido. Cortesía: User-Agent identificable y 5 s entre peticiones (una por sitemap).

Salida: datos/06_Scraping/diario_yucatan_notas_lluvia_2017_2026.csv
Uso:    python scripts/scraping_diario_yucatan.py
"""
import re
import time
import urllib.request
from pathlib import Path

import pandas as pd

UA = "MeridaCiudadEsponja-UniProject/0.1 (proyecto universitario)"
PAUSA = 5
OUT = Path(__file__).resolve().parent.parent / "datos" / "06_Scraping"
CLAVES = re.compile(r"lluvi|inunda|encharca|aguacero|tormenta|chubasco|precipitaci|huracan|ciclon|pozos-pluvial|onda-tropical|frente-frio", re.I)


def get(url):
    for intento in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read().decode("utf-8", "replace")
        except Exception:
            if intento == 2:
                raise
            time.sleep(15)


def main():
    idx = get("https://www.yucatan.com.mx/sitemap_index.xml")
    posts = [u for u in re.findall(r"<loc>(.*?)</loc>", idx) if "post-sitemap" in u]
    posts.sort(key=lambda u: int(re.search(r"post-sitemap(\d*)", u).group(1) or 1))
    print(f"{len(posts)} sitemaps de notas")
    filas, total = [], 0
    for sm in posts:
        time.sleep(PAUSA)
        urls = re.findall(r"<loc>(https://www\.yucatan\.com\.mx/[^<]+\.html)</loc>", get(sm))
        total += len(urls)
        for u in urls:
            m = re.match(r"https://www\.yucatan\.com\.mx/([\w-]+)/(\d{4})/(\d{2})/(\d{2})/([^/]+)\.html", u)
            if not m or not CLAVES.search(m.group(5)):
                continue
            filas.append(dict(fecha=f"{m.group(2)}-{m.group(3)}-{m.group(4)}", seccion=m.group(1),
                              menciona_merida_slug=int("merida" in m.group(5) or m.group(1) == "merida"),
                              slug=m.group(5), url=u, sitemap=sm.rsplit("/", 1)[-1]))
    df = pd.DataFrame(filas).drop_duplicates("url").sort_values("fecha", ascending=False)
    df.to_csv(OUT / "diario_yucatan_notas_lluvia_2017_2026.csv", index=False)
    print(f"{len(df):,} notas con palabras clave de lluvia, de {total:,} URLs revisadas ({df.fecha.min()} a {df.fecha.max()})")


if __name__ == "__main__":
    main()
