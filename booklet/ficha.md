# Capítulo 04 · Cuando llueve en una ciudad plana

**Equipo 1 · Mérida, Ciudad Esponja** (Diego Loria, Rama Marin, José Ángel Pech) · Acto 4: Plana sobre el agua

## Título-hallazgo

**Cuando llueve en una ciudad plana, Espo se satura: 322 reportes en un solo día.**

*Espo es Mérida: una esponja que se moja con el calendario. Es una metáfora; el capítulo cuenta, con datos, cuánto le llueve y cuándo la ciudad empieza a reportar calles inundadas.*

## Pregunta del capítulo

¿A dónde se va el agua cuando llueve?

## Entrada

Espo es Mérida: una esponja que se moja con el calendario. ¿A dónde se va el agua cuando llueve? Casi todo cae de junio a octubre (el 75 % del año) y un solo día puede traer 223 mm. Mientras la lluvia del día no pasa de 50 mm, casi nadie reporta calles inundadas; pasando de ahí, los reportes se disparan: hasta 322 en un día.

## La historia en 10 segundos

| Cifra | Unidad | Fuente y corte |
|---|---|---|
| **75** | % de la lluvia del año cae de junio a octubre | SMN/CONAGUA, estación 31044 Mérida (OBS), CLICOM, normal 1991–2020 · corte 25-sep-2026 |
| **223** | mm en un solo día (récord de las estaciones urbanas: CICY, 23-sep-2002) | SMN/CONAGUA, estación 31036 C.I.C.Y., CLICOM · corte 25-sep-2026 |
| **322** | reportes de calles inundadas en un solo día (1-jun-2026) | Ayuntamiento de Mérida, respuesta al folio 1190579126000596 (PNT) · corte 29-oct-2026 |

Las tres salen de `datos/cifras.csv`, que dice cómo se calculó cada una.

## La historia (un hilo, cuatro escenas)

Espo se moja con el calendario → le caen aguaceros de golpe → ¿cuánto aguanta? → así se saturó en el temporal de 2026.

| # | Título-hallazgo | Datos | Gráfica |
|---|---|---|---|
| 1 | Cinco meses en remojo, siete a secas: de junio a octubre cae el 75 % de la lluvia | `datos/escena-1.csv` | `graficas/escena-1.html` |
| 2 | 2020 se pasó de lanza: 12 días con 50 mm o más, cuando el promedio es de 3.0 | `datos/escena-2.csv` | `graficas/escena-2.html` |
| 3 | Hasta los 50 mm Espo aguanta; de ahí en adelante, los reportes pasan de 4.5 a 75.5 al día | `datos/escena-3.csv` | `graficas/escena-3.html` |
| 4 | Cinco días de temporal: 834 reportes de calles inundadas y una lluvia que cayó por parches | `datos/escena-4.csv` | `graficas/escena-4.html` |

El capítulo completo (con la narración entre escenas, las cifras y los límites) se ve en `graficas/capitulo.html`. Títulos y cifras se calculan en D3 desde los CSV, no están escritos a mano.

## Lo que estos datos no dicen

- Cada estación mide un punto. En una misma tormenta, estaciones a pocos kilómetros marcan cosas muy distintas, y el Centro no tiene estación propia.
- El SMN entrega lluvia acumulada en 24 horas, no por hora. La intensidad (cada 10 minutos) solo existe para abril a junio de 2022; no alcanza para contar una historia y **se dejó fuera del booklet**.
- Un reporte no es una inundación: cuenta quién llamó y cuándo, no cuánta agua hubo.
- **Reportes del Ayuntamiento:** no hay datos de 2023 y mezclan dos entregas distintas (2018–2022: anexo en PDF; 2024–2026: hoja de cálculo) que pueden no contar igual. Está dicho en el pie de las escenas 3 y 4, que usan solo la entrega 2024–2026. Los días sin reportes cuentan como cero.
- Espo es una metáfora: no medimos cuánta agua absorbe Mérida. En la escena 3 los grupos de lluvia (10, 25 y 50 mm) los eligió el equipo y el grupo de 50 mm o más tiene solo 8 días: es una pista, no una ley. No sabemos si el culpable es el drenaje, el relieve, la falta de suelo que absorba o que ahora se reporta más.
- Quitamos meses con ceros falsos de las series del SMN (faltantes codificados como 0.0 mm); el detalle está en `subtema_1_precipitacion/datos/REPORTE_CALIDAD.md`.
- Que Mérida sea plana no se mide aquí: es un dato del capítulo de relieve.
- Escena 4: no sabemos si el 30 de mayo una estación midió 153.6 mm y las otras 0.5 mm o menos por lluvia muy localizada o por cómo se corta el día de cada estación.

## Frase puente

Y el agua que no se queda en la calle, ¿por dónde se va? Eso lo cuentan el drenaje, el acuífero y la mancha urbana: el siguiente capítulo.

## Qué se arregló de la revisión del 26 de noviembre

| Falla señalada | Qué se hizo |
|---|---|
| Figuras en matplotlib y dashboard en SVG propio | Las 4 escenas están en D3 v7.9.0 (`graficas/`) con la paleta común (morado, oro, gris). El dashboard anterior y las figuras de matplotlib siguen en `subtema_1_precipitacion/` solo como material del catálogo de fuentes; no entran al booklet |
| Reportes sin 2023 y con dos entregas mezcladas | Dicho en el pie de las escenas 3 y 4, en la gráfica (hueco rayado «2023 sin entrega» y llaves por entrega) y arriba |
| Intensidad solo de abril a junio de 2022 | Fuera del booklet (los datos siguen en el repositorio, en `05_Solicitudes_gobierno/`) |
| `merida_ciudad_esponja_prototipo.html` decía «Sin datos» | Eliminado del repositorio |
