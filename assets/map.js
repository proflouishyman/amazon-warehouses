/* map.html: Leaflet map of the roster with a year slider and a pullback layer.
   Data: AMZ_FAC.facilities (assets/data_facilities.js: year_used, year_basis, year_source, year_flag, mwpvl_*, pullback_*),
   AMZ_PULL.sites (data_pullback.js), AMZ_MWPVL.snapshots (data_mwpvl.js), AMZ_LOG.timeline / sqft / fc_counts_early / trade_press / epi_openings (data_logistics.js). */
(function () {
"use strict";
var A = AMZ, FA = AMZ_FAC, LG = AMZ_LOG, PU = window.AMZ_PULL || { sites: { cols: [], rows: [] }, aggregates: { cols: [], rows: [] } }, MW = window.AMZ_MWPVL || { snapshots: { cols: [], rows: [] } };
A.page({ title: "Map of Amazon US logistics sites", sub: "Every located site in the roster, colored by type, with a year slider from 1997 to 2026. Each site is dated by the best available basis (MWPVL opening year first, then EPI or MWPVL 2012, then a press or database event year, then first OSHA filing); the basis is in every popup. A pullback layer marks sites reported closed, delayed, subleased or dropped from the MWPVL list." });
var app = A.$("#app");

var TYPES = [
  ["fulfillment_center", "Fulfillment center", "var(--t1)"],
  ["delivery_station", "Delivery station", "var(--t2)"],
  ["sort_center", "Sort center", "var(--t3)"],
  ["other_logistics", "Other logistics", "var(--t4)"],
  ["air_hub", "Air hub", "var(--t5)"]
];
var TLAB = {}; TYPES.forEach(function (t) { TLAB[t[0]] = t[1]; });
var Y0 = 1997, Y1 = 2026;
var BASIS = {
  mwpvl_opening_year: ["MWPVL opening year", "mwpvl_opening_year (MWPVL table read from Wayback Machine snapshots; the most common year where captures disagree)"],
  epi_mwpvl2012_opening_year: ["EPI / MWPVL 2012 opening year", "epi_mwpvl2012_opening_year (EPI appendix or MWPVL April 2012 table)"],
  press_event_year: ["Press or database event year", "press_event_year (opening year stated in a news or database item; exact or probable match to the site)"],
  first_osha_filing: ["First OSHA filing (operating by)", "first_osha_filing (an upper bound on the opening date: the site was operating by then)"]
};
var BKEYS = Object.keys(BASIS);
var FLAGTXT = {
  mwpvl_year_conflict: "MWPVL captures disagree on the year; the most common value is used",
  mwpvl_later_year_after_planned: "MWPVL first listed the site as planned, then moved its year later",
  mwpvl_projection_not_used: "MWPVL year was a projection for a planned site; not used",
  year_after_first_osha_filing: "MWPVL year is later than the site's first OSHA filing",
  press_year_well_before_first_osha_filing: "press year is 3 or more years before the first OSHA filing; probably an announcement date"
};
var PBG = { closed: "closed", closed_temporary: "closed", closed_partial: "closed", cancelled: "cancelled", delayed: "delayed", paused: "delayed", sublease: "sublease", removed_from_mwpvl_list: "removed" };
var PBL = { closed: ["Closed (incl. temporary, partial)", "x"], delayed: ["Delayed or paused", "!"], sublease: ["Sublease", "S"], removed: ["Dropped from MWPVL list (not a confirmed closure)", "-"], cancelled: ["Cancelled", "c"] };
function yearOf(d) { var m = /^(\d{4})/.exec(String(d || "")); return m ? +m[1] : null; }
var TP = A.rows(LG.trade_press).filter(function (r) { return r.lat != null && r.lat !== ""; });
var TPALL = A.rows(LG.trade_press);
var EPI = A.rows(LG.epi_openings);
var EPIC = {};
EPI.forEach(function (r) { var k = r.state_abbr + '|' + r.county; (EPIC[k] = EPIC[k] || { state: r.state, county: r.county, lat: +r.lat, lon: +r.lon, years: [] }).years.push(r.open_year); });
var EPIK = Object.keys(EPIC).map(function (k) { return EPIC[k]; });

/* ---------- roster rows with the year each site first appears ---------- */
var all = A.rows(FA.facilities);
all.forEach(function (r) {
  r.located = r.lat != null && r.lat !== "" && r.lon != null && r.lon !== "";
  r.approx = r.geo_method === "zip_centroid_census_zcta2020";
  r.yb = r.year_basis || "";
  r.ay = r.year_used != null && r.year_used !== "" && BASIS[r.yb] ? +r.year_used : Y1;
  r.ab = BASIS[r.yb] ? BASIS[r.yb][1] : "undated (no opening year, event year or OSHA filing; shown in the last year)";
  r.abShort = BASIS[r.yb] ? BASIS[r.yb][0] : "Undated";
  r.flags = r.year_flag ? String(r.year_flag).split(";") : [];
  r.pbg = r.pullback_status ? PBG[r.pullback_status] || null : null;
  r.pby = yearOf(r.pullback_date);
  if (r.ay < Y0) r.ay = Y0;
});
var located = all.filter(function (r) { return r.located; });
var nUnloc = all.length - located.length;
var nBasis = {}; all.forEach(function (r) { var k = r.yb || "undated"; nBasis[k] = (nBasis[k] || 0) + 1; });
var nBasisLoc = {}; located.forEach(function (r) { var k = r.yb || "undated"; nBasisLoc[k] = (nBasisLoc[k] || 0) + 1; });
function yrange(k) { var v = all.filter(function (r) { return r.yb === k; }).map(function (r) { return r.ay; }); return v.length ? Math.min.apply(null, v) + " to " + Math.max.apply(null, v) : "none"; }
var nFlag = {}; Object.keys(FLAGTXT).forEach(function (k) { nFlag[k] = all.filter(function (r) { return r.flags.indexOf(k) >= 0; }).length; });
var nMw = nBasis.mwpvl_opening_year || 0;
var pbAll = all.filter(function (r) { return r.pbg; }), pbLoc = pbAll.filter(function (r) { return r.located; });
var pbCnt = {}; pbAll.forEach(function (r) { pbCnt[r.pbg] = (pbCnt[r.pbg] || 0) + 1; });
var pbRows = A.rows(PU.sites), pbUnmatched = pbRows.filter(function (r) { return !r.site_code; }), pbCancelled = pbRows.filter(function (r) { return r.status === "cancelled"; });
var snapRows = A.rows(MW.snapshots), snapFirst = snapRows.length ? snapRows[0].snapshot_date : "", snapLast = snapRows.length ? snapRows[snapRows.length - 1].snapshot_date : "";
var nApprox = located.filter(function (r) { return r.approx; }).length;

/* ---------- headline ---------- */
A.tiles(app, [
  { value: A.fmt(located.length), label: "sites shown on the map", context: A.fmt(nUnloc) + " roster sites have no coordinates and are not drawn" },
  { value: A.fmt(nMw), label: "sites dated by an MWPVL opening year", context: "MWPVL International (Marc Wulfraat) table, " + A.fmt(snapRows.length) + " Wayback Machine captures " + snapFirst + " to " + snapLast + "; years " + yrange("mwpvl_opening_year") + ". Another " + A.fmt((nBasis.epi_mwpvl2012_opening_year || 0) + (nBasis.press_event_year || 0)) + " are dated by EPI/MWPVL 2012 or a press event year, and " + A.fmt(nBasis.first_osha_filing || 0) + " by first OSHA filing (an upper bound)" },
  { value: A.fmt(pbAll.length), label: "roster sites with a pullback status", context: A.fmt(pbCnt.removed || 0) + " dropped from MWPVL's list, " + A.fmt(pbCnt.delayed || 0) + " delayed or paused, " + A.fmt(pbCnt.closed || 0) + " closed, " + A.fmt(pbCnt.sublease || 0) + " sublease. " + A.fmt(pbUnmatched.length) + " of " + A.fmt(pbRows.length) + " pullback rows have no site code and cannot be placed" },
  { value: A.fmt(nApprox), label: "sites placed only at a ZIP centroid", context: "drawn as dashed hollow circles; true position can be miles off" }
]);
A.caveat(app, "<b>How to read the year slider.</b><ul>" +
  "<li>Each site appears in one year, chosen by a fixed order of evidence (the <b>year basis</b>): (1) its <b>MWPVL opening year</b> (" + A.fmt(nMw) + " sites, " + yrange("mwpvl_opening_year") + "), read from archived copies of MWPVL's Amazon table; where captures disagree the most common year is used; else (2) the <b>EPI or MWPVL 2012 opening year</b> (" + (nBasis.epi_mwpvl2012_opening_year || 0) + " sites); else (3) a <b>press or database event year</b>, an opening date stated in an item matched exactly or probably to the site (" + (nBasis.press_event_year || 0) + " sites, reported, not verified against Amazon); else (4) the <b>first OSHA filing</b> year (" + A.fmt(nBasis.first_osha_filing || 0) + " sites, " + yrange("first_osha_filing") + "). The fourth basis means the site was <i>operating by</i> that year, so it is an upper bound on the opening date. " + (nBasis.undated || 0) + " sites have no evidence and appear in " + Y1 + ".</li>" +
  "<li>Flags on the MWPVL years (shown in the popup): " + A.fmt(nFlag.mwpvl_year_conflict) + " sites where captures disagree on the year; " + A.fmt(nFlag.mwpvl_later_year_after_planned) + " where MWPVL moved the year later after first listing the site as planned; " + A.fmt(nFlag.mwpvl_projection_not_used) + " where the MWPVL year was only a projection and is not used; and " + A.fmt(nFlag.year_after_first_osha_filing) + " where the MWPVL year is later than a filing the site had already made (the MWPVL year is still used, as the order says).</li>" +
  "<li>The map shows when the roster first has evidence of a site, <b>not</b> always when it opened. MWPVL's table lists planned sites as well as open ones, and its years are its own compilation, not an Amazon record.</li>" +
  "<li><b>Pullback layer.</b> A badge marks a site when its first pullback date is on or before the slider year: " + PBL.closed[0].toLowerCase() + ", " + PBL.delayed[0].toLowerCase() + ", sublease, or dropped from MWPVL's list. The strongest status wins when a site has several (closed first, dropped-from-list last); the popup lists all of them. <b>Dropped from the list is not proof of a closure</b>: the site may have been merged, renamed or re-coded. Sites never disappear from the map, because closing dates are mostly unknown. Cancelled projects (" + A.fmt(pbCancelled.length) + " rows) have no roster site and appear in the table below the map, not on it.</li>" +
  "<li>Form 300A electronic filing has covered warehousing establishments with 20 or more employees since the 2016 data year, so the growth in filers after 2016 reflects network growth and improving compliance (2016 data were collected late and compliance was low in the first years), not rule changes.</li></ul>");

/* ---------- controls: one row above the map ---------- */
var sec = A.section(app, "mapsec", "Network by year");
A.mount(sec,
  '<div class="yearrow"><label for="yr" class="muted">Year</label><output id="yrout" for="yr" aria-live="polite">' + Y1 + '</output>' +
  '<input id="yr" type="range" min="' + Y0 + '" max="' + Y1 + '" step="1" value="' + Y1 + '" aria-label="Year to show">' +
  '<button class="btn ghost" id="play" type="button">Play</button></div>' +
  '<div class="mapfilters" id="tf">' + TYPES.map(function (t) {
    return '<label><input type="checkbox" data-t="' + t[0] + '" checked><i class="sw" style="background:' + t[2] + '"></i>' + A.esc(t[1]) + ' <span class="lcount" id="lc-' + t[0] + '"></span></label>';
  }).join("") + '</div>' +
  '<div class="basisleg" id="bl" aria-label="Legend: year basis"><b>Year basis</b> (1 to 4 = order of preference for each site\'s year; counts follow the slider and filters): ' +
  BKEYS.map(function (k, i) { return '<span class="bchip"><i class="bdot">' + (i + 1) + '</i>' + A.esc(BASIS[k][0]) + ' <span class="lcount" id="bc-' + k + '"></span></span>'; }).join("") +
  '<span class="bchip"><i class="bdot">-</i>Undated <span class="lcount" id="bc-undated"></span></span></div>' +
  '<div class="basisleg" id="pbl" aria-label="Legend: pullback layer"><label class="bchip"><input type="checkbox" id="fpb" checked><b>Pullback layer</b></label> (' + A.fmt(pbLoc.length) + ' of ' + A.fmt(pbAll.length) + ' roster sites with a status are located): ' +
  ["closed", "delayed", "sublease", "removed"].map(function (k) { return '<span class="bchip"><i class="pb pb-' + k + '">' + PBL[k][1] + '</i>' + A.esc(PBL[k][0]) + ' <span class="lcount" id="pc-' + k + '"></span></span>'; }).join("") + '</div>' +
  '<div class="mapfilters">' +
  '<label><input type="checkbox" id="fapprox" checked><i class="sw hollow"></i>Include ZIP-centroid locations (' + nApprox + ', approximate)</label>' +
  '<label><input type="checkbox" id="f25"> Only sites in the 2025 OSHA filing</label>' +
  '<label><input type="checkbox" id="fepi" checked><i class="sw epi"></i>Early openings layer, 1997 to 2017 (EPI, county level; ' + EPI.length + ' fulfillment centers)</label>' +
  '<label><input type="checkbox" id="ftp"><span class="tpkey"><i class="tp high"></i><i class="tp medium"></i><i class="tp low approx"></i></span>Trade-press openings layer (' + TP.length + ' of ' + TPALL.length + ' reported rows located; shape: solid = high, half = medium, hollow = low confidence; dashed outline = approximate city or county centroid)</label></div>' +
  '<div class="muted" style="font-size:12px;margin:-4px 0 6px">The trade-press layer is a list of what articles reported, not a complete or verified set, and is not filtered by the slider (the opening date is in each popup).</div>' +
  '<div id="amap" role="application" aria-label="Map of Amazon sites. A table of the same sites follows below the map."></div>' +
  '<div class="readout" id="readout" aria-live="polite"></div>');

/* ---------- Leaflet (CDN may fail; the table and chart still work) ---------- */
var map = null, layer = null, markers = [], epiLayer = null, epiMarkers = [], tpLayer = null, tpMarkers = [], pbLayer = null, pbMarkers = [];
var hasL = typeof window.L !== "undefined";
function css(v) { return getComputedStyle(document.documentElement).getPropertyValue(v).trim() || "#888"; }
function tcolor(type) { for (var i = 0; i < TYPES.length; i++) if (TYPES[i][0] === type) return css(TYPES[i][2].replace(/var\(|\)/g, "")); return "#888"; }
function restyle(m) {
  var r = m._r, c = tcolor(r.facility_type), ring = css("--surface");
  m.setStyle(r.approx ? { color: c, weight: 1.6, dashArray: "3 2", fillColor: c, fillOpacity: .18, opacity: .95 } : { color: ring, weight: 1.2, fillColor: c, fillOpacity: .85, opacity: 1 });
}
function link(u) { return String(u || "").split(/\s*;\s*/).filter(function (x) { return /^https?:/.test(x); }); }
function popup(r) {
  var flags = r.flags.map(function (k) { return FLAGTXT[k] || k; }).join("; ");
  var pb = r.pullback_status ? String(r.pullback_status).replace(/_/g, " ") + (r.pullback_date ? " (" + r.pullback_date + ")" : "") : "none";
  var hist = r.pullback_history && String(r.pullback_history) !== String(r.pullback_status + " " + r.pullback_date) ? String(r.pullback_history).replace(/_/g, " ") : "";
  var rows = [
    ["Type", TLAB[r.facility_type] || r.facility_type],
    ["Site code", r.site_code || "none"],
    ["Place", [r.city, r.state, r.zip].filter(Boolean).join(", ") || "unknown"],
    ["Year shown", r.ay + (r.yb ? "" : " (undated)")],
    ["Year basis", r.ab],
    ["Year source", r.year_source || "none"],
    ["Year flag", flags || "none"],
    ["MWPVL year", r.mwpvl_year ? r.mwpvl_year + (r.mwpvl_year_is_projection ? " (projection, not used)" : "") + (r.mwpvl_year_resolution ? " [" + String(r.mwpvl_year_resolution).replace(/_/g, " ") + "]" : "") : "none"],
    ["MWPVL status", r.mwpvl_status || "not listed"],
    ["MWPVL listed size", r.mwpvl_sq_ft ? A.fmt(r.mwpvl_sq_ft) + " sq ft (capture " + r.mwpvl_sq_ft_snapshot + ")" : "none"],
    ["EPI / MWPVL 2012 year", r.opening_year || "none"],
    ["Press event year", r.event_opening_year || "none"],
    ["First OSHA filing", r.first_osha_filing_year || "none"],
    ["OSHA filings", r.osha_matched_year_count ? r.osha_matched_year_count + " years, " + r.first_osha_filing_year + " to " + r.last_osha_filing_year : "none matched"],
    ["Latest staff", r.osha_latest_employees ? A.fmt(r.osha_latest_employees) + " avg. employees (" + r.osha_latest_year + ", OSHA 300A)" : "n/a"],
    ["Pullback", pb + (hist ? "; history: " + hist : "")],
    ["Location", r.approx ? "ZIP centroid only (approximate)" : "geocoded address (" + String(r.geo_method).replace(/_/g, " ") + ")"],
    ["Confidence", r.confidence + " (roster match)"]
  ];
  var pu = link(r.press_source_url).map(function (u) { return '<a href="' + A.esc(u) + '" target="_blank" rel="noopener">press article</a>'; }).join(", ");
  var src = link(r.source_url).map(function (u, i) { return '<a href="' + A.esc(u) + '" target="_blank" rel="noopener">source ' + (i + 1) + "</a>"; }).join(", ");
  return "<table>" + rows.map(function (x) { return "<tr><td>" + A.esc(x[0]) + "</td><td>" + A.esc(x[1]) + "</td></tr>"; }).join("") + "</table>" +
    '<div style="margin-top:6px;font-size:12px">' + (pu ? 'Press date source: ' + pu + ' &middot; ' : '') + 'Roster sources: ' + (src || "see Sources page") + ' &middot; MWPVL years, sizes and statuses: <a href="https://www.mwpvl.com/html/amazon_com.html" target="_blank" rel="noopener">MWPVL International</a> via Wayback Machine &middot; <a href="sources.html">all sources</a></div>';
}
var TPT = { exact: "exact", probable: "probable", none: "unmatched" };
function tpPopup(r) {
  var u = String(r.article_url || ""), q = String(r.quote || "");
  var rows = [
    ["Type", r.facility_type],
    ["Place", [r.city, r.state].filter(Boolean).join(", ") || "unknown"],
    ["Opening date stated", r.opening_date || "not stated"],
    ["Reported by", [r.publication, r.article_date].filter(Boolean).join(", ")],
    ["Confidence", r.confidence + " (" + r.evidence_basis + (r.evidence_basis !== "full text" ? "; low-confidence, snippet or title only" : "") + ")"],
    ["Roster match", r.matched_facility_id ? TPT[r.match_quality] + " to " + r.match_site_code : TPT[r.match_quality] + " (no roster site)"],
    ["Location", r.loc_approx === "yes" ? "approximate: " + String(r.loc_method).replace(/_/g, " ") : "roster site geocode"]
  ];
  return "<b>Trade-press report</b><table>" + rows.map(function (x) { return "<tr><td>" + A.esc(x[0]) + "</td><td>" + A.esc(x[1]) + "</td></tr>"; }).join("") + "</table>" +
    (q && u ? '<div style="margin-top:4px;font-size:12px"><i>"' + A.esc(q.length > 170 ? q.slice(0, 167) + "..." : q) + '"</i></div>' : "") +
    '<div style="margin-top:6px;font-size:12px">' + (/^https?:/.test(u) ? '<a href="' + A.esc(u) + '" target="_blank" rel="noopener">Read the article</a>' : "Subscription source (ProQuest); no public link") + " &middot; <a href=\"sources.html#s-industry\">about this layer</a></div>";
}
if (hasL) {
  try {
    map = L.map("amap", { preferCanvas: true, minZoom: 3, maxZoom: 14, worldCopyJump: false, zoomSnap: .5 });
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", { maxZoom: 19, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' }).addTo(map);
    map.fitBounds([[24.5, -125], [49.5, -66.5]]);
    map.attributionControl.addAttribution('Site years, sizes and statuses: <a href="https://www.mwpvl.com/html/amazon_com.html" target="_blank" rel="noopener">MWPVL International</a> (Wayback Machine)');
    layer = L.layerGroup().addTo(map);
    located.forEach(function (r) {
      var m = L.circleMarker([+r.lat, +r.lon], { radius: r.facility_type === "air_hub" ? 7 : 4.5 });
      m._r = r; m._vis = false;
      m.bindTooltip(A.esc((r.site_code || "no code") + " " + (TLAB[r.facility_type] || "") + (r.city ? ", " + r.city : "") + (r.state ? " " + r.state : "")), { direction: "top", offset: [0, -4] });
      m.bindPopup(function () { return popup(r); }, { maxWidth: 340 });
      restyle(m); markers.push(m);
    });
    epiLayer = L.layerGroup().addTo(map);
    pbLayer = L.layerGroup().addTo(map);
    pbLoc.forEach(function (r) {
      var m = L.marker([+r.lat, +r.lon], { keyboard: false, zIndexOffset: 800, icon: L.divIcon({ className: "", iconSize: [16, 16], html: '<i class="pb pb-' + r.pbg + '">' + PBL[r.pbg][1] + '</i>' }) });
      m._r = r; m._vis = false;
      m.bindTooltip(A.esc((r.site_code || "no code") + ": " + String(r.pullback_status).replace(/_/g, " ") + (r.pullback_date ? ", " + r.pullback_date : "")), { direction: "top", offset: [0, -6] });
      m.bindPopup(function () { return popup(r); }, { maxWidth: 340 });
      pbMarkers.push(m);
    });
    tpLayer = L.layerGroup();
    TP.forEach(function (r) {
      var m = L.marker([+r.lat, +r.lon], { keyboard: false, zIndexOffset: 500, icon: L.divIcon({ className: "", iconSize: [14, 14], html: '<i class="tp ' + r.confidence + (r.loc_approx === "yes" ? " approx" : "") + '"></i>' }) });
      m.bindTooltip(A.esc("Press: " + (r.city || "city not given") + (r.state ? " " + r.state : "") + ", " + r.facility_type + (r.press_year ? ", " + r.press_year : "")), { direction: "top", offset: [0, -6] });
      m.bindPopup(function () { return tpPopup(r); }, { maxWidth: 340 });
      tpMarkers.push(m);
    });
    EPIK.forEach(function (c) {
      var m = L.circleMarker([c.lat, c.lon], { radius: 6, color: css("--cat3"), weight: 2, dashArray: "1 3", fillColor: css("--cat3"), fillOpacity: .2 });
      m._c = c; m._vis = false;
      m.bindTooltip(A.esc(c.county + ", " + c.state + " (EPI)"), { direction: "top" });
      m.bindPopup(function () { var y = +yr.value, n = c.years.filter(function (v) { return v <= y; }).length; return "<b>" + A.esc(c.county + ", " + c.state) + "</b><br>" + n + " of " + c.years.length + " EPI-listed fulfillment centers opened by " + Math.min(y, 2017) + " (opening years: " + c.years.slice().sort().join(", ") + ").<br>Source: Economic Policy Institute, Zipperer and Jones (2018), Appendix Table 3. Position is the county centroid, not a building."; });
      epiMarkers.push(m);
    });
  } catch (e) { map = null; hasL = false; if (window.console) console.error(e); }
}
if (!hasL) {
  var mb = A.$("#amap"); mb.style.display = "flex"; mb.style.alignItems = "center"; mb.style.justifyContent = "center"; mb.style.padding = "16px";
  mb.innerHTML = "<p class=\"muted\">The map library (Leaflet from cdnjs) or the map tiles did not load, probably because this device is offline. The counts, chart and site table below still work.</p>";
}

/* ---------- state ---------- */
var yr = A.$("#yr"), out = A.$("#yrout"), tsel = {};
TYPES.forEach(function (t) { tsel[t[0]] = true; });
var tbl = null, sqRows = A.rows(LG.sqft), early = A.rows(LG.fc_counts_early), tl = A.rows(LG.timeline);

function visible(r, y) {
  if (r.ay > y || !tsel[r.facility_type]) return false;
  if (!A.$("#fapprox").checked && r.approx) return false;
  if (A.$("#f25").checked && r.status !== "in_2025_osha_filing") return false;
  return true;
}
function milestones(y) {
  return tl.filter(function (e) {
    var s = String(e.date), y1 = +s.slice(0, 4), m = /^(\d{4})-(\d{4})$/.exec(s), y2 = m ? +m[2] : y1;
    return y >= y1 && y <= y2;
  }).slice(0, 4);
}
function update() {
  var y = +yr.value; out.textContent = y;
  var cnt = {}, tot = 0, rowsShown = [];
  TYPES.forEach(function (t) { cnt[t[0]] = 0; });
  located.forEach(function (r) { if (visible(r, y)) { cnt[r.facility_type] = (cnt[r.facility_type] || 0) + 1; tot++; rowsShown.push(r); } });
  if (layer) markers.forEach(function (m) {
    var v = visible(m._r, y);
    if (v && !m._vis) { layer.addLayer(m); m._vis = true; } else if (!v && m._vis) { layer.removeLayer(m); m._vis = false; }
  });
  var epiN = 0;
  EPIK.forEach(function (c) { epiN += c.years.filter(function (v) { return v <= y; }).length; });
  epiMarkers.forEach(function (m) {
    var n = m._c.years.filter(function (v) { return v <= y; }).length, on = n > 0 && y <= 2017 && A.$("#fepi").checked;
    if (on) { m.setRadius(4 + 3 * Math.sqrt(n)); if (!m._vis) { epiLayer.addLayer(m); m._vis = true; } } else if (m._vis) { epiLayer.removeLayer(m); m._vis = false; }
  });
  /* the legend counts ignore the type checkboxes so you can see what you switched off */
  TYPES.forEach(function (t) {
    var n = 0; located.forEach(function (r) { if (r.facility_type === t[0] && r.ay <= y && (A.$("#fapprox").checked || !r.approx) && (!A.$("#f25").checked || r.status === "in_2025_osha_filing")) n++; });
    A.$("#lc-" + t[0]).textContent = "(" + A.fmt(n) + ")";
  });
  var bc = {}; located.forEach(function (r) { if (r.ay <= y && (A.$("#fapprox").checked || !r.approx) && (!A.$("#f25").checked || r.status === "in_2025_osha_filing") && tsel[r.facility_type]) { var k = r.yb || "undated"; bc[k] = (bc[k] || 0) + 1; } });
  BKEYS.concat(["undated"]).forEach(function (k) { A.$("#bc-" + k).textContent = "(" + A.fmt(bc[k] || 0) + ")"; });
  var pc = {}, pbOn = A.$("#fpb").checked;
  pbMarkers.forEach(function (m) {
    var r = m._r, v = pbOn && r.pby != null && r.pby <= y && visible(r, y);
    if (r.pby != null && r.pby <= y && visible(r, y)) pc[r.pbg] = (pc[r.pbg] || 0) + 1;
    if (v && !m._vis) { pbLayer.addLayer(m); m._vis = true; } else if (!v && m._vis) { pbLayer.removeLayer(m); m._vis = false; }
  });
  ["closed", "delayed", "sublease", "removed"].forEach(function (k) { A.$("#pc-" + k).textContent = "(" + A.fmt(pc[k] || 0) + ")"; });
  if (tpLayer && map) { var on = A.$("#ftp").checked; if (on && !map.hasLayer(tpLayer)) { tpMarkers.forEach(function (m) { tpLayer.addLayer(m); }); tpLayer.addTo(map); } else if (!on && map.hasLayer(tpLayer)) map.removeLayer(tpLayer); }
  var ctx = "";
  var s = sqRows.filter(function (r) { return +r.fiscal_year_end_dec31 === y; })[0], e = early.filter(function (r) { return +r.fiscal_year === y; })[0];
  if (s) ctx = "10-K context: at the end of FY" + y + " Amazon reported <b>" + A.fmt(s.na_fulfil_dc_other_total_ksf / 1000, 1) + " million sq ft</b> of North America fulfillment, data-center and other space (includes AWS data centers; Item 2).";
  else if (e) ctx = "10-K context: FY" + y + " lists <b>" + e.us_fulfillment_centers + " US fulfillment centers</b> (" + A.fmt(e.us_fc_sqft_ksf / 1000, 1) + " million sq ft).";
  else if (y < 2000) ctx = "10-K context: no square footage or site count is reported in this year's filings in this dataset.";
  var epiTxt = (A.$("#fepi").checked && y <= 2017) ? "<br><b>" + epiN + "</b> fulfillment centers opened by " + y + " in the EPI list (dashed county markers; source: Economic Policy Institute 2018, fulfillment centers only, county centroids)." : (y > 2017 ? "<br>The EPI early-openings layer ends at 2017." : "");
  var warn = y < 2017 ? "Before 2017 this map shows only sites with a known opening year (MWPVL, EPI or a press event year); it is a partial sample of the real network." : (y < 2026 ? "From 2017 the dots are sites whose opening year (MWPVL, EPI or press event) or first OSHA filing (\"operating by\") is this year or earlier." : "OSHA filings for 2026 are not yet public, so 2026 adds only sites with an MWPVL or press-event year of 2026 plus the undated sites.");
  var ms = milestones(y);
  A.$("#readout").innerHTML = "<b>" + A.fmt(tot) + "</b> sites shown for " + y + " (" + TYPES.filter(function (t) { return tsel[t[0]]; }).map(function (t) { return A.fmt(cnt[t[0]]) + " " + A.esc(t[1].toLowerCase()); }).join(", ") + ")." +
    (warn ? "<br>" + warn : "") + "<br>Pullback by " + y + ": " + A.fmt((pc.closed || 0) + (pc.delayed || 0) + (pc.sublease || 0) + (pc.removed || 0)) + " located roster sites carry a status (" + A.fmt(pc.closed || 0) + " closed, " + A.fmt(pc.delayed || 0) + " delayed or paused, " + A.fmt(pc.sublease || 0) + " sublease, " + A.fmt(pc.removed || 0) + " dropped from the MWPVL list)." + epiTxt + (ctx ? "<br>" + ctx : "") +
    (ms.length ? "<br>Milestones in " + y + ":<ul>" + ms.map(function (m) { return "<li>" + A.esc(m.event.length > 150 ? m.event.slice(0, 147) + "..." : m.event) + ' <span class="muted">(' + A.esc(m.publisher) + ", confidence " + A.esc(m.confidence) + ")</span></li>"; }).join("") + "</ul>" : "");
  if (tbl) tbl.setRows(rowsShown);
  rowsShownCache = rowsShown;
}
var rowsShownCache = [];

yr.addEventListener("input", update);
A.$("#tf").addEventListener("change", function (ev) { var k = ev.target.getAttribute("data-t"); if (k) { tsel[k] = ev.target.checked; update(); } });
A.$("#fapprox").addEventListener("change", update);
A.$("#f25").addEventListener("change", update);
A.$("#fepi").addEventListener("change", update);
A.$("#ftp").addEventListener("change", update);
A.$("#fpb").addEventListener("change", update);
var timer = null;
A.$("#play").addEventListener("click", function () {
  var b = A.$("#play");
  if (timer) { clearInterval(timer); timer = null; b.textContent = "Play"; return; }
  if (+yr.value >= Y1) yr.value = Y0;
  b.textContent = "Pause";
  timer = setInterval(function () {
    if (+yr.value >= Y1) { clearInterval(timer); timer = null; b.textContent = "Play"; return; }
    yr.value = +yr.value + 1; update();
  }, 450);
});
if (window.matchMedia) {
  var mq = window.matchMedia("(prefers-color-scheme: dark)");
  var re = function () { markers.forEach(restyle); };
  if (mq.addEventListener) mq.addEventListener("change", re); else if (mq.addListener) mq.addListener(re);
  new MutationObserver(re).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
}

/* ---------- chart: cumulative located sites by type ---------- */
var s2 = A.section(app, "cum", "How the mapped roster builds up", "Cumulative count of located sites by the year each first appears (opening year if known, then trade-press opening year, then first OSHA filing year). It describes the evidence, not the buildings.");
var yrs = []; for (var y = Y0; y <= Y1; y++) yrs.push(y);
var series = TYPES.map(function (t) {
  return { name: t[1], color: t[2], points: yrs.map(function (y) { return [y, located.filter(function (r) { return r.facility_type === t[0] && r.ay <= y; }).length]; }) };
});
var epiSeries = ({ name: "EPI fulfillment-center openings (county level, 1997-2017, cumulative)", color: css("--cat3"), dash: "4 3", points: yrs.filter(function (y) { return y <= 2017; }).map(function (y) { return [y, EPI.filter(function (r) { return r.open_year <= y; }).length]; }) });
A.mount(s2, '<div id="cumc"></div>');
A.lineChart("#cumc", { title: "Located roster sites by earliest evidence year and type", series: series.concat([epiSeries]), yFmt: function (v) { return A.fmt(v); }, xFmt: function (v) { return String(v); },
  caption: "Data: <span class=\"mono\">AMZ_FAC.facilities</span> (assets/data_facilities.js; file data/processed/facilities_master.csv), columns year_used, year_basis, facility_type, lat, lon. Year basis: MWPVL opening year (MWPVL International, archived copies of its Amazon table via the Wayback Machine, " + snapFirst + " to " + snapLast + "), then EPI / MWPVL 2012 opening year, then press or database event year (facility_events_all.csv; exact or probable matches, dated 2026 or earlier), then first OSHA filing (OSHA Injury Tracking Application 300A establishment data, osha.gov). The dashed EPI series is a separate source (Economic Policy Institute, Zipperer and Jones 2018, Appendix Table 3; fulfillment centers only, 95 openings 1997 to 2017, county level) and is not part of the roster. Counts of 2016 onward step up partly because OSHA electronic filing began with 2016 data (collected late, low compliance at first)." });

/* ---------- table view of what is on the map ---------- */
var s3 = A.section(app, "tv", "Table view of the sites shown", "The same sites as the map for the selected year and filters. Sort by clicking a heading.");
A.mount(s3, '<div id="tvt"></div>');
tbl = A.table("#tvt", { rows: [], pageSize: 20, sort: "ay", dir: -1, cols: [
  { key: "site_code", label: "Site code" },
  { key: "facility_type", label: "Type", fmt: function (v) { return TLAB[v] || v; } },
  { key: "city", label: "City" }, { key: "state", label: "State" },
  { key: "ay", label: "Shown from", num: true },
  { key: "abShort", label: "Year basis" },
  { key: "pullback_status", label: "Pullback status", fmt: function (v) { return v ? String(v).replace(/_/g, " ") : ""; } },
  { key: "pullback_date", label: "Pullback date" },
  { key: "mwpvl_sq_ft", label: "MWPVL listed sq ft", num: true, fmt: function (v) { return A.fmt(v); } },
  { key: "osha_latest_employees", label: "Latest OSHA avg. employees", num: true, fmt: function (v) { return A.fmt(v); } },
  { key: "approx", label: "Location", fmt: function (v) { return v ? "ZIP centroid (approx.)" : "address geocode"; } },
  { key: "confidence", label: "Confidence" }
] });
A.mount(s3, '<p class="cap">Data: <span class="mono">AMZ_FAC.facilities</span>. Counts by year and type are also in the chart above. Cumulative figures by year as a table:</p><details class="tv"><summary>Show counts by year and type</summary><div class="tw"><table><thead><tr><th>Year</th>' +
  TYPES.map(function (t) { return '<th class="n">' + A.esc(t[1]) + "</th>"; }).join("") + '<th class="n">All</th></tr></thead><tbody>' +
  yrs.map(function (y, i) { var tot = 0; return "<tr><td>" + y + "</td>" + series.map(function (s) { var v = s.points[i][1]; tot += v; return '<td class="n">' + A.fmt(v) + "</td>"; }).join("") + '<td class="n">' + A.fmt(tot) + "</td></tr>"; }).join("") + "</tbody></table></div></details>");

/* ---------- pullback rows that cannot be placed on the map ---------- */
var s5 = A.section(app, "pbtab", "Pullback rows with no site on the map", "Cancelled projects and other pullback rows that carry no site code, or whose site code is not in the roster, cannot be placed. They are listed here so the layer is not read as complete. Each row cites the report it comes from.");
var rosterCodes = {}; all.forEach(function (r) { if (r.site_code) rosterCodes[r.site_code] = 1; });
var pbOff = pbRows.filter(function (r) { return !r.site_code || !rosterCodes[r.site_code]; });
var offCnt = {}; pbOff.forEach(function (r) { offCnt[r.status] = (offCnt[r.status] || 0) + 1; });
A.mount(s5, '<p class="cap">' + A.fmt(pbOff.length) + ' of ' + A.fmt(pbRows.length) + ' pullback rows are not on the map: ' + Object.keys(offCnt).map(function (k) { return A.fmt(offCnt[k]) + " " + String(k).replace(/_/g, " "); }).join(", ") + '.</p><div id="pbt"></div>');
A.table("#pbt", { rows: pbOff, pageSize: 15, sort: "date", dir: -1, cols: [
  { key: "status", label: "Status", fmt: function (v) { return String(v || "").replace(/_/g, " "); } },
  { key: "date", label: "Date" }, { key: "city", label: "City" }, { key: "state", label: "State" },
  { key: "type", label: "Type", fmt: function (v) { return String(v || "").replace(/_/g, " "); } },
  { key: "site_code", label: "Site code" },
  { key: "sq_ft", label: "Sq ft", num: true, fmt: function (v) { return A.fmt(v); } },
  { key: "confidence", label: "Confidence" },
  { key: "sources", label: "Source (publication, date, title, via database)" }
] });
A.mount(s5, '<p class="cap">Data: <span class="mono">AMZ_PULL.sites</span> (assets/data_pullback.js; file data/processed/pullback_sites.csv), columns site_code, city, state, type, sq_ft, status, date, sources, confidence. Original sources: the publications named in each row, and MWPVL International snapshots via the Wayback Machine. Roster sites with a status are on the map above (<span class="mono">AMZ_FAC.facilities</span> columns pullback_status, pullback_date, pullback_history).</p>');

/* ---------- sources ---------- */
var s4 = A.section(app, "src", "Sources for this page");
A.sources(s4, [
  { label: "Roster of " + A.fmt(all.length) + " Amazon US logistics sites (this project, data/processed/facilities_master.csv)", publisher: "built here from OSHA, TaxJar, MWPVL, EPI and press reports", url: "sources.html", note: "Types are inferred from site-code and NAICS and may be wrong for individual sites." },
  { label: "OSHA Injury Tracking Application, Form 300A establishment data", url: "https://www.osha.gov/Establishment-Specific-Injury-and-Illness-Data", publisher: "US Department of Labor, OSHA", note: "First and last filing years, employees. Retrieved 2026-10-31." },
  { label: "MWPVL International (Marc Wulfraat), Amazon fulfillment network table, " + A.fmt(snapRows.length) + " archived captures " + snapFirst + " to " + snapLast, url: "https://www.mwpvl.com/html/amazon_com.html", publisher: "MWPVL International, read from the Internet Archive Wayback Machine", note: "Source of " + A.fmt(nMw) + " opening years, listed sizes, listed statuses and the dropped-from-list pullback status. MWPVL's years are its own compilation and may be projections; MWPVL asks that the table not be copied wholesale, so the page shows derived years and sizes per site; see Methods." },
  { label: "Press and database reports of Amazon openings, closures, delays and subleases (facility events, pullback rows)", url: "sources.html#s-industry", publisher: "publications named per row (see the pullback table and popups)", note: "Source of " + (nBasis.press_event_year || 0) + " opening years and of the pullback statuses other than dropped-from-list. Reported, not complete; low-confidence rows rest on titles or snippets. Cited by publication, date and title." },
  { label: "Trade-press openings layer (" + TPALL.length + " article rows)", url: "sources.html#s-industry", publisher: "various outlets, listed per row in the popup", note: "Toggle layer only; not filtered by the slider." },
  { label: "TaxJar, Amazon warehouse locations", url: "https://blog.taxjar.com/amazon-warehouse-locations/", publisher: "TaxJar", note: "Fulfillment and sort-center list, page modified 2025-10-29." },
  { label: "US Census Bureau geocoder, ZCTA 2020 centroids and 2020 Gazetteer (place, county-subdivision and county centroids)", url: "https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html", publisher: "US Census Bureau", note: "Street-level coordinates, or ZIP centroid where the address did not geocode; city or county centroids for trade-press rows with no roster match." },
  { label: "Amazon 10-K, Item 2 Properties (square feet) and early-year fulfillment-center counts", url: "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=1018724&type=10-K", publisher: "SEC EDGAR", note: "Used for the readout only." },
  { label: "Fulfillment-center openings 1997-2017 by county and quarter (95 FCs)", url: "https://files.epi.org/pdf/138921.pdf", publisher: "Economic Policy Institute (Zipperer and Jones, 2018), Appendix Table 3", note: "Early-openings layer; county centroids from the Census 2020 Gazetteer. FCs only, no addresses; EPI states a Feb 2018 MWPVL update raised its 2017 total from 95 to 120." },
  { label: "Base map tiles", url: "https://www.openstreetmap.org/copyright", publisher: "OpenStreetMap contributors", note: "Leaflet 1.9.4 from cdnjs. Needs an internet connection." }
]);
update();
})();
