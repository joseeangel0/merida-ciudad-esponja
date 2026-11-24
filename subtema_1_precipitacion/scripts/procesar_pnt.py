"""Limpia y ANONIMIZA las respuestas de las solicitudes de la PNT (categoría C5).

Entrada (fuera del repo, porque trae datos personales): carpeta con
  1191217326000207.zip   PROCIVY (oficio, resolución y Excel de eventos)         -> C5.3
  596-.zip               Ayuntamiento de Mérida (oficios, Excel y PDF de reportes) -> C5.2
Salida: datos/05_Solicitudes_gobierno/ (solo tablas agregadas, sin nombres, teléfonos, direcciones
ni coordenadas exactas) y las cartas oficiales de respuesta en respuestas/.

Los Excel/PDF del Ayuntamiento traen "Nombre Solicitante", teléfonos, direcciones y coordenadas de
domicilios: NUNCA se copian al repositorio; aquí solo se conservan conteos por día, por mes y AGEB.

Requisitos: pandas, openpyxl, xlrd, pyshp, pyproj, numpy y la herramienta `pdftotext` (poppler).
Uso:        python scripts/procesar_pnt.py [carpeta_con_los_zip]
"""
import collections
import datetime as dt
import hashlib
import io
import re
import statistics
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import openpyxl
import pandas as pd
import xlrd

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from geo_agebs import IndiceAgeb  # noqa: E402

