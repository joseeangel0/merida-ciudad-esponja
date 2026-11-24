# 08_LiDAR — Modelos de elevación de Mérida (descargados 2026-10-01)

Área de interés: lon -89.75 a -89.53, lat 20.88 a 21.10 (centro 20.97, -89.62).

## AVISO IMPORTANTE sobre el origen de los datos

INEGI publica estos modelos dentro de la línea "Modelos Digitales de Elevación de alta
resolución LiDAR" (la ruta de descarga incluye `/lidar/`), pero los **metadatos de las
cartas que cubren Mérida dicen que se derivan de fotogrametría de imágenes de satélite
estereoscópicas, no de un vuelo LiDAR**:

- 5 m F16C52A1 (2016): "Modelo Digital de Elevación de Tipo Terreno, elaborado con insumos de imágenes ópticas de satélite".
- 1.5 m F16C52A1 (2023/2025): "derivado de nubes de puntos fotogramétricas ... imágenes de satélite de alta resolución captadas en modo estereoscópico"; insumos del 2017-03-11 y del 2023-07-05.
- Solo F16C51F1 y F16C51F2 (2011–2012, formato GRID) traen la etiqueta "LIDAR" en las palabras clave, aunque su título dice "insumos de métodos fotogramétricos".

Cítese en el proyecto como "MDE de alta resolución INEGI (fotogramétrico)", no como "LiDAR".

## Contenido

| Carpeta/archivo | Qué es |
|---|---|
| `MDT_5m/` | 25 cartas 1:10 000, MDT (terreno) de 5 m, BIL float32 (2 en GRID de Esri), UTM 16N ITRF08. Cubren todo el bbox. |
| `MDT_1_5m_2025/F16C52A1_794551140758_t.zip` | MDT de 1.5 m (GeoTIFF), carta F16C52A1 (centro histórico). |
| `MDS_1_5m_2025/F16C52A1_794551133323_t.zip` | MDS (superficie) de 1.5 m, misma carta. MDS − MDT = alturas de edificios/árboles. |
| `CEM/e31_cem_r15_v4_tif.zip` | Continuo de Elevaciones Mexicano 4.0, Yucatán completo, 15 m (GeoTIFF). |
| `indice_cartas_merida.csv` | Claves de carta + UPC + URL directa (MDT 5 m y MDT 1.5 m) de las 25 cartas. |

## Claves de carta 1:10 000 que cubren Mérida

- Centro (20.97, -89.62): **F16C52A1**
- Mancha urbana: F16C41F3, F16C41F4, F16C42D3, F16C42D4, F16C42E3, F16C51C1, F16C51C2, F16C51C3, F16C51C4,
  F16C52A1, F16C52A2, F16C52A3, F16C52A4, F16C52B1, F16C52B3
- Bordes N y S: F16C41F1, F16C41F2, F16C42D1, F16C42D2, F16C42E1, F16C51F1, F16C51F2, F16C52D1, F16C52D2, F16C52E1
- Hay MDT de 1.5 m para 24 de las 25 cartas (no hay para F16C52E1). Las URLs están en `indice_cartas_merida.csv`.

## Descarga manual (portal)

1. Abrir https://www.inegi.org.mx/app/geo2/elevacionesmex/
2. Pestaña "Relieve / formato 1:10 000" (la segunda pestaña del panel lateral).
3. Marcar tipo (Terreno = MDT, Superficie = MDS) y resolución (5 m o 1.5 m).
4. Escribir la clave (p. ej. `F16C52A1`) o hacer clic en el mapa, y descargar en BIL, ASCII, GRID o TIFF.

## Descarga programática (la que se usó)

```bash
# Lista de cartas disponibles (mod T=terreno, S=superficie; res 5 o 1.5)
curl -X POST -d "res=5&mod=T" https://www.inegi.org.mx/app/geo2/elevacionesmex/getFormato10k.do
# Registro de una carta: devuelve url_descarga + sufijos (_b.zip BIL, _as.zip ASCII, _gr.zip GRID, _t.zip TIFF)
curl -X POST -d "res=1.5&mod=T&cve=F16C52A1" https://www.inegi.org.mx/app/geo2/elevacionesmex/getF10KDescarga.do
# CEM 4.0 Yucatán 15 m
curl -G https://www.inegi.org.mx/app/geo2/elevacionesmex/DownloadFile.do \
  --data-urlencode file=e31_cem_r15_v4_tif.zip --data-urlencode res=15 --data-urlencode "entidad=Yucatán"
```
CEM 3.0 Yucatán 15 m (no descargado): mismo endpoint, `file=CEM_V3_20170619_R15_E31_TIF.zip` (36.69 MB).

Licencia: Términos de Libre Uso de la Información del INEGI (https://www.inegi.org.mx/inegi/terminos.html), con cita de la fuente.

## Notas técnicas

- Proyección: MEXICO_ITRF_2008_UTM_Zone_16N. NoData = -3.4028e38. Altura ortométrica (m s. n. m.).
- MDT 1.5 m en F16C52A1: cotas de 0.01 a 12.88 m. El relieve es muy plano, así que unos decímetros de error
  vertical cambian dónde aparecen las depresiones. Por eso hay que validar con los puntos de inundación conocidos.
- Los ZIP usan `\` como separador de rutas. En macOS/Linux, `unzip` avisa pero extrae bien.
