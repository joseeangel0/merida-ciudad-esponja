/* Utilidades comunes del booklet (D3 v7.9.0, sin frameworks).
   Aquí viven: la paleta, el formato numérico a la mexicana, la anatomía de cada escena
   (rótulo, título-hallazgo, subtítulo, lectura, pie) y los personajes (esponja, gota, patito).
   Ninguna cifra de datos se escribe a mano: todo se calcula de los CSV de ../datos/. */
(function () {
  const PAL = { morado: "#600d8b", oro: "#ed9f22", oroOscuro: "#b45309", gris: "#9ca3af", tinta: "#0d0d0d", borde: "#e5e7eb" };

  // Números a la mexicana: 8,815 · 153.6 · $2,379.47 · +19.0 %
  const loc = d3.formatLocale({ decimal: ".", thousands: ",", grouping: [3], currency: ["$", ""] });
  const fmt = {
    n0: loc.format(",.0f"),
    n1: loc.format(",.1f"),
    n2: loc.format(",.2f"),
    pct: (v) => loc.format(",.0f")(v) + " %",
    signo1: (v) => (v >= 0 ? "+" : "−") + loc.format(",.1f")(Math.abs(v)),
  };

  const MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"];
  const MESES_3 = MESES.map((m) => m.slice(0, 3));
  // "2026-06-01" -> "1 de junio de 2026"  (sin pasar por Date para no depender de la zona horaria)
  const fechaLarga = (iso) => { const [a, m, d] = iso.split("-").map(Number); return `${d} de ${MESES[m - 1]} de ${a}`; };
  const fechaCorta = (iso) => { const [, m, d] = iso.split("-").map(Number); return `${d} de ${MESES[m - 1]}`; };

  const r = d3.format(".1f");
  const correlacion = (xs, ys) => {
    const mx = d3.mean(xs), my = d3.mean(ys);
    const num = d3.sum(xs, (x, i) => (x - mx) * (ys[i] - my));
    return num / Math.sqrt(d3.sum(xs, (x) => (x - mx) ** 2) * d3.sum(ys, (y) => (y - my) ** 2));
  };
  // Pendiente de mínimos cuadrados (y por unidad de x)
  const pendiente = (xs, ys) => {
    const mx = d3.mean(xs), my = d3.mean(ys);
    return d3.sum(xs, (x, i) => (x - mx) * (ys[i] - my)) / d3.sum(xs, (x) => (x - mx) ** 2);
  };

  /* ---------- Anatomía de una escena ---------- */
  function marco(contenedor, o) {
    const cont = d3.select(contenedor);
    cont.selectAll("*").remove();
    const fig = cont.append("figure").attr("class", "escena").style("margin", null);
    fig.append("div").attr("class", "rotulo").text(`Escena ${o.num}`);
    fig.append("h2").text(o.titulo);
    fig.append("p").attr("class", "subtitulo").text(o.subtitulo);
    const svg = fig.append("svg")
      .attr("viewBox", `0 0 ${o.ancho} ${o.alto}`)
      .attr("role", "img")
      .attr("aria-label", `${o.titulo}. ${o.subtitulo}`)
      .attr("preserveAspectRatio", "xMidYMid meet");
    fig.append("p").attr("class", "lectura").text(o.lectura);
    if (o.aviso) fig.append("p").attr("class", "pie aviso").text(o.aviso);
    fig.append("p").attr("class", "pie").text(o.pie);
    return svg;
  }

  function errorEscena(contenedor, e) {
    d3.select(contenedor).append("p").attr("class", "error")
      .text("No se pudieron leer los datos de la escena. Abre esta página desde un servidor (por ejemplo: python3 -m http.server) y no con doble clic. " + (e && e.message ? e.message : ""));
    console.error(e);
  }

  // Chip de «dato anotado» (anatomía del plan): texto en oro oscuro dentro de una cápsula blanca
  function chip(g, x, y, texto, anchor = "start") {
    const a = g.append("g");
    const t = a.append("text").attr("class", "nota").attr("x", x).attr("y", y).attr("text-anchor", anchor).text(texto);
    const b = t.node().getBBox();
    a.insert("rect", "text")
      .attr("x", b.x - 6).attr("y", b.y - 2).attr("width", b.width + 12).attr("height", b.height + 4)
      .attr("rx", (b.height + 4) / 2).attr("fill", "#fff").attr("stroke", PAL.oroOscuro).attr("stroke-width", 1.2);
    return a;
  }

  /* ---------- Personajes ---------- */
  // Ojos saltones: dos círculos blancos con pupila que mira hacia (mx, my) en [-1, 1]
  function ojos(g, cx, cy, sep, rad, mx = 0, my = -0.5) {
    [-1, 1].forEach((s) => {
      g.append("circle").attr("cx", cx + s * sep).attr("cy", cy).attr("r", rad).attr("fill", "#fff").attr("stroke", PAL.tinta).attr("stroke-width", Math.max(0.6, rad * 0.14));
      g.append("circle").attr("cx", cx + s * sep + mx * rad * 0.35).attr("cy", cy + my * rad * 0.35).attr("r", rad * 0.48).attr("fill", PAL.tinta);
    });
  }

  // Gota con cara. (cx, cy) = centro del cuerpo, rad = radio del cuerpo.
  function gota(g, cx, cy, rad, color, conOjos = true) {
    const d = `M0,${-1.9 * rad} L${0.88 * rad},${-0.47 * rad} A${rad},${rad} 0 1 1 ${-0.88 * rad},${-0.47 * rad} Z`;
    const a = g.append("g").attr("transform", `translate(${cx},${cy})`);
    a.append("path").attr("d", d).attr("fill", color);
    if (conOjos) ojos(a, 0, rad * 0.1, rad * 0.36, rad * 0.3, 0, 0.4);
    return a;
  }

  // Patito de hule: marca a los meses y días con más reportes
  function pato(g, x, y, s) {
    const a = g.append("g").attr("transform", `translate(${x},${y})`);
    a.append("ellipse").attr("cx", 0).attr("cy", -0.45 * s).attr("rx", 0.95 * s).attr("ry", 0.62 * s).attr("fill", PAL.oro).attr("stroke", PAL.oroOscuro).attr("stroke-width", 1);
    a.append("path").attr("d", `M${-0.9 * s},${-0.7 * s} Q${-1.5 * s},${-1.2 * s} ${-1.2 * s},${-1.35 * s} Q${-0.8 * s},${-1.0 * s} ${-0.4 * s},${-0.75 * s} Z`).attr("fill", PAL.oro).attr("stroke", PAL.oroOscuro).attr("stroke-width", 1);
    a.append("circle").attr("cx", 0.62 * s).attr("cy", -1.2 * s).attr("r", 0.46 * s).attr("fill", PAL.oro).attr("stroke", PAL.oroOscuro).attr("stroke-width", 1);
    a.append("path").attr("d", `M${1.02 * s},${-1.25 * s} L${1.6 * s},${-1.1 * s} L${1.02 * s},${-0.95 * s} Z`).attr("fill", PAL.oroOscuro);
    a.append("path").attr("d", `M${-0.2 * s},${-0.5 * s} Q${0.15 * s},${-0.15 * s} ${0.55 * s},${-0.5 * s}`).attr("fill", "none").attr("stroke", PAL.oroOscuro).attr("stroke-width", 1);
    a.append("circle").attr("cx", 0.7 * s).attr("cy", -1.3 * s).attr("r", 0.11 * s).attr("fill", PAL.tinta);
    return a;
  }

  // Globo de diálogo (humor): texto corto centrado en (x, y) y colita hacia (colaX, colaY)
  function globo(g, x, y, texto, colaX, colaY) {
    const a = g.append("g").attr("class", "globo");
    const t = a.append("text").attr("x", x).attr("y", y).attr("text-anchor", "middle").text(texto);
    const b = t.node().getBBox();
    const bx = b.x - 7, by = b.y - 3, bw = b.width + 14, bh = b.height + 6;
    const tx = Math.max(bx + 10, Math.min(colaX, bx + bw - 10));
    a.insert("path", "text")
      .attr("d", `M${bx + 8},${by} H${bx + bw - 8} Q${bx + bw},${by} ${bx + bw},${by + 8} V${by + bh - 8} Q${bx + bw},${by + bh} ${bx + bw - 8},${by + bh} H${tx + 5} L${colaX},${colaY} L${tx - 5},${by + bh} H${bx + 8} Q${bx},${by + bh} ${bx},${by + bh - 8} V${by + 8} Q${bx},${by} ${bx + 8},${by} Z`)
      .attr("fill", "#fff").attr("stroke", PAL.gris).attr("stroke-width", 1);
    t.raise();
    return a;
  }

  /* Espo, la esponja (Mérida). g = grupo con origen en el centro de la base.
     nivel (0 a 1) = qué tanto se llena de agua; nivelMediana (opcional) = raya dorada;
     color = color del agua; rebosa = dibuja chorritos que se salen por los lados. */
  let uid = 0;
  const POROS = [[-0.26, 0.16, 3.4], [0.22, 0.3, 2.6], [0.04, 0.5, 2.2], [-0.2, 0.62, 2.8], [0.27, 0.74, 3.2], [-0.02, 0.86, 2.4], [-0.3, 0.9, 2], [0.12, 0.16, 1.8]];
  function esponja(g, w, h, nivel, nivelMediana = null, color = PAL.morado, rebosa = false) {
    const id = `esp-${++uid}`;
    nivel = Math.max(0, Math.min(1, nivel));
    g.append("clipPath").attr("id", id).append("rect").attr("x", -w / 2).attr("y", -h).attr("width", w).attr("height", h).attr("rx", Math.min(12, w / 3));
    g.append("rect").attr("x", -w / 2).attr("y", -h).attr("width", w).attr("height", h).attr("rx", Math.min(12, w / 3)).attr("fill", "#f3f4f6");
    const agua = g.append("g").attr("clip-path", `url(#${id})`);
    const y0 = -h * nivel;
    const ola = d3.range(-w / 2 - 8, w / 2 + 9, 4).map((x, i) => [x, y0 + 2.2 * Math.sin(i * 1.1)]);
    agua.append("path").attr("class", "ola").attr("d", d3.line().curve(d3.curveBasis)(ola) + `L${w / 2 + 8},0 L${-w / 2 - 8},0 Z`).attr("fill", color);
    POROS.forEach(([fx, fy, rad]) => g.append("ellipse").attr("cx", fx * w).attr("cy", -h + fy * h).attr("rx", Math.min(rad, w / 10)).attr("ry", Math.min(rad, w / 10) * 0.8).attr("fill", "rgba(13,13,13,.16)"));
    g.append("rect").attr("x", -w / 2).attr("y", -h).attr("width", w).attr("height", h).attr("rx", Math.min(12, w / 3)).attr("fill", "none").attr("stroke", PAL.gris).attr("stroke-width", 1.5);
    if (nivelMediana !== null) {
      const ym = -h * nivelMediana;
      g.append("line").attr("x1", -w / 2 - 3).attr("x2", w / 2 + 3).attr("y1", ym).attr("y2", ym).attr("stroke", PAL.oro).attr("stroke-width", 3.5).attr("stroke-linecap", "round");
    }
    if (rebosa) {
      [-1, 1].forEach((s) => {
        g.append("path").attr("d", `M${s * w / 2},${-h * 0.35} q${s * 9},2 ${s * 11},16 q${s * 1},12 ${s * -2},22`).attr("fill", "none").attr("stroke", color).attr("stroke-width", 4).attr("stroke-linecap", "round");
      });
    }
    // Cara: ojos arriba, boca según qué tan empapada está
    ojos(g, 0, -h + Math.min(22, h * 0.3), w * 0.2, Math.max(2.6, w * 0.13), 0, -0.7);
    const boca = g.append("g").attr("transform", `translate(0,${-h + Math.min(40, h * 0.55)})`);
    const k = Math.max(0.6, Math.min(1, w / 50));
    if (nivel < 0.15) boca.append("path").attr("d", `M${-5 * k},${2 * k} Q0,${-2 * k} ${5 * k},${2 * k}`).attr("fill", "none").attr("stroke", PAL.tinta).attr("stroke-width", 1.6).attr("stroke-linecap", "round");
    else if (nivel < 0.55) boca.append("path").attr("d", `M${-5 * k},0 Q0,${5 * k} ${5 * k},0`).attr("fill", "none").attr("stroke", PAL.tinta).attr("stroke-width", 1.6).attr("stroke-linecap", "round");
    else if (nivel < 0.85) boca.append("path").attr("d", `M${-6 * k},${-k} Q0,${9 * k} ${6 * k},${-k} Z`).attr("fill", PAL.tinta);
    else boca.append("circle").attr("r", 4.6 * k).attr("fill", PAL.tinta);
  }

  // Lluvia diaria (promedio de las estaciones, mm) desde la que el equipo cuenta un «aguacero fuerte».
  // Es un parámetro de análisis (el mismo de «días con 50 mm o más»), no un dato medido.
  const UMBRAL_MM = 50;

  window.Booklet = { UMBRAL_MM, esponja, PAL, fmt, MESES, MESES_3, fechaLarga, fechaCorta, correlacion, pendiente, marco, errorEscena, chip, ojos, gota, pato, globo, r };
})();
