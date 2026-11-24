# 09_AR — Insumos 3D para una experiencia de RA (descargados 2026-10-01)

| Archivo | Fuente | Extensión |
|---|---|---|
| `osm_edificios_merida_centro.geojson` | OpenStreetMap vía Overpass (espejo overpass.private.coffee, base OSM 2026-07-15), ODbL | bbox 20.955,-89.640 a 20.985,-89.605 |
| `overture_edificios_merida_centro.geojson` | Overture Maps, release 2026-09-23.1, tema buildings (mezcla Microsoft ML + Google Open Buildings + OSM), ODbL | mismo bbox |
| `overture_edificios_merida_centro_con_altura_inegi.geojson` | Derivado: huellas de Overture + `altura_ndsm_p75_m` (percentil 75 de MDS−MDT INEGI 1.5 m, carta F16C52A1) + `cota_terreno_mdt_m` (mediana del MDT) | parte del bbox dentro de F16C52A1 |

Las alturas derivadas son una estimación: el MDS/MDT de INEGI es fotogramétrico y la vegetación sobre los techos las infla.
Para RA de inundación: cota de lámina = cota_terreno_mdt_m + tirante simulado (p. ej. 0.215 m si toda la lluvia de 24 h
de Cristóbal 2020 se acumulara sin infiltrar, que es un caso extremo y no realista en karst).

Nota: del GeoJSON de OSM se eliminaron las etiquetas `phone` y `email` (contactos de negocios) porque no se usan en el proyecto.
