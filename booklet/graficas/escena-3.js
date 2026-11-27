/* Escena 3 · ¿Cuánto aguanta Espo? La lluvia del día contra los reportes de calles inundadas.
   Datos: ../datos/escena-3.csv (un renglón por día, 2024-2026). */
(function () {
  const { PAL, fmt, UMBRAL_MM, marco, errorEscena, pato, globo, esponja } = Booklet;
  const r1 = (v) => fmt.n1(v).replace(".0", "");

  async function escena3(contenedor) {
    try {
      const datos = await d3.csv("../datos/escena-3.csv", (d) => ({
        fecha: d.fecha, lluvia: +d.lluvia_mm, reportes: +d.reportes_desague,
      }));
      // Grupos de lluvia del día (mm). 10 y 25 son una elección del equipo; el último corte es el umbral de aguacero fuerte.
      const cortes = [0, 10, 25, UMBRAL_MM, Infinity];
      const nombre = (lo, hi) => (lo === 0 ? `menos de ${fmt.n0(hi)} mm` : hi === Infinity ? `${fmt.n0(lo)} mm o más` : `${fmt.n0(lo)} a ${fmt.n0(hi)} mm`);
      const grupos = d3.range(cortes.length - 1).map((i) => {
        const dias = datos.filter((d) => d.lluvia >= cortes[i] && d.lluvia < cortes[i + 1]);
        return {
          nombre: nombre(cortes[i], cortes[i + 1]), n: dias.length,
          lluvia: d3.median(dias, (d) => d.lluvia), rep: d3.median(dias, (d) => d.reportes), max: d3.max(dias, (d) => d.reportes),
        };
      });
      const penultimo = grupos[grupos.length - 2], ultimo = grupos[grupos.length - 1];
      const anios = d3.extent(datos, (d) => +d.fecha.slice(0, 4));

      const W = 760, H = 452, ml = 30;
      const hEsp = 132, wEsp = 112, base = 196, yBase = 396, altoRep = 112;
      const svg = marco(contenedor, {
        num: 3,
        titulo: `Hasta los ${fmt.n0(UMBRAL_MM)} mm Espo aguanta; de ahí en adelante, los reportes pasan de ${r1(penultimo.rep)} a ${r1(ultimo.rep)} al día`,
        subtitulo: `${fmt.n0(datos.length)} días de ${anios[0]} a ${anios[1]} agrupados por la lluvia del día (promedio de las estaciones urbanas, mm). Debajo de cada grupo: reportes de calles inundadas por día, mediana del grupo.`,
        lectura: `Cada esponja es un grupo de días y su agua es la lluvia mediana del grupo. Debajo, cuántos reportes de calles inundadas llegaron al Ayuntamiento en un día típico de ese grupo. El último grupo tiene pocos días (${fmt.n0(ultimo.n)}): léelo como pista, no como regla.`,
        aviso: `Ojo: solo entran días de la entrega ${anios[0]}–${anios[1]} del Ayuntamiento (hoja de cálculo). No hay datos de 2023, y la entrega de 2018–2022 no se mezcla aquí porque pudo contar distinto. Los días sin reportes cuentan como cero.`,
        pie: `Fuente: SMN/CONAGUA, estaciones urbanas 31036, 31044, 31078, 31095 y 31097, CLICOM (C7.1; corte 25 de septiembre de 2026) · Ayuntamiento de Mérida, respuesta al folio 1190579126000596 de la PNT (C5.2; corte 29 de octubre de 2026), solo reportes de «desagüe de calles inundadas» · Los grupos de lluvia los eligió el equipo.`,
        ancho: W, alto: H,
      });

      const x = d3.scaleBand().domain(d3.range(grupos.length)).range([ml, W - ml]).paddingInner(0.1);
      const nivelMax = d3.max(grupos, (g) => g.lluvia);
      const yR = d3.scaleLinear().domain([0, d3.max(grupos, (g) => g.rep)]).nice().range([0, altoRep]);

      svg.append("text").attr("class", "etiqueta").attr("x", ml).attr("y", 18).style("fill", PAL.morado).text("Lo que le cae a Espo: lluvia mediana del grupo ↓");
      svg.append("text").attr("class", "etiqueta").attr("x", ml).attr("y", base + 66).style("fill", PAL.oroOscuro).text("Lo que reporta la ciudad: reportes por día, mediana del grupo ↓");
      svg.append("line").attr("x1", ml).attr("x2", W - ml).attr("y1", yBase).attr("y2", yBase).attr("stroke", PAL.borde);

      grupos.forEach((g, i) => {
        const cx = x(i) + x.bandwidth() / 2;
        const esUltimo = i === grupos.length - 1;
        const e = svg.append("g").attr("transform", `translate(${cx},${base})`);
        esponja(e, wEsp, hEsp, g.lluvia / nivelMax, null, PAL.morado, esUltimo);
        svg.append("text").attr("class", "etiqueta").attr("x", cx).attr("y", base + 20).attr("text-anchor", "middle").text(g.nombre);
        svg.append("text").attr("class", "etiqueta-suave").attr("x", cx).attr("y", base + 35).attr("text-anchor", "middle").text(`${fmt.n0(g.n)} días · lluvia mediana ${fmt.n1(g.lluvia)} mm`);

        // Reportes: barra de oro
        const h = yR(g.rep);
        svg.append("rect").attr("x", cx - 26).attr("y", yBase - h).attr("width", 52).attr("height", Math.max(h, 1.5)).attr("fill", PAL.oro);
        svg.append("text").attr("class", "num").attr("x", cx).attr("y", yBase - h - (esUltimo ? 24 : 8)).attr("text-anchor", "middle").attr("font-size", 15).attr("font-weight", 600).text(r1(g.rep));
        svg.append("text").attr("class", "etiqueta-suave").attr("x", cx).attr("y", yBase + 16).attr("text-anchor", "middle").text(`el día con más: ${fmt.n0(g.max)}`);
        if (esUltimo) pato(svg, cx, yBase - h - 1, 10);
      });

      const cx0 = x(0) + x.bandwidth() / 2, cxN = x(grupos.length - 1) + x.bandwidth() / 2;
      globo(svg, cx0 + 34, 56, "Ni lo siento.", cx0, base - hEsp + 4);
      globo(svg, cxN - 60, 56, "¡Glub! Me desbordé.", cxN - 12, base - hEsp + 6);
    } catch (e) { errorEscena(contenedor, e); }
  }

  window.escena3 = escena3;
})();
