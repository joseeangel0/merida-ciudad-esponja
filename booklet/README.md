# booklet/ · Capítulo 04 · Cuando llueve en una ciudad plana

Equipo 1 · Mérida, Ciudad Esponja (Diego Loria, Rama Marin, José Ángel Pech). Versión final para el booklet «Mérida a ras de calle».

| Qué | Dónde |
|---|---|
| Ficha del capítulo (título-hallazgo, 3 cifras, escenas, límites, puente) | [`ficha.md`](ficha.md) |
| Un CSV por escena + las 3 cifras | [`datos/`](datos/) |
| Fuente, corte y cálculo de cada CSV | [`datos/FUENTES.md`](datos/FUENTES.md) |
| Escenas en D3 v7.9.0 (`.html` + `.js`) y el capítulo completo | [`graficas/`](graficas/) |

## Cómo verlo

Las gráficas leen los CSV con rutas relativas, así que hay que abrirlas desde un servidor (con doble clic el navegador bloquea la lectura):

```bash
cd booklet
python3 -m http.server 8000
# abrir http://localhost:8000/graficas/capitulo.html
```

También están publicadas junto con el dashboard (`/booklet/graficas/capitulo.html` en el sitio del repositorio).

## Escenas

Hilo de la historia: **Espo es Mérida, una esponja**. Se moja con el calendario, le caen aguaceros de golpe, se satura y así se vio en el temporal de 2026.

1. `graficas/escena-1.html` · ciclo anual de la lluvia (12 esponjas)
2. `graficas/escena-2.html` · días con 50 mm o más por año (gotas con cara)
3. `graficas/escena-3.html` · ¿cuánto aguanta Espo? lluvia del día contra reportes de desagüe
4. `graficas/escena-4.html` · el temporal de mayo y junio de 2026, día por día (Espo se llena de reportes)

Cada escena se dibuja con `escenaN("#contenedor")` (definida en `escena-N.js`) y usa `comun.js` (paleta, formato numérico a la mexicana, personajes) y `estilo.css`. D3 está incluido en `graficas/d3.v7.9.0.min.js` (versión fija, sin depender de internet). La tipografía Outfit se pide a Google Fonts.

## Regenerar los CSV

```bash
cd subtema_1_precipitacion/scripts
python3 generar_booklet_datos.py
```

## Reglas que cumple

- Paleta común: morado `#600d8b` (lo que se analiza), oro `#ed9f22` (contra qué se compara), oro oscuro `#b45309` (anotaciones), gris `#9ca3af` (contexto).
- Sin `Math.random`, sin cifras escritas a mano en el código, sin datos simulados ni de muestra.
- Sin nombres, teléfonos ni direcciones de personas: los reportes del Ayuntamiento van agregados por día y mes.
- Todo en español.
