/* Escena 1 · El ciclo anual de la lluvia, contado con 12 esponjas.
   Datos: ../datos/escena-1.csv (normal climatológica 1991-2020 de Mérida, OBS). */
(function () {
  const { PAL, fmt, MESES_3, marco, errorEscena, chip, globo, esponja } = Booklet;
  async function escena1(contenedor) {
    try {
      const datos = await d3.csv("../datos/escena-1.csv", d3.autoType);
      const total = d3.sum(datos, (d) => d.promedio_mm);
      // Ventana de 5 meses seguidos con más lluvia (sale de los datos: junio a octubre)
      let mejor = { i: 0, suma: -1 };
      for (let i = 0; i + 5 <= datos.length; i++) {
        const s = d3.sum(datos.slice(i, i + 5), (d) => d.promedio_mm);
        if (s > mejor.suma) mejor = { i, suma: s };
      }
      const ventana = datos.slice(mejor.i, mejor.i + 5);
      const pct = (mejor.suma / total) * 100;
      const bajoMediana = datos.filter((d) => d.mediana_mm < d.promedio_mm).length;
      const minimo = d3.least(datos, (d) => d.promedio_mm);
      const anios = d3.extent(datos, (d) => d.anios_validos);

      const W = 760, H = 262, base = 226, h = 118;
      const svg = marco(contenedor, {
        num: 1,
        titulo: `Cinco meses en remojo, siete a secas: de ${ventana[0].nombre_mes} a ${ventana[4].nombre_mes} cae el ${fmt.pct(pct)} de la lluvia`,
        subtitulo: "Lluvia mensual promedio (agua de la esponja) y mediana (raya dorada), en milímetros por mes. Mérida (OBS), 1991–2020.",
        lectura: `Cada esponja se moja hasta el promedio de su mes. En ${bajoMediana} de 12 meses la raya dorada queda por debajo del agua: unos cuantos temporales inflan el promedio, y el mes típico es más tranquilo de lo que parece.`,
        pie: `Fuente: SMN/CONAGUA, estación 31044 Mérida (OBS), normal climatológica 1991–2020 calculada por el equipo con CLICOM (C7.1) · De ${anios[0]} a ${anios[1]} años con dato por mes · Corte: 25 de septiembre de 2026.`,
        ancho: W, alto: H,
      });

      const x = d3.scaleBand().domain(datos.map((d) => d.mes)).range([10, W - 10]).paddingInner(0.14).paddingOuter(0);
      const ymax = Math.ceil(d3.max(datos, (d) => Math.max(d.promedio_mm, d.mediana_mm)) / 10) * 10;
      const w = x.bandwidth();

      // Llave sobre los meses lluviosos
      const x0 = x(ventana[0].mes), x1 = x(ventana[4].mes) + w;
      const yL = base - h - 30;
      svg.append("path").attr("d", `M${x0},${yL + 7} V${yL} H${x1} V${yL + 7}`).attr("fill", "none").attr("stroke", PAL.oroOscuro).attr("stroke-width", 1.6);
      chip(svg, (x0 + x1) / 2, yL - 8, `${fmt.pct(pct)} de la lluvia del año`, "middle");

      datos.forEach((d) => {
        const g = svg.append("g").attr("transform", `translate(${x(d.mes) + w / 2},${base})`);
        esponja(g, w, h, d.promedio_mm / ymax, d.mediana_mm / ymax);
        g.append("text").attr("class", "etiqueta num").attr("text-anchor", "middle").attr("y", -h - 6).attr("fill", PAL.morado).style("fill", PAL.morado).text(fmt.n1(d.promedio_mm));
        g.append("text").attr("class", "etiqueta-suave").attr("text-anchor", "middle").attr("y", 18).text(MESES_3[d.mes - 1]);
      });

      // Chips de lectura y un globo de humor (el texto sale del mes más seco)
      chip(svg, 8, 16, "agua = promedio");
      chip(svg, 138, 16, "raya dorada = mediana");
      const gm = x(minimo.mes) + w / 2;
      globo(svg, gm + 14, base - h - 40, "¿Lluvia? Yo vengo por el sol.", gm, base - h - 22);
    } catch (e) { errorEscena(contenedor, e); }
  }

  window.escena1 = escena1;
})();
