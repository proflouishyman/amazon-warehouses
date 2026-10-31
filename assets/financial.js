/* financial.html: subsidies, database cross-check and market context sections.
   Reads window.AMZ_SUB (data_subsidies.js), AMZ_MARKET (data_market.js), AMZ_FIN (data_financial.js).
   Called from the page script: FIN_SUBS(app, {src, dtable}). No data is hand-coded here except prose labels. */
(function () {
"use strict";
var A = window.AMZ;
var CLASS_LABEL = { direct: "Direct to Amazon or its developer", infrastructure: "Public infrastructure", no_incentive_found: "No incentive found (search finding)" };
var BASIS_LABEL = { announced_max: "Announced maximum", estimated_value: "Estimated value", realized: "Realized", annual: "Annual amount" };
var BASIS_HELP = { announced_max: "a stated cap or announced package", estimated_value: "a projected value of an abatement, PILOT or credit", realized: "an amount reported as actually forgone or paid", annual: "a per-year amount" };
var COV_LABEL = { awards_with_amount: "Awards found, with a dollar amount", awards_without_amount: "Awards found, no dollar amount", partial_search_only: "Partial search only, no award found", searched_none: "Searched, none found (not a proven zero)" };
var COV_COLOR = { awards_with_amount: "var(--cat2)", awards_without_amount: "var(--cat5)", partial_search_only: "var(--cat6)", searched_none: "var(--cat3)" };
var COV_ORDER = ["awards_with_amount", "awards_without_amount", "partial_search_only", "searched_none"];
var CLASS_ORDER = ["direct", "infrastructure", "no_incentive_found"], BASIS_ORDER = ["announced_max", "estimated_value", "realized", "annual"];

function usd(v) { return v == null ? "" : "$" + A.fmt(v); }
function usdC(v) { return v == null ? "" : "$" + A.compact(v); }
function host(u) { try { return new URL(u).hostname.replace(/^www\./, ""); } catch (e) { return "source"; } }
function safeUrl(u) { return typeof u === "string" && /^https?:\/\//.test(u) && !/proxy|ezproxy/i.test(u); }
function trunc(s, n) { s = String(s == null ? "" : s); return s.length > n ? s.slice(0, n - 1) + "…" : s; }
function num(v) { var x = parseFloat(v); return isNaN(x) ? null : x; }
function sel(id, label, opts) { return '<label>' + A.esc(label) + ' <select id="' + id + '">' + opts.map(function (o) { return '<option value="' + A.esc(o[0]) + '">' + A.esc(o[1]) + "</option>"; }).join("") + "</select></label>"; }

window.FIN_SUBS = function (app, H) {
  var S = window.AMZ_SUB, M = window.AMZ_MARKET, F = window.AMZ_FIN;
  if (!S) { A.mount(app, '<p class="note">Subsidy data file did not load.</p>'); return; }
  var awards = A.rows(S.awards), totals = A.rows(S.totals), summary = A.rows(S.summary), cov = A.rows(S.coverage), classes = A.rows(S.classes);
  function tot(c, b, v) { return totals.filter(function (r) { return r.recipient_class === c && r.amount_basis === b && r.verification === v; })[0]; }
  var covCount = {}; cov.forEach(function (r) { covCount[r.coverage] = (covCount[r.coverage] || 0) + 1; });
  var withAwards = cov.filter(function (r) { return r.award_rows > 0; }).length;
  var excl = S.excluded_from_totals || {};

  /* ===== subsidies ===== */
  var s6 = A.section(app, "subs", "Public subsidies",
    "State and local incentives tied to Amazon facilities, collected state by state from official records first (agency releases, development-authority and council agendas, state datasets) and then press. Every row keeps its source link. This is a floor, not a census: no state is marked complete. Amounts are never added across amount bases, because an announced maximum, a projected value and a realized amount measure different things.");

  var t1 = tot("direct", "announced_max", "verified"), t2 = tot("direct", "estimated_value", "verified"), t3 = tot("direct", "realized", "verified"), t4 = tot("infrastructure", "announced_max", "verified");
  A.tiles(s6, [
    { value: usdC(t1.amount_usd), label: "Direct, announced maximum, verified", context: t1.rows + " rows. A cap, not money paid. AMZ_SUB.totals" },
    { value: usdC(t2.amount_usd), label: "Direct, estimated value, verified", context: t2.rows + " rows. Projections. AMZ_SUB.totals" },
    { value: usdC(t3.amount_usd), label: "Direct, realized, verified", context: t3.rows + " rows. Amounts recorded as forgone or paid. AMZ_SUB.totals" },
    { value: usdC(t4.amount_usd), label: "Public infrastructure, announced maximum, verified", context: t4.rows + " rows. Money for roads or utilities, not a payment to Amazon. AMZ_SUB.totals" },
    { value: withAwards + " of " + cov.length, label: "States with at least one award row", context: A.fmt(awards.length) + " award rows in all. AMZ_SUB.coverage" }
  ]);
  A.mount(s6, '<p class="cap">The first four tiles are separate bases and classes. They are not added together and must not be. Verified means primary or secondary verification level. AMZ_SUB.totals, rows with verification = verified.</p>');

  A.caveat(s6, "<b>Read these before using any number below.</b><ul>" +
    "<li><b>Announced maximum is not money received.</b> It is the cap or package figure stated when an incentive was approved. Realized amounts are the few cases where a record shows what was actually forgone or paid; they are far fewer than announced figures.</li>" +
    "<li><b>Coverage is a floor.</b> " + A.fmt(covCount.awards_with_amount || 0) + " states have awards with an amount, " + (covCount.awards_without_amount || 0) + " has awards without an amount, " + (covCount.partial_search_only || 0) + " were only partly searched with nothing found, and " + (covCount.searched_none || 0) + " were searched with none found on secondary evidence. No state is marked complete. A missing award means not found, not none exists.</li>" +
    "<li><b>Many primary records carry no amount</b> (for example abatements and credits whose value the agency does not publish), so they appear in the coverage counts but not in the dollar totals.</li>" +
    "<li><b>Rows can overlap.</b> Several rows may describe parts of one package. Overlap-flagged rows are counted in each total, and their count and amount are shown beside it. Totals can therefore overstate a package.</li>" +
    "<li><b>Unverified rows</b> are shown only where labelled and are left out of the verified totals. " + A.fmt(S.withheld ? S.withheld.rows : 0) + " rows that rested only on a snippet of a third-party tracker are withheld from this page entirely.</li>" +
    "<li><b>Recipient class is a rule, not a legal finding.</b> Money for roads or utilities that went to a public body is classed as infrastructure; the rule is under the table. Some direct rows also name infrastructure in a bundled package (flagged in the data as recipient_mixed).</li></ul>");

  /* -- coverage map -- */
  var covBy = {}; cov.forEach(function (r) { covBy[r.state] = r; });
  A.mount(s6, "<h3>State coverage</h3>");
  A.usMap(s6, {
    label: "Map of states by subsidy search coverage",
    fill: function (k) { var r = covBy[k]; return r ? COV_COLOR[r.coverage] : null; },
    stateTip: function (k, name) { var r = covBy[k]; if (!r) return "<b>" + A.esc(name) + "</b><br>Not in coverage table"; return "<b>" + A.esc(name) + "</b><br>" + A.esc(COV_LABEL[r.coverage]) + "<br>Award rows: " + r.award_rows + " (with amount " + r.awards_with_amount + ", verified " + r.awards_verified + ")<br>Direct " + r.awards_direct + ", infrastructure " + r.awards_infrastructure + "<br>Search-only rows: partial " + r.partial_search_rows + ", none found " + r.searched_none_rows; },
    caption: "Source: AMZ_SUB.coverage (state, coverage). Hover a state for its counts. State search was done from official records and press in 2026; see the notes in the Methods page."
  });
  A.mount(s6, '<div class="legend">' + COV_ORDER.map(function (k) { return '<span><i class="sw" style="background:' + COV_COLOR[k] + '"></i>' + A.esc(COV_LABEL[k]) + ": " + (covCount[k] || 0) + " states</span>"; }).join("") + "</div>");
  A.mount(s6, '<p class="cap">Search-only marker rows (' + A.fmt(excl.partial_search || 0) + " partial-search, " + A.fmt(excl.searched_none || 0) + " searched-none) are excluded from every dollar total. Colour is not the only code: the table below lists the same status in text for every state.</p>");
  H.src(s6, "data/processed/subsidies_verified.csv, via AMZ_SUB.coverage", "state and local government records and press, per row; see the source links in the awards table. Compiled by this project; Good Jobs First's tracker was not obtained.");
  var covRows = cov.slice().sort(function (a, b) { return COV_ORDER.indexOf(a.coverage) - COV_ORDER.indexOf(b.coverage) || (b.award_rows - a.award_rows) || (a.state < b.state ? -1 : 1); });
  H.dtable(s6, [{ k: "state", l: "State" }, { k: "coverage", l: "Status", f: function (v) { return COV_LABEL[v] || v; } }, { k: "award_rows", l: "Award rows", n: 1 }, { k: "awards_with_amount", l: "With amount", n: 1 }, { k: "awards_verified", l: "Verified", n: 1 }, { k: "awards_direct", l: "Direct", n: 1 }, { k: "awards_infrastructure", l: "Infra.", n: 1 }, { k: "partial_search_rows", l: "Partial-search rows", n: 1 }, { k: "searched_none_rows", l: "Searched-none rows", n: 1 }], covRows);

  /* -- totals by class and basis -- */
  A.mount(s6, "<h3>Totals by recipient class and amount basis</h3>");
  var trs = "";
  CLASS_ORDER.forEach(function (c) {
    BASIS_ORDER.forEach(function (b) {
      var v = tot(c, b, "verified"), a = tot(c, b, "all");
      if (!v && !a) return;
      v = v || { rows: 0, amount_usd: 0, rows_overlap_flagged: 0, amount_overlap_flagged: 0 }; a = a || { rows: 0, amount_usd: 0 };
      trs += "<tr><td>" + A.esc(CLASS_LABEL[c]) + "</td><td>" + A.esc(BASIS_LABEL[b]) + '</td><td class="n">' + A.fmt(v.rows) + '</td><td class="n">' + usd(v.amount_usd) + '</td><td class="n">' + A.fmt(v.rows_overlap_flagged) + " / " + usd(v.amount_overlap_flagged) + '</td><td class="n">' + A.fmt(a.rows) + '</td><td class="n">' + usd(a.amount_usd) + "</td></tr>";
    });
  });
  A.mount(s6, '<div class="tw"><table><thead><tr><th>Recipient class</th><th>Amount basis</th><th class="n">Verified rows</th><th class="n">Verified USD</th><th class="n">Of which overlap-flagged (rows / USD)</th><th class="n">All rows incl. unverified</th><th class="n">All USD</th></tr></thead><tbody>' + trs + "</tbody></table></div>");
  A.mount(s6, '<p class="cap">There is deliberately no grand total. Each line is one class and one basis; ' + BASIS_ORDER.map(function (b) { return A.esc(BASIS_LABEL[b].toLowerCase()) + " is " + BASIS_HELP[b]; }).join("; ") + ". Overlap-flagged rows are included in the verified and all columns.</p>");
  H.src(s6, "data/processed/subsidies_verified.csv, summarised in AMZ_SUB.totals (fields recipient_class, amount_basis, verification, rows, amount_usd, rows_overlap_flagged, amount_overlap_flagged)", "per-row sources listed in the awards table below. Reconciles to data/processed/subsidies_verified_summary.csv by basis and verification level.");
  A.mount(s6, '<details class="dt"><summary>How recipient class is assigned</summary><ol class="rule">' + (S.rule || []).map(function (r) { return "<li>" + A.esc(r) + "</li>"; }).join("") + '</ol><p class="cap">AMZ_SUB.rule. First matching rule wins. Classes by verification level (AMZ_SUB.classes): ' + classes.map(function (r) { return A.esc(CLASS_LABEL[r.recipient_class] || r.recipient_class) + " " + A.esc(r.verification_level) + " " + r.award_rows; }).join("; ") + ".</p></details>");

  /* -- controls, bars and table (one basis at a time) -- */
  A.mount(s6, "<h3>By state and by award</h3>");
  A.mount(s6, '<div class="bar finctl">' + sel("fc-class", "Recipient class", [["direct", CLASS_LABEL.direct], ["infrastructure", CLASS_LABEL.infrastructure]]) +
    sel("fc-basis", "Amount basis", [["announced_max", BASIS_LABEL.announced_max], ["estimated_value", BASIS_LABEL.estimated_value], ["realized", BASIS_LABEL.realized], ["annual", BASIS_LABEL.annual]]) +
    sel("fc-ver", "Verification", [["verified", "Verified (primary or secondary)"], ["all", "All, including unverified"]]) + "</div>");
  var barsHost = document.createElement("div"); barsHost.id = "fin-bars"; s6.appendChild(barsHost);
  var tblHost = document.createElement("div"); tblHost.id = "fin-awards"; s6.appendChild(tblHost);
  var tbl = null;
  function pick() { return { c: A.$("#fc-class").value, b: A.$("#fc-basis").value, v: A.$("#fc-ver").value }; }
  function okVer(v, lvl) { return v === "all" || lvl === "primary" || lvl === "secondary"; }
  function render() {
    var p = pick();
    var by = {};
    summary.forEach(function (r) { if (r.recipient_class === p.c && r.amount_basis === p.b && okVer(p.v, r.verification_level) && r.amount_usd) by[r.state] = (by[r.state] || 0) + r.amount_usd; });
    var items = Object.keys(by).map(function (k) { return { label: ((window.AMZ_GEO && AMZ_GEO.states[k]) ? AMZ_GEO.states[k].name : k), value: by[k], color: p.c === "direct" ? "var(--cat1)" : "var(--cat2)", note: "Rows in state: " + (cov.filter(function (r) { return r.state === k; })[0] || {}).award_rows } ; }).sort(function (a, b) { return b.value - a.value; });
    var shown = items.slice(0, 15), sum = items.reduce(function (s, d) { return s + d.value; }, 0);
    barsHost.innerHTML = "";
    if (!items.length) { barsHost.innerHTML = '<p class="note">No rows with an amount for this combination.</p>'; }
    else A.barChart(barsHost, { title: BASIS_LABEL[p.b] + ", " + CLASS_LABEL[p.c] + ", by state (top " + shown.length + " of " + items.length + " states)", items: shown, valFmt: usdC, labelWidth: 130,
      caption: "All " + items.length + " states with an amount sum to " + usd(sum) + " on this one basis. " + (p.v === "verified" ? "Primary and secondary rows only. " : "Includes unverified rows. ") + "Source: AMZ_SUB.summary (state, recipient_class, amount_basis, verification_level, amount_usd). Overlap-flagged rows are included." });
    var rows = awards.filter(function (r) { return r.recipient_class === p.c && r.amount_basis === p.b && r.amount_usd != null && okVer(p.v, r.verification_level); });
    A.$("#fin-awards-count") && (A.$("#fin-awards-count").textContent = A.fmt(rows.length) + " rows");
    if (!tbl) {
      tbl = A.table(tblHost, { rows: rows, pageSize: 15, sort: "amount_usd", dir: -1, cols: [
        { key: "state", label: "State" }, { key: "locality", label: "Locality", fmt: function (v) { return trunc(v, 40); } },
        { key: "program", label: "Program", fmt: function (v) { return trunc(v, 110); } },
        { key: "award_year", label: "Year", num: 1 }, { key: "amount_usd", label: "Amount", num: 1, fmt: usd },
        { key: "verification_level", label: "Verification" },
        { key: "overlap_flag", label: "Overlaps another row", fmt: function (v) { return v ? "yes" : "no"; } },
        { key: "source_url", label: "Source", html: function (v, r) { return safeUrl(v) ? '<a href="' + A.esc(v) + '" target="_blank" rel="noopener">' + A.esc(host(v)) + "</a>" + (r.issuer ? '<br><span class="muted">' + A.esc(trunc(r.issuer, 70)) + "</span>" : "") : "none"; } }
      ] });
    } else tbl.setRows(rows);
  }
  ["fc-class", "fc-basis", "fc-ver"].forEach(function (id) { A.$("#" + id).addEventListener("change", render); });
  render();
  A.mount(s6, '<p class="cap">Largest awards for the class, basis and verification level selected above, sortable by any column header. Source: AMZ_SUB.awards (fields state, locality, program, award_year, amount_usd, amount_basis, verification_level, overlap_flag, source_url, issuer). Source links go to the public page the row was taken from. Amounts are as stated there; a row marked overlap shares money with another row.</p>');
  A.mount(s6, '<p class="est"><b>One known edge case.</b> The Jefferson County, Alabama $3.3m incentive package is typed as infrastructure in the source data, but its program text does not itself say so. Recipient class trusts the recorded subsidy type.</p>');

  /* ===== database cross-check ===== */
  var s7 = A.section(app, "xcheck", "Cross-check against subscription databases",
    "The 10-K transcriptions on this page were compared with figures in three licensed financial databases. The comparison agreed. It also found one error in our data and one definitional difference, both described here.");
  A.mount(s7, '<div class="tw"><table><thead><tr><th>Database</th><th>What was compared</th><th>Result</th></tr></thead><tbody>' +
    "<tr><td>Mergent Archives, scanned Amazon.com Inc annual reports</td><td>54 values (net sales, fulfillment expense, operating and net income, shipping revenue and net shipping cost, purchases of property and equipment, PP&amp;E net, finance-lease and segment square-footage items) for FY1999, FY2002 to FY2004 and FY2020 to FY2022</td><td>47 equal, 6 equal after rounding, 1 definitional difference: FY1999 fulfillment expense appears as $188.4m in the FY1999 10-K and $237.3m after the later restatement. This page uses the restated figure and says so.</td></tr>" +
    "<tr><td>S&amp;P Capital IQ (NetAdvantage), Financials As Presented</td><td>35 values for FY2021 to FY2025: net sales, fulfillment expense, operating income, net income, gross capital expenditure, proceeds from PP&amp;E sales and incentives, PP&amp;E net</td><td>All 35 agree with this page's files.</td></tr>" +
    "<tr><td>D&amp;B Hoovers (Morningstar standardized financials)</td><td>75 values for FY2016 to FY2025: net sales, operating income, net income, gross and net purchases of property and equipment, PP&amp;E net and gross, employees</td><td>64 agree. 1 error in this project's data: FY2016 gross purchases of property and equipment had been entered as the net figure; it is corrected (see the capital-spending chart). 10 PP&amp;E values for FY2019 on differ by definition: the database's PP&amp;E appears to include operating-lease right-of-use assets, which the 10-K line used here excludes.</td></tr>" +
    "</tbody></table></div>");
  A.mount(s7, '<p class="cap">Counts were read from this project\'s private cross-check extracts and are stated here as facts, not republished data. Sources: Amazon.com Inc, Annual/10K Report, fiscal years 1999, 2002 to 2004 and 2020 to 2022 (via Mergent Archives); S&amp;P Capital IQ Financials As Presented (annual), retrieved 2026-10-31 (via S&amp;P Capital IQ NetAdvantage); D&amp;B Hoovers, Amazon.com Inc standardized annual financials, retrieved 2026-10-31 (via Hoovers Online). The underlying 10-Ks are on SEC EDGAR.</p>');
  var cap16 = A.rows(F.capex).filter(function (r) { return r.fiscal_year === 2016; })[0];
  A.caveat(s7, "<b>Correction made: FY2016 capital spending.</b> The cross-check showed that an earlier value of $" + A.fmt(cap16.purchases_net_of_proceeds_incentives_usd_m) + "m, the figure the FY2016 10-K labels as net, had been entered as gross. Gross purchases of property and equipment are $" + A.fmt(cap16.purchases_of_ppe_gross_usd_m) + "m (the purchases line in the FY2017 10-K comparative cash flow statement), and $" + A.fmt(cap16.purchases_net_of_proceeds_incentives_usd_m) + "m is the net-of-incentives figure. The capital-spending chart above uses the corrected values. AMZ_FIN.capex, fiscal_year 2016.");
  var ppe = A.rows(F.ppe).filter(function (r) { return r.fixed_assets_net_usd_m != null; });
  A.lineChart(s7, { title: "Property and equipment, net, year end, USD billions (excludes operating-lease right-of-use assets)", series: [{ name: "Property and equipment, net (10-K balance sheet)", color: "var(--cat1)", points: ppe.map(function (r) { return [r.fiscal_year, r.fixed_assets_net_usd_m / 1000]; }) }], yFmt: function (v) { return "$" + A.fmt(v, 0) + "bn"; }, xFmt: String, height: 240, yMin: 0 });
  H.src(s7, "data/processed/amazon_ppe_year_end.csv (AMZ_FIN.ppe, columns fixed_assets_net_usd_m and basis)", H.tenk + ", balance sheets.");
  A.caveat(s7, "<b>PP&amp;E is not comparable with database figures from 2019.</b> This page uses the 10-K 'property and equipment, net' line, which excludes operating-lease right-of-use assets. Database PP&amp;E series that add those assets are higher from 2019 onward (after the leasing standard took effect). That is a definitional difference, not an error in either source, and it matters for Amazon because most of its warehouse space is leased.");

  /* ===== market context ===== */
  var s8 = A.section(app, "market", "Market context: landlords and carriers",
    "Two outside measures of how large Amazon is as a customer: the share of Prologis's rent that comes from Amazon, and Amazon's share of UPS revenue. They are context for the network, not measures of Amazon's own spending.");
  if (!M) { A.mount(s8, '<p class="note">Market data file did not load.</p>'); return; }
  var mr = A.rows(M.rows);
  function ms(topic, test) { return mr.filter(function (r) { return r.topic === topic && test(r) && num(r.value) != null; }).sort(function (a, b) { return a.year - b.year; }); }
  function mp(rows) { return rows.map(function (r) { return [r.year, num(r.value), r.citation]; }); }
  var pCons = ms("prologis_amazon_rent_share", function (r) { return /consolidated/.test(r.measure); });
  var pOwn = ms("prologis_amazon_rent_share", function (r) { return /owned and managed/.test(r.measure); });
  var pVL = ms("prologis_amazon_rent_share", function (r) { return /Value Line/.test(r.measure); });
  var rank = mr.filter(function (r) { return r.topic === "prologis_amazon_rent_share" && /rank/.test(r.measure); });
  var rankAll1 = rank.length > 0 && rank.every(function (r) { return num(r.value) === 1; });
  A.lineChart(s8, { title: "Amazon share of Prologis net effective rent, percent", series: [
    { name: "Consolidated (Prologis 10-K)", color: "var(--cat1)", points: mp(pCons) },
    { name: "Owned and managed (Prologis 10-K)", color: "var(--cat2)", points: mp(pOwn) },
    { name: "As shown by Value Line", color: "var(--cat3)", dash: "5 4", points: mp(pVL) }],
    yFmt: function (v) { return v.toFixed(0) + "%"; }, xFmt: String, height: 270, yMin: 0,
    caption: "Prologis publishes two measures and does not report the owned-and-managed one every year, so that line has gaps. Value Line's 2022 figure equals the owned-and-managed measure; its later years extend the series but are Value Line's own." + (rankAll1 ? " Amazon ranked first among Prologis's top customers in every 10-K from FY" + rank[0].year + " to FY" + rank[rank.length - 1].year + "." : "") });
  H.src(s8, "data/processed/market_context.csv (AMZ_MARKET.rows, topic prologis_amazon_rent_share)", "Prologis Inc, annual reports (Form 10-K), FY2015 to FY2022 (via Mergent Archives); Value Line Investment Survey, Prologis (NYSE-PLD), 2023-03-31, 2024-03-29, 2025-03-28 and 2026-09-25 (via Value Line). It is Prologis's rent roll, not a measure restricted to US sites.");
  H.dtable(s8, [{ k: "year", l: "Year" }, { k: "measure", l: "Measure" }, { k: "value", l: "Value", n: 1 }, { k: "unit", l: "Unit" }, { k: "citation", l: "Citation" }], mr.filter(function (r) { return r.topic === "prologis_amazon_rent_share"; }));

  var upsAll = mr.filter(function (r) { return r.topic === "amazon_share_of_ups_revenue"; });
  var upsPts = {}; ms("amazon_share_of_ups_revenue", function (r) { return !/Financial Times/.test(r.citation); }).forEach(function (r) { upsPts[r.year] = r; });
  var upsRows = Object.keys(upsPts).map(function (y) { return upsPts[y]; });
  var below = upsAll.filter(function (r) { return /^</.test(String(r.value)); });
  A.lineChart(s8, { title: "Amazon share of UPS consolidated revenue, percent", series: [{ name: "Amazon share of UPS revenue", color: "var(--cat1)", points: mp(upsRows) }],
    yFmt: function (v) { return v.toFixed(0) + "%"; }, xFmt: String, height: 240, yMin: 0,
    caption: below.map(function (r) { return r.year + ": UPS reported no single customer at or above 10 percent, so no point is plotted."; }).join(" ") + " 2024 is plotted from The Insight Partners (11.8); a Financial Times figure for the same year is 12, rounded. Years differ in source; hover a point for its citation." });
  H.src(s8, "data/processed/market_context.csv (AMZ_MARKET.rows, topic amazon_share_of_ups_revenue)", "United Parcel Service Inc, annual reports (Form 10-K) (via Mergent Archives) for 2019 to 2022; The Insight Partners, 2026-03, Global & United States Outsourcing Contract Logistics Market to 2031 (via ProQuest Business Market Research Collection) for 2023 and 2024; IBISWorld, Couriers & Local Delivery Services in the US (49222), Jul 2026, and CFRA Equity Research, 2026-10-27, United Parcel Service, Inc. (via MyIBISWorld and S&P Capital IQ) for 2025. Sources differ by year and are not one consistent series.");
  H.dtable(s8, [{ k: "year", l: "Year" }, { k: "value", l: "Value (%)", n: 1 }, { k: "basis", l: "Basis" }, { k: "citation", l: "Citation" }, { k: "note", l: "Note" }], upsAll.slice().sort(function (a, b) { return a.year - b.year; }));
};
})();
