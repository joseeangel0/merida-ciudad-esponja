"""
Descarga y limpia el LiDAR satelital de la NASA sobre Mérida (fuente C8.3):
  - GEDI L2A v002 (LP DAAC): elevación del terreno y alturas de dosel (rh) por huella de ~25 m
  - ICESat-2 ATL08 v007 (NSIDC): terreno y dosel por segmento de 100 m

No se bajan los archivos completos (GEDI pesa ~100 GB para Mérida). Se usa el servicio
Harmony "Trajectory Subsetter" de la NASA, que recorta en su servidor al bbox de Mérida
y devuelve HDF5 pequeños. Después se extraen los puntos, se filtran por calidad y se
convierten las alturas elipsoidales (WGS84) a ortométricas (geoide EGM2008) para que
sean comparables con el MDT de INEGI.

Salidas en datos/08_LiDAR/NASA_GEDI_ICESat2/:
  hdf5_gedi/, hdf5_atl08/        HDF5 recortados (no van a git)
  gedi_l2a_merida.csv            huellas GEDI que pasan los filtros de calidad
  atl08_merida.csv               segmentos ATL08 con terreno válido

Credenciales de NASA Earthdata (en este orden):
  1. Variables de entorno EARTHDATA_USERNAME / EARTHDATA_PASSWORD
  2. ~/.netrc (machine urs.earthdata.nasa.gov)
  3. Se piden en la terminal y, si aceptas, se guardan en ~/.netrc (permisos 600)

Requisitos: harmony-py, h5py, pandas, numpy, pyproj
Uso:        python descargar_nasa_lidar.py                  # descarga + procesa
            python descargar_nasa_lidar.py --solo-procesar  # reprocesa HDF5 ya bajados
            python descargar_nasa_lidar.py --producto gedi  # solo uno (gedi | atl08)
"""
import argparse
import getpass
import netrc
import os
import sys
from pathlib import Path

import h5py
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent.parent / "datos" / "08_LiDAR" / "NASA_GEDI_ICESat2"
BBOX = (-89.75, 20.88, -89.53, 21.10)  # oeste, sur, este, norte (mismo AOI que 08_LiDAR/README.md)
URS = "urs.earthdata.nasa.gov"

PRODUCTOS = {
    # concept-id de CMR: GEDI02_A v002 (LPCLOUD) y ATL08 v007 (NSIDC_CPRD)
    "gedi": {"coleccion": "C2142771958-LPCLOUD", "carpeta": "hdf5_gedi"},
    "atl08": {"coleccion": "C3565574177-NSIDC_CPRD", "carpeta": "hdf5_atl08"},
}

GEDI_BEAMS_POTENCIA = {"BEAM0101", "BEAM0110", "BEAM1000", "BEAM1011"}
GEDI_SENSIBILIDAD_MIN = 0.9   # recomendación LP DAAC para filtrar huellas confiables
ATL08_FILL = 3.0e38           # valores >= a esto son "sin dato" en ATL08


# ---------------------------------------------------------------- credenciales
def credenciales():
    u, p = os.environ.get("EARTHDATA_USERNAME"), os.environ.get("EARTHDATA_PASSWORD")
    if u and p:
        return u, p
    try:
        auth = netrc.netrc().authenticators(URS)
        if auth:
            return auth[0], auth[2]
    except (FileNotFoundError, netrc.NetrcParseError):
        pass
    if not sys.stdin.isatty():
        sys.exit("No hay credenciales de Earthdata. Corre el script en tu terminal o define "
                 "EARTHDATA_USERNAME y EARTHDATA_PASSWORD.")
    print("Credenciales de NASA Earthdata (https://urs.earthdata.nasa.gov)")
    u = input("  Usuario: ").strip()
    p = getpass.getpass("  Contraseña: ")
    if input("  ¿Guardar en ~/.netrc para no volver a pedirlas? [s/N]: ").strip().lower() == "s":
        ruta = Path.home() / ".netrc"
        with open(ruta, "a") as f:
            f.write(f"\nmachine {URS} login {u} password {p}\n")
        ruta.chmod(0o600)
        print(f"  Guardadas en {ruta}")
    return u, p