BASE = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else Path.home() / "Developer/dev-des/inbox-upy"
OUT = AQUI.parent / "datos" / "05_Solicitudes_gobierno"
RESP = OUT / "respuestas"
FECHA_RESPUESTA_PROCIVY = dt.date(2026, 10, 28)
MESES = {"ENE": 1, "FEB": 2, "MAR": 3, "ABR": 4, "MAY": 5, "JUN": 6, "JUL": 7, "AGO": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DIC": 12}
# Procedencias que son trabajo programado por el propio Ayuntamiento (no responden a la lluvia ni traen coordenadas).
PROGRAMADO = ("COORDINADOR/TRABAJOS PROGRAMADOS", "PROGRAMA DE MANTENIMIENTO PARA COMISARIAS",
              "PROGRAMA DE MANTENIMIENTO A COLONIAS Y FRACCIONAMIENTOS")
PII = re.compile(r"solicitante|telefono|teléfono|direcci|nombre|correo|calle", re.I)


CONTROLES = []


def ctl(control, valor, detalle=""):
    CONTROLES.append(dict(control=control, valor=valor, detalle=detalle))


def leer_zip(ruta):
    """{nombre_seguro: bytes}. Los datos de la PNT no son de confianza: no se extrae a disco ni se ejecuta nada."""
    with zipfile.ZipFile(ruta) as z:
        return {re.sub(r"[^A-Za-z0-9._ -]", "_", i.filename): z.read(i) for i in z.infolist()}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def limpia(s):
    return re.sub(r"\s+", " ", str(s or "")).strip()


# --------------------------------------------------------------------------- PROCIVY (C5.3)
def parse_fecha_texto(txt):
    """'26 SEP- AL 8 DE OCT. 2024' -> (2024-09-26, 2024-10-08); '1° JUN. 2026' -> (2026-06-01, 2026-06-01)."""
    s = re.sub(r"[.°]", " ", txt.upper()).replace("-", " ")
    s = re.sub(r"\bDE\b", " ", s)
    anio = int(re.search(r"(20\d\d)", s).group(1))
    s = re.sub(r"20\d\d", " ", s)
    partes = re.split(r"\bAL\b|\bY\b", s)
    toks = [re.match(r"\s*(\d{1,2})\s*([A-Z]{3})?", p) for p in partes]
    mes_fin = next((t.group(2) for t in reversed(toks) if t and t.group(2)), None)
    fechas = [dt.date(anio, MESES[(t.group(2) or mes_fin)], int(t.group(1))) for t in toks if t]
    return fechas[0], fechas[-1]


def procivy(z):
    nombre = next(k for k in z if k.endswith(".xlsx"))
    ws = openpyxl.load_workbook(io.BytesIO(z[nombre]), data_only=True).worksheets[0]
    filas = list(ws.iter_rows(values_only=True))
    hi = next(i for i, r in enumerate(filas) if r[0] == "FECHA")
    extra = [c for r in filas[hi:] for c in r[10:] if c not in (None, "")]
    if extra:
        print("AVISO: hay contenido en columnas > 10 del Excel de PROCIVY:", extra[:3])
    out = []
    for r in filas[hi + 1:]:
        if not r[0]:
            continue
        ini, fin = parse_fecha_texto(str(r[0]))
        nota = ""
        if ini > FECHA_RESPUESTA_PROCIVY:
            nota = (f"La fecha original ({limpia(r[0])}) es posterior a la respuesta ({FECHA_RESPUESTA_PROCIVY}): "
                    "probable error de captura; no se corrigió.")
        out.append(dict(fecha_texto_original=limpia(r[0]), fecha_inicio=ini, fecha_fin=fin,
                        fenomeno=limpia(r[1]), alerta_siat=limpia(r[2]), efectos=limpia(r[3]),
                        afectaciones_merida=limpia(r[4]), viviendas_afectadas=limpia(r[5]),
                        personas_afectadas=limpia(r[6]), refugios_activados=limpia(r[7]),
                        lamina_lluvia=limpia(r[8]), declaratorias=limpia(r[9]), nota=nota))
    df = pd.DataFrame(out)
    df.to_csv(OUT / "procivy_eventos_2024_2026.csv", index=False)
    ctl("PROCIVY: eventos registrados", len(df), f"{df.fecha_inicio.min()} a {df[df.nota == ''].fecha_inicio.max()} (sin contar la fecha con error)")
    ctl("PROCIVY: fechas posteriores a la respuesta (no corregidas)", int((df.nota != "").sum()), "; ".join(df[df.nota != ""].fecha_texto_original))
    return df


# --------------------------------------------------------------------------- Ayuntamiento: reportes de drenaje (xls)
def fecha_dmy(v):
    m = re.match(r"(\d{2})-(\d{2})-(\d{4})", str(v).strip())
    return dt.date(int(m[3]), int(m[2]), int(m[1])) if m else None


def drenaje_xls(z, idx):
    nombre = next(k for k in z if k.lower().endswith(".xls"))
    wb = xlrd.open_workbook(file_contents=z[nombre])
    filas = []
    for sh in wb.sheets():
        hi = next(i for i in range(min(15, sh.nrows)) if "Folio" in [str(c.value).strip() for c in sh.row(i)])
        col = {str(c.value).strip(): j for j, c in enumerate(sh.row(hi)) if str(c.value).strip()}
        for i in range(hi + 1, sh.nrows):
            r = [c.value for c in sh.row(i)]
            if not str(r[col["Folio"]]).strip():
                continue
            lat = lon = None
            m = re.match(r"\s*(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)", str(r[col["Coordenadas"]]))
            if m:
                lat, lon = float(m[1]), float(m[2])
            sol, atn = fecha_dmy(r[col["Fecha Sol"]]), fecha_dmy(r[col["Fecha ATN"]])
            filas.append(dict(sol=sol, dias=(atn - sol).days if sol and atn and atn >= sol else None,
                              depto=limpia(r[col["Dep"]]).replace("DRENAJE ", "").title(),
                              servicio=limpia(r[col["Servicio"]]), estado=limpia(r[col["Estado"]]),
                              procedencia=limpia(r[col["Procedencia"]]),
                              lat=lat, lon=lon))
    df = pd.DataFrame(filas)
    print(f"reportes de drenaje: {len(df):,} ({df.sol.min()} a {df.sol.max()}); sin fecha: {df.sol.isna().sum()}")

    df["origen"] = df.procedencia.map(lambda p: "trabajo_programado" if p in PROGRAMADO else "solicitud")
    ctl("Drenaje: reportes en el XLS", len(df), f"{df.sol.min()} a {df.sol.max()}; sin fecha: {int(df.sol.isna().sum())}")
    ctl("Drenaje: reportes por trabajo programado", f"{100 * (df.origen == 'trabajo_programado').mean():.1f} %", "sin coordenadas; no responden a la lluvia")
    ctl("Drenaje: solicitudes con coordenadas", f"{100 * df[df.origen == 'solicitud'].lat.notna().mean():.1f} %", "el campo trae solo una coma cuando no hay coordenadas")
    print("  origen:", df.origen.value_counts().to_dict(),
          "| con coordenadas por origen:", df.assign(c=df.lat.notna()).groupby("origen").c.mean().round(2).to_dict())

    # --- por día
    g = df.dropna(subset=["sol"]).groupby(["sol", "depto", "servicio", "procedencia", "origen"])
    dia = g.agg(reportes=("estado", "size"), atendidos=("estado", lambda s: int((s == "Atendida").sum())),
                dias_atencion_mediana=("dias", "median")).reset_index().rename(columns={"sol": "fecha_solicitud", "depto": "departamento"})
    dia["dias_atencion_mediana"] = dia["dias_atencion_mediana"].round(1)
    dia.to_csv(OUT / "ayuntamiento_reportes_drenaje_dia.csv", index=False, date_format="%Y-%m-%d")

    # --- por mes y AGEB (las coordenadas exactas no salen de esta función)
    cache = {}
    def agebs(lat, lon):
        if lat is None or not (20.5 <= lat <= 21.5 and -90.2 <= lon <= -89.2):
            return "SIN_COORDENADAS_VALIDAS"
        k = (round(lat, 5), round(lon, 5))
        if k not in cache:
            cache[k] = idx.ubicar(lat, lon)["cvegeo_ageb"] or "SIN_AGEB_URBANA"
        return cache[k]
    df["cvegeo_ageb"] = [agebs(a, b) for a, b in zip(df.lat, df.lon)]
    d2 = df.dropna(subset=["sol"]).copy()
    d2["mes"] = pd.to_datetime(d2["sol"]).dt.strftime("%Y-%m")
    mes = (d2.groupby(["mes", "cvegeo_ageb", "servicio", "origen"]).size().reset_index(name="reportes")
           .sort_values(["mes", "cvegeo_ageb", "servicio", "origen"]))
    mes.to_csv(OUT / "ayuntamiento_reportes_drenaje_ageb_mes.csv", index=False)
    sin = d2.cvegeo_ageb.str.startswith("SIN_")
    print(f"  AGEB únicas: {d2.cvegeo_ageb.nunique()}; sin AGEB o sin coordenadas: {100 * sin.mean():.1f} % del total, "
          f"{100 * sin[d2.origen == 'solicitud'].mean():.1f} % de las solicitudes")
    ctl("Drenaje: AGEB distintas con reportes", d2.cvegeo_ageb[~sin].nunique(), "Marco Geoestadístico 2025")
    ctl("Drenaje: solicitudes sin AGEB urbana o sin coordenadas", f"{100 * sin[d2.origen == 'solicitud'].mean():.1f} %", "quedan como SIN_*")
    return dia, mes


# --------------------------------------------------------------------------- anexo PDF: desagüe de calles 2018-2022
def desague_historico(z):
    nombre = next(k for k in z if k.upper().startswith("ANEXO") and k.lower().endswith(".pdf"))
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "anexo.pdf"
        p.write_bytes(z[nombre])
        txt = subprocess.run(["pdftotext", "-layout", str(p), "-"], capture_output=True, text=True, check=True).stdout
    pat = re.compile(r"^(\d{5,7})\s+(\d{2}/\d{2}/\d{4})\s+(\d{2}/\d{2}/\d{4})\s+\d{2}:\d{2}\s+"
                     r"DESAG[ÜU]E DE CALLES INUNDADAS \((ORIENTE|PONIENTE)\)", re.M)
    vistos, filas = set(), []
    for folio, s, a, zona in pat.findall(txt):
        if folio in vistos:
            continue
        vistos.add(folio)
        fs, fa = dt.datetime.strptime(s, "%d/%m/%Y").date(), dt.datetime.strptime(a, "%d/%m/%Y").date()
        filas.append(dict(fecha_solicitud=fs, zona=zona.title(), dias=(fa - fs).days if fa >= fs else None))
    esperado = len(re.findall(r"^\d{5,7}\s+\d{2}/\d{2}/\d{4}", txt, re.M))
    df = pd.DataFrame(filas)
    print(f"anexo PDF: {len(df):,} reportes únicos (líneas con folio: {esperado:,}); {df.fecha_solicitud.min()} a {df.fecha_solicitud.max()}")
    ctl("Anexo PDF: líneas con folio / reportes únicos", f"{esperado:,} / {len(df):,}", f"{esperado - len(df)} folios repetidos descartados; {df.fecha_solicitud.min()} a {df.fecha_solicitud.max()}")
    ctl("Anexo PDF: años cubiertos", ", ".join(map(str, sorted({d.year for d in df.fecha_solicitud}))), "no hay registros de 2023")
    g = df.groupby(["fecha_solicitud", "zona"]).agg(reportes=("dias", "size"), dias_atencion_mediana=("dias", "median")).reset_index()
    g["dias_atencion_mediana"] = g["dias_atencion_mediana"].round(1)
    g.to_csv(OUT / "ayuntamiento_desague_calles_historico_dia.csv", index=False, date_format="%Y-%m-%d")
    return df


# --------------------------------------------------------------------------- Excel de desagüe con litros
def norm_colonia(s):
    s = re.sub(r"\s*\.\s*", ". ", str(s or "").upper()).strip()
    return re.sub(r"\s+", " ", s)


def desague_litros(z):
    nombre = next(k for k in z if k.lower().endswith(".xlsx"))
    wb = openpyxl.load_workbook(io.BytesIO(z[nombre]), read_only=True, data_only=True)
    filas, por_hoja = [], {}
    for hoja in ("2024", "2025", "2026", "30MAY-1JUNIO"):
        rows = list(wb[hoja].iter_rows(values_only=True))
        h = [str(c).strip() if c is not None else "" for c in rows[1]]
        col = {n: i for i, n in enumerate(h) if n}
        c_f = col.get("FECHA ATENCIÓN", col.get("FECHA"))
        n = 0
        for r in rows[2:]:
            f = r[c_f] if r[c_f] else r[col.get("FECHA SOLICITUD", c_f)]
            if r[0] in (None, "") or not isinstance(f, dt.datetime):
                continue
            filas.append(dict(hoja=hoja, fecha=f.date(), colonia=norm_colonia(r[col["COLONIA"]]),
                              litros=int(r[col["LITROS"]] or 0)))
            n += 1
        por_hoja[hoja] = n
    df = pd.DataFrame(filas)
    print("desagüe con litros, filas por hoja:", por_hoja, "(la hoja 30MAY-1JUNIO es un extracto de 2026 y no se suma)")
    base = df[df.hoja != "30MAY-1JUNIO"]
    g = base.groupby(["fecha", "colonia"]).agg(servicios=("litros", "size"), litros=("litros", "sum")).reset_index()
    g.to_csv(OUT / "ayuntamiento_desague_calles_litros_colonia_dia.csv", index=False, date_format="%Y-%m-%d")
    tot = [c for c in list(wb["TOTALES"].iter_rows(values_only=True))[4] if c is not None]  # [rep24, lt24, rep25, lt25, rep26, lt26, rep, lt]
    for i, hoja in enumerate(("2024", "2025", "2026")):
        h = df[df.hoja == hoja]
        ok = len(h) == tot[2 * i] and int(h.litros.sum()) == tot[2 * i + 1]
        ctl(f"Desagüe con litros, hoja {hoja}: filas y litros vs hoja TOTALES", "coincide" if ok else "NO COINCIDE",
            f"{len(h)} reportes y {int(h.litros.sum()):,} L (oficial: {tot[2 * i]} y {tot[2 * i + 1]:,} L)")
    e = df[(df.hoja == "2026") & (df.fecha >= dt.date(2026, 5, 30)) & (df.fecha <= dt.date(2026, 6, 1))]
    x = df[df.hoja == "30MAY-1JUNIO"]
    ctl("Desagüe: hoja 30MAY-1JUNIO es un extracto de 2026", "sí" if (len(e), e.litros.sum()) == (len(x), x.litros.sum()) else "NO",
        f"{len(x)} reportes y {int(x.litros.sum()):,} L; no se suma dos veces")
    desfase = df[df.hoja.isin(["2024", "2025", "2026"]) & (df.fecha.map(lambda d: str(d.year)) != df.hoja)]
    ctl("Desagüe: filas con año distinto al de su hoja", len(desfase), "se conservan con su fecha real")
    return df


# --------------------------------------------------------------------------- cartas oficiales + procedencia
def sin_metadatos(pdf_bytes):
    """Copia el PDF sin metadatos (autor, programa, etc.): son datos incidentales de quien lo redactó."""
    from pypdf import PdfReader, PdfWriter
    w = PdfWriter()
    for pagina in PdfReader(io.BytesIO(pdf_bytes)).pages:
        w.add_page(pagina)
    w.add_metadata({"/Producer": "", "/Creator": "", "/Author": "", "/Title": ""})
    buf = io.BytesIO()
    w.write(buf)
    return buf.getvalue()


def copiar_respuestas(z207, z596):
    """Cartas oficiales de respuesta (sin metadatos). Los Excel/PDF con datos personales no se copian."""
    RESP.mkdir(exist_ok=True)
    pdfs = {
        "C5.1_conagua_340009400252326_respuesta.pdf": (BASE / "Respuesta 340009400252326_r.pdf").read_bytes(),
        "C5.1_conagua_340009400252226_respuesta_folio_erroneo.pdf": (BASE / "Respuesta 340009400252226_r.pdf").read_bytes(),
    }
    originales_no_publicados = {}
    for k, v in z207.items():
        if k.endswith(".pdf"):
            pdfs["C5.3_procivy_1191217326000207_" + ("oficio_respuesta" if "Oficio" in k else "resolucion_UT") + ".pdf"] = v
        else:  # Excel de PROCIVY: su contenido está en procivy_eventos_2024_2026.csv
            originales_no_publicados[f"1191217326000207.zip/{k}"] = (v, "no (el contenido está en procivy_eventos_2024_2026.csv; metadatos de autoría)")
    nombres596 = {"Respuesta 596.pdf": "oficio_gobernacion_GOB-367", "Ofic 571 Respuesta Solicitud 1190579126000596.pdf": "oficio_participacion_ciudadana_571",
                  "596 sp.pdf": "oficio_servicios_publicos_677"}
    for k, v in z596.items():
        if k in nombres596:
            pdfs[f"C5.2_ayuntamiento_1190579126000596_{nombres596[k]}.pdf"] = v
        else:
            originales_no_publicados[f"596-.zip/{k}"] = (v, "no (contiene datos personales de solicitantes)")
    for f in RESP.glob("*"):
        f.unlink()
    filas = []
    for k, v in pdfs.items():
        limpio = sin_metadatos(v)
        (RESP / k).write_bytes(limpio)
        filas.append(dict(archivo=f"respuestas/{k}", en_git="si (carta oficial sin metadatos)", sha256_original=sha(v),
                          sha256_publicado=sha(limpio), bytes_publicado=len(limpio)))
    for k, (v, motivo) in originales_no_publicados.items():
        filas.append(dict(archivo=f"[original] {k}", en_git=motivo, sha256_original=sha(v), sha256_publicado="", bytes_publicado=0))
    pd.DataFrame(filas).to_csv(OUT / "respuestas_pnt_procedencia.csv", index=False)


if __name__ == "__main__":
    z207 = leer_zip(BASE / "1191217326000207.zip")
    z596 = leer_zip(BASE / "596-.zip")
    OUT.mkdir(exist_ok=True)
    idx = IndiceAgeb()
    p = procivy(z207)
    print(f"PROCIVY: {len(p)} eventos; con nota: {int((p.nota != '').sum())}")
    drenaje_xls(z596, idx)
    desague_historico(z596)
    desague_litros(z596)
    copiar_respuestas(z207, z596)
    pd.DataFrame(CONTROLES).to_csv(OUT / "controles_calidad_pnt.csv", index=False)
    # control de privacidad: ninguna salida debe traer columnas con datos personales
    for f in OUT.glob("*.csv"):
        malas = [c for c in pd.read_csv(f, nrows=0).columns if PII.search(c)]
        if malas:
            sys.exit(f"{f.name} trae columnas sensibles: {malas}")
    print("control de privacidad: sin columnas de nombre, teléfono o dirección en las salidas")
