var STATS = {
  months:    ["أكتوبر","نوفمبر","ديسمبر","يناير","فبراير","مارس","أبريل","مايو","يونيو","يوليو","أغسطس","سبتمبر"],
  spendK:    [48, 55, 60, 62, 70, 75, 80, 85, 95, 105, 110, 115],          // الإنفاق الإعلاني بالألف ريال
  roas:      [3.1, 3.4, 3.3, 3.8, 4.0, 4.2, 4.4, 4.5, 4.9, 5.2, 5.4, 5.8], // العائد على الإنفاق
  campaigns: [8, 9, 10, 11, 12, 12, 13, 13, 14, 15, 15, 16],               // حملات جديدة كل شهر
  seoVisits: [4200, 4800, 5600, 6300, 7400, 8200, 9500, 10800, 12100, 13600, 14900, 16300], // زيارات جوجل
  mix: [                                                                   // توزيع الميزانية %
    { name: "Google Ads", value: 34, color: "#86C144" },
    { name: "Instagram",  value: 24, color: "#E1306C" },
    { name: "TikTok",     value: 18, color: "#25F4EE" },
    { name: "Snapchat",   value: 16, color: "#FFFC00" },
    { name: "LinkedIn",   value: 8,  color: "#4E8FD6" }
  ]
};


