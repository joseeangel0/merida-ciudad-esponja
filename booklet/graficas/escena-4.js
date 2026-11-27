/* Escena 4 · El temporal de mayo y junio de 2026, día por día.
   Datos: ../datos/escena-4.csv (lluvia diaria de 5 estaciones + reportes de desagüe por día). */
(function () {
  const { PAL, fmt, fechaCorta, fechaLarga, MESES, marco, errorEscena, chip, ojos, pato, esponja } = Booklet;

  async function escena4(contenedor) {
    try {
      const filas = await d3.csv("../datos/escena-4.csv", (d) => ({
        fecha: d.fecha, clave: d.estacion_clave, estacion: d.estacion,
        lluvia: d.lluvia_mm === "" ? null : +d.lluvia_mm, reportes: +d.reportes_desague_dia,
      }));
      const dias = Array.from(new Set(filas.map((d) => d.fecha))).sort();
      const estaciones = Array.from(new Map(filas.map((d) => [d.clave, d.estacion])).entries());
      const repDia = new Map(filas.map((d) => [d.fecha, d.reportes]));
      const porDia = dias.map((f) => ({ fecha: f, reportes: repDia.get(f) }));

      // Los 5 días seguidos con más reportes (el pico del temporal)
      let pico = { i: 0, suma: -1 };
      for (let i = 0; i + 5 <= porDia.length; i++) {
        const s = d3.sum(porDia.slice(i, i + 5), (d) => d.reportes);
        if (s > pico.suma) pico = { i, suma: s };
      }
      const diasPico = porDia.slice(pico.i, pico.i + 5);

      // La lectura más fuerte de la ventana y qué marcaron las demás estaciones ese mismo día
      const fuerte = d3.greatest(filas.filter((d) => d.lluvia !== null), (d) => d.lluvia);
      const otras = filas.filter((d) => d.fecha === fuerte.fecha && d.clave !== fuerte.clave && d.lluvia !== null);
      const maxOtras = d3.max(otras, (d) => d.lluvia);

      const W = 760, H = 500, ml = 132, mr = 14;
      const yFila0 = 98, hFila = 42, yBase = 478, altoRep = 108;
      const svg = marco(contenedor, {
        num: 4,
        titulo: `Cinco días de temporal: ${fmt.n0(pico.suma)} reportes de calles inundadas y una lluvia que cayó por parches`,
        subtitulo: `Lluvia diaria en ${estaciones.length} estaciones (mm; el área del círculo es proporcional a la lluvia) y reportes de desagüe de calles inundadas por día, del ${fechaCorta(dias[0])} al ${fechaLarga(dias[dias.length - 1])}.`,
        lectura: `El ${fechaCorta(fuerte.fecha)}, ${fuerte.estacion} midió ${fmt.n1(fuerte.lluvia)} mm y las otras ${otras.length} estaciones, ${fmt.n1(maxOtras)} mm o menos: la lluvia no cayó pareja. Abajo, Espo se llena de oro con los reportes de cada día y el patito se queda con el día en que más se llenó.`,
        aviso: `Ojo: los reportes son de la entrega de 2024–2026 del Ayuntamiento (hoja de cálculo); no incluye 2023 ni se mezcla con la entrega de 2018–2022. Cada círculo vacío es un día sin lluvia registrada.`,
        pie: `Fuente: SMN/CONAGUA, estaciones urbanas, CLICOM (C7.1; corte al 25 de septiembre de 2026) · Ayuntamiento de Mérida, respuesta al folio 1190579126000596 de la PNT (C5.2; corte al 29 de octubre de 2026), solo reportes de «desagüe de calles inundadas».`,
        ancho: W, alto: H,
      });

      const x = d3.scaleBand().domain(dias).range([ml, W - mr]).paddingInner(0);
      const bw = x.bandwidth();
      const maxLluvia = d3.max(filas, (d) => d.lluvia);
      const rad = d3.scaleSqrt().domain([0, maxLluvia]).range([0, Math.min(bw, hFila) / 2 - 1]);
      const yR = d3.scaleLinear().domain([0, d3.max(porDia, (d) => d.reportes)]).nice().range([0, altoRep]);
      const yTopRep = yBase - altoRep;

      // Franja del pico de 5 días
      const xp0 = x(diasPico[0].fecha), xp1 = x(diasPico[4].fecha) + bw;
      svg.append("rect").attr("x", xp0).attr("y", yFila0 - hFila / 2 - 4).attr("width", xp1 - xp0).attr("height", yBase - (yFila0 - hFila / 2 - 4) + 4).attr("fill", "#f3f4f6");

      // Filas de estaciones
      const rej = svg.append("g").attr("class", "eje");
      estaciones.forEach(([clave, nombre], i) => {
        const cy = yFila0 + i * hFila;
        rej.append("line").attr("x1", ml).attr("x2", W - mr).attr("y1", cy + hFila / 2).attr("y2", cy + hFila / 2);
        svg.append("text").attr("class", "etiqueta-suave").attr("x", ml - 10).attr("y", cy + 4).attr("text-anchor", "end").text(nombre);
        dias.forEach((f) => {
          const d = filas.find((q) => q.fecha === f && q.clave === clave);
          const cx = x(f) + bw / 2;
          if (!d || d.lluvia === null) {
            svg.append("text").attr("x", cx).attr("y", cy + 4).attr("text-anchor", "middle").attr("class", "etiqueta-suave").text("×");
          } else if (d.lluvia === 0) {
            svg.append("circle").attr("cx", cx).attr("cy", cy).attr("r", 2.2).attr("fill", "none").attr("stroke", PAL.gris).attr("stroke-width", 1.2);
          } else {
            const r = Math.max(2, rad(d.lluvia));
            const g = svg.append("g").attr("transform", `translate(${cx},${cy})`);
            g.append("circle").attr("r", r).attr("fill", PAL.morado);
            if (r >= 9) ojos(g, 0, -r * 0.4, r * 0.36, r * 0.27, 0, 0.5);
            if (r >= 14) g.append("text").attr("y", r * 0.68).attr("text-anchor", "middle").attr("font-size", 11).attr("font-weight", 600).style("fill", "#fff").text(fmt.n1(d.lluvia));
          }
        });
      });

      // Anotación del día de lluvia desigual
      const xf = x(fuerte.fecha) + bw / 2;
      chip(svg, Math.min(xf, W - 190), 40, `${fechaCorta(fuerte.fecha)}: ${fmt.n1(fuerte.lluvia)} mm en una estación, ${fmt.n1(maxOtras)} mm o menos en las otras`, xf > W - 190 ? "end" : "middle");

      // Eje de días
      const yDia = yFila0 + (estaciones.length - 1) * hFila + hFila / 2 + 16;
      dias.forEach((f, i) => {
        const dd = +f.slice(8, 10);
        svg.append("text").attr("class", "etiqueta-suave num").attr("x", x(f) + bw / 2).attr("y", yDia).attr("text-anchor", "middle").text(dd);
        if (i === 0 || dd === 1) {
          svg.append("text").attr("class", "nota").attr("x", x(f) + bw / 2 - 8).attr("y", yDia + 14).text(MESES[+f.slice(5, 7) - 1]);
        }
      });

      // Panel de reportes (oro = comparación)
      const eje = svg.append("g").attr("class", "eje");
      yR.ticks(3).forEach((t) => {
        eje.append("line").attr("x1", ml).attr("x2", W - mr).attr("y1", yBase - yR(t)).attr("y2", yBase - yR(t));
        eje.append("text").attr("x", ml - 8).attr("y", yBase - yR(t) + 4).attr("text-anchor", "end").text(fmt.n0(t));
      });
      svg.append("text").attr("class", "etiqueta").attr("x", ml - 124).attr("y", yTopRep - 34).style("fill", PAL.oroOscuro).text("Espo se llena con los reportes de calles inundadas de cada día ↑");
      // Espo día por día: su agua es de oro (reportes) y se llena a la par de los reportes del día
      porDia.forEach((d) => {
        const g = svg.append("g").attr("transform", `translate(${x(d.fecha) + bw / 2},${yBase})`);
        esponja(g, bw * 0.8, altoRep, d.reportes / yR.domain()[1], null, PAL.oro, d.reportes === d3.max(porDia, (q) => q.reportes));
      });
      const maxRep = d3.greatest(porDia, (d) => d.reportes);
      porDia.filter((d) => d.reportes >= 0.25 * maxRep.reportes && d !== maxRep).forEach((d) => {
        svg.append("text").attr("class", "etiqueta-suave num").attr("x", x(d.fecha) + bw / 2).attr("y", yBase - altoRep - 5).attr("text-anchor", "middle").text(fmt.n0(d.reportes));
      });
      const cxm = x(maxRep.fecha) + bw / 2;
      pato(svg, cxm, yBase - altoRep - 1, 11);
      chip(svg, cxm + 20, yBase - altoRep - 24, `${fmt.n0(maxRep.reportes)} reportes · ${fechaCorta(maxRep.fecha)}`, "start");

      // Etiqueta de la franja del pico
      chip(svg, (xp0 + xp1) / 2, yBase + 20, `${fechaCorta(diasPico[0].fecha)} a ${fechaCorta(diasPico[4].fecha)}: ${fmt.n0(pico.suma)} reportes`, "middle");
    } catch (e) { errorEscena(contenedor, e); }
  }

  window.escena4 = escena4;
})();
