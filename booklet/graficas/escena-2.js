/* Escena 2 · Días con 50 mm o más por año: una gota con cara por cada aguacero.
   Datos: ../datos/escena-2.csv (Mérida CONAGUA, estación 31097, 1961-2026). */
(function () {
  const { PAL, fmt, fechaCorta, pendiente, marco, errorEscena, chip, gota, globo, esponja } = Booklet;

  async function escena2(contenedor) {
    try {
      const datos = await d3.csv("../datos/escena-2.csv", (d) => ({
        anio: +d.anio, dias_50mm_o_mas: +d.dias_50mm_o_mas, meses_validos: +d.meses_validos, completo: d.anio_completo === "si",
        max_diaria_mm: d.max_diaria_mm === "" ? null : +d.max_diaria_mm, fecha_max_diaria: d.fecha_max_diaria,
      }));
      const completos = datos.filter((d) => d.completo);
      const promedio = d3.mean(completos, (d) => d.dias_50mm_o_mas);
      const maxDias = d3.max(completos, (d) => d.dias_50mm_o_mas);
      const anioMax = completos.find((d) => d.dias_50mm_o_mas === maxDias);
      const tendencia = pendiente(completos.map((d) => d.anio), completos.map((d) => d.dias_50mm_o_mas)) * 10;
      const a = d3.extent(datos, (d) => d.anio);
      const signo = tendencia >= 0 ? "+" : "−";

      const W = 760, H = 218, ml = 30, mr = 190, mb = 30;
      const svg = marco(contenedor, {
        num: 2,
        titulo: `${anioMax.anio} se pasó de lanza: ${maxDias} días con 50\u00A0mm o más, cuando el promedio es de ${fmt.n1(promedio)}`,
        subtitulo: `Días con lluvia de 50 mm o más en 24 horas, por año. Una gota = un día. Mérida (CONAGUA), ${a[0]}–${a[1]}.`,
        lectura: `Cada gota es un día de aguacero fuerte. La línea dorada es el promedio de los años completos; las gotas grises son años con meses sin dato, donde el conteo puede quedarse corto. La tendencia de los años completos es de ${signo}${fmt.n2(Math.abs(tendencia))} días por década: casi plana.`,
        pie: `Fuente: SMN/CONAGUA, estación 31097 Mérida (CONAGUA), CLICOM; índices calculados por el equipo (C7.2) · ${completos.length} años completos de ${datos.length} · Corte: 25 de septiembre de 2026.`,
        ancho: W, alto: H,
      });

      const x = d3.scaleBand().domain(datos.map((d) => d.anio)).range([ml, W - mr]).paddingInner(0.1);
      const bw = x.bandwidth();
      const rad = Math.min(bw * 0.5, 4.6);
      const paso = rad * 2.15;
      const y0 = H - mb;

      // Eje de años (cada 10)
      const eje = svg.append("g").attr("class", "eje");
      eje.append("line").attr("x1", ml - 4).attr("x2", W - mr + 4).attr("y1", y0 + 2).attr("y2", y0 + 2);
      datos.filter((d) => d.anio % 10 === 0).forEach((d) => {
        eje.append("text").attr("x", x(d.anio) + bw / 2).attr("y", y0 + 18).attr("text-anchor", "middle").text(d.anio);
        eje.append("line").attr("x1", x(d.anio) + bw / 2).attr("x2", x(d.anio) + bw / 2).attr("y1", y0 + 2).attr("y2", y0 + 6);
      });

      // Línea del promedio (oro = comparación)
      const yProm = y0 - promedio * paso;
      svg.append("line").attr("x1", ml - 4).attr("x2", W - mr + 6).attr("y1", yProm).attr("y2", yProm)
        .attr("stroke", PAL.oro).attr("stroke-width", 2.2).attr("stroke-dasharray", "6 4");
      svg.append("text").attr("class", "etiqueta").attr("x", W - mr + 12).attr("y", yProm + 4).style("fill", PAL.oroOscuro).text(`promedio: ${fmt.n1(promedio)} días`);

      // Gotas con cara: una por cada día de 50 mm o más
      datos.forEach((d) => {
        const color = d.completo ? PAL.morado : PAL.gris;
        for (let k = 0; k < d.dias_50mm_o_mas; k++) {
          gota(svg, x(d.anio) + bw / 2, y0 - rad - 1 - k * paso, rad, color, true);
        }
      });

      // Anotaciones: el año récord, con su cifra y su día más fuerte
      const cx = x(anioMax.anio) + bw / 2;
      const yTope = y0 - anioMax.dias_50mm_o_mas * paso - rad * 2;
      chip(svg, cx, yTope - 22, `${anioMax.anio}: ${anioMax.dias_50mm_o_mas} días`, "middle");
      svg.append("text").attr("class", "etiqueta-suave").attr("x", cx).attr("y", yTope - 4).attr("text-anchor", "middle")
        .text(`máx. ${fmt.n0(anioMax.max_diaria_mm)} mm el ${fechaCorta(anioMax.fecha_max_diaria)}`);
      // Espo, empapada por tanto aguacero
      const espo = svg.append("g").attr("transform", `translate(${W - 34},${y0})`);
      esponja(espo, 44, 60, 0.92);
      globo(svg, W - 76, y0 - 90, "¡Ya estuvo bueno!", W - 44, y0 - 64);
    } catch (e) { errorEscena(contenedor, e); }
  }

  window.escena2 = escena2;
})();