(function(){
  /* ---------- Results dashboard ---------- */
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var fmt = function(n, d){ return n.toLocaleString("en-US", { minimumFractionDigits: d||0, maximumFractionDigits: d||0 }); };
  var shown = {};
  function countTo(id, to, decimals, prefix, suffix){
    var el = document.getElementById(id), from = shown[id] || 0, start = null, dur = reduce ? 0 : 900;
    shown[id] = to;
    function step(t){
      if (!start) start = t;
      var p = dur ? Math.min((t - start) / dur, 1) : 1, e = 1 - Math.pow(1 - p, 3);
      el.textContent = (prefix||"") + fmt(from + (to - from) * e, decimals) + (suffix||"");
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  var charts = {}, current = 12;
  function slice(arr, n){ return arr.slice(arr.length - n); }

  function updateKpis(n){
    var sp = slice(STATS.spendK, n), ro = slice(STATS.roas, n), ca = slice(STATS.campaigns, n), se = slice(STATS.seoVisits, n);
    var spend = sp.reduce(function(a,b){return a+b;},0);
    var weighted = sp.reduce(function(a,v,i){ return a + v * ro[i]; },0) / spend;
    var base = n < STATS.seoVisits.length ? STATS.seoVisits[STATS.seoVisits.length - n - 1] : STATS.seoVisits[0];
    var growth = (se[se.length-1] - base) / base * 100;
    countTo("kRoas", weighted, 1, "", "x");
    countTo("kRoasSar", weighted, 1);
    countTo("kSeo", growth, 0, "+", "%");
    countTo("kSeoVisits", se.reduce(function(a,b){return a+b;},0), 0);
    countTo("kCamp", ca.reduce(function(a,b){return a+b;},0), 0);
    countTo("kBudget", spend * 1000, 0);
  }

  function buildCharts(){
    if (!window.Chart) return;
    Chart.defaults.font.family = "Cairo, Tahoma, sans-serif";
    Chart.defaults.font.size = 13;
    Chart.defaults.color = "#AEBACB";
    var grid = { color: "rgba(255,255,255,.06)" };
    var tip = { rtl: true, textDirection: "rtl", backgroundColor: "#fff", titleColor: "#0A1321", bodyColor: "#0A1321", padding: 12, cornerRadius: 10, titleFont: { weight: "800" }, bodyFont: { weight: "600" } };

    charts.roas = new Chart(document.getElementById("cRoas"), {
      data: { labels: [], datasets: [
        { type: "line", label: "العائد على الإنفاق", data: [], yAxisID: "y1", borderColor: "#86C144", backgroundColor: "#86C144", borderWidth: 3, tension: .35, pointRadius: 3, pointHoverRadius: 6, order: 0 },
        { type: "bar", label: "الإنفاق (ألف ريال)", data: [], yAxisID: "y", backgroundColor: "#2E4062", hoverBackgroundColor: "#4E6079", borderRadius: 6, order: 1 }
      ]},
      options: { maintainAspectRatio: false, interaction: { mode: "index", intersect: false },
        plugins: { legend: { display: false }, tooltip: Object.assign({}, tip, { callbacks: { label: function(c){ return c.dataset.yAxisID === "y1" ? " العائد: " + c.parsed.y + "x" : " الإنفاق: " + c.parsed.y + " ألف ريال"; } } }) },
        scales: { x: { grid: { display: false }, ticks: { maxRotation: 0, autoSkipPadding: 10 } }, y: { position: "left", grid: grid, beginAtZero: true }, y1: { position: "right", grid: { display: false }, beginAtZero: true, ticks: { callback: function(v){ return v + "x"; } } } } }
    });

    var ctx = document.getElementById("cSeo").getContext("2d");
    var grad = ctx.createLinearGradient(0, 0, 0, 260);
    grad.addColorStop(0, "rgba(134,193,68,.45)"); grad.addColorStop(1, "rgba(134,193,68,0)");
    charts.seo = new Chart(ctx, {
      type: "line",
      data: { labels: [], datasets: [{ label: "زيارات جوجل", data: [], fill: true, backgroundColor: grad, borderColor: "#86C144", borderWidth: 3, tension: .4, pointRadius: 0, pointHoverRadius: 6, pointBackgroundColor: "#86C144" }] },
      options: { maintainAspectRatio: false, interaction: { mode: "index", intersect: false },
        plugins: { legend: { display: false }, tooltip: Object.assign({}, tip, { callbacks: { label: function(c){ return " " + fmt(c.parsed.y) + " زيارة"; } } }) },
        scales: { x: { grid: { display: false }, ticks: { maxRotation: 0, autoSkipPadding: 10 } }, y: { position: "left", grid: grid, ticks: { callback: function(v){ return v >= 1000 ? (v/1000) + "k" : v; } } } } }
    });

    charts.mix = new Chart(document.getElementById("cMix"), {
      type: "doughnut",
      data: { labels: STATS.mix.map(function(m){return m.name;}), datasets: [{ data: STATS.mix.map(function(m){return m.value;}), backgroundColor: STATS.mix.map(function(m){return m.color;}), borderColor: "#1A2638", borderWidth: 3, hoverOffset: 8 }] },
      options: { maintainAspectRatio: false, cutout: "66%", plugins: { legend: { display: false }, tooltip: Object.assign({}, tip, { callbacks: { label: function(c){ return " " + c.label + ": " + c.parsed + "%"; } } }) } }
    });
    document.getElementById("mixLegend").innerHTML = STATS.mix.map(function(m){
      return '<li><i style="background:'+m.color+'"></i><span class="ltr" style="margin:0;color:#fff">'+m.name+'</span><span>'+m.value+'%</span></li>';
    }).join("");

    charts.camp = new Chart(document.getElementById("cCamp"), {
      type: "bar",
      data: { labels: [], datasets: [{ label: "حملات جديدة", data: [], backgroundColor: "#86C144", hoverBackgroundColor: "#A3D66A", borderRadius: 6, maxBarThickness: 34 }] },
      options: { maintainAspectRatio: false,
        plugins: { legend: { display: false }, tooltip: Object.assign({}, tip, { callbacks: { label: function(c){ return " " + c.parsed.y + " حملة"; } } }) },
        scales: { x: { grid: { display: false }, ticks: { maxRotation: 0, autoSkipPadding: 10 } }, y: { position: "left", grid: grid, beginAtZero: true, ticks: { precision: 0 } } } }
    });
  }

  function updateCharts(n){
    if (!charts.roas) return;
    var labels = slice(STATS.months, n);
    charts.roas.data.labels = labels;
    charts.roas.data.datasets[0].data = slice(STATS.roas, n);
    charts.roas.data.datasets[1].data = slice(STATS.spendK, n);
    charts.seo.data.labels = labels;
    charts.seo.data.datasets[0].data = slice(STATS.seoVisits, n);
    charts.camp.data.labels = labels;
    charts.camp.data.datasets[0].data = slice(STATS.campaigns, n);
    ["roas","seo","camp"].forEach(function(k){ charts[k].update(reduce ? "none" : undefined); });
  }

  var seg = document.getElementById("periodSeg");
  seg.addEventListener("click", function(e){
    var b = e.target.closest("button"); if (!b) return;
    seg.querySelectorAll("button").forEach(function(x){ x.setAttribute("aria-pressed", x === b); });
    current = +b.dataset.period;
    updateKpis(current); updateCharts(current);
  });

  // Build dashboard when it scrolls into view (so the counters are seen)
  var started = false;
  function startDash(){
    if (started) return; started = true;
    buildCharts(); updateKpis(current); updateCharts(current);
  }
  if ("IntersectionObserver" in window){
    var io = new IntersectionObserver(function(en){ if (en[0].isIntersecting){ startDash(); io.disconnect(); } }, { threshold: .2 });
    io.observe(document.getElementById("results"));
  } else { startDash(); }


})();
