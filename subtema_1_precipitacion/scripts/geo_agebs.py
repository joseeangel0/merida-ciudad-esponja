"""Ubica puntos (lat, lon) en AGEB urbanas y municipios del Marco Geoestadístico 2025 de INEGI (Yucatán).

Sin shapely: pyshp + pyproj + numpy. Uso:

    idx = IndiceAgeb()                 # lee datos/01_INEGI/mg2025_31_yucatan.zip
    idx.ubicar(20.95, -89.65)          # -> dict(cve_mun, nom_mun, cve_loc, cve_ageb, cvegeo_ageb, ubicacion)
"""
import tempfile
import warnings
import zipfile
from pathlib import Path

import numpy as np
import shapefile  # pyshp
from pyproj import CRS, Transformer

warnings.filterwarnings("ignore", category=UserWarning, module="shapefile")

ZIP_MG = Path(__file__).resolve().parent.parent / "datos" / "01_INEGI" / "mg2025_31_yucatan.zip"
VACIO = dict(cve_mun="", nom_mun="", cve_loc="", cve_ageb="", cvegeo_ageb="",
             ubicacion="fuera del Marco Geoestadístico de Yucatán")


class _Capa:
    """Polígonos con prefiltro por caja envolvente (vectorizado) y regla par-impar."""

    def __init__(self, shp_path, encoding="latin-1"):
        r = shapefile.Reader(str(shp_path), encoding=encoding)
        self.campos = [f[0] for f in r.fields[1:]]
        self.formas = list(r.iterShapes())
        self.regs = [dict(zip(self.campos, rec)) for rec in r.iterRecords()]
        self.bbox = np.array([f.bbox for f in self.formas])  # xmin, ymin, xmax, ymax
        self.anillos = []
        for f in self.formas:
            pts = np.asarray(f.points)
            partes = list(f.parts) + [len(pts)]
            self.anillos.append([pts[partes[i]:partes[i + 1]] for i in range(len(partes) - 1)])

    def buscar(self, x, y):
        b = self.bbox
        cand = np.nonzero((x >= b[:, 0]) & (x <= b[:, 2]) & (y >= b[:, 1]) & (y <= b[:, 3]))[0]
        for i in cand:
            cruces = 0
            for ring in self.anillos[i]:
                x1, y1 = ring[:-1, 0], ring[:-1, 1]
                x2, y2 = ring[1:, 0], ring[1:, 1]
                m = (y1 > y) != (y2 > y)
                if m.any():
                    xi = (x2[m] - x1[m]) * (y - y1[m]) / (y2[m] - y1[m]) + x1[m]
                    cruces += int(np.count_nonzero(x < xi))
            if cruces % 2 == 1:
                return self.regs[i]
        return None


class IndiceAgeb:
    def __init__(self, zip_mg=ZIP_MG):
        with tempfile.TemporaryDirectory() as tmp, zipfile.ZipFile(zip_mg) as z:
            for n in z.namelist():
                if Path(n).stem in ("31a", "31mun"):
                    z.extract(n, tmp)
            base = Path(tmp) / "conjunto_de_datos"
            crs = CRS.from_wkt((base / "31a.prj").read_text())
            self.tr = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
            self.agebs = _Capa(base / "31a")
            self.muns = _Capa(base / "31mun")
        self.nom_mun = {r["CVE_MUN"]: r["NOMGEO"] for r in self.muns.regs}

    def ubicar(self, lat, lon):
        out = dict(VACIO)
        x, y = self.tr.transform(lon, lat)
        a = self.agebs.buscar(x, y)
        if a:
            out.update(cve_mun=a["CVE_MUN"], nom_mun=self.nom_mun.get(a["CVE_MUN"], ""), cve_loc=a["CVE_LOC"],
                       cve_ageb=a["CVE_AGEB"], cvegeo_ageb=a["CVEGEO"], ubicacion="AGEB urbana")
            return out
        m = self.muns.buscar(x, y)
        if m:
            out.update(cve_mun=m["CVE_MUN"], nom_mun=m["NOMGEO"], ubicacion="solo municipio (fuera de AGEB urbana)")
        return out