# ---------------------------------------------------------------- descarga (Harmony)
def descargar(producto, auth):
    from harmony import BBox, Client, Collection, Request

    destino = BASE / PRODUCTOS[producto]["carpeta"]
    destino.mkdir(parents=True, exist_ok=True)
    cliente = Client(auth=auth)
    req = Request(
        collection=Collection(id=PRODUCTOS[producto]["coleccion"]),
        spatial=BBox(*BBOX),
        ignore_errors=True,  # granulos sin puntos dentro del bbox no tumban el trabajo
        skip_preview=True,
    )
    if not req.is_valid():
        sys.exit(f"Solicitud inválida para {producto}: {req.validation_errors()}")
    job = cliente.submit(req)
    print(f"[{producto}] Trabajo Harmony {job}: https://harmony.earthdata.nasa.gov/jobs/{job}")
    cliente.wait_for_processing(job, show_progress=True)
    estado = cliente.status(job)
    print(f"[{producto}] Estado: {estado['status']} — {estado.get('message', '')}")
    archivos = [f.result() for f in cliente.download_all(job, directory=str(destino))]
    print(f"[{producto}] {len(archivos)} archivos en {destino}")


# ---------------------------------------------------------------- lectura HDF5
def leer(grupo, ruta, n):
    """Dataset 1-D o NaN si no existe en el archivo recortado."""
    return grupo[ruta][()] if ruta in grupo else np.full(n, np.nan)


def extraer_gedi(path):
    filas = []
    with h5py.File(path, "r") as f:
        for beam in [k for k in f if k.startswith("BEAM")]:
            g = f[beam]
            if "lat_lowestmode" not in g or g["lat_lowestmode"].shape[0] == 0:
                continue
            n = g["lat_lowestmode"].shape[0]
            rh = g["rh"][()] if "rh" in g else np.full((n, 101), np.nan)
            filas.append(pd.DataFrame({
                "shot_number": g["shot_number"][()].astype("uint64"),
                "delta_time": g["delta_time"][()],
                "beam": beam,
                "potencia": beam in GEDI_BEAMS_POTENCIA,
                "lat": g["lat_lowestmode"][()],
                "lon": g["lon_lowestmode"][()],
                "elev_terreno_elip_m": g["elev_lowestmode"][()],
                "elev_dosel_elip_m": leer(g, "elev_highestreturn", n),
                "rh50_m": rh[:, 50],
                "rh98_m": rh[:, 98],
                "rh100_m": rh[:, 100],
                "quality_flag": g["quality_flag"][()],
                "degrade_flag": leer(g, "degrade_flag", n),
                "sensitivity": g["sensitivity"][()],
                "elev_tandemx_m": leer(g, "digital_elevation_model", n),
                "archivo": path.name,
            }))
    return pd.concat(filas) if filas else pd.DataFrame()


def extraer_atl08(path):
    filas = []
    with h5py.File(path, "r") as f:
        # sc_orient 0 = hacia atrás (haces izquierdos fuertes), 1 = hacia adelante (derechos fuertes)
        orient = int(f["orbit_info/sc_orient"][0]) if "orbit_info/sc_orient" in f else -1
        for gt in [k for k in f if k.startswith("gt")]:
            if "land_segments/latitude" not in f[gt]:
                continue
            s = f[gt]["land_segments"]
            n = s["latitude"].shape[0]
            if n == 0:
                continue
            fuerte = (orient == 0 and gt.endswith("l")) or (orient == 1 and gt.endswith("r"))
            filas.append(pd.DataFrame({
                "delta_time": s["delta_time"][()],
                "beam": gt,
                "haz_fuerte": fuerte,
                "lat": s["latitude"][()],
                "lon": s["longitude"][()],
                "elev_terreno_elip_m": leer(s, "terrain/h_te_best_fit", n),
                "incert_terreno_m": leer(s, "terrain/h_te_uncertainty", n),
                "altura_dosel_m": leer(s, "canopy/h_canopy", n),
                "night_flag": leer(s, "night_flag", n),
                "urban_flag": leer(s, "urban_flag", n),
                "segment_watermask": leer(s, "segment_watermask", n),
                "archivo": path.name,
            }))
    return pd.concat(filas) if filas else pd.DataFrame()


