/* benchmark.html page logic. Reads window.AMZ_BENCH (assets/data_bench.js) only; no numbers are typed in here. */
(function () {
"use strict";
var A = AMZ, B = AMZ_BENCH, esc = A.esc;
/* nav: add this page if the generated AMZ_META.pages lacks it */
(function () { var p = AMZ_META.pages; if (!p.some(function (x) { return x[0] === "benchmark.html"; })) { var i = p.findIndex(function (x) { return x[0] === "environment.html"; }); p.splice(i < 0 ? p.length - 2 : i + 1, 0, ["benchmark.html", "Benchmark"]); } })();

A.page({ title: "Benchmark: Amazon against its peers",
  sub: "Amazon set against Walmart, Target, the other warehouse and parcel operators and the industry, from public filings and government data." });
var app = A.$("#app");
var T = {}; Object.keys(B).forEach(function (k) { if (B[k] && B[k].cols) T[k] = A.rows(B[k]); });
var FILES = B.files || {};
function furl(k) { return "data/processed/" + FILES[k]; }
function flink(k) { return '<a href="' + esc(furl(k)) + '">' + esc(FILES[k]) + "</a>"; }
function f1(v) { return v == null || isNaN(v) ? "n/a" : Number(v).toFixed(1); }
function f2(v) { return v == null || isNaN(v) ? "n/a" : Number(v).toFixed(2); }
function pc(v, d) { return v == null || isNaN(v) ? "n/a" : (100 * v).toFixed(d || 0) + "%"; }
function yr(p) { var m = String(p).match(/(\d{4})/); return m ? +m[1] : 0; }
function first(a, f) { return a.filter(f)[0]; }

/* ---------- builders ---------- */
function card(host, o) {
  var id = "bc-" + o.id;
  A.mount(host, '<div class="bcard" id="' + id + '"><h3 class="bt"></h3><p class="bc">' + o.cav + '</p><div class="body"></div><p class="bs">Source: ' + o.files.map(flink).join(", ") + ". " + o.orig + "</p></div>");
  var el = A.$("#" + id);
  var c = { el: el, body: A.$(".body", el), title: function (t) { A.$("h3.bt", el).textContent = t; } };
  c.title(o.title || "");
  A.bindTips(el);
  return c;
}
function tv(host, cols, rows, label) {
  A.mount(host, '<details class="tv"><summary>' + esc(label || "Table view") + '</summary><div class="twrap"><table class="btab"><thead><tr>' + cols.map(function (c) { return '<th class="' + (c.n ? "n" : "") + '">' + esc(c.h) + "</th>"; }).join("") + "</tr></thead><tbody>" +
    rows.map(function (r) { return "<tr>" + cols.map(function (c) { return '<td class="' + (c.n ? "n" : "") + '">' + (c.html ? r[c.k] : esc(r[c.k] == null ? "" : r[c.k])) + "</td>"; }).join("") + "</tr>"; }).join("") + "</tbody></table></div></details>");
}
function key(host, parts) { A.mount(host, '<div class="mkey">' + parts.map(function (p) { return "<span><i class=\"" + p[0] + "\"></i>" + esc(p[1]) + "</span>"; }).join("") + "</div>"); }
/* items: [{label,sub,value,cls,tip,text,group}], o:{fmt, ref, refLabel, max} */
function hbar(host, items, o) {
  o = o || {};
  var fmt = o.fmt || f1, vals = items.map(function (d) { return d.value; }).filter(function (v) { return v != null && !isNaN(v); });
  var mx = Math.max.apply(null, vals.concat(o.ref != null ? [o.ref] : [])) * 1.2 || 1;
  if (o.max) mx = o.max;
  var h = '<div class="br' + (o.ref != null ? " hasref" : "") + '"' + (o.ref != null ? ' style="--ref:' + (100 * o.ref / mx).toFixed(2) + '%"' : "") + ">", lastg = null;
  items.forEach(function (d) {
    if (d.group && d.group !== lastg) { h += '<div class="grp">' + esc(d.group) + "</div>"; lastg = d.group; }
    var has = d.value != null && !isNaN(d.value), w = has ? 100 * d.value / mx : 0;
    h += '<div class="r ' + (d.cls || "") + '"><div class="lb">' + esc(d.label) + (d.sub ? '<span class="sb">' + esc(d.sub) + "</span>" : "") + '</div><div class="trk">' +
      (has ? '<i class="fill" style="width:' + w.toFixed(2) + '%"></i><span class="v" style="left:calc(' + w.toFixed(2) + '% + 5px)">' + esc(d.text || fmt(d.value)) + "</span>" : '<span class="nov">' + esc(d.text || "no value in file") + "</span>") +
      '<span class="hit" tabindex="0" data-t="' + esc("<b>" + d.label + "</b><br>" + (has ? (d.text || fmt(d.value)) : "no value") + (d.tip ? "<br>" + d.tip : "")) + '"></span></div></div>';
  });
  A.mount(host, h + "</div>");
}
function clear(el) { el.innerHTML = ""; }
var NAME = { amazon: "Amazon", ita_493110_ex_amazon: "Other NAICS 493110 filers", walmart: "Walmart DCs", target: "Target supply-chain sites", group_3pl: "3PLs combined", group_retailer_dcs: "Retailer DCs combined", costco: "Costco", ups: "UPS", fedex_express: "FedEx Express" };
var CLS = { amazon: "amz", ita_493110_ex_amazon: "agg", group_3pl: "agg", group_retailer_dcs: "agg" };

/* ---------- headline tiles ---------- */
var P24 = {}; T.injuries_peer_year.filter(function (r) { return r.scope === "headline" && r.year === 2024; }).forEach(function (r) { P24[r.peer] = r; });
var SH = {}; T.industry_amazon_share_493.forEach(function (r) { SH[r.year] = r; });
var NET = {}; T.network_headline.forEach(function (r) { if (r.cal_year_approx === 2024) NET[r.slug + "|" + r.metric] = r; });
A.tiles(app, [
  { value: f1(P24.amazon.trc) + " vs " + f1(P24.ita_493110_ex_amazon.trc), label: "2024 recordable injuries per 100 FTE: Amazon against other NAICS 493110 filers", context: "OSHA ITA, hours-weighted; Amazon is " + f2(P24.amazon.trc / P24.ita_493110_ex_amazon.trc) + " times the other filers", href: "#bc-inj-bar" },
  { value: pc(P24.amazon.trc_share_sites_above_bls), label: "of Amazon sites are above the BLS warehousing rate", context: pc(P24.ita_493110_ex_amazon.trc_share_sites_above_bls) + " of other 493110 filers; " + pc(P24.walmart.trc_share_sites_above_bls) + " of Walmart sites", href: "#bc-inj-share" },
  { value: "$" + f1(NET["amazon|revenue_per_employee_usd_k"].value) + "k", label: "Revenue per employee, 2024 (company-wide)", context: "Includes AWS; see caveat", href: "#bc-fin-rpe" },
  { value: f1(SH[2024].amazon_share_of_qcew_493_pct_estimate) + "%", label: "Amazon's estimated share of NAICS 493 employment, 2024", context: "Estimate from OSHA filings against QCEW", href: "#bc-ind-share" }
]);
A.caveat(app, "<b>Read before using.</b><ul><li>Companies report on different bases. The note under each chart gives its main limit.</li><li>Injury rates are self-reported establishment filings, not audited. Amazon is filed under NAICS 493 plus 492 and most peers under 493110.</li><li>Revenue, capital spending and headcount are company-wide. Amazon's include AWS.</li><li>Industry shares are estimates, not strict bounds.</li></ul>");

/* =================== 1. INJURIES =================== */
var s1 = A.section(app, "injuries", "Injuries by operator (OSHA ITA Form 300A)", "Total recordable cases (TRC) are all logged work-related injuries and illnesses. DART cases involved days away, restricted duty or transfer. DAFW cases involved days away from work. Rates are cases per 100 full-time workers, hours-weighted across sites.");
var MEAS = { trc: { name: "TRC", long: "total recordable case" }, dart: { name: "DART", long: "days away, restricted or transferred" }, dafw: { name: "DAFW", long: "days away from work" } };
var meas = "trc";
A.mount(s1, '<div class="tools" role="group" aria-label="Injury measure"><span>Measure:</span><span class="seg" id="mseg">' + Object.keys(MEAS).map(function (k) { return '<button type="button" data-m="' + k + '" aria-pressed="' + (k === meas) + '">' + MEAS[k].name + "</button>"; }).join("") + "</span></div>");
var cInj = card(s1, { id: "inj-bar", files: ["injuries_peer_year"], orig: "Original sources: OSHA Injury Tracking Application (Form 300A, CY2024) at osha.gov/Establishment-Specific-Injury-and-Illness-Data; BLS Survey of Occupational Injuries and Illnesses, NAICS 493110.",
  cav: "Cases per 100 full-time workers, as filed with OSHA. Amazon is on NAICS 493 plus 492; others on 493110. FedEx Ground is left out because its 2024 filings cover only part of the year. Sites with few filings give noisy rates; the number of valid sites is under each name." });
var cLine = card(s1, { id: "inj-line", files: ["injuries_peer_year"], orig: "Original sources: OSHA ITA Form 300A, CY2017 to CY2024.",
  cav: "2019 Walmart matching is approximate. 2025 is partial and omitted; 2016 is omitted because Amazon filed for one site." });
var cShare = card(s1, { id: "inj-share", files: ["injuries_peer_year"], orig: "Original sources: OSHA ITA Form 300A, CY2024; BLS SOII NAICS 493110 (the reference rate for the year).",
  cav: "Share of sites whose own rate exceeds the BLS 493110 rate for the year." });
var SINGLES = ["walmart", "target", "costco", "ups", "fedex_express"];
function renderInj() {
  var m = meas, M = MEAS[m].name, bls = P24.amazon["bls_493110_" + m];
  /* chart 1 */
  var peers = ["amazon", "ita_493110_ex_amazon", "walmart", "target", "group_3pl", "group_retailer_dcs", "costco", "ups", "fedex_express"].filter(function (p) { return P24[p] && String(P24[p].headline_comparison_ok) === "True"; });
  var items = peers.map(function (p) { var r = P24[p]; return { key: p, label: NAME[p] || p, sub: A.fmt(r.n_valid) + " sites" + (String(r.supplementary) === "True" ? ", supplementary" : ""), value: r[m], cls: CLS[p] || "", tip: (r.peer_label || "") + "<br>" + A.fmt(r.n_valid) + " valid sites, CY2024" }; }).sort(function (a, b) { return b.value - a.value; });
  var higher = SINGLES.filter(function (p) { return P24[p][m] > P24.amazon[m]; }).map(function (p) { return NAME[p].replace(" supply-chain sites", "").replace(" DCs", ""); });
  cInj.title("Amazon's 2024 " + M + " rate is " + f1(P24.amazon[m]) + ", " + f2(P24.amazon[m] / P24.ita_493110_ex_amazon[m]) + " times other warehouse filers and " + f2(P24.amazon[m] / P24.walmart[m]) + " times Walmart DCs" + (higher.length ? "; higher: " + higher.join(", ") : ""));
  clear(cInj.body);
  key(cInj.body, [["amz", "Amazon"], ["bn", "Single company"], ["agg", "Group of sites"], ["ref", "BLS NAICS 493110 " + M + " rate (" + f1(bls) + ")"]]);
  hbar(cInj.body, items, { ref: bls });
  tv(cInj.body, [{ h: "Population", k: "label" }, { h: "Valid sites", k: "n", n: 1 }, { h: M + " rate", k: "v", n: 1 }, { h: "Share of sites above BLS", k: "s", n: 1 }], items.map(function (d) { var r = P24[d.key]; return { label: d.label, n: A.fmt(r.n_valid), v: f2(r[m]), s: pc(r[m + "_share_sites_above_bls"]) }; }));
  /* chart 2 */
  var YR = []; for (var y = 2017; y <= 2024; y++) YR.push(y);
  var PY = {}; T.injuries_peer_year.forEach(function (r) { if (r.scope === "headline") PY[r.peer + "|" + r.year] = r; });
  function pts(p) { return YR.map(function (y) { var r = PY[p + "|" + y]; return [y, r ? r[m] : null]; }); }
  var a17 = PY["amazon|2017"][m], a24 = PY["amazon|2024"][m], o17 = PY["ita_493110_ex_amazon|2017"][m], o24 = PY["ita_493110_ex_amazon|2024"][m];
  cLine.title("Amazon's " + M + " rate moved from " + f1(a17) + " in 2017 to " + f1(a24) + " in 2024; other warehouse filers moved from " + f1(o17) + " to " + f1(o24));
  clear(cLine.body);
  A.lineChart(cLine.body, { title: "Injury rate by year", height: 300, yMin: 0, yFmt: f1, series: [
    { name: "Amazon", color: "var(--amz)", points: pts("amazon") },
    { name: "Other NAICS 493110 filers", color: "var(--bench)", points: pts("ita_493110_ex_amazon") },
    { name: "Walmart DCs", color: "var(--cat3)", dash: "6 3", points: pts("walmart") },
    { name: "3PLs combined", color: "var(--cat6)", dash: "2 3", points: pts("group_3pl") }] });
  tv(cLine.body, [{ h: "Year", k: "y" }, { h: "Amazon", k: "a", n: 1 }, { h: "Other 493110 filers", k: "o", n: 1 }, { h: "Walmart DCs", k: "w", n: 1 }, { h: "3PLs combined", k: "t", n: 1 }], YR.map(function (y) { return { y: y, a: f2(PY["amazon|" + y][m]), o: f2(PY["ita_493110_ex_amazon|" + y][m]), w: f2(PY["walmart|" + y][m]), t: f2(PY["group_3pl|" + y][m]) }; }));
  /* chart 3 */
  var sp = ["amazon", "ita_493110_ex_amazon", "walmart", "group_3pl", "group_retailer_dcs", "ups"];
  var si = sp.map(function (p) { var r = P24[p]; return { label: NAME[p], sub: A.fmt(r.n_valid) + " sites", value: r[m + "_share_sites_above_bls"], cls: CLS[p] || "", tip: "Share of sites above the BLS " + M + " rate of " + f1(bls) }; }).sort(function (a, b) { return b.value - a.value; });
  cShare.title(pc(P24.amazon[m + "_share_sites_above_bls"]) + " of Amazon sites exceed the BLS warehousing " + M + " rate, against " + pc(P24.ita_493110_ex_amazon[m + "_share_sites_above_bls"]) + " of other filers and " + pc(P24.walmart[m + "_share_sites_above_bls"]) + " of Walmart sites");
  clear(cShare.body);
  hbar(cShare.body, si, { fmt: function (v) { return pc(v); }, max: 1 });
  tv(cShare.body, [{ h: "Population", k: "l" }, { h: "Sites", k: "n", n: 1 }, { h: "Share above BLS " + M + " (" + f1(bls) + ")", k: "s", n: 1 }], sp.map(function (p) { return { l: NAME[p], n: A.fmt(P24[p].n_valid), s: pc(P24[p][m + "_share_sites_above_bls"], 1) }; }));
}
A.$("#mseg").addEventListener("click", function (e) { var b = e.target.closest("button[data-m]"); if (!b) return; meas = b.getAttribute("data-m"); Array.prototype.forEach.call(A.$("#mseg").children, function (x) { x.setAttribute("aria-pressed", x === b); }); renderInj(); });
renderInj();

/* chart 4: percentile strip */
var D = {}; T.injuries_493110_distribution.filter(function (r) { return r.year === 2024 && r.measure === "trc"; }).forEach(function (r) { D[r.population] = r; });
var cDist = card(s1, { id: "inj-dist", files: ["injuries_493110_distribution"], orig: "Original sources: OSHA ITA Form 300A, CY2024, NAICS 493110 filers (Amazon removed by name rules), valid sites only; BLS SOII NAICS 493110.",
  title: "Half of other warehouse sites report a rate below " + f1(D.ita_493110_ex_amazon.p50) + ", but the top tenth are above " + f1(D.ita_493110_ex_amazon.p90) + " (2024 TRC)",
  cav: "Many small sites report zero cases (the 25th percentile is " + f1(D.ita_493110_ex_amazon.p25) + "); read hours-weighted rates, not medians. Amazon is shown on its 493110-coded sites only, so its hours-weighted rate differs from the 493 plus 492 figure above." });
(function () {
  var pops = [["ita_493110_ex_amazon", "Other NAICS 493110 filers", ""], ["ita_493110_amazon", "Amazon sites coded 493110", "amz"]].filter(function (p) { return D[p[0]]; });
  var mx = Math.ceil(Math.max.apply(null, pops.map(function (p) { return D[p[0]].p99; })) / 5) * 5;
  var sc = function (v) { return (100 * v / mx).toFixed(2) + "%"; };
  key(cDist.body, [["bn", "Band: 25th to 75th percentile"], ["dia", "Hours-weighted rate"], ["ref", "BLS 493110 rate (" + f1(D.ita_493110_ex_amazon.bls_493110_rate) + ")"]]);
  var h = '<div class="br strip hasref" style="--ref:' + sc(D.ita_493110_ex_amazon.bls_493110_rate) + '">';
  pops.forEach(function (p) {
    var d = D[p[0]];
    function m(cls, v, lab) { return '<span class="' + cls + '" style="left:' + sc(v) + '" data-t="' + esc("<b>" + p[1] + "</b><br>" + lab + ": " + f2(v)) + '"></span>'; }
    h += '<div class="r ' + p[2] + '"><div class="lb">' + esc(p[1]) + '<span class="sb">' + A.fmt(d.n_sites_valid) + ' sites</span></div><div class="trk"><span class="band" style="left:' + sc(d.p25) + ";width:" + (100 * (d.p75 - d.p25) / mx).toFixed(2) + '%"></span>' +
      m("tick", d.p50, "median") + m("p", d.p90, "90th percentile") + m("p", d.p99, "99th percentile") + m("hw", d.hours_weighted_rate, "hours-weighted rate") + "</div></div>";
  });
  A.mount(cDist.body, h + '</div><p class="cap">Scale 0 to ' + mx + " cases per 100 full-time workers. Vertical tick: median. Dots: 90th and 99th percentiles.</p>");
  tv(cDist.body, [{ h: "Population", k: "l" }, { h: "Sites", k: "n", n: 1 }, { h: "p25", k: "a", n: 1 }, { h: "p50", k: "b", n: 1 }, { h: "p75", k: "c", n: 1 }, { h: "p90", k: "d", n: 1 }, { h: "p99", k: "e", n: 1 }, { h: "Hours-weighted", k: "f", n: 1 }, { h: "Share above BLS", k: "g", n: 1 }],
    pops.map(function (p) { var d = D[p[0]]; return { l: p[1], n: A.fmt(d.n_sites_valid), a: f2(d.p25), b: f2(d.p50), c: f2(d.p75), d: f2(d.p90), e: f2(d.p99), f: f2(d.hours_weighted_rate), g: pc(d.share_sites_above_bls) }; }), "Table view (always the full numbers)");
})();

/* =================== 2. NETWORK AND FINANCE =================== */
var s2 = A.section(app, "network", "Network and finance (SEC 10-K filings)", "Company-wide figures from annual reports, matched to EDGAR. Revenue per employee and capital spending are not logistics measures: they cover each whole company.");
var CO = { amazon: "Amazon", costco: "Costco", homedepot: "Home Depot", walmart: "Walmart", target: "Target", ups: "UPS", fedex: "FedEx" };
var FYN = { walmart: "year ended Jan 2025", fedex: "year ended May 2025" };
var SLUGS = Object.keys(CO);
function netItems(metric, fmt) {
  return SLUGS.map(function (s) { var r = NET[s + "|" + metric]; return r && { slug: s, label: CO[s], sub: FYN[s] ? "FY " + r.fiscal_year_label + " (" + FYN[s] + ")" : "FY " + r.fiscal_year_label, value: r.value, cls: s === "amazon" ? "amz" : "", tip: r.basis + (r.note ? ". " + r.note : "") }; }).filter(Boolean).sort(function (a, b) { return b.value - a.value; });
}
function rank(items, s) { for (var i = 0; i < items.length; i++) if (items[i].slug === s) return i + 1; }
var ordn = ["", "first", "second", "third", "fourth", "fifth", "sixth", "seventh"];
var rpe = netItems("revenue_per_employee_usd_k"), cpx = netItems("capex_pct_revenue");
var cRpe = card(s2, { id: "fin-rpe", files: ["network_headline"], orig: "Original sources: company 10-K filings via SEC EDGAR (XBRL revenue; employee counts from the filings).",
  title: "Amazon's revenue per employee ($" + Math.round(NET["amazon|revenue_per_employee_usd_k"].value) + "k) ranks " + ordn[rank(rpe, "amazon")] + " of " + rpe.length + " companies, behind " + rpe.slice(0, rank(rpe, "amazon") - 1).map(function (d) { return d.label; }).join(", "),
  cav: "Company-wide revenue and headcount, including AWS and international for Amazon and Walmart. Walmart is the year ended Jan 2025; FedEx the year ended May 2025. Employee counts are approximate and may include part-time and seasonal staff." });
hbar(cRpe.body, rpe, { fmt: function (v) { return "$" + f1(v) + "k"; } });
tv(cRpe.body, [{ h: "Company", k: "l" }, { h: "Fiscal year", k: "y" }, { h: "Revenue per employee, USD thousand", k: "v", n: 1 }], rpe.map(function (d) { return { l: d.label, y: d.sub, v: f1(d.value) }; }));
var cCpx = card(s2, { id: "fin-capex", files: ["network_headline"], orig: "Original sources: company 10-K filings via SEC EDGAR (cash capital expenditure and revenue).",
  title: "Amazon spent " + f1(NET["amazon|capex_pct_revenue"].value) + "% of revenue on capital, " + f1(NET["amazon|capex_pct_revenue"].value / cpx[1].value) + " times the next company, but that includes AWS data centers",
  cav: "Amazon capital spending includes AWS data centers, so it is not a logistics figure. Revenue is company-wide." });
hbar(cCpx.body, cpx, { fmt: function (v) { return f2(v) + "%"; } });
tv(cCpx.body, [{ h: "Company", k: "l" }, { h: "Fiscal year", k: "y" }, { h: "Capex, % of revenue", k: "v", n: 1 }], cpx.map(function (d) { return { l: d.label, y: d.sub, v: f2(d.value) }; }));

/* chart 6: footprint table */
var FAC = T.network_facilities, DEF = T.network_definitions;
function lastFac(slug, metric, type, geo, ten) { var c = FAC.filter(function (r) { return r.slug === slug && r.metric === metric && r.facility_type === type && (geo == null || r.geography === geo) && (ten == null || r.tenure === ten); }); c.sort(function (a, b) { return b.fiscal_year_label - a.fiscal_year_label; }); return c[0]; }
function defOf(slug) { var r = first(DEF, function (d) { return d.company_slug === slug && /what counts as a DC/i.test(d.topic); }); return r ? r.definition_or_difference : ""; }
var amzSq = NET["amazon|network_sqft_thousand"];
var foot = [
  { co: "Amazon", cnt: null, sq: amzSq && { v: amzSq.value, fy: amzSq.fiscal_year_label, b: amzSq.basis, note: amzSq.note }, d: defOf("amazon"), src: null, amz: 1, cntNote: "Not disclosed" },
  { co: "Walmart", cnt: lastFac("walmart", "facility_count", "us_dc_total", "US"), sq: null, d: defOf("walmart"), cntNote: "", sqNote: "Not disclosed" },
  { co: "Target", cnt: lastFac("target", "facility_count", "supply_chain_facility", "US", "all"), sq: lastFac("target", "sqft_thousand", "supply_chain_facility", "US", "all"), d: defOf("target") },
  { co: "Home Depot", cnt: lastFac("homedepot", "facility_count", "distribution_fulfillment_center_and_warehouse"), sq: lastFac("homedepot", "sqft_thousand", "distribution_fulfillment_center_and_warehouse"), d: defOf("homedepot") },
  { co: "UPS (US package facilities)", cnt: lastFac("ups", "facility_count", "us_package_operating_facilities", "US"), sq: lastFac("ups", "sqft_thousand", "us_package_operating_facilities", "US"), d: defOf("ups") },
  { co: "FedEx (US operating facilities)", cnt: lastFac("fedex", "facility_count", "federal_express_us_operating_facilities", "US"), sq: null, d: defOf("fedex"), sqNote: "No total disclosed" },
  { co: "Costco (distribution and logistics)", cnt: null, sq: lastFac("costco", "sqft_thousand", "distribution_and_logistics_facilities", "Worldwide"), d: defOf("costco"), cntNote: "Depot count stopped after FY2019" }
];
function basisTxt(b) { return ({ reported: "reported", reported_approx: "approximate", reported_lower_bound: "lower bound", reported_rounded: "rounded" })[b] || b || ""; }
var cFoot = card(s2, { id: "fin-foot", files: ["network_facilities", "network_headline", "network_definitions"], orig: "Original sources: company 10-K filings, Item 2 Properties (EDGAR). Item 2 figures were script-parsed; facility and area counts for Target, Home Depot, UPS, Costco and Walmart were checked by the reviewer.",
  title: "Network footprint as each company discloses it",
  cav: "Each company defines its network differently, so counts are not comparable and the table is not ranked. Revenue per square foot is not shown because the denominators are not comparable." });
A.mount(cFoot.body, '<div class="twrap full"><table class="btab"><thead><tr><th>Company</th><th class="n">Facilities</th><th class="n">Million sq ft</th><th>Fiscal year</th><th>What the company counts</th></tr></thead><tbody>' +
  foot.map(function (r) {
    var cnt = r.cnt ? A.fmt(r.cnt.value) + (r.cnt.basis !== "reported" ? " (" + basisTxt(r.cnt.basis) + ")" : "") : (r.cntNote || "n/a");
    var sqv = r.sq ? f1((r.sq.v != null ? r.sq.v : r.sq.value) / 1000) + ((r.sq.b || r.sq.basis) !== "reported" ? " (" + basisTxt(r.sq.b || r.sq.basis) + ")" : "") : (r.sqNote || "n/a");
    var fy = [r.cnt && r.cnt.fiscal_year_label, r.sq && (r.sq.fy || r.sq.fiscal_year_label)].filter(function (x, i, a) { return x != null && a.indexOf(x) === i; }).join(" / ");
    var def = (r.sq && r.sq.note && r.amz ? r.sq.note + ". " : "") + r.d;
    return '<tr class="' + (r.amz ? "amz" : "") + '"><td>' + esc(r.co) + '</td><td class="n">' + esc(cnt) + '</td><td class="n">' + esc(sqv) + "</td><td>" + esc(fy) + '</td><td class="def">' + esc(def.length > 330 ? def.slice(0, 330).replace(/\s\S*$/, "") + " ..." : def) + "</td></tr>";
  }).join("") + "</tbody></table></div>");

/* =================== 3. LABOR =================== */
var s3 = A.section(app, "labor", "Labor: pay and NLRB activity", "Pay is shown against the industry average; labor conflict is shown as rank order of case counts, not as a measure of working conditions.");
var AV = T.labor_announced_vs_qcew493;
var pay = [], byco = A.by(AV, function (r) { return r.company; });
Object.keys(byco).forEach(function (co) {
  var rows = byco[co].filter(function (r) { return !/PRIOR/.test(r.metric); }), best = rows.map(function (r) { return r.announce_date; }).sort().pop();
  var last = rows.filter(function (r) { return r.announce_date === best; });
  var pref = last.filter(function (r) { return /^(yes|partly)/.test(r.warehouse_dc_specific || ""); });
  (pref.length ? pref : last).forEach(function (r) { pay.push(r); });
});
pay.sort(function (a, b) { return (b.announced_low_as_pct_of_qcew_493) - (a.announced_low_as_pct_of_qcew_493); });
var amzPay = pay.filter(function (r) { return r.company === "Amazon"; }).sort(function (a, b) { return a.announced_low_as_pct_of_qcew_493 - b.announced_low_as_pct_of_qcew_493; });
var cPay = card(s3, { id: "lab-pay", files: ["labor_announced_vs_qcew493", "labor_announced_wages"], orig: "Original sources: company and news announcements (URLs in the wages file), BLS QCEW NAICS 493 annual average weekly wage converted to a 40-hour hourly equivalent.",
  title: "Amazon's announced average pay is " + f1(amzPay[0].announced_low_as_pct_of_qcew_493) + "% of the industry average wage (total compensation, " + f1(amzPay[amzPay.length - 1].announced_low_as_pct_of_qcew_493) + "%)",
  cav: "Announced starting or average wages compared with the QCEW industry average (which includes Amazon). Not like-for-like. Several peer figures come from news reports. Latest announcement per company; warehouse or distribution-specific rows preferred where the file marks them. Prior-contract and driver pay rows are not shown." });
(function () {
  var hi = Math.max.apply(null, pay.map(function (r) { return r.announced_high_as_pct_of_qcew_493 || r.announced_low_as_pct_of_qcew_493; })), mx = Math.ceil(hi * 1.1 / 20) * 20, sc = function (v) { return (100 * v / mx).toFixed(2) + "%"; };
  key(cPay.body, [["amz", "Amazon"], ["bn", "Peer"], ["ref", "100% = QCEW NAICS 493 average (40-hour equivalent)"]]);
  var h = '<div class="br hasref" style="--ref:' + sc(100) + '">';
  pay.forEach(function (r) {
    var lo = r.announced_low_as_pct_of_qcew_493, hh = r.announced_high_as_pct_of_qcew_493, usd = "$" + f2(r.announced_usd_hr_low) + (r.announced_usd_hr_high ? " to $" + f2(r.announced_usd_hr_high) : "");
    var lab = r.company + " (" + (/^\d{4}/.test(r.announce_date) ? r.announce_date.slice(0, 4) : "2026 page") + ")";
    var t = esc("<b>" + lab + "</b><br>" + r.metric + "<br>" + usd + " an hour<br>" + f1(lo) + "%" + (hh ? " to " + f1(hh) + "%" : "") + " of QCEW 493 (" + r.qcew_year + ": $" + f2(r.qcew_493_hourly_equiv_40h) + ")<br>Warehouse or DC specific: " + r.warehouse_dc_specific);
    h += '<div class="r ' + (r.company === "Amazon" ? "amz" : "") + '"><div class="lb">' + esc(lab) + '<span class="sb">' + esc(r.metric.length > 60 ? r.metric.slice(0, 58) + "..." : r.metric) + '</span></div><div class="trk">' +
      (hh ? '<span class="rg" style="left:' + sc(lo) + ";width:" + (100 * (hh - lo) / mx).toFixed(2) + '%"></span><span class="dot" style="left:' + sc(lo) + '"></span><span class="dot hi" style="left:' + sc(hh) + '"></span>' : '<span class="dot" style="left:' + sc(lo) + '"></span>') +
      '<span class="v" style="left:calc(' + sc(hh || lo) + ' + 12px)">' + f1(lo) + "%" + (hh ? " to " + f1(hh) + "%" : "") + '</span><span class="hit" tabindex="0" data-t="' + t + '"></span></div></div>';
  });
  A.mount(cPay.body, h + "</div>");
  tv(cPay.body, [{ h: "Company", k: "c" }, { h: "Announced", k: "d" }, { h: "Measure", k: "m" }, { h: "USD an hour", k: "u", n: 1 }, { h: "% of QCEW 493 (low)", k: "l", n: 1 }, { h: "% of QCEW 493 (high)", k: "h", n: 1 }, { h: "Warehouse or DC specific", k: "w" }],
    pay.map(function (r) { return { c: r.company, d: r.announce_date.slice(0, 10), m: r.metric, u: f2(r.announced_usd_hr_low) + (r.announced_usd_hr_high ? " to " + f2(r.announced_usd_hr_high) : ""), l: f1(r.announced_low_as_pct_of_qcew_493), h: f1(r.announced_high_as_pct_of_qcew_493), w: r.warehouse_dc_specific }; }));
})();
/* OEWS premium */
var OE = T.industry_oews_premium.filter(function (r) { return r.year === 2025 && (r.occ_code === "53-7062" || r.occ_code === "53-7065"); });
var cOe = card(s3, { id: "lab-oews", files: ["industry_oews_premium"], orig: "Original source: BLS Occupational Employment and Wage Statistics, May 2025, national, mean hourly wage.",
  title: "For the same jobs, warehousing pays " + OE.map(function (r) { return Math.round((r.warehousing_over_all_ratio - 1) * 100) + "% more (" + r.occupation.split(",")[0].toLowerCase() + ")"; }).join(" and ") + " than private industry as a whole",
  cav: "Mean hourly wage of two warehouse occupations in warehousing (NAICS 493, all employers including Amazon) against the same occupation across private industry. Not specific to Amazon." });
(function () {
  var items = []; OE.forEach(function (r) {
    var nm = r.occupation.split(",")[0];
    items.push({ label: nm, sub: "Warehousing (NAICS 493)", value: r.warehousing_493_mean_hourly_usd, cls: "", tip: r.occ_code });
    items.push({ label: nm, sub: "All private industry", value: r.all_industries_private_mean_hourly_usd, cls: "alt", tip: r.occ_code });
  });
  key(cOe.body, [["bn", "Warehousing (NAICS 493)"], ["agg", "All private industry"]]);
  hbar(cOe.body, items, { fmt: function (v) { return "$" + f2(v); } });
  tv(cOe.body, [{ h: "Occupation (code)", k: "o" }, { h: "Warehousing, USD an hour", k: "w", n: 1 }, { h: "All private industry", k: "a", n: 1 }, { h: "Ratio", k: "r", n: 1 }], OE.map(function (r) { return { o: r.occupation + " (" + r.occ_code + ")", w: f2(r.warehousing_493_mean_hourly_usd), a: f2(r.all_industries_private_mean_hourly_usd), r: f2(r.warehousing_over_all_ratio) }; }));
})();
/* NLRB */
var NL = T.labor_nlrb_counts_by_year.filter(function (r) { return r.year_filed === 2024; });
var byCA = NL.slice().sort(function (a, b) { return b.ca_ulp_charges_vs_employer - a.ca_ulp_charges_vs_employer; });
var byRate = NL.filter(function (r) { return r.ca_per_10k_employees != null; }).sort(function (a, b) { return b.ca_per_10k_employees - a.ca_per_10k_employees; });
var cNl = card(s3, { id: "lab-nlrb", files: ["labor_nlrb_counts_by_year"], orig: "Original sources: NLRB case search (nlrb.gov/search/case), cases filed in 2024, charge type CA (unfair labor practice against an employer); headcount from company 10-K filings.",
  title: byCA[0].company + " drew the most unfair labor practice charges filed in 2024 (" + byCA[0].ca_ulp_charges_vs_employer + "), then " + byCA[1].company + " (" + byCA[1].ca_ulp_charges_vs_employer + "); per 10,000 employees the order is " + byRate.slice(0, 3).map(function (r) { return r.company + " " + f2(r.ca_per_10k_employees); }).join(", "),
  cav: "Cases matched by company name only; subsidiaries are missed. Rates use worldwide 10-K headcount. UPS counts include charges against unions that name UPS. A count of filed charges is not a finding that a law was broken. FedEx shows cases only because no rate is in the file." });
(function () {
  A.mount(cNl.body, '<div class="two"><div><h4>Charges against the employer, filed 2024</h4><div id="nl1"></div></div><div><h4>Per 10,000 employees</h4><div id="nl2"></div></div></div>');
  hbar("#nl1", byCA.map(function (r) { return { label: r.company, value: r.ca_ulp_charges_vs_employer, cls: r.company === "Amazon" ? "amz" : "", tip: "Charges against employer (CA). All case types: " + r.all_cases }; }), { fmt: function (v) { return A.fmt(v); } });
  hbar("#nl2", NL.slice().sort(function (a, b) { return (b.ca_per_10k_employees == null ? -1 : b.ca_per_10k_employees) - (a.ca_per_10k_employees == null ? -1 : a.ca_per_10k_employees); }).map(function (r) { return { label: r.company, sub: r.employees_total_10k ? A.fmt(r.employees_total_10k) + " employees" : "no headcount in file", value: r.ca_per_10k_employees, text: r.ca_per_10k_employees == null ? "cases only (" + r.ca_ulp_charges_vs_employer + ")" : null, cls: r.company === "Amazon" ? "amz" : "", tip: r.ca_ulp_charges_vs_employer + " charges" }; }), { fmt: f2 });
  tv(cNl.body, [{ h: "Company", k: "c" }, { h: "CA charges against employer", k: "a", n: 1 }, { h: "Employees (10-K, worldwide)", k: "e", n: 1 }, { h: "CA per 10,000", k: "r", n: 1 }], byCA.map(function (r) { return { c: r.company, a: r.ca_ulp_charges_vs_employer, e: A.fmt(r.employees_total_10k), r: r.ca_per_10k_employees == null ? "" : f2(r.ca_per_10k_employees) }; }));
})();

/* =================== 4. ENVIRONMENT =================== */
var s4 = A.section(app, "environment", "Environment (company sustainability reports)", "Scope 1 and 2 are a company's own fuel and purchased electricity. Scope 3 (supply chain and product use) is defined differently by each company and is not compared.");
var INT = T.environment_intensity, latest = {};
INT.forEach(function (r) { if (/base/i.test(r.period)) return; var c = latest[r.company]; if (!c || yr(r.period) > yr(c.period)) latest[r.company] = r; });
var RET = ["Amazon", "Walmart", "Target", "Costco", "Home Depot"].filter(function (c) { return latest[c]; }), DEL = ["UPS", "FedEx"].filter(function (c) { return latest[c]; });
function envItem(c, group) { var r = latest[c]; var der = c === "Target"; return { label: c, sub: r.period + (der ? ", derived" : ""), value: r.s12_market_g_per_usd, cls: c === "Amazon" ? "amz" : "", group: group, tip: "Scope 1 + 2 market-based " + A.fmt(r.s12_market_t) + " t CO2e on revenue of $" + A.fmt(r.revenue_usd_m) + " million" + (der ? "<br>Derived from reported percent changes" : "") + (r.note ? "<br>" + String(r.note).slice(0, 200) : "") }; }
var envItems = RET.sort(function (a, b) { return latest[b].s12_market_g_per_usd - latest[a].s12_market_g_per_usd; }).map(function (c) { return envItem(c, "Retailers"); }).concat(DEL.sort(function (a, b) { return latest[b].s12_market_g_per_usd - latest[a].s12_market_g_per_usd; }).map(function (c) { return envItem(c, "Delivery operators"); }));
var amzE = latest.Amazon, upsE = latest.UPS;
var cEnv = card(s4, { id: "env-int", files: ["environment_intensity"], orig: "Original sources: company sustainability and ESG reports and GHG methodology pages (page references and URLs in the emissions file); revenue from SEC 10-K filings.",
  title: "Amazon emitted " + f1(amzE.s12_market_g_per_usd) + " g CO2e per dollar of revenue (Scope 1 and 2), " + (RET.indexOf("Amazon") === 0 ? "the highest" : "number " + (RET.indexOf("Amazon") + 1)) + " of " + RET.length + " retailers shown; UPS and FedEx are " + Math.round(latest.FedEx.s12_market_g_per_usd) + " to " + Math.round(latest.UPS.s12_market_g_per_usd) + " g",
  cav: "Scope 1 and 2 only, market-based, latest year each company reports. Scope 3 is not comparable across these companies and is not shown. Amazon includes AWS data centers in Scope 2. Walmart's private fleet is in Scope 1. UPS and FedEx are delivery operators, so they are not like-for-like with retailers. Target is derived from reported percent changes, not printed tonnes. Home Depot's reported intensity does not match its own tonnes for FY2023 and FY2024; the FY2025 figure is used." });
hbar(cEnv.body, envItems, { fmt: f1 });
tv(cEnv.body, [{ h: "Company", k: "c" }, { h: "Period", k: "p" }, { h: "g CO2e per $ revenue", k: "g", n: 1 }, { h: "Scope 1 + 2 market-based, tonnes", k: "t", n: 1 }, { h: "Revenue, USD million", k: "r", n: 1 }],
  envItems.map(function (d) { var r = latest[d.label]; return { c: d.label, p: r.period, g: f1(r.s12_market_g_per_usd), t: A.fmt(r.s12_market_t), r: A.fmt(r.revenue_usd_m) }; }));
/* Amazon trend, from the same file */
var amzTrend = INT.filter(function (r) { return r.company === "Amazon" && r.period !== "CY2019"; });
A.mount(cEnv.body, '<p class="cap">Amazon over time (same basis): ' + amzTrend.map(function (r) { return r.period + " " + f1(r.s12_market_g_per_usd); }).join(", ") + " g per dollar. Absolute Scope 1 and 2 in " + amzE.period + ": " + f1(amzE.s12_market_t / 1e6) + " million tonnes.</p>");

/* chart 12: clean energy and fleet */
var RF = T.environment_renewables_fleet.filter(function (r) { return r.category === "renewable_share" || r.category === "ev_fleet"; });
var latestRF = {};
RF.forEach(function (r) { var k = r.company + "|" + r.metric; var c = latestRF[k]; if (!c || yr(r.period) > yr(c.period)) latestRF[k] = r; });
var ORDER = ["Amazon", "Walmart", "Target", "Costco", "Home Depot", "UPS", "FedEx"];
var rfRows = Object.keys(latestRF).map(function (k) { return latestRF[k]; }).sort(function (a, b) { return ORDER.indexOf(a.company) - ORDER.indexOf(b.company) || (a.category < b.category ? -1 : a.category > b.category ? 1 : 0) || (a.metric < b.metric ? -1 : 1); });
var cRf = card(s4, { id: "env-clean", files: ["environment_renewables_fleet", "environment_boundaries"], orig: "Original sources: company sustainability reports (document, page and link in each row).",
  title: "Clean-energy shares and electric fleets, each on the company's own definition",
  cav: "Renewable shares use different definitions and are not ranked. The definition is shown beside every share. Amazon's rooftop solar capacity row is not used because it does not reconcile with its generation figure. Electric-van counts exist only for the companies listed." });
A.mount(cRf.body, '<div class="twrap full"><table class="btab"><thead><tr><th>Company</th><th>Period</th><th>Measure</th><th class="n">Value</th><th>Definition</th><th>Source</th></tr></thead><tbody>' +
  rfRows.map(function (r) {
    return '<tr class="' + (r.company === "Amazon" ? "amz" : "") + '"><td>' + esc(r.company) + "</td><td style=\"white-space:nowrap\">" + esc(r.period) + "</td><td>" + esc(String(r.metric).replace(/_/g, " ")) + '</td><td class="n">' + esc(r.value == null ? "n/a" : A.fmt(r.value, /\./.test(String(r.value)) ? 1 : 0) + (r.unit ? " " + r.unit : "")) + '</td><td class="def">' + esc(r.definition) + "</td><td>" +
      (/^https?:/.test(r.source_url || "") ? '<a href="' + esc(r.source_url) + '" target="_blank" rel="noopener">' + esc(r.source_doc) + "</a>" : esc(r.source_doc)) + (r.page_ref ? ", p. " + esc(r.page_ref) : "") + "</td></tr>";
  }).join("") + "</tbody></table></div>");
var BD = T.environment_boundaries;
A.mount(cRf.body, '<details class="tv"><summary>Reporting boundaries by company (' + BD.length + " statements)</summary><div class=\"twrap\"><table class=\"btab\"><thead><tr><th>Company</th><th>Topic</th><th>What the report says</th><th>Source</th></tr></thead><tbody>" +
  BD.map(function (r) { return "<tr><td>" + esc(r.company) + "</td><td>" + esc(r.topic) + '</td><td class="def">' + esc(r.statement) + "</td><td>" + (/^https?:/.test(r.source_url || "") ? '<a href="' + esc(r.source_url) + '" target="_blank" rel="noopener">' + esc(r.source_doc) + "</a>" : esc(r.source_doc)) + (r.page_ref ? ", p. " + esc(r.page_ref) : "") + "</td></tr>"; }).join("") + "</tbody></table></div></details>");

/* =================== 5. INDUSTRY BASELINE =================== */
var s5 = A.section(app, "industry", "Industry baseline: Amazon in warehousing employment", "Amazon's share of the warehousing and storage industry (NAICS 493) is an estimate built from its OSHA-reported average employees and the BLS Quarterly Census of Employment and Wages (QCEW).");
A.estimate(s5, "These shares are estimates, not strict bounds: the numerator may include sites that QCEW does not code to NAICS 493, and early OSHA coverage is low. Temp-agency workers (NAICS 5613) are excluded throughout.");
var SHU = T.industry_amazon_share_493.filter(function (r) { return r.share_usable === "yes"; });
var s17 = SHU[0], sLast = SHU[SHU.length - 1];
var cSh = card(s5, { id: "ind-share", files: ["industry_amazon_share_493"], orig: "Original sources: OSHA ITA Form 300A average employees (Amazon sites); BLS QCEW private employment, NAICS 493 and 492 (data.bls.gov/cew).",
  title: "Amazon's estimated share of NAICS 493 employment rose from " + f1(s17.amazon_share_of_qcew_493_pct_estimate) + "% in " + s17.year + " to " + f1(sLast.amazon_share_of_qcew_493_pct_estimate) + "% in " + sLast.year + " (estimate)",
  cav: "Sum of Amazon's OSHA-reported average employees against QCEW employment. Not a strict bound; 2019 and 2020 are omitted because the filing coding changed, and the line breaks there. 2017 and 2018 are understated by low early filing." });
(function () {
  var ys = []; for (var y = 2017; y <= sLast.year; y++) ys.push(y);
  var use = {}; SHU.forEach(function (r) { use[r.year] = r; });
  A.lineChart(cSh.body, { title: "Amazon share of warehousing employment (estimate)", height: 300, yMin: 0, yFmt: function (v) { return v.toFixed(0) + "%"; }, series: [
    { name: "Amazon 493110 filers over QCEW NAICS 493 (estimate)", color: "var(--amz)", points: ys.map(function (y) { return [y, use[y] ? use[y].amazon_share_of_qcew_493_pct_estimate : null]; }) },
    { name: "Amazon 493110 plus 492110 over QCEW 493 plus 492 (estimate)", color: "var(--bench)", dash: "6 3", points: ys.map(function (y) { return [y, use[y] ? use[y].amazon_493110_plus_492110_share_of_qcew_493_plus_492_pct_estimate : null]; }) }] });
  tv(cSh.body, [{ h: "Year", k: "y" }, { h: "Amazon share of 493 (estimate, %)", k: "a", n: 1 }, { h: "Combined 493+492 share (estimate, %)", k: "b", n: 1 }, { h: "QCEW 493 private employment", k: "q", n: 1 }, { h: "Amazon ITA avg employees, 493110", k: "e", n: 1 }],
    SHU.map(function (r) { return { y: r.year, a: f1(r.amazon_share_of_qcew_493_pct_estimate), b: f1(r.amazon_493110_plus_492110_share_of_qcew_493_plus_492_pct_estimate), q: A.fmt(r.qcew_493_private_employment), e: A.fmt(r.amazon_ita_avg_employees_493110) }; }));
})();
var SZ = T.industry_amazon_vs_qcew_size.filter(function (r) { return r.year === 2025 && r.usable === "yes"; });
var big = first(SZ, function (r) { return /^1000/.test(r.establishment_size_class_employees); });
var cSz = card(s5, { id: "ind-size", files: ["industry_amazon_vs_qcew_size"], orig: "Original sources: OSHA ITA Form 300A (Amazon sites with 493110 codes, by average employees); BLS QCEW establishments by size class, Q1 2025, private NAICS 493.",
  title: "In 2025 Amazon holds an estimated " + f1(big.amazon_share_of_qcew_establishments_pct) + "% of NAICS 493 establishments with 1,000 or more employees and " + f1(big.amazon_share_of_qcew_employment_pct) + "% of their employment (estimate)",
  cav: "Sum of Amazon's OSHA-reported average employees against QCEW employment. Not a strict bound; 2019 and 2020 are omitted because the filing coding changed. Size classes are by establishment employment." });
(function () {
  key(cSz.body, [["amz", "Amazon share of QCEW 493 establishments with 1,000 or more employees, 2025"]]);
  hbar(cSz.body, [
    { label: "Establishments", sub: A.fmt(big.amazon_ita_493110_establishments) + " Amazon of " + A.fmt(big.qcew_493_private_establishments_q1) + " in QCEW", value: big.amazon_share_of_qcew_establishments_pct, cls: "amz", tip: "Estimate" },
    { label: "Employment", sub: A.fmt(big.amazon_ita_493110_employees) + " Amazon employees", value: big.amazon_share_of_qcew_employment_pct, cls: "amz", tip: "Estimate" }], { fmt: function (v) { return f1(v) + "%"; }, max: 100 });
  tv(cSz.body, [{ h: "Size class (employees)", k: "c" }, { h: "QCEW 493 establishments", k: "q", n: 1 }, { h: "Amazon establishments", k: "a", n: 1 }, { h: "Amazon share of establishments (est., %)", k: "s", n: 1 }, { h: "Amazon share of employment (est., %)", k: "e", n: 1 }],
    SZ.map(function (r) { return { c: r.establishment_size_class_employees, q: A.fmt(r.qcew_493_private_establishments_q1), a: A.fmt(r.amazon_ita_493110_establishments), s: f1(r.amazon_share_of_qcew_establishments_pct), e: f1(r.amazon_share_of_qcew_employment_pct) }; }), "Table view (all size classes, 2025)");
})();

A.mount(app, '<p class="footcav">Figures come from OSHA, BLS, NLRB, SEC filings and company sustainability reports. Companies report on different bases; the note under each chart gives the main limit. Full method and files are in <span class="mono">data/notes/benchmark_findings.md</span> and the <span class="mono">bench_*.md</span> notes, and on the <a href="methods.html#m-bench">Methods</a> page.</p>');
})();
