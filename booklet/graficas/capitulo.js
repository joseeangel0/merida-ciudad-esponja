/* Capítulo completo: título-hallazgo, entrada, 3 cifras, 4 escenas, límites y puente.
   Las cifras y los números del texto salen de ../datos/cifras.csv, no se escriben a mano. */
(async function () {
  const { fmt, UMBRAL_MM } = Booklet;
  const nb = (v, u) => `${v} ${u}`;
  try {
    const filas = await d3.csv("../datos/cifras.csv");
    const c = Object.fromEntries(filas.map((d) => [d.cifra, d]));
    const pct = fmt.n0(+c.lluvia_junio_octubre.valor);
    const mm = fmt.n0(+c.maxima_lluvia_24h.valor);
    const rep = fmt.n0(+c.maximo_reportes_dia.valor);

    d3.select("#titulo").text(`Cuando llueve en una ciudad plana, Espo se satura: ${rep} reportes en un solo día`);
    d3.select("#entrada").text(
      `Espo es Mérida: una esponja que se moja con el calendario. ¿A dónde se va el agua cuando llueve? Casi todo cae de junio a octubre (el ${pct} % del año) y un solo día puede traer ${nb(mm, "mm")}. ` +
      `Mientras la lluvia del día no pasa de ${nb(fmt.n0(UMBRAL_MM), "mm")}, casi nadie reporta calles inundadas; pasando de ahí, los reportes se disparan: hasta ${rep} en un día.`);

    const unidadCorta = { lluvia_junio_octubre: "% de la lluvia del año cae de junio a octubre", maxima_lluvia_24h: "mm en un solo día (récord de las estaciones urbanas)", maximo_reportes_dia: "reportes de calles inundadas en un solo día" };
    const valores = { lluvia_junio_octubre: pct, maxima_lluvia_24h: mm, maximo_reportes_dia: rep };
    const caja = d3.select("#cifras").selectAll("div.cifra").data(filas).join("div").attr("class", "cifra");
    caja.append("div").attr("class", "valor").text((d) => valores[d.cifra]);
    caja.append("div").attr("class", "unidad").text((d) => unidadCorta[d.cifra]);
    caja.append("p").attr("class", "fuente").text((d) => `Fuente: ${d.fuente} · Corte: ${d.fecha_corte}`);
  } catch (e) {
    d3.select("#titulo").text("No se pudieron leer los datos");
    console.error(e);
  }
  // Las escenas se dibujan en su contenedor, una tras otra
  await escena1("#escena-1");
  await escena2("#escena-2");
  await escena3("#escena-3");
  await escena4("#escena-4");
})();