# ---------------------------------------------------------------- limpieza
def geoide_egm2008(df, col_elip, col_orto):
    """Altura elipsoidal WGS84 -> ortométrica EGM2008 (descarga la malla de cdn.proj.org)."""
    import pyproj
    from pyproj import Transformer

    pyproj.network.set_network_enabled(True)
    t = Transformer.from_crs("EPSG:4979", "EPSG:4326+3855", always_xy=True)
    if abs(t.transform(-89.62, 20.97, 0.0)[2]) < 1:  # sin malla del geoide no hay corrección
        print("  AVISO: no se pudo cargar la malla EGM2008; la columna ortométrica queda vacía.")
        df[col_orto] = np.nan
        return df
    df[col_orto] = t.transform(df["lon"].values, df["lat"].values, df[col_elip].values)[2].round(3)
    return df


def dentro_bbox(df):
    w, s, e, n = BBOX
    return df[df.lon.between(w, e) & df.lat.between(s, n)]


def hdf5_locales(producto):
    carpeta = BASE / PRODUCTOS[producto]["carpeta"]
    return sorted(a for a in carpeta.glob("*") if a.suffix.lower() in {".h5", ".hdf5", ".he5"})


def procesar_gedi():
    archivos = hdf5_locales("gedi")
    if not archivos:
        return print("[gedi] No hay HDF5 descargados.")
    df = pd.concat([extraer_gedi(a) for a in archivos], ignore_index=True)
    total = len(df)
    df = dentro_bbox(df)
    df = df[(df.quality_flag == 1) & (df.degrade_flag == 0) & (df.sensitivity >= GEDI_SENSIBILIDAD_MIN)]
    df["fecha_utc"] = pd.Timestamp("2018-01-01", tz="UTC") + pd.to_timedelta(df.delta_time, unit="s")
    df = geoide_egm2008(df, "elev_terreno_elip_m", "elev_terreno_egm08_m")
    df["shot_number"] = df.shot_number.astype(str)  # evita que Excel lo redondee
    cols = ["shot_number", "fecha_utc", "beam", "potencia", "lat", "lon",
            "elev_terreno_elip_m", "elev_terreno_egm08_m", "elev_dosel_elip_m",
            "rh50_m", "rh98_m", "rh100_m", "sensitivity", "elev_tandemx_m", "archivo"]
    salida = BASE / "gedi_l2a_merida.csv"
    df.sort_values("fecha_utc")[cols].to_csv(salida, index=False)
    print(f"[gedi] {total} huellas leídas -> {len(df)} válidas en el bbox ({df.archivo.nunique()} órbitas) -> {salida.name}")


def procesar_atl08():
    archivos = hdf5_locales("atl08")
    if not archivos:
        return print("[atl08] No hay HDF5 descargados.")
    df = pd.concat([extraer_atl08(a) for a in archivos], ignore_index=True)
    total = len(df)
    for c in ["elev_terreno_elip_m", "incert_terreno_m", "altura_dosel_m"]:
        df.loc[df[c] >= ATL08_FILL, c] = np.nan
    df = dentro_bbox(df).dropna(subset=["elev_terreno_elip_m"])
    # delta_time cuenta desde la época ATLAS (2018-01-01); el desfase GPS-UTC (~18 s) no importa aquí
    df["fecha_utc"] = pd.Timestamp("2018-01-01", tz="UTC") + pd.to_timedelta(df.delta_time, unit="s")
    df = geoide_egm2008(df, "elev_terreno_elip_m", "elev_terreno_egm08_m")
    cols = ["fecha_utc", "beam", "haz_fuerte", "lat", "lon", "elev_terreno_elip_m",
            "elev_terreno_egm08_m", "incert_terreno_m", "altura_dosel_m",
            "night_flag", "urban_flag", "segment_watermask", "archivo"]
    salida = BASE / "atl08_merida.csv"
    df.sort_values("fecha_utc")[cols].to_csv(salida, index=False)
    print(f"[atl08] {total} segmentos leídos -> {len(df)} con terreno válido ({df.archivo.nunique()} pasadas) -> {salida.name}")


# ---------------------------------------------------------------- principal
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--producto", choices=["gedi", "atl08", "ambos"], default="ambos")
    ap.add_argument("--solo-procesar", action="store_true", help="no descarga; solo reprocesa los HDF5 locales")
    args = ap.parse_args()
    productos = ["gedi", "atl08"] if args.producto == "ambos" else [args.producto]

    if not args.solo_procesar:
        auth = credenciales()
        for p in productos:
            descargar(p, auth)
    for p in productos:
        {"gedi": procesar_gedi, "atl08": procesar_atl08}[p]()
