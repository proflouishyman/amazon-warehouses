/* Shared helpers for every page. Load after the data_*.js files the page needs and after data_meta.js.
   Usage: AMZ.page({id:"injuries", title:"Workplace injuries", sub:"..."}); then build content into #app. */
(function () {
"use strict";
var AMZ = window.AMZ = {};
var $ = AMZ.$ = function (s, r) { return (r || document).querySelector(s); };
var META = window.AMZ_META || { pages: [], title: "Amazon US warehouse network" };

/* ---------- basics ---------- */
AMZ.esc = function (s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); };
AMZ.fmt = function (n, d) { if (n == null || n === "" || isNaN(n)) return ""; return Number(n).toLocaleString("en-US", { minimumFractionDigits: d || 0, maximumFractionDigits: d || 0 }); };
AMZ.pct = function (x, d) { return x == null || isNaN(x) ? "" : (100 * x).toFixed(d == null ? 1 : d) + "%"; };
AMZ.compact = function (n) { if (n == null || isNaN(n)) return ""; var a = Math.abs(n); if (a >= 1e9) return (n / 1e9).toFixed(1) + "bn"; if (a >= 1e6) return (n / 1e6).toFixed(1) + "m"; if (a >= 1e3) return (n / 1e3).toFixed(1) + "k"; return String(Math.round(n * 10) / 10); };
AMZ.rows = function (t) { if (!t) return []; return t.rows.map(function (r) { var o = {}; t.cols.forEach(function (c, i) { o[c] = r[i]; }); return o; }); };
AMZ.sum = function (a, f) { return a.reduce(function (s, x) { var v = f ? f(x) : x; return s + (v == null || isNaN(v) ? 0 : v); }, 0); };
AMZ.by = function (a, f) { var o = {}; a.forEach(function (x) { var k = f(x); (o[k] = o[k] || []).push(x); }); return o; };
AMZ.el = function (html) { var d = document.createElement("div"); d.innerHTML = html; return d.firstElementChild; };
AMZ.mount = function (host, html) { var h = typeof host === "string" ? $(host) : host; if (h) h.insertAdjacentHTML("beforeend", html); return h; };
AMZ.sourcesOf = function (domain) { return ((window.AMZ_SOURCES || {}).catalog || []).filter(function (c) { return c.domain === domain; }); };

/* ---------- page chrome ---------- */
AMZ.page = function (o) {
  var here = location.pathname.split("/").pop() || "index.html";
  var nav = (META.pages || []).map(function (p) { return '<a href="' + p[0] + '"' + (p[0] === here ? ' aria-current="page"' : "") + ">" + AMZ.esc(p[1]) + "</a>"; }).join("");
  var h = '<header class="top"><div class="in"><h1>' + AMZ.esc(o.title || META.title) + "</h1>" +
    '<p class="sub">' + (o.sub || "") + "</p>" + (o.stats ? '<div class="stats">' + o.stats + "</div>" : "") +
    '<nav id="mainnav" aria-label="Pages" class="multi">' + nav + "</nav></div></header>";
  document.body.insertAdjacentHTML("afterbegin", h);
  document.body.insertAdjacentHTML("beforeend", '<footer class="foot">Static page generated ' + AMZ.esc(META.generated || "") + ". Data retrieved " + AMZ.esc(META.retrieved || "") +
    ". Independent project, not affiliated with Amazon. Figures marked estimate are screening-level; see <a href=\"methods.html\">Methods</a> and <a href=\"sources.html\">Sources</a>. No data about individual workers.</footer>");
  var t = document.createElement("div"); t.id = "tip"; t.setAttribute("role", "status"); document.body.appendChild(t);
};
AMZ.tiles = function (host, list) {
  var h = '<div class="hl"><div class="hlg">' + list.map(function (t) {
    var tag = t.href ? "a" : "div";
    return "<" + tag + ' class="hlt' + (String(t.value).length > 14 ? " long" : "") + '"' + (t.href ? ' href="' + t.href + '"' : "") + "><b>" + AMZ.esc(t.value) + "</b><span class=\"hll\">" + AMZ.esc(t.label) + "</span>" +
      (t.context ? '<span class="hlc">' + AMZ.esc(t.context) + "</span>" : "") + "</" + tag + ">";
  }).join("") + "</div></div>";
  AMZ.mount(host, h);
};
AMZ.estimate = function (host, text) { AMZ.mount(host, '<div class="est"><b>Estimate.</b> ' + text + "</div>"); };
AMZ.caveat = function (host, html) { AMZ.mount(host, '<div class="find cav">' + html + "</div>"); };
AMZ.section = function (host, id, title, intro) { AMZ.mount(host, '<section class="gsec" id="' + id + '"><h2>' + AMZ.esc(title) + "</h2>" + (intro ? '<p class="method">' + intro + "</p>" : "") + '<div id="' + id + '-body"></div></section>'); return $("#" + id + "-body"); };
AMZ.sources = function (host, list) {
  /* list: [{label,url,publisher,note}] or a domain name string -> built from AMZ_SOURCES.catalog */
  if (typeof list === "string") list = AMZ.sourcesOf(list).map(function (c) { return { label: c.what, url: String(c.url).split(" ; ")[0], publisher: c.publisher, note: c.coverage + ". " + c.caveats }; });
  AMZ.mount(host, '<div class="srcs"><h3>Sources</h3><ul>' + list.map(function (s) {
    return "<li>" + (s.url && /^https?:/.test(s.url) ? '<a href="' + AMZ.esc(s.url) + '" target="_blank" rel="noopener">' + AMZ.esc(s.label) + "</a>" : AMZ.esc(s.label)) +
      (s.publisher ? " (" + AMZ.esc(s.publisher) + ")" : "") + (s.note ? ". <span class=\"muted\">" + AMZ.esc(s.note) + "</span>" : "") + "</li>";
  }).join("") + "</ul></div>");
};

/* ---------- tooltip ---------- */
var tip = function () { return document.getElementById("tip"); };
AMZ.showTip = function (ev, html) {
  var t = tip(); if (!t) return; t.innerHTML = html; t.style.display = "block";
  var x = ev.clientX + 12, y = ev.clientY + 12, w = t.offsetWidth, h = t.offsetHeight;
  if (x + w > window.innerWidth - 8) x = ev.clientX - w - 12; if (y + h > window.innerHeight - 8) y = ev.clientY - h - 12;
  t.style.left = Math.max(4, x) + "px"; t.style.top = Math.max(4, y) + "px";
};
AMZ.hideTip = function () { var t = tip(); if (t) t.style.display = "none"; };
document.addEventListener("scroll", function () { AMZ.hideTip(); }, true);

/* ---------- charts (inline SVG, no libraries) ---------- */
function niceTicks(lo, hi, n) {
  if (lo === hi) { hi = lo + 1; }
  var span = hi - lo, step = Math.pow(10, Math.floor(Math.log(span / n) / Math.LN10)), err = n / span * step;
  if (err <= .15) step *= 10; else if (err <= .35) step *= 5; else if (err <= .75) step *= 2;
  var a = Math.floor(lo / step) * step, b = Math.ceil(hi / step) * step, t = [];
  for (var v = a; v <= b + step / 2; v += step) t.push(Math.round(v / step * 1e6) / 1e6 * step);
  return t;
}
/* o: {series:[{name,color,dash,points:[[x,y],...]}], yFmt, xFmt, yMin, yMax, yLabel, height, zeroBase, title}
   null y values break the line. Colors default to the --cat tokens. */
AMZ.lineChart = function (host, o) {
  var W = 760, H = o.height || 300, m = { l: 52, r: 14, t: 12, b: 30 }, S = o.series, C = ["var(--cat1)", "var(--cat2)", "var(--cat3)", "var(--cat4)", "var(--cat5)", "var(--cat6)"];
  var xs = [], ys = [];
  S.forEach(function (s) { s.points.forEach(function (p) { xs.push(p[0]); if (p[1] != null && !isNaN(p[1])) ys.push(p[1]); }); });
  if (!xs.length || !ys.length) { AMZ.mount(host, '<p class="muted">No data.</p>'); return; }
  var x0 = Math.min.apply(null, xs), x1 = Math.max.apply(null, xs), y0 = o.yMin != null ? o.yMin : (o.zeroBase === false ? Math.min.apply(null, ys) : Math.min(0, Math.min.apply(null, ys))), y1 = o.yMax != null ? o.yMax : Math.max.apply(null, ys);
  var yt = niceTicks(y0, y1, 5); y0 = Math.min(y0, yt[0]); y1 = Math.max(y1, yt[yt.length - 1]);
  var X = function (v) { return m.l + (x1 === x0 ? .5 : (v - x0) / (x1 - x0)) * (W - m.l - m.r); }, Y = function (v) { return H - m.b - (v - y0) / (y1 - y0) * (H - m.t - m.b); };
  var yf = o.yFmt || AMZ.compact, xf = o.xFmt || function (v) { return String(v); };
  var g = "";
  yt.forEach(function (v) { g += '<line class="gl" x1="' + m.l + '" x2="' + (W - m.r) + '" y1="' + Y(v) + '" y2="' + Y(v) + '"/><text x="' + (m.l - 6) + '" y="' + (Y(v) + 3) + '" text-anchor="end">' + AMZ.esc(yf(v)) + "</text>"; });
  var step = Math.max(1, Math.ceil((x1 - x0 + 1) / 10));
  for (var xv = x0; xv <= x1; xv += step) g += '<text x="' + X(xv) + '" y="' + (H - 10) + '" text-anchor="middle">' + AMZ.esc(xf(xv)) + "</text>";
  g += '<line class="ax" x1="' + m.l + '" x2="' + (W - m.r) + '" y1="' + Y(y0) + '" y2="' + Y(y0) + '"/>';
  var dots = "";
  S.forEach(function (s, i) {
    var col = s.color || C[i % C.length], d = "", pen = false;
    s.points.forEach(function (p) {
      if (p[1] == null || isNaN(p[1])) { pen = false; return; }
      d += (pen ? "L" : "M") + X(p[0]).toFixed(1) + "," + Y(p[1]).toFixed(1); pen = true;
      dots += '<circle class="pt" tabindex="0" cx="' + X(p[0]).toFixed(1) + '" cy="' + Y(p[1]).toFixed(1) + '" r="' + (s.points.length > 40 ? 2.2 : 3.5) + '" fill="' + col + '" data-t="' + AMZ.esc("<b>" + s.name + "</b><br>" + xf(p[0]) + ": " + yf(p[1]) + (p[2] ? "<br>" + p[2] : "")) + '"/>';
    });
    g += '<path d="' + d + '" fill="none" stroke="' + col + '" stroke-width="2.2"' + (s.dash ? ' stroke-dasharray="' + s.dash + '"' : "") + "/>";
  });
  var leg = S.map(function (s, i) { return '<span><i class="sw" style="background:' + (s.color || C[i % C.length]) + '"></i>' + AMZ.esc(s.name) + "</span>"; }).join("");
  var id = "c" + Math.random().toString(36).slice(2, 8);
  AMZ.mount(host, '<div class="card ch" id="' + id + '">' + (o.title ? "<h3>" + AMZ.esc(o.title) + "</h3>" : "") + '<svg class="rs" viewBox="0 0 ' + W + " " + H + '" role="img" aria-label="' + AMZ.esc(o.title || "Line chart") + '">' + g + dots + "</svg>" +
    '<div class="legend">' + leg + "</div>" + (o.caption ? '<p class="cap">' + o.caption + "</p>" : "") + "</div>");
  bindTips($("#" + id));
};
/* o: {items:[{label,value,color,note}], valFmt, title, horizontal(default true)} */
AMZ.barChart = function (host, o) {
  var it = o.items, n = it.length, rowH = 22, W = 760, lab = o.labelWidth || 150, H = n * rowH + 12, mx = Math.max.apply(null, it.map(function (d) { return d.value || 0; })) || 1, vf = o.valFmt || AMZ.compact, g = "";
  it.forEach(function (d, i) {
    var y = 6 + i * rowH, w = (d.value || 0) / mx * (W - lab - 70);
    g += '<text x="' + (lab - 6) + '" y="' + (y + 14) + '" text-anchor="end" class="t1">' + AMZ.esc(d.label) + '</text><rect class="pt" tabindex="0" x="' + lab + '" y="' + y + '" width="' + Math.max(1, w).toFixed(1) + '" height="16" rx="2" fill="' + (d.color || "var(--cat1)") + '" data-t="' + AMZ.esc("<b>" + d.label + "</b><br>" + vf(d.value) + (d.note ? "<br>" + d.note : "")) + '"/><text x="' + (lab + w + 5) + '" y="' + (y + 13) + '">' + AMZ.esc(vf(d.value)) + "</text>";
  });
  var id = "c" + Math.random().toString(36).slice(2, 8);
  AMZ.mount(host, '<div class="card ch" id="' + id + '">' + (o.title ? "<h3>" + AMZ.esc(o.title) + "</h3>" : "") + '<svg class="rs" viewBox="0 0 ' + W + " " + H + '" role="img" aria-label="' + AMZ.esc(o.title || "Bar chart") + '">' + g + "</svg>" + (o.caption ? '<p class="cap">' + o.caption + "</p>" : "") + "</div>");
  bindTips($("#" + id));
};
function bindTips(root) {
  if (!root) return;
  root.addEventListener("mousemove", function (e) { var t = e.target.getAttribute && e.target.getAttribute("data-t"); if (t) AMZ.showTip(e, t); else AMZ.hideTip(); });
  root.addEventListener("mouseleave", AMZ.hideTip);
  root.addEventListener("focusin", function (e) { var t = e.target.getAttribute && e.target.getAttribute("data-t"); if (t) { var r = e.target.getBoundingClientRect(); AMZ.showTip({ clientX: r.left, clientY: r.top }, t); } });
  root.addEventListener("focusout", AMZ.hideTip);
}
AMZ.bindTips = bindTips;

/* ---------- US map: state fill + points. o:{points:[{x,y,r,color,html}], fill:function(stateCode)->css color|null, stateTip:function(code,name)->html} ----------
   Facility x,y come precomputed in AMZ_FAC.facilities (columns x,y; 960 x 600 viewBox, AK/HI insets). */
AMZ.usMap = function (host, o) {
  var G = window.AMZ_GEO; if (!G) return;
  var paths = Object.keys(G.states).map(function (k) { var f = o.fill ? o.fill(k) : null; return '<path class="st pt" data-s="' + k + '" d="' + G.states[k].d + '"' + (f ? ' style="fill:' + f + '"' : "") + ' data-t="' + AMZ.esc(o.stateTip ? o.stateTip(k, G.states[k].name) : G.states[k].name) + '"/>'; }).join("");
  var pts = (o.points || []).map(function (p) { return '<circle class="pt" cx="' + p.x + '" cy="' + p.y + '" r="' + (p.r || 2) + '" fill="' + (p.color || "var(--amz)") + '" fill-opacity=".75" data-t="' + AMZ.esc(p.html || "") + '"/>'; }).join("");
  var id = "m" + Math.random().toString(36).slice(2, 8);
  AMZ.mount(host, '<div class="mapbox" id="' + id + '"><svg viewBox="0 0 ' + G.w + " " + G.h + '" role="img" aria-label="' + AMZ.esc(o.label || "Map of the United States") + '">' + paths + pts + "</svg></div>" + (o.caption ? '<p class="cap">' + o.caption + "</p>" : ""));
  bindTips($("#" + id));
};

/* ---------- sortable table. o:{cols:[{key,label,num,fmt,html}], rows:[obj], pageSize, sort:key, dir:1|-1} ---------- */
AMZ.table = function (host, o) {
  var h = typeof host === "string" ? $(host) : host, st = { sort: o.sort, dir: o.dir || 1, page: 0 }, ps = o.pageSize || 25, rows = o.rows;
  var box = document.createElement("div"); h.appendChild(box);
  function draw() {
    var r = rows.slice();
    if (st.sort) { var k = st.sort; r.sort(function (a, b) { var x = a[k], y = b[k]; if (x == null || x === "") return 1; if (y == null || y === "") return -1; return (x < y ? -1 : x > y ? 1 : 0) * st.dir; }); }
    var np = Math.max(1, Math.ceil(r.length / ps)); if (st.page >= np) st.page = np - 1;
    var pr = r.slice(st.page * ps, st.page * ps + ps);
    box.innerHTML = '<div class="tw"><table><thead><tr>' + o.cols.map(function (c) { return '<th class="' + (c.num ? "n" : "") + '" data-sort="' + c.key + '"' + (st.sort === c.key ? ' aria-sort="' + (st.dir > 0 ? "ascending" : "descending") + '"' : "") + ">" + AMZ.esc(c.label) + "</th>"; }).join("") + "</tr></thead><tbody>" +
      pr.map(function (x) { return "<tr>" + o.cols.map(function (c) { var v = x[c.key]; var s = c.html ? c.html(v, x) : AMZ.esc(c.fmt ? c.fmt(v, x) : (v == null ? "" : v)); return '<td class="' + (c.num ? "n" : "") + '">' + s + "</td>"; }).join("") + "</tr>"; }).join("") + "</tbody></table></div>" +
      '<div class="pager"><button class="btn ghost" data-p="-1"' + (st.page === 0 ? " disabled" : "") + '>Prev</button><span>Page ' + (st.page + 1) + " of " + np + " (" + AMZ.fmt(r.length) + ' rows)</span><button class="btn ghost" data-p="1"' + (st.page >= np - 1 ? " disabled" : "") + ">Next</button></div>";
  }
  box.addEventListener("click", function (e) {
    var th = e.target.closest && e.target.closest("th[data-sort]"); if (th) { var k = th.getAttribute("data-sort"); st.dir = st.sort === k ? -st.dir : 1; st.sort = k; st.page = 0; draw(); return; }
    var b = e.target.closest && e.target.closest("button[data-p]"); if (b) { st.page += +b.getAttribute("data-p"); draw(); }
  });
  draw();
  return { setRows: function (r) { rows = r; st.page = 0; draw(); } };
};

/* ---------- minimal markdown (headings, paragraphs, lists, tables, code, links, bold/italic) ---------- */
AMZ.md = function (src) {
  var L = String(src || "").replace(/\r/g, "").split("\n"), out = [], i = 0;
  function inl(s) {
    s = AMZ.esc(s);
    s = s.replace(/`([^`]+)`/g, "<code>$1</code>").replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>").replace(/(^|[^*])\*([^*\s][^*]*)\*/g, "$1<i>$2</i>");
    s = s.replace(/\[([^\]]+)\]\((https?:[^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
    s = s.replace(/(^|[\s(])(https?:\/\/[^\s<)]+)/g, '$1<a href="$2" target="_blank" rel="noopener">$2</a>');
    return s;
  }
  while (i < L.length) {
    var l = L[i], m;
    if (/^```/.test(l)) { var b = []; i++; while (i < L.length && !/^```/.test(L[i])) b.push(L[i++]); i++; out.push("<pre><code>" + AMZ.esc(b.join("\n")) + "</code></pre>"); continue; }
    if ((m = /^(#{1,4})\s+(.*)$/.exec(l))) { var lv = Math.min(4, m[1].length + 1); out.push("<h" + lv + ">" + inl(m[2]) + "</h" + lv + ">"); i++; continue; }
    if (/^\s*\|.*\|\s*$/.test(l) && i + 1 < L.length && /^\s*\|[\s:|-]+\|\s*$/.test(L[i + 1])) {
      var hd = l.trim().replace(/^\||\|$/g, "").split("|"); i += 2; var body = [];
      while (i < L.length && /^\s*\|.*\|\s*$/.test(L[i])) { body.push(L[i].trim().replace(/^\||\|$/g, "").split("|")); i++; }
      out.push("<table><thead><tr>" + hd.map(function (c) { return "<th>" + inl(c.trim()) + "</th>"; }).join("") + "</tr></thead><tbody>" + body.map(function (r) { return "<tr>" + r.map(function (c) { return "<td>" + inl(c.trim()) + "</td>"; }).join("") + "</tr>"; }).join("") + "</tbody></table>"); continue;
    }
    if (/^\s*([-*]|\d+\.)\s+/.test(l)) {
      var ord = /^\s*\d+\./.test(l), items = [];
      while (i < L.length && /^\s*([-*]|\d+\.)\s+/.test(L[i])) { var t = L[i].replace(/^\s*([-*]|\d+\.)\s+/, ""); i++; while (i < L.length && /^\s{2,}\S/.test(L[i]) && !/^\s*([-*]|\d+\.)\s+/.test(L[i])) t += " " + L[i++].trim(); items.push("<li>" + inl(t) + "</li>"); }
      out.push((ord ? "<ol>" : "<ul>") + items.join("") + (ord ? "</ol>" : "</ul>")); continue;
    }
    if (!l.trim()) { i++; continue; }
    var p = [l]; i++; while (i < L.length && L[i].trim() && !/^(#{1,4}\s|```|\s*([-*]|\d+\.)\s+|\s*\|)/.test(L[i])) p.push(L[i++]);
    out.push("<p>" + inl(p.join(" ")) + "</p>");
  }
  return out.join("\n");
};
})();
