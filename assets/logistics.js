/* logistics.html: network counts by type, space, milestones, Amazon Air, DSPs, population coverage.
   Data: AMZ_LOG (assets/data_logistics.js), AMZ_FAC (data_facilities.js), AMZ_POP (data_population.js). */
(function () {
"use strict";
var A = AMZ, LG = AMZ_LOG, FA = AMZ_FAC, PO = AMZ_POP;
A.page({ title: "Logistics network over time", sub: "Site counts by type, MWPVL openings and status by year, pullback (closures, cancellations, delays, subleases), facility events, warehouse space, milestones, Amazon Air, delivery partners, parcel share and volume, and how much of the country lives near a site. No continuous public count of sites by type exists; each view says what it counts." });
var app = A.$("#app");

var TYPES = [["fulfillment_center", "Fulfillment center", "var(--t1)"], ["delivery_station", "Delivery station", "var(--t2)"], ["sort_center", "Sort center", "var(--t3)"], ["other_logistics", "Other logistics", "var(--t4)"], ["air_hub", "Air hub", "var(--t5)"]];
var TLAB = {}; TYPES.forEach(function (t) { TLAB[t[0]] = t[1]; });
function link(u) { var m = String(u || "").split(/\s*;\s*/).filter(function (x) { return /^https?:/.test(x); }); return m[0] || ""; }
function a(u, t) { return u ? '<a href="' + A.esc(u) + '" target="_blank" rel="noopener">' + A.esc(t || "source") + "</a>" : ""; }
function conf(c) { var low = /low/i.test(c || ""); return '<span class="pill' + (low ? " no" : "") + '">' + A.esc(c || "") + "</span>"; }
function simple(cols, rows) {
  return '<div class="tw simple"><table><thead><tr>' + cols.map(function (c) { return "<th" + (c.num ? ' class="n"' : "") + ">" + A.esc(c.label) + "</th>"; }).join("") + "</tr></thead><tbody>" +
    rows.map(function (r) { return "<tr>" + cols.map(function (c) { var v = c.html ? c.html(r) : A.esc(r[c.key] == null ? "" : (c.fmt ? c.fmt(r[c.key]) : r[c.key])); return "<td" + (c.num ? ' class="n"' : "") + ">" + v + "</td>"; }).join("") + "</tr>"; }).join("") + "</tbody></table></div>";
}
function cite(host, data, orig) { A.mount(host, '<p class="cap">Data: ' + String(data).replace(/\.\s*$/, "") + (orig ? ". Original source: " + orig : ".") + "</p>"); }

var fac = A.rows(FA.facilities), oby = A.rows(FA.osha_by_year);
var typeOf = {}; fac.forEach(function (r) { typeOf[r.facility_id] = r.facility_type; });
var sq = A.rows(LG.sqft), early = A.rows(LG.fc_counts_early), snaps = A.rows(LG.snapshots), tl = A.rows(LG.timeline);
var fleet = A.rows(LG.air_fleet), hubs = A.rows(LG.air_hubs), dsp = A.rows(LG.dsp), pvol = A.rows(LG.parcel_volume), osc = A.rows(LG.osha_site_counts);
var pop = A.rows(PO.by_year);

/* ---------- headline tiles ---------- */
var lastSq = sq[sq.length - 1];
var moraine = snaps.filter(function (r) { return /^all US sites/.test(r.facility_type); })[0];
var amzLog24 = pvol.filter(function (r) { return r.carrier === "Amazon Logistics" && r.year === 2024; })[0];
var dsp24 = dsp.filter(function (r) { return r.metric === "dsp_count" && String(r.date) === "2024"; })[0];
var fleetHi = fleet.filter(function (r) { return /^2024-12|^2025-01/.test(r.as_of); });
var pop25 = pop.filter(function (r) { return r.set === "2025" && r.site_type === "all"; })[0];
A.tiles(app, [
  { value: A.fmt(lastSq.na_fulfil_dc_other_total_ksf / 1000, 0) + "m sq ft", label: "North America fulfillment, data-center and other space, FY" + lastSq.fiscal_year_end_dec31, context: "10-K Item 2; includes AWS data centers" },
  { value: A.fmt(moraine.count), label: "operating US sites with a 2025 OSHA filing, Sept 2025", context: "Moraine Research, medium confidence; single third-party count" },
  { value: A.fmt(amzLog24.volume_billion_parcels, 1) + "bn", label: "parcels delivered by Amazon Logistics in 2024", context: "Pitney Bowes Parcel Shipping Index; " + A.fmt(amzLog24.share_of_volume_pct, 1) + "% of US volume (computed)" },
  { value: A.fmt(dsp24.value) + " DSPs", label: "delivery service partner firms, 2024, worldwide", context: "Low confidence: from a news summary, global not US" },
  { value: fleetHi.map(function (r) { return r.aircraft_count; }).sort().join(" to "), label: "Amazon Air aircraft, Dec 2024 to Jan 2025", context: "Two sources disagree; low to medium confidence" },
  { value: A.pct(pop25.share20, 0), label: "of the US population within 20 miles of a site (2025 OSHA filers)", context: "2020 population, straight-line distance" }
]);
A.caveat(app, "<b>Read before using.</b><ul>" +
  "<li>Amazon does not publish a list of sites by type or by year. Counts here come from OSHA injury filings (a lower bound: only establishments that must file appear, and 2016 data were collected late with low compliance), one third-party snapshot, and 10-K square footage.</li>" +
  "<li>Site type in the roster is inferred from the site code and industry code, so type counts have error. Years before 2016 cannot be counted from filings at all.</li>" +
  "<li>MWPVL International (Marc Wulfraat) is a private consultancy that tracks Amazon sites; its table is read here from archived copies (Wayback Machine). Its years, statuses and sizes are its own compilation, include planned sites, and are not Amazon records. Pullback rows are reports, not confirmed closures, and overlap one another.</li>" +
  "<li>Air, DSP and milestone rows are mostly secondary sources (Wikipedia, trade press, search summaries) and are tagged with a confidence level.</li></ul>");

/* ---------- 1. counts by type over time ---------- */
var s1 = A.section(app, "types", "Sites by type, 2017 to 2025", "The number of roster sites with a matched OSHA ITA Form 300A filing in each calendar year, by inferred type. This is the only year-by-year count of sites by type available; it measures filing, which is not the same as operating.");
var byYT = {};
oby.forEach(function (r) { var t = typeOf[r.facility_id]; if (!t) return; var k = r.year + "|" + t; (byYT[k] = byYT[k] || {})[r.facility_id] = 1; });
function cnt(y, t) { return Object.keys(byYT[y + "|" + t] || {}).length; }
var yrs = []; for (var y = 2017; y <= 2025; y++) yrs.push(y);
A.mount(s1, '<div class="cols2" id="typec"></div>');
A.lineChart("#typec", { title: "Roster sites with an OSHA filing, by type (2025 is partial and left out)", yFmt: function (v) { return A.fmt(v); },
  series: TYPES.map(function (t) { return { name: t[1], color: t[2], points: yrs.filter(function (y) { return y <= 2024; }).map(function (y) { return [y, cnt(y, t[0])]; }) }; }),
  caption: "Data: <span class=\"mono\">AMZ_FAC.osha_by_year</span> joined to <span class=\"mono\">AMZ_FAC.facilities.facility_type</span> (assets/data_facilities.js). Original source: OSHA ITA 300A establishment data, osha.gov. Growth in filers reflects network growth and improving compliance, not rule changes: Form 300A electronic submission has covered warehousing (NAICS 4931) establishments with 20 or more employees since the 2016 data year. 2016 (1 site) omitted." });
var nGroups = {};
osc.forEach(function (r) { nGroups[r.group] = nGroups[r.group] || {}; nGroups[r.group][r.year] = r.distinct_site_codes; });
var GL = { naics_493110_general_warehousing: ["NAICS 493110 general warehousing", "var(--t1)"], naics_492110_courier_express: ["NAICS 492110 couriers and express delivery", "var(--t2)"], other_naics: ["Other NAICS codes", "var(--t3)"] };
A.lineChart("#typec", { title: "Distinct Amazon site codes filing with OSHA, by filed industry code", yFmt: function (v) { return A.fmt(v); },
  series: Object.keys(GL).map(function (g) { return { name: GL[g][0], color: GL[g][1], points: yrs.filter(function (y) { return y <= 2024 && nGroups[g] && nGroups[g][y] != null; }).map(function (y) { return [y, nGroups[g][y]]; }) }; }),
  caption: "Data: <span class=\"mono\">AMZ_LOG.osha_site_counts</span> (assets/data_logistics.js). Original source: OSHA ITA 300A, osha.gov. This counts every Amazon-named site code, so it exceeds the roster counts on the left. NAICS 492110 first appears in 2021 while the 493110 count falls that year, consistent with delivery sites being filed under couriers instead of warehousing (an inference from these counts, not stated by OSHA)." });
A.mount(s1, '<details class="tv"><summary>Table view of the left chart, including 2025 (partial)</summary>' + simple(
  [{ key: "y", label: "Year" }].concat(TYPES.map(function (t) { return { key: t[0], label: t[1], num: true, fmt: A.fmt }; })).concat([{ key: "all", label: "All", num: true, fmt: A.fmt }]),
  yrs.map(function (y) { var o = { y: y + (y === 2025 ? " (partial)" : ""), all: 0 }; TYPES.forEach(function (t) { o[t[0]] = cnt(y, t[0]); o.all += o[t[0]]; }); return o; })) + "</details>");

/* ---------- 2. snapshot counts ---------- */
var s2 = A.section(app, "snap", "Single-date counts by type", "Third-party counts at one date. The categories overlap (a rural delivery station is also a delivery station; same-day sites sit across types), so the bars are not additive.");
var snapItems = snaps.filter(function (r) { return r.as_of === "2025-09-30" && !/^all US sites/.test(r.facility_type); });
A.mount(s2, '<div id="snapc"></div>');
A.barChart("#snapc", { title: "Operating US sites by type, 30 Sept 2025 (Moraine Research)", labelWidth: 170, valFmt: function (v) { return A.fmt(v); },
  items: snapItems.map(function (r) { return { label: r.facility_type, value: r.count, color: "var(--t1)", note: r.caveats || "" }; }) });
cite(s2, "<span class=\"mono\">AMZ_LOG.snapshots</span> (assets/data_logistics.js)", "Moraine Research, Amazon logistics network map, published 2026-10-04 (morainecre.com). Method: CoStar buildings matched to OSHA CY2025 filings and Amazon 10-K. Total in this method: " + A.fmt(moraine.count) + " sites; confidence medium.");
A.mount(s2, "<h3>Other published totals</h3>" + simple([{ key: "as_of", label: "As of" }, { key: "facility_type", label: "What" }, { key: "count", label: "Count", num: true, fmt: A.fmt }, { key: "publisher_or_method", label: "Publisher" }, { label: "Confidence", html: function (r) { return conf(r.confidence); } }, { key: "caveats", label: "Caveat" }],
  snaps.filter(function (r) { return r.as_of !== "2025-09-30"; })));

/* ---------- 3. space ---------- */
var s3 = A.section(app, "space", "Warehouse space, 2004 to 2025", "The longest consistent series: square feet of fulfillment, data-center and other space in North America from Amazon's 10-K Item 2. It is company-wide and includes AWS data centers; the definition changes over time, so read the trend, not exact steps.");
A.mount(s3, '<div class="cols2" id="spacec"></div>');
var sqY = sq.map(function (r) { return +r.fiscal_year_end_dec31; });
A.lineChart("#spacec", { title: "North America fulfillment, data-center and other space (million sq ft)", yFmt: function (v) { return A.fmt(v, 0); },
  series: [
    { name: "Total", color: "var(--t1)", points: sq.map(function (r) { return [+r.fiscal_year_end_dec31, r.na_fulfil_dc_other_total_ksf / 1000]; }) },
    { name: "Leased", color: "var(--t2)", points: sq.map(function (r) { return [+r.fiscal_year_end_dec31, r.na_fulfil_dc_other_leased_ksf / 1000]; }) },
    { name: "Owned", color: "var(--t3)", points: sq.map(function (r) { return [+r.fiscal_year_end_dec31, r.na_fulfil_dc_other_owned_ksf / 1000]; }) }],
  caption: "Data: <span class=\"mono\">AMZ_LOG.sqft</span> (assets/data_logistics.js). Original source: Amazon.com 10-K Item 2 Properties via SEC EDGAR. Owned space is first reported in 2012. Growth is fastest in 2020 and 2021 and slows in 2022 and 2023; the timeline below records MWPVL's report of over 123 buildings closed, cancelled or delayed in 2022 to 2023." });
var gr = sq.map(function (r, i) { return i ? [+r.fiscal_year_end_dec31, (r.na_fulfil_dc_other_total_ksf / sq[i - 1].na_fulfil_dc_other_total_ksf - 1) * 100] : null; }).filter(Boolean);
A.lineChart("#spacec", { title: "Year-on-year change in North America space (%)", yFmt: function (v) { return A.fmt(v, 0) + "%"; },
  series: [{ name: "Total NA space, change vs prior year-end", color: "var(--t1)", points: gr.map(function (p) { return [p[0], Math.round(p[1] * 10) / 10]; }) }],
  caption: "Computed here from the same column (growth = this year / last year minus 1). Not a number from Amazon." });
A.mount(s3, "<h3>Before 2004: US fulfillment centers in the 10-Ks</h3>" + simple([{ key: "fiscal_year", label: "Fiscal year" }, { key: "us_fulfillment_centers", label: "US fulfillment centers", num: true }, { key: "us_fc_sqft_ksf", label: "Sq ft (thousand)", num: true, fmt: A.fmt }, { key: "description", label: "As listed" }, { key: "note", label: "Note" }], early));
cite(s3, "<span class=\"mono\">AMZ_LOG.fc_counts_early</span>", "Amazon.com 10-Ks for FY2000 to FY2003 via SEC EDGAR; confidence high.");

/* ---------- 4. milestones ---------- */
var s4 = A.section(app, "time", "Milestones, 1997 to 2025", "Dated events from filings, Amazon statements and trade press. Each carries its publisher and a confidence level; entries tagged low are search summaries or secondary sources and should be checked before reuse.");
var CAT = { network: ["Network", "var(--t1)"], speed: ["Delivery speed", "var(--t2)"], air: ["Air", "var(--t3)"], dsp: ["Delivery partners", "var(--t4)"], volume: ["Volume", "var(--t5)"] };
var catSel = {}; Object.keys(CAT).forEach(function (k) { catSel[k] = true; });
A.mount(s4, '<div class="tlf" id="tlf">' + Object.keys(CAT).map(function (k) { return '<label><input type="checkbox" data-c="' + k + '" checked><i class="sw" style="background:' + CAT[k][1] + '"></i>' + A.esc(CAT[k][0]) + "</label>"; }).join("") + '</div><ol class="tl" id="tlo"></ol>');
var tlSorted = tl.slice().sort(function (x, y) { return String(x.date) < String(y.date) ? -1 : 1; });
function drawTl() {
  A.$("#tlo").innerHTML = tlSorted.filter(function (e) { return catSel[e.category]; }).map(function (e) {
    var c = CAT[e.category] || [e.category, "var(--ink-3)"];
    return '<li style="--dot:' + c[1] + '"><span class="d">' + A.esc(e.date) + "</span>" + A.esc(e.event) + '<span class="m">' + A.esc(c[0]) + " &middot; " + A.esc(e.publisher) + " &middot; confidence " + conf(e.confidence) + " " + a(link(e.source_url), "source") + "</span></li>";
  }).join("");
}
A.$("#tlf").addEventListener("change", function (ev) { var k = ev.target.getAttribute("data-c"); if (k) { catSel[k] = ev.target.checked; drawTl(); } });
drawTl();
cite(s4, "<span class=\"mono\">AMZ_LOG.timeline</span> (assets/data_logistics.js, " + tl.length + " rows)", "per row: MWPVL International, SEC EDGAR 10-Ks, Wikipedia, Amazon Science, Pitney Bowes, trade press.");

/* ---------- 5. Amazon Air ---------- */
var s5 = A.section(app, "air", "Amazon Air", "Reported aircraft counts and US hub openings. Counts come from different outlets at different dates with different definitions, so they are shown as separate reports, not a trend line.");
A.mount(s5, '<div id="airc"></div>');
var fl = fleet.filter(function (r) { return !/Purchased 11/.test(r.description); });
A.barChart("#airc", { title: "Aircraft count as reported (excludes the 2021 purchase of 11 aircraft, which is not a fleet total)", labelWidth: 210, valFmt: function (v) { return A.fmt(v); },
  items: fl.map(function (r) { return { label: r.as_of + " " + r.publisher + (/^low$/.test(r.confidence) ? " (low)" : ""), value: r.aircraft_count, color: "var(--t3)", note: r.description + ". " + (r.caveats || "") }; }) });
cite(s5, "<span class=\"mono\">AMZ_LOG.air_fleet</span>", "Wikipedia (Amazon Air) citing ATSG and press; FreightWaves and Cargo Facts Consulting via search summaries (not confirmed from the pages). The Dec 2024 (104) and Jan 2025 (101) figures differ by definition and date.");
A.mount(s5, "<h3>Hub dates</h3>" + simple([{ key: "date", label: "Date" }, { key: "location", label: "Hub" }, { key: "event", label: "Event" }, { label: "Confidence", html: function (r) { return conf(r.confidence); } }, { label: "Source", html: function (r) { return a(link(r.source_url), r.source_basis ? String(r.source_basis).split(" (")[0] : "source"); } }], hubs));
var airSites = fac.filter(function (r) { return r.facility_type === "air_hub"; });
A.mount(s5, "<h3>Air sites in the roster</h3>" + simple([{ key: "site_code", label: "Site code" }, { label: "Place", html: function (r) { return A.esc([r.city, r.state].filter(Boolean).join(", ")); } }, { key: "first_osha_filing_year", label: "First OSHA filing" }, { key: "osha_latest_employees", label: "Latest avg. employees (OSHA)", num: true, fmt: A.fmt }, { key: "confidence", label: "Roster confidence" }], airSites));
cite(s5, "<span class=\"mono\">AMZ_FAC.facilities</span> where facility_type is air_hub (" + airSites.length + " sites)", "OSHA ITA 300A and the roster build (see Methods). Type is inferred in the roster build; this is not a list of airports.");

/* ---------- 6. DSPs ---------- */
var s6 = A.section(app, "dsp", "Delivery service partners (DSPs)", "Amazon's program of independent delivery companies, launched 2018. All counts below are worldwide and reported by news outlets quoting Amazon, so they are low or medium confidence and not US-only.");
var dspCount = dsp.filter(function (r) { return r.metric === "dsp_count"; }), dspJobs = dsp.filter(function (r) { return r.metric === "dsp_jobs"; });
A.mount(s6, '<div class="cols2" id="dspc"></div>');
A.barChart("#dspc", { title: "DSP firms, worldwide", labelWidth: 110, valFmt: function (v) { return A.fmt(v); }, items: dspCount.map(function (r) { return { label: String(r.date).slice(0, 7) + (r.confidence === "low" ? " (low)" : ""), value: r.value, color: "var(--t4)", note: r.publisher + ". " + (r.caveats || "") }; }) });
A.barChart("#dspc", { title: "DSP driving jobs, worldwide", labelWidth: 110, valFmt: function (v) { return A.fmt(v); }, items: dspJobs.map(function (r) { return { label: String(r.date).slice(0, 7) + (r.confidence === "low" ? " (low)" : ""), value: r.value, color: "var(--t4)", note: r.publisher + ". " + (r.caveats || "") }; }) });
cite(s6, "<span class=\"mono\">AMZ_LOG.dsp</span>", "Post&Parcel citing Amazon's blog (2020); GeekWire citing Amazon (2023, 2024; page not fetchable, figures from search summaries); ChannelX and aboutamazon.com for program launch. The 2024 jobs figure may be cumulative since 2018 (unverified).");
A.mount(s6, simple([{ key: "date", label: "Date" }, { key: "description", label: "What was reported" }, { label: "Confidence", html: function (r) { return conf(r.confidence); } }, { key: "publisher", label: "Publisher" }, { label: "Source", html: function (r) { return a(link(r.source_url), "link"); } }, { key: "caveats", label: "Caveat" }], dsp));

/* ---------- 7. population coverage ---------- */
var s7 = A.section(app, "cover", "Population coverage", "Share of the 2020 US population living within 20 or 50 straight-line miles of at least one site. Population is held at 2020 for every year; only the set of sites changes, so this shows reach of the filing-visible network.");
A.estimate(s7, "Straight-line distance from 2020 Census tract centroids, not drive time. A year's site set is the sites with a matched OSHA filing that year, so the rise reflects network growth and improving compliance with the filing requirement, not only new buildings. 2016 (1 site) is omitted and 2025 is partial.");
A.mount(s7, '<div class="cols2" id="covc"></div>');
function ps(type, field) { return pop.filter(function (r) { return /^\d{4}$/.test(r.set) && +r.set >= 2017 && +r.set <= 2024 && r.site_type === type; }).map(function (r) { return [+r.set, Math.round(r[field] * 1000) / 10]; }); }
A.lineChart("#covc", { title: "Share of US population near a site, all types (%)", yFmt: function (v) { return A.fmt(v, 0) + "%"; }, yMin: 0, yMax: 100,
  series: [{ name: "Within 20 miles", color: "var(--t1)", points: ps("all", "share20") }, { name: "Within 50 miles", color: "var(--t2)", points: ps("all", "share50") }],
  caption: "Data: <span class=\"mono\">AMZ_POP.by_year</span> (assets/data_population.js; data/processed/population_access_by_year.csv). Original source: US Census Bureau 2020 population-weighted tract centroids (www2.census.gov/geo/docs/reference/cenpop2020/tract). Site set from OSHA ITA 300A matches." });
A.lineChart("#covc", { title: "Within 20 miles, by site type (%)", yFmt: function (v) { return A.fmt(v, 0) + "%"; }, yMin: 0, yMax: 100,
  series: [["fulfillment_center", "var(--t1)"], ["delivery_station", "var(--t2)"], ["sort_center", "var(--t3)"]].map(function (t) { return { name: TLAB[t[0]], color: t[1], points: ps(t[0], "share20") }; }),
  caption: "Same data and method, by inferred type. Delivery stations cover a larger share than fulfillment centers in most years, but they are also the more numerous type; the chart does not say why." });
var ra = pop.filter(function (r) { return r.set === "roster_all" && r.site_type === "all"; })[0];
A.mount(s7, '<details class="tv"><summary>Table view of all sets</summary>' + simple([{ key: "set", label: "Site set" }, { key: "site_type", label: "Type" }, { key: "n_sites", label: "Sites", num: true, fmt: A.fmt }, { key: "share20", label: "Within 20 mi", num: true, fmt: function (v) { return A.pct(v, 1); } }, { key: "share50", label: "Within 50 mi", num: true, fmt: function (v) { return A.pct(v, 1); } }], pop) + "</details>");
if (ra) A.mount(s7, '<p class="cap">Full roster (' + A.fmt(ra.n_sites) + " located sites, any year): " + A.pct(ra.share20, 1) + " within 20 miles and " + A.pct(ra.share50, 1) + " within 50 miles.</p>");

/* ---------- 8. Amazon Logistics parcel volume (Pitney Bowes), with release revisions ---------- */
var pbr = A.rows(LG.pitney_amazon);
var s9 = A.section(app, "parcels", "Amazon Logistics parcel volume and share (Pitney Bowes)", "Parcels delivered by Amazon's own US network, and its share of US parcel volume, from the annual Pitney Bowes Parcel Shipping Index. Each point comes from the edition covering that data year; later editions restate earlier years, so the points are not one consistent series.");
A.estimate(s9, "<b>Release revisions.</b> Pitney Bowes revises earlier years in each release. Examples seen in the saved releases: 2019 Amazon Logistics volume is 1.9bn in the 2020 and 2021 editions and about 2bn in the 2024 edition; the 2022 US total is 21.2bn in the 2023 edition and 21.5bn in the 2024 edition; the 2021 US total is 21.5bn then 21.7bn. The 2019 to 2021 data years come from trade-press reproductions of the releases, not the release documents. Hover a point to see its edition date. The share line mixes reported (rounded) shares and shares computed here as Amazon volume divided by US total.");
A.mount(s9, '<div class="cols2" id="pbc"></div>');
A.lineChart("#pbc", { title: "Amazon Logistics US parcel volume (billion parcels)", yFmt: function (v) { return A.fmt(v, 1); }, yMin: 0,
  series: [{ name: "Volume, as published in the edition for each data year", color: "var(--t1)", points: pbr.filter(function (r) { return r.amazon_volume_bn != null; }).map(function (r) { return [+r.data_year, +r.amazon_volume_bn, "Edition released " + r.release_date]; }) }],
  caption: "Data: <span class=\"mono\">AMZ_LOG.pitney_amazon</span> (data/processed/industry_pitney_bowes_parcel_index.csv). Original source: Pitney Bowes Inc., Parcel Shipping Index press releases (links in the table below)." });
A.lineChart("#pbc", { title: "Amazon Logistics share of US parcel volume (%)", yFmt: function (v) { return A.fmt(v, 0) + "%"; }, yMin: 0,
  series: [
    { name: "Share as reported (rounded)", color: "var(--t2)", points: pbr.map(function (r) { return [+r.data_year, r.share_reported_pct == null ? null : +r.share_reported_pct, "Edition released " + r.release_date]; }) },
    { name: "Share computed here (volume / US total)", color: "var(--t3)", dash: "5 3", points: pbr.map(function (r) { return [+r.data_year, r.share_computed_pct == null ? null : +r.share_computed_pct, "Computed; volume and total from the edition released " + r.release_date]; }) }],
  caption: "Same source. 2022 has no reported share in the saved text. Computed shares can differ from reported ones because of rounding and because the edition's own total can differ from the figure used for its published share." });
A.mount(s9, '<details class="tv"><summary>Table view with edition dates and links</summary>' + simple([{ key: "data_year", label: "Data year" }, { key: "release_date", label: "Edition released" }, { key: "amazon_volume_bn", label: "Amazon volume (bn)", num: true, fmt: function (v) { return A.fmt(v, 2); } }, { key: "total_us_volume_bn", label: "US total (bn)", num: true, fmt: function (v) { return A.fmt(v, 2); } }, { key: "share_reported_pct", label: "Share reported (%)", num: true }, { key: "share_computed_pct", label: "Share computed (%)", num: true }, { label: "Source", html: function (r) { return a(r.source_url, "edition"); } }], pbr) + "</details>");

/* ---------- 8b. parcel share and volume: market_context next to Pitney Bowes ---------- */
var MK = A.rows((window.AMZ_MARKET || { rows: { cols: [], rows: [] } }).rows);
function num(v) { var x = parseFloat(v); return isNaN(x) || /^</.test(String(v)) ? null : x; }
function cit(c) { return String(c || "").split(/(https?:\/\/[^\s,;)]+)/).map(function (p) { return /^https?:/.test(p) ? '<a href="' + A.esc(p) + '" target="_blank" rel="noopener">link</a>' : A.esc(p); }).join(""); }
var mkVol = MK.filter(function (r) { return r.measure === "Amazon Logistics US parcel volume"; });
var mkShV = MK.filter(function (r) { return r.measure === "Amazon Logistics share of US parcel volume"; });
var mkShM = MK.filter(function (r) { return /ShipMatrix/.test(r.measure) && /share/.test(r.measure); });
var mkUps = MK.filter(function (r) { return r.topic === "amazon_share_of_ups_revenue"; });
var sM = A.section(app, "market", "Parcel share and volume: market_context next to Pitney Bowes", "The market-context table repeats the Pitney Bowes figures as each source printed them and adds other measures of the same thing (ShipMatrix shares reported by IBISWorld and Market Share Reporter, and Amazon's share of UPS revenue from UPS filings and reports). The charts put the Pitney Bowes editions on the same axes so the sources can be compared; they are not one consistent series.");
var agree = 0, cmp = 0, disagree = [];
mkVol.forEach(function (r) { var p = pbr.filter(function (x) { return +x.data_year === +r.year; })[0]; if (p && p.amazon_volume_bn != null) { cmp++; if (Math.abs(p.amazon_volume_bn - num(r.value)) < 0.05) agree++; else disagree.push(r.year + ": " + p.amazon_volume_bn + " vs " + r.value); } });
A.estimate(sM, "<b>Different sources, different definitions.</b> Pitney Bowes counts parcels delivered by Amazon's own US network as a share of US parcel <i>volume</i>. ShipMatrix (via IBISWorld and Market Share Reporter) uses its own parcel panel, and IBISWorld notes the two differ. Amazon's share of UPS revenue is a customer-concentration figure, not a parcel share. In " + agree + " of " + cmp + " data years the volume recorded in market_context equals the Pitney Bowes edition figure in <span class=\"mono\">AMZ_LOG.pitney_amazon</span>" + (disagree.length ? " (differences: " + A.esc(disagree.join("; ")) + ")" : "") + ".");
A.mount(sM, '<div class="cols2" id="mkc"></div>');
A.lineChart("#mkc", { title: "Amazon Logistics US parcel volume (billion parcels)", yFmt: function (v) { return A.fmt(v, 1); }, yMin: 0,
  series: [
    { name: "Pitney Bowes, edition for each data year (AMZ_LOG.pitney_amazon)", color: "var(--t1)", points: pbr.filter(function (r) { return r.amazon_volume_bn != null; }).map(function (r) { return [+r.data_year, +r.amazon_volume_bn, "Edition released " + r.release_date]; }) },
    { name: "As recorded in market_context", color: "var(--t2)", dash: "5 3", points: mkVol.map(function (r) { return [+r.year, num(r.value), "market_context, " + r.unit]; }).sort(function (a, b) { return a[0] - b[0]; }) }],
  caption: "Data: <span class=\"mono\">AMZ_MARKET.rows</span> (data/processed/market_context.csv), measure \"Amazon Logistics US parcel volume\", columns year, value, unit; and <span class=\"mono\">AMZ_LOG.pitney_amazon</span>. Original source: Pitney Bowes Inc., Parcel Shipping Index releases (links in the table below). Where the two lines coincide, market_context carries the same Pitney Bowes figure." });
var shS = [
  { name: "Pitney Bowes, share as published (market_context)", color: "var(--t1)", points: mkShV.map(function (r) { return [+r.year, num(r.value), String(r.basis)]; }).sort(function (a, b) { return a[0] - b[0]; }) },
  { name: "ShipMatrix share of US parcel market (via IBISWorld)", color: "var(--t3)", points: mkShM.filter(function (r) { return /IBISWorld/.test(r.citation); }).map(function (r) { return [+r.year, num(r.value), "ShipMatrix via IBISWorld"]; }).sort(function (a, b) { return a[0] - b[0]; }) },
  { name: "ShipMatrix share of volume (via Market Share Reporter)", color: "var(--t4)", points: mkShM.filter(function (r) { return /Market Share Reporter/.test(r.citation); }).map(function (r) { return [+r.year, num(r.value), "ShipMatrix via Market Share Reporter (Gale)"]; }) }];
A.lineChart("#mkc", { title: "Amazon Logistics share of US parcel volume (%)", yFmt: function (v) { return A.fmt(v, 0) + "%"; }, yMin: 0, series: shS,
  caption: "Data: <span class=\"mono\">AMZ_MARKET.rows</span>, measures \"Amazon Logistics share of US parcel volume\" and the ShipMatrix share rows, columns year, value, basis, citation. Original sources: Pitney Bowes Parcel Shipping Index releases; IBISWorld, Postal Service in the US (49111), May 2026, citing ShipMatrix (via MyIBISWorld); Market Share Reporter, 33rd ed., 2023 (via Gale Directory Library), citing ShipMatrix via Logistics Management, 2021-06-29. The single-year ShipMatrix point is a dot, not a line." });
A.lineChart("#mkc", { title: "Amazon share of UPS consolidated revenue (%)", yFmt: function (v) { return A.fmt(v, 0) + "%"; }, yMin: 0,
  series: [
    { name: "UPS filings and market reports", color: "var(--t5)", points: mkUps.filter(function (r) { return !/Financial Times/.test(r.citation); }).map(function (r) { return [+r.year, num(r.value), String(r.citation).slice(0, 90)]; }).sort(function (a, b) { return a[0] - b[0]; }) },
    { name: "Financial Times, 2025-04-29 (rounded)", color: "var(--t2)", points: mkUps.filter(function (r) { return /Financial Times/.test(r.citation); }).map(function (r) { return [+r.year, num(r.value), "Financial Times, 2025-04-29"]; }) }],
  caption: "Data: <span class=\"mono\">AMZ_MARKET.rows</span>, topic amazon_share_of_ups_revenue, columns year, value, citation. Original sources: UPS annual reports (Form 10-K), The Insight Partners (2026-03), Financial Times (2025-04-29), IBISWorld and CFRA (see table). 2018 is reported only as below 10 percent (UPS names no customer at or above 10 percent) and is not plotted." });
var mkTab = MK.filter(function (r) { return r.topic === "amazon_logistics_parcels" || r.topic === "amazon_share_of_ups_revenue"; }).sort(function (a, b) { return a.measure < b.measure ? -1 : a.measure > b.measure ? 1 : a.year - b.year; });
A.mount(sM, '<details class="tv"><summary>Table view with citations (' + mkTab.length + ' rows)</summary><div id="mkt"></div></details>');
A.table("#mkt", { rows: mkTab, pageSize: 15, sort: "year", dir: 1, cols: [
  { key: "measure", label: "Measure" }, { key: "year", label: "Year", num: true }, { key: "value", label: "Value", num: true }, { key: "unit", label: "Unit" }, { key: "basis", label: "Basis" },
  { key: "citation", label: "Source (publication, date, title, via database)", html: function (v) { return cit(v); } }, { key: "note", label: "Note" }] });
cite(sM, "<span class=\"mono\">AMZ_MARKET.rows</span> (data/processed/market_context.csv, " + A.fmt(MK.length) + " rows in all; the " + A.fmt(mkTab.length) + " on parcels and UPS are shown here).", "the publication named in each citation. Subscription databases are named only as the access route; no passages are reproduced.");

/* ---------- 9. early fulfillment-center openings (EPI), 1997 to 2017 ---------- */
var epi = A.rows(LG.epi_openings), epic = A.rows(LG.epi_cumulative);
var s10 = A.section(app, "early", "Fulfillment-center openings, 1997 to 2017 (EPI)", "The only open, itemized count of early openings: 95 Amazon fulfillment centers by state, county and quarter, compiled by the Economic Policy Institute. It covers fulfillment centers only (no delivery stations, sort centers or air hubs) and has no addresses, so it is shown as counts, and as county-level markers on the map page.");
var ey = []; for (var yy = 1997; yy <= 2017; yy++) ey.push(yy);
var cumEpi = ey.map(function (y) { return [y, epi.filter(function (r) { return r.open_year <= y; }).length]; });
function epiSeries(vintage, color, dash) { return { name: "EPI reported total, " + vintage, color: color, dash: dash, points: epic.filter(function (r) { return r.dataset_vintage.indexOf(vintage) === 0; }).map(function (r) { return [+r.as_of_year_end, +r.cumulative_fc_openings]; }) }; }
A.mount(s10, '<div id="epic"></div>');
A.lineChart("#epic", { title: "Cumulative Amazon fulfillment-center openings, 1997 to 2017", yFmt: function (v) { return A.fmt(v); },
  series: [{ name: "EPI Appendix Table 3 (95 FCs, itemized rows)", color: "var(--t1)", points: cumEpi }, epiSeries("original", "var(--t2)", "2 3"), epiSeries("updated", "var(--t3)", "5 3")],
  caption: "Data: <span class=\"mono\">AMZ_LOG.epi_openings</span> and <span class=\"mono\">AMZ_LOG.epi_cumulative</span> (data/processed/industry_epi_fc_openings_2017.csv, industry_epi_fc_cumulative_counts.csv). Original source: Zipperer and Jones (2018), Unfulfilled promises, Economic Policy Institute, Appendix Table 3 (files.epi.org/pdf/138921.pdf), compiled from Avalara, Guided Imports and MWPVL. The February 2018 MWPVL update raised the 2015 to 2017 totals to 75, 100 and 120; the extra 25 openings are not itemized, so the line of itemized rows follows the original vintage." });
var byState = {}; epi.forEach(function (r) { byState[r.state] = (byState[r.state] || 0) + 1; });
A.mount(s10, '<div id="epis"></div>');
A.barChart("#epis", { title: "EPI-listed fulfillment centers opened by 2017, by state", labelWidth: 120, valFmt: function (v) { return A.fmt(v); },
  items: Object.keys(byState).sort(function (x, y2) { return byState[y2] - byState[x]; }).map(function (k) { return { label: k, value: byState[k], color: "var(--t1)" }; }),
  caption: "Same source. Counts are fulfillment centers opened 1997 to 2017 and not necessarily still operating." });

/* ---------- 10. robots ---------- */
var rob = A.rows(LG.robots);
var s11 = A.section(app, "robots", "Warehouse robots", "Amazon's robot count as reported at irregular dates. These are separate reports, not a series: early counts are Kiva drive units in US warehouses, later counts are worldwide and include other robot types. Confidence is shown for each.");
A.mount(s11, '<div id="robc"></div>');
A.barChart("#robc", { title: "Reported Amazon warehouse robots", labelWidth: 200, valFmt: function (v) { return A.fmt(v); },
  items: rob.map(function (r) { return { label: String(r.as_of).replace(/\s*\(.*$/, "") + (r.qualifier ? " (" + r.qualifier + ")" : "") + " " + String(r.source_type).split(/[ :(]/)[0], value: +r.robots, color: /^medium/.test(r.confidence) ? "var(--t1)" : "var(--t4)", note: A.esc(r.what_counted) + ". " + A.esc(r.confidence) }; }),
  caption: "Data: <span class=\"mono\">AMZ_LOG.robots</span> (data/processed/industry_amazon_robot_counts.csv). Dark bars are Amazon's own statements (medium confidence); lighter bars are news or secondary reports. The 2014 holiday figure appears twice because two outlets reported 15,000 for ten US warehouses." });
A.mount(s11, '<details class="tv"><summary>Table view with sources and caveats</summary>' + simple([{ key: "as_of", label: "As of" }, { key: "robots", label: "Robots", num: true, fmt: A.fmt }, { key: "qualifier", label: "Qualifier" }, { key: "what_counted", label: "What was counted" }, { key: "confidence", label: "Confidence" }, { key: "note", label: "Note" }, { label: "Source", html: function (r) { return a(r.source_url, "link"); } }], rob) + "</details>");

/* ---------- 12. trade-press openings by year and type ---------- */
var tp = A.rows(LG.trade_press);
var TPG = [["fc", "Fulfillment center (incl. robotic, big-and-bulky)", function (t) { return /fulfillment/.test(t); }], ["ds", "Delivery station", function (t) { return /delivery/.test(t); }], ["air", "Air hub", function (t) { return /air hub/.test(t); }], ["oth", "Sort, distribution and other", function (t) { return /sortation|distribution/.test(t); }]];
var tpSeen = {}, tpByY = {}, tpPlanned = 0, tpNoYear = 0;
tp.forEach(function (r) {
  var s = String(r.opening_date || ""), m = /^(\d{4})/.exec(s), y = m ? +m[1] : null;
  if (!y) { tpNoYear++; return; }
  if (y > 2026) { tpPlanned++; return; }
  var g = TPG.filter(function (x) { return x[2](r.facility_type); })[0]; if (!g) return;
  var k = [y, g[0], String(r.city || "").toLowerCase(), r.state].join("|");   /* one count per place, type and year even when several articles report it */
  if (tpSeen[k]) return; tpSeen[k] = 1;
  var o = tpByY[y] = tpByY[y] || { fc: 0, ds: 0, air: 0, oth: 0, low: 0 }; o[g[0]]++; if (r.confidence === "low") o.low++;
});
var tpYears = Object.keys(tpByY).map(Number).sort(function (a, b) { return a - b; });
var tpTot = 0; tpYears.forEach(function (y) { tpTot += tpByY[y].fc + tpByY[y].ds + tpByY[y].air + tpByY[y].oth; });
var s12 = A.section(app, "press", "Trade-press openings by year and type (reported, not complete)", "Openings that trade and local press reported with a stated date. This is a list of what articles said, found by search, so it is neither complete nor a count of the network; a quiet year may only mean no article was found. Each place, type and year is counted once even when several articles cover it.");
A.mount(s12, '<div class="est"><b>Reported, not complete.</b> ' + tpTot + ' distinct reported openings from ' + tp.length + ' article rows. ' + tpNoYear + ' rows state no opening date, ' + tpPlanned + ' give a planned date after 2026 and are left out. The "low" column counts rows resting on search snippets or titles only. Loveland CO and Wilmington NC have source conflicts on size.</div>' +
  simple([{ key: "y", label: "Year" }].concat(TPG.map(function (g) { return { key: g[0], label: g[1], num: true }; })).concat([{ key: "t", label: "All", num: true }, { key: "low", label: "of which low confidence", num: true }]),
    tpYears.map(function (y) { var o = tpByY[y]; return { y: y, fc: o.fc, ds: o.ds, air: o.air, oth: o.oth, t: o.fc + o.ds + o.air + o.oth, low: o.low }; })));
cite(s12, "<span class=\"mono\">AMZ_LOG.trade_press</span> (data/processed/industry_trade_press_openings.csv, with parsed years in trade_press_openings_located.csv). Original sources: the articles linked in each popup on the <a href=\"map.html\">map</a> (toggle \"Trade-press openings layer\"); publishers include Supply Chain Dive, FreightWaves, Transport Topics, Logistics Management and local outlets. Dates are as stated in the article (some are month or year only).");

/* ---------- MWPVL, pullback and facility events ---------- */
var MWD = window.AMZ_MWPVL || { openings_by_year: { cols: [], rows: [] }, status_by_snapshot: { cols: [], rows: [] }, snapshots: { cols: [], rows: [] } };
var PUD = window.AMZ_PULL || { sites: { cols: [], rows: [] }, aggregates: { cols: [], rows: [] } };
var EVD = window.AMZ_EVENTS || { events: { cols: [], rows: [] } };
var oby2 = A.rows(MWD.openings_by_year), sbs = A.rows(MWD.status_by_snapshot), msn = A.rows(MWD.snapshots);
var msnFirst = msn.length ? msn[0].snapshot_date : "", msnLast = msn.length ? msn[msn.length - 1].snapshot_date : "";
var MWATTR = "MWPVL International (Marc Wulfraat), archived copies of its Amazon table via the Internet Archive Wayback Machine, " + A.fmt(msn.length) + " captures " + msnFirst + " to " + msnLast;
function niceStep(mx, n) { var raw = mx / n, p = Math.pow(10, Math.floor(Math.log(raw) / Math.LN10)), f = raw / p; return (f <= 1 ? 1 : f <= 2 ? 2 : f <= 5 ? 5 : 10) * p; }
/* stacked columns. o: {title, cats:[{key,label,color,hatch}], rows:[{x,label,vals:{key:n}}], xEvery, caption} */
function stacked(host, o) {
  var W = 760, H = o.height || 300, m = { l: 46, r: 10, t: 10, b: 30 }, n = o.rows.length, id = "st" + Math.random().toString(36).slice(2, 7);
  var tot = o.rows.map(function (r) { return o.cats.reduce(function (s, c) { return s + (r.vals[c.key] || 0); }, 0); });
  var lineV = o.line ? o.rows.map(function (r) { return o.line.vals[r.x]; }) : [], mx = Math.max.apply(null, tot.concat(lineV.filter(function (v) { return v != null; })).concat([1])), st = niceStep(mx, 5), top = Math.ceil(mx / st) * st;
  var bw = (W - m.l - m.r) / Math.max(1, n), w = Math.max(2, bw * .74), Y = function (v) { return H - m.b - v / top * (H - m.t - m.b); };
  var g = '<defs><pattern id="' + id + 'h" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="5" height="5" fill="var(--surface)"/><rect width="2" height="5" fill="var(--ink-3)"/></pattern></defs>';
  for (var v = 0; v <= top + st / 2; v += st) g += '<line class="gl" x1="' + m.l + '" x2="' + (W - m.r) + '" y1="' + Y(v) + '" y2="' + Y(v) + '"/><text x="' + (m.l - 6) + '" y="' + (Y(v) + 3) + '" text-anchor="end">' + A.esc(A.fmt(v)) + "</text>";
  var ev = o.xEvery || Math.max(1, Math.ceil(n / 14));
  o.rows.forEach(function (r, i) {
    var x = m.l + i * bw + (bw - w) / 2, acc = 0, t = tot[i];
    o.cats.forEach(function (c) {
      var val = r.vals[c.key] || 0; if (!val) return;
      var y1 = Y(acc + val), y0 = Y(acc); acc += val;
      g += '<rect class="pt" tabindex="0" x="' + x.toFixed(1) + '" y="' + y1.toFixed(1) + '" width="' + w.toFixed(1) + '" height="' + Math.max(1, y0 - y1).toFixed(1) + '" fill="' + (c.hatch ? "url(#" + id + "h)" : c.color) + '" stroke="var(--surface)" stroke-width="1.5" data-t="' + A.esc("<b>" + r.label + "</b><br>" + c.label + ": " + A.fmt(val) + "<br>All: " + A.fmt(t)) + '"/>';
    });
    if (i % ev === 0) g += '<text x="' + (x + w / 2).toFixed(1) + '" y="' + (H - 12) + '" text-anchor="middle">' + A.esc(r.x) + "</text>";
  });
  g += '<line class="ax" x1="' + m.l + '" x2="' + (W - m.r) + '" y1="' + Y(0) + '" y2="' + Y(0) + '"/>';
  if (o.line) o.rows.forEach(function (r, i) { var v = lineV[i]; if (v == null) return; var cx = m.l + i * bw + bw / 2; g += '<path class="pt" tabindex="0" d="M' + (cx - 5).toFixed(1) + ',' + Y(v).toFixed(1) + 'h10" stroke="var(--ink)" stroke-width="3" fill="none" data-t="' + A.esc("<b>" + r.label + "</b><br>" + o.line.label + ": " + A.fmt(v)) + '"/>'; });
  var leg = o.cats.map(function (c) { return '<span><i class="sw" style="' + (c.hatch ? "background:repeating-linear-gradient(135deg,var(--ink-3) 0 2px,var(--surface) 2px 4px);border:1px solid var(--ink-3)" : "background:" + c.color) + '"></i>' + A.esc(c.label) + "</span>"; }).join("") + (o.line ? '<span><i class="sw" style="background:var(--ink);height:3px;vertical-align:3px"></i>' + A.esc(o.line.label) + "</span>" : "");
  A.mount(host, '<div class="card ch" id="' + id + '"><h3>' + A.esc(o.title) + '</h3><svg class="rs" viewBox="0 0 ' + W + " " + H + '" role="img" aria-label="' + A.esc(o.title) + '">' + g + '</svg><div class="legend">' + leg + "</div>" + (o.caption ? '<p class="cap">' + o.caption + "</p>" : "") + "</div>");
  A.bindTips(A.$("#" + id));
}
function plain(s) { return String(s == null ? "" : s).replace(/_/g, " "); }

/* ---- openings by year and type (MWPVL) ---- */
var mwFac = fac.filter(function (r) { return r.mwpvl_year != null && r.mwpvl_year !== ""; });
var mwYears = oby2.map(function (r) { return r.year; });
var yLo = Math.min.apply(null, mwFac.map(function (r) { return +r.mwpvl_year; })), yHi = Math.max.apply(null, mwFac.map(function (r) { return +r.mwpvl_year; }));
var mwRows = [], mwCheck = [];
for (var yy = yLo; yy <= yHi; yy++) {
  var vals = {}, inY = mwFac.filter(function (r) { return +r.mwpvl_year === yy; });
  inY.forEach(function (r) { var k = r.mwpvl_year_is_projection ? "proj" : r.facility_type; vals[k] = (vals[k] || 0) + 1; });
  mwRows.push({ x: String(yy), label: String(yy), vals: vals, n: inY.length });
  var rec = oby2.filter(function (r) { return +r.year === yy; })[0];
  if ((rec ? +rec.sites : 0) !== inY.length) mwCheck.push(yy + " (" + inY.length + " in roster, " + (rec ? rec.sites : 0) + " in the table)");
}
var sOp = A.section(app, "mwpvlopen", "Openings by year and type (MWPVL)", "Each roster site with an MWPVL year, counted in that year and split by the roster's inferred type. MWPVL's year is the year its table gives for the site, which can be a planned date; it is not an Amazon record. Years where MWPVL gave only a projection for a planned site (hatched) are not used as an opening year on the map.");
var tblVals = {}, tblTot = 0; oby2.forEach(function (r) { tblVals[String(r.year)] = +r.sites; tblTot += +r.sites; });
var mwTot = mwFac.length, mwProj = mwFac.filter(function (r) { return r.mwpvl_year_is_projection; }).length;
A.estimate(sOp, "<b>Read with care.</b> " + A.fmt(mwTot) + " roster sites carry an MWPVL year (" + A.fmt(mwTot - mwProj) + " used, " + A.fmt(mwProj) + " projections not used). <b>The bars are roster sites only.</b> MWPVL's own table counts " + A.fmt(tblTot) + " rows with a year (black marks, <span class=\"mono\">AMZ_MWPVL.openings_by_year.sites</span>), so the roster holds " + A.pct(mwTot / tblTot, 0) + " of them; the table also lists rows that are not in the roster, which may include rows with no site code; the data do not say which, and do not split the gap by type. Years with no bar have no site in the table; MWPVL's early years (before 2012) are sparse because the table was a short list then. Types are the roster's (inferred from site code and industry code), not MWPVL's own categories. Year totals match the table in " + (mwRows.length - mwCheck.length) + " of " + mwRows.length + " years.");
stacked(sOp, { title: "Roster sites by MWPVL year and type, against all rows in MWPVL's table", rows: mwRows, xEvery: 2, line: { label: "All rows with a year in MWPVL's table", vals: tblVals },
  cats: TYPES.map(function (t) { return { key: t[0], label: t[1], color: t[2] }; }).concat([{ key: "proj", label: "Projection year (planned site, not used)", hatch: true }]),
  caption: "Data: <span class=\"mono\">AMZ_FAC.facilities</span> columns mwpvl_year, mwpvl_year_is_projection, facility_type (file data/processed/facilities_master.csv, built from mwpvl_wayback_sites_all.csv with mwpvl_corrections.csv applied); checked against <span class=\"mono\">AMZ_MWPVL.openings_by_year</span>. Original source: " + A.esc(MWATTR) + " (mwpvl.com/html/amazon_com.html). Where captures disagree on a site's year, the most common value is used." });
A.mount(sOp, '<details class="tv"><summary>Table view: sites by MWPVL year, with year-resolution and size</summary>' + simple([
  { key: "year", label: "Year" }, { key: "sites", label: "Sites", num: true }, { key: "single_value", label: "One value in all captures", num: true }, { key: "conflict_modal_value", label: "Captures disagree (most common used)", num: true },
  { key: "later_year_after_planned", label: "Year moved later after planned", num: true }, { key: "projection", label: "Projection", num: true }, { key: "active", label: "Listed active", num: true }, { key: "not_active", label: "Not active", num: true },
  { key: "sqft_sites", label: "Sites with size", num: true }, { key: "sqft_total", label: "Listed sq ft, total", num: true, fmt: function (v) { return A.fmt(v); } }], oby2) + "</details>");
cite(sOp, "<span class=\"mono\">AMZ_MWPVL.openings_by_year</span> (assets/data_mwpvl.js).", A.esc(MWATTR) + ". MWPVL asks that its table not be copied wholesale; only derived per-year counts and sizes are shown.");

/* ---- pullback: timeline and tallies ---- */
var pbs = A.rows(PUD.sites), pba = A.rows(PUD.aggregates);
var PG = [
  { key: "closed", short: "closed", label: "Closed (incl. temporary, partial)", color: "var(--t2)", st: ["closed", "closed_temporary", "closed_partial"] },
  { key: "cancelled", short: "cancelled", label: "Cancelled", color: "var(--t5)", st: ["cancelled"] },
  { key: "delayed", short: "delayed or paused", label: "Delayed or paused", color: "var(--t4)", st: ["delayed", "paused"] },
  { key: "sublease", short: "sublease", label: "Sublease", color: "var(--t1)", st: ["sublease"] },
  { key: "removed", short: "dropped from MWPVL's list", label: "Dropped from MWPVL list (not a confirmed closure)", hatch: true, st: ["removed_from_mwpvl_list"] }];
var pgOf = {}; PG.forEach(function (g) { g.st.forEach(function (s) { pgOf[s] = g.key; }); });
var qk = function (d) { var m = /^(\d{4})-(\d{2})/.exec(String(d || "")); return m ? m[1] + "-Q" + (Math.floor((+m[2] - 1) / 3) + 1) : null; };
var pbQ = {}, pbNoDate = 0, pbTot = {};
pbs.forEach(function (r) { var g = pgOf[r.status]; if (!g) return; pbTot[g] = (pbTot[g] || 0) + 1; var q = qk(r.date); if (!q) { pbNoDate++; return; } (pbQ[q] = pbQ[q] || {})[g] = (pbQ[q][g] || 0) + 1; });
var qs = Object.keys(pbQ).sort();
/* fill empty quarters between first and last */
var qAll = []; if (qs.length) { var a0 = qs[0].split("-Q"), b0 = qs[qs.length - 1].split("-Q"), cy = +a0[0], cq = +a0[1]; while (cy < +b0[0] || (cy === +b0[0] && cq <= +b0[1])) { qAll.push(cy + "-Q" + cq); cq++; if (cq > 4) { cq = 1; cy++; } } }
var sPb = A.section(app, "pullback", "Pullback: closures, cancellations, delays and subleases", "Reported pullback, by the date of the report or MWPVL capture that shows it, and the tallies that press and analysts published. A site-level row is one site in one report; a tally is a count somebody published, with its own scope.");
A.estimate(sPb, "<b>What these rows are.</b> " + A.fmt(pbs.length) + " pullback rows (<span class=\"mono\">AMZ_PULL.sites</span>): " + PG.map(function (g) { return A.fmt(pbTot[g.key] || 0) + " " + g.short; }).join(", ") + ". Rows dropped from MWPVL's list are dated by the first capture without the site and mean only that the site left that list (it may have been merged, renamed or re-coded). " + A.fmt(pbs.filter(function (r) { return !r.site_code; }).length) + " rows have no site code and cannot be joined to the roster. The same project can appear in several reports, so rows are not unique closures.");
stacked(sPb, { title: "Pullback rows by quarter of report or capture and status", xEvery: 4,
  rows: qAll.map(function (q) { return { x: q.replace("-Q", " Q"), label: q.replace("-Q", " Q"), vals: pbQ[q] || {} }; }),
  cats: PG.map(function (g) { return { key: g.key, label: g.label, color: g.color, hatch: g.hatch }; }),
  caption: "Data: <span class=\"mono\">AMZ_PULL.sites</span> (assets/data_pullback.js; file data/processed/pullback_sites.csv), columns status, date. " + (pbNoDate ? A.fmt(pbNoDate) + " rows without a usable date are not charted. " : "") + "Original sources: MWPVL International via the Wayback Machine (dropped-from-list rows and some delays), and the publications named per row in the table below (cited by publication, date and title; subscription databases are named only as the access route)." });
var aggMw = pba.filter(function (r) { return r.scope === "mwpvl_snapshot"; }), aggPress = pba.filter(function (r) { return r.scope !== "mwpvl_snapshot"; });
A.mount(sPb, '<h3 class="subh">Published tallies (not site-level, not additive)</h3><p class="cap">Counts that press and analysts published at one date, each with its own scope. Different tallies overlap and cannot be summed; blanks mean the source gave no such figure. A stated total can differ from the sum of its parts as printed.</p><div id="pba1"></div>');
A.table("#pba1", { rows: aggPress, pageSize: 20, sort: "date", dir: 1, cols: [
  { key: "date", label: "Date" }, { key: "scope", label: "Scope", fmt: plain },
  { key: "closed", label: "Closed", num: true }, { key: "cancelled", label: "Cancelled", num: true }, { key: "delayed", label: "Delayed", num: true }, { key: "paused", label: "Paused", num: true }, { key: "sublease", label: "Sublease", num: true },
  { key: "closed_or_cancelled", label: "Closed or cancelled", num: true }, { key: "total_stated", label: "Total stated", num: true }, { key: "sq_ft", label: "Sq ft", num: true, fmt: function (v) { return A.fmt(v); } }, { key: "states", label: "States", num: true },
  { key: "source", label: "Source" }, { key: "note", label: "Note" }] });
A.mount(sPb, '<h3 class="subh">MWPVL capture tallies (sites flagged in each capture)</h3><p class="cap">Distinct site codes carrying a delayed, on-hold or sublease flag in the capture. Sites first absent from a capture are not counted as closures.</p><div id="pba2"></div>');
A.table("#pba2", { rows: aggMw, pageSize: 10, sort: "date", dir: 1, cols: [
  { key: "date", label: "Capture" }, { key: "delayed", label: "Delayed", num: true }, { key: "paused", label: "Paused or on hold", num: true }, { key: "sublease", label: "Sublease", num: true },
  { key: "sq_ft", label: "Listed sq ft of flagged sites", num: true, fmt: function (v) { return A.fmt(v); } }, { key: "source", label: "Source" }] });
cite(sPb, "<span class=\"mono\">AMZ_PULL.aggregates</span> (assets/data_pullback.js; file data/processed/pullback_aggregates.csv), columns date, scope, closed, cancelled, delayed, paused, sublease, closed_or_cancelled, total_stated, sq_ft, states, source, note.", "the publication or MWPVL capture named in each row's source.");
A.mount(sPb, '<h3 class="subh">Site-level pullback rows</h3><div id="pbs"></div>');
A.table("#pbs", { rows: pbs, pageSize: 15, sort: "date", dir: -1, cols: [
  { key: "status", label: "Status", fmt: plain }, { key: "date", label: "Date" }, { key: "city", label: "City" }, { key: "state", label: "State" }, { key: "type", label: "Type", fmt: plain }, { key: "site_code", label: "Site code" },
  { key: "sq_ft", label: "Sq ft", num: true, fmt: function (v) { return A.fmt(v); } }, { key: "confidence", label: "Confidence" }, { key: "match_basis", label: "Roster match", fmt: plain },
  { key: "sources", label: "Source (publication, date, title, via database)" }] });
cite(sPb, "<span class=\"mono\">AMZ_PULL.sites</span> (file data/processed/pullback_sites.csv).", "the publication named in each row's source, and MWPVL International snapshots via the Wayback Machine. Roster sites with a status are marked on the <a href=\"map.html\">map</a>.");

/* ---- MWPVL status by snapshot ---- */
var snapDates = Object.keys(sbs.reduce(function (o, r) { o[r.snapshot_date] = 1; return o; }, {})).sort();
function stSum(d, st) { return sbs.filter(function (r) { return r.snapshot_date === d && r.status === st; }).reduce(function (s, r) { return s + (+r.sites || 0); }, 0); }
function dec(d) { var p = String(d).split("-"); return +p[0] + (+p[1] - 1) / 12 + (+p[2] - 1) / 365; }
var pipe = snapDates.map(function (d) { return stSum(d, "active") + stSum(d, "planned"); });
var partial = {};
pipe.forEach(function (v, i) { var nb = []; for (var k = -2; k <= 2; k++) if (k && pipe[i + k] != null) nb.push(pipe[i + k]); nb.sort(function (a, b) { return a - b; }); var med = nb.length ? nb[Math.floor(nb.length / 2)] : v; if (v < .6 * med) partial[snapDates[i]] = v + " listed vs about " + med + " in neighbouring captures"; });
var partK = Object.keys(partial);
var sSt = A.section(app, "mwpvlstatus", "MWPVL's status column across captures", "How many sites each archived capture of MWPVL's Amazon table lists as active, planned, delayed, on hold or subleased. Counts are of listings in the table, not of confirmed openings or closures, and the table's coverage and layout changed over the years.");
A.estimate(sSt, "<b>Captures excluded.</b> " + (partK.length ? partK.length + " captures list far fewer sites than their neighbours, which indicates an incomplete read of the archived page, and are left out of the lines: " + partK.map(function (d) { return d + " (" + partial[d] + ")"; }).join("; ") + "." : "No capture was left out.") + " Captures up to 2016-02-24 are read from the page's text table; later captures are read from the page's table images, so site counts there depend on that reading. Rows without a site code (" + A.fmt(sbs.filter(function (r) { return r.snapshot_date === snapDates[snapDates.length - 1]; }).reduce(function (s, r) { return s + (+r.rows_without_code || 0); }, 0)) + " in the latest capture, " + snapDates[snapDates.length - 1] + ") are not counted. The table includes more than fulfillment centers (delivery stations, sort centers, cross-docks, air hubs, food and other sites).");
var eraOf = {}; sbs.forEach(function (r) { eraOf[r.snapshot_date] = r.era; });
function sline(st, name, color, dash, imgOnly) { return { name: name, color: color, dash: dash, points: snapDates.map(function (d) { return [dec(d), partial[d] || (imgOnly && eraOf[d] === "text") ? null : stSum(d, st), "Capture " + d]; }) }; }
A.mount(sSt, '<div class="cols2" id="sbs"></div>');
A.lineChart("#sbs", { title: "Sites listed as active or planned, by capture date", yFmt: function (v) { return A.fmt(v); }, yMin: 0, xFmt: function (v) { return String(Math.floor(v + .02)); },
  series: [sline("active", "Active", "var(--t1)"), sline("planned", "Planned", "var(--t3)", "5 3")],
  caption: "Data: <span class=\"mono\">AMZ_MWPVL.status_by_snapshot</span> (assets/data_mwpvl.js; file data/processed/mwpvl_wayback_facts.csv and mwpvl_wayback_image_facts.csv), columns snapshot_date, status, sites summed over table types. Original source: " + A.esc(MWATTR) + "." });
A.lineChart("#sbs", { title: "Sites listed as delayed, on hold or sublease, by capture date", yFmt: function (v) { return A.fmt(v); }, yMin: 0, xFmt: function (v) { return String(Math.floor(v + .02)); },
  series: [sline("delayed", "Delayed", "var(--t2)", null, 1), sline("on_hold", "On hold", "var(--t4)", "5 3", 1), sline("sublease", "Sublease", "var(--t5)", "2 3", 1)],
  caption: "Same source and columns. Captures read from the text table (to 2016-02-24) carry no delay, hold or sublease flag and are not plotted; in later captures a zero means no site carried the flag." });
A.mount(sSt, '<details class="tv"><summary>Table view: sites by status and capture</summary><div class="tw simple"><table><thead><tr><th>Capture</th><th>Read from</th><th class="n">Active</th><th class="n">Planned</th><th class="n">Delayed</th><th class="n">On hold</th><th class="n">Sublease</th><th>Note</th></tr></thead><tbody>' +
  snapDates.map(function (d) { var era = (sbs.filter(function (r) { return r.snapshot_date === d; })[0] || {}).era; return "<tr><td>" + d + "</td><td>" + (era === "text" ? "text table" : "table image") + '</td><td class="n">' + ["active", "planned", "delayed", "on_hold", "sublease"].map(function (st) { return A.fmt(stSum(d, st)); }).join('</td><td class="n">') + "</td><td>" + (partial[d] ? "likely incomplete read, not charted" : "") + "</td></tr>"; }).join("") + "</tbody></table></div></details>");
cite(sSt, "<span class=\"mono\">AMZ_MWPVL.status_by_snapshot</span> and <span class=\"mono\">AMZ_MWPVL.snapshots</span> (assets/data_mwpvl.js).", A.esc(MWATTR) + ".");

/* ---- facility events ---- */
var evs = A.rows(EVD.events).map(function (r) { r.when = r.opening_date || r.announced_date || r.article_date || ""; return r; });
var sEv = A.section(app, "events", "Facility events in the press and databases", "Openings, announcements and related events that publications and business databases reported for Amazon sites. Each row is one report, cited by publication and date; the same event can appear in several rows. A row is joined to a roster site only when the match is exact or probable.");
A.estimate(sEv, "<b>Reported, not verified.</b> " + A.fmt(evs.length) + " rows; " + A.fmt(evs.filter(function (r) { return r.match_quality === "exact" || r.match_quality === "probable"; }).length) + " matched to a roster site, " + A.fmt(evs.filter(function (r) { return r.confidence === "low"; }).length) + " low confidence (title or snippet only). Rows give the event date as the publication stated it (some are month or year only); passages from articles are not reproduced.");
var mqs = Object.keys(evs.reduce(function (o, r) { o[r.match_quality || "none"] = 1; return o; }, {})).sort();
A.mount(sEv, '<div class="tlf"><label>Search <input id="evq" type="search" placeholder="city, state, publication" aria-label="Search events"></label><label>Roster match <select id="evm"><option value="">all</option>' + mqs.map(function (q) { return '<option>' + A.esc(q) + "</option>"; }).join("") + '</select></label><label>Confidence <select id="evc"><option value="">all</option><option>high</option><option>medium</option><option>low</option></select></label><span class="lcount" id="evn"></span></div><div id="evt"></div>');
var evT = A.table("#evt", { rows: evs, pageSize: 15, sort: "when", dir: -1, cols: [
  { key: "when", label: "Event date" }, { key: "city", label: "City" }, { key: "state", label: "State" }, { key: "facility_type", label: "Type" },
  { key: "sq_ft", label: "Sq ft", num: true, fmt: function (v) { return A.fmt(v); } }, { key: "match_site_code", label: "Roster site" }, { key: "match_quality", label: "Match" }, { key: "confidence", label: "Confidence" },
  { key: "sources", label: "Source (publication, date, via database)", html: function (v, r) { return /^https?:/.test(String(r.article_url || "")) ? '<a href="' + A.esc(r.article_url) + '" target="_blank" rel="noopener">' + A.esc(v) + "</a>" : A.esc(v); } }] });
function evFilter() {
  var q = A.$("#evq").value.toLowerCase().trim(), m = A.$("#evm").value, c = A.$("#evc").value;
  var r = evs.filter(function (x) { return (!m || (x.match_quality || "none") === m) && (!c || x.confidence === c) && (!q || [x.city, x.state, x.publication, x.facility_type, x.match_site_code].join(" ").toLowerCase().indexOf(q) >= 0); });
  evT.setRows(r); A.$("#evn").textContent = A.fmt(r.length) + " of " + A.fmt(evs.length) + " rows";
}
["#evq", "#evm", "#evc"].forEach(function (s) { A.$(s).addEventListener("input", evFilter); });
evFilter();
cite(sEv, "<span class=\"mono\">AMZ_EVENTS.events</span> (assets/data_events.js; file data/processed/facility_events_all.csv), columns opening_date, announced_date, article_date, city, state, facility_type, sq_ft, match_site_code, match_quality, confidence, sources.", "the publications named in each row (links shown where the article is public).");

/* ---------- logistics acquisitions and investments (public citations; AMZ_DEALS) ---------- */
(function () {
  if (typeof AMZ_DEALS === "undefined") return;
  var all = A.rows(AMZ_DEALS.deals).filter(function (r) { return r.peer_group === "amazon"; });
  var CATL = { robotics: "Warehouse robotics and automation", last_mile: "Last-mile and delivery", vehicles: "Delivery vehicles and autonomy", air: "Air", real_estate: "Warehouse and land purchases", software: "Software", other: "Other" };
  var cats = Object.keys(CATL).filter(function (c) { return all.some(function (r) { return r.category === c; }); });
  var sD = A.section(app, "deals", "Amazon's logistics acquisitions and investments", "Deals that Amazon (or one of its investment funds) made in logistics-related companies and property, 2012 to 2026, listed only where a public source (company release, filing or press article) reports the deal. Each row cites that public source first; the commercial deal database consulted through the Johns Hopkins University Libraries is named second and is not redistributed.");
  A.estimate(sD, "<b>Not a complete list.</b> " + A.fmt(all.length) + " deals with a public source found. It leaves out deals no public source could be matched to, the Industrial Innovation Fund's full portfolio (the database does not list the fund as an entity) and delivery-van stakes other than Rivian. Years come from the matched record and can differ by a few months from the announcement. Amounts are shown only where the cited page states them, and are the size of the round or purchase, not necessarily Amazon's share. Property purchases are not all confirmed as logistics sites.");
  A.mount(sD, '<div class="cols2" id="dealc"></div>');
  var yrs = []; for (var y = 2012; y <= 2026; y++) yrs.push(y);
  A.lineChart("#dealc", { title: "Public logistics deals by year, by category (count)", yFmt: function (v) { return A.fmt(v); },
    series: cats.map(function (c, i) { return { name: CATL[c], color: "var(--t" + ((i % 5) + 1) + ")", points: yrs.map(function (y) { return [y, all.filter(function (r) { return r.category === c && r.year === y; }).length]; }) }; }),
    caption: "Data: <span class=\"mono\">AMZ_DEALS.deals</span> (assets/data_deals.js; file data/processed/logistics_deals_public.csv), Amazon rows only. Original sources: the public page cited in each row." });
  A.mount(sD, '<div class="ctl"><label>Category <select id="dealcat"><option value="">All categories</option>' + cats.map(function (c) { return '<option value="' + c + '">' + A.esc(CATL[c]) + " (" + all.filter(function (r) { return r.category === c; }).length + ")</option>"; }).join("") + "</select></label></div>");
  var host = document.createElement("div"); sD.appendChild(host);
  var tb = A.table(host, { sort: "year", pageSize: 15, rows: all, cols: [
    { key: "year", label: "Year" }, { key: "target", label: "Target or asset" }, { key: "category", label: "Category", fmt: function (v) { return CATL[v] || v; } },
    { key: "deal_type", label: "Type" }, { key: "actor", label: "Through" },
    { key: "amount_usd", label: "Amount stated in source (USD m)", num: true, fmt: function (v) { return v == null ? "" : A.fmt(v / 1e6, v < 1e7 ? 1 : 0); } },
    { key: "source_publisher", label: "Public source", html: function (v, r) { return a(r.source_url, v); } },
    { key: "source_type", label: "Source kind", fmt: function (v) { return v === "primary" ? "company or filing" : v === "press" ? "news" : "other"; } }] });
  A.$("#dealcat").addEventListener("change", function () { var c = this.value; tb.setRows(c ? all.filter(function (r) { return r.category === c; }) : all); });
  cite(sD, "<span class=\"mono\">AMZ_DEALS.deals</span> (data/processed/logistics_deals_public.csv). Each row's citation reads \"public source; also PitchBook (via JHU Libraries)\".", "the public page linked in each row; PitchBook (via Johns Hopkins University Libraries) as a second source, not redistributed.");
})();

/* ---------- sources ---------- */
var s8 = A.section(app, "src", "Sources for this page");
A.sources(s8, "logistics");
A.sources(s8, "population");
A.sources(s8, "industry");
A.sources(s8, [
  { label: "MWPVL International (Marc Wulfraat), Amazon fulfillment network table, " + A.fmt(msn.length) + " archived captures " + msnFirst + " to " + msnLast, url: "https://www.mwpvl.com/html/amazon_com.html", publisher: "MWPVL International, read from the Internet Archive Wayback Machine", note: "Openings by year, status by capture and dropped-from-list pullback rows. MWPVL's own compilation, includes planned sites; MWPVL asks that its table not be copied wholesale, so only derived counts are shown." },
  { label: "Pullback tallies and site rows (closures, cancellations, delays, subleases)", url: "sources.html", publisher: "publications named per row, plus MWPVL via the Wayback Machine", note: "Cited by publication, date and title; subscription databases are named only as the access route." },
  { label: "Facility events (openings and announcements reported by publications and business databases)", url: "sources.html", publisher: "publications named per row", note: "Reported, not verified; no article passages reproduced." },
  { label: "Logistics acquisitions and investments (public citations)", url: "sources.html", publisher: "company releases, SEC filings and press named per row; PitchBook via Johns Hopkins University Libraries as second source", note: "Citations only; the database is not redistributed. Not a complete list." },
  { label: "Market context: parcel share and volume, Amazon share of UPS revenue", url: "sources.html", publisher: "Pitney Bowes, IBISWorld (citing ShipMatrix), Market Share Reporter, UPS, Financial Times, The Insight Partners", note: "Each row's citation is in the table view of the market section." }]);
})();
