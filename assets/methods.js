/* methods.html: sections on MWPVL, year basis, pullback, subsidies, benchmark matching and database cross-checks.
   Runs after the inline script of methods.html. Figures come from the data globals where one exists
   (AMZ_MWPVL, AMZ_FAC, AMZ_PULL, AMZ_SUB, AMZ_BENCH); the few that exist only in the build notes are
   labelled with their file. */
(function () {
"use strict";
var A = window.AMZ, E = A.esc, F = A.fmt;
var app = A.$("#app");
var MW = window.AMZ_MWPVL, FAC = window.AMZ_FAC, PU = window.AMZ_PULL, SU = window.AMZ_SUB, BE = window.AMZ_BENCH;

function sec(id, title, html) {
  var b = A.section(app, id, title);
  var d = document.createElement("div"); d.className = "mx"; d.innerHTML = html; b.appendChild(d);
  return d;
}
function srcline(html) { return '<p class="srcline"><b>Source.</b> ' + html + "</p>"; }
function tbl(caption, heads, rows, numFrom) {
  numFrom = numFrom == null ? 99 : numFrom;
  return '<div class="twrap">' + (caption ? '<p class="cap">' + caption + "</p>" : "") + '<div class="tw"><table><thead><tr>' +
    heads.map(function (h, i) { return '<th class="' + (i >= numFrom ? "n" : "") + '">' + h + "</th>"; }).join("") + "</tr></thead><tbody>" +
    rows.map(function (r) { return "<tr>" + r.map(function (c, i) { return '<td class="' + (i >= numFrom ? "n" : "") + '">' + c + "</td>"; }).join("") + "</tr>"; }).join("") +
    "</tbody></table></div></div>";
}
function f(name) { return '<span class="fld">' + E(name) + "</span>"; }
function yr(d) { var p = d.split("-"); return +p[0] + (+p[1] - 1) / 12 + (+p[2] - 1) / 365; }
function count(arr, key) { var o = {}; arr.forEach(function (x) { var k = typeof key === "function" ? key(x) : x[key]; o[k] = (o[k] || 0) + 1; }); return o; }
function usd(n) { return n == null ? "" : "$" + F(n); }

var fac = A.rows(FAC.facilities);

/* ================= contents ================= */
var toc = [["m-mwpvl", "MWPVL"], ["m-year", "Year basis"], ["m-pull", "Pullback"], ["m-sub", "Subsidies"], ["m-benchmatch", "Benchmark matching"], ["m-xcheck", "Database cross-checks"], ["m-gaps", "Known gaps"]];
var tocHtml = '<nav aria-label="New method sections"><ul class="mtoc">' + toc.map(function (t) { return '<li><a href="#' + t[0] + '">' + t[1] + "</a></li>"; }).join("") + "</ul></nav>";
var general = A.$("#m-general");
if (general) general.insertAdjacentHTML("beforebegin", '<section class="gsec" id="m-toc"><h2>Contents of the added sections</h2><p class="method">The earlier sections on each domain follow these. The sections below were added for the MWPVL, year-basis, pullback, subsidy and benchmark work.</p>' + tocHtml + "</section>");

/* ================= MWPVL ================= */
(function () {
  var snaps = A.rows(MW.snapshots), sbs = A.rows(MW.status_by_snapshot);
  var textSn = snaps.filter(function (s) { return s.parse_mode === "html_text_table"; });
  var byDate = {}; sbs.forEach(function (r) { byDate[r.snapshot_date] = (byDate[r.snapshot_date] || 0) + r.sites; });
  var imgAll = snaps.filter(function (s) { return s.parse_mode !== "html_text_table"; });
  var imgSn = imgAll.filter(function (s) { return byDate[s.snapshot_date] > 0; });
  var skipped = imgAll.length - imgSn.length;
  var pts = function (arr) { return arr.map(function (s) { return [yr(s.snapshot_date), byDate[s.snapshot_date] || 0, s.snapshot_date]; }); };
  var d = sec("m-mwpvl", "MWPVL network list (Internet Archive captures)",
    "<p>MWPVL International is a consultancy that has published a site-by-site list of Amazon's distribution buildings. The live page is no longer a usable source, so every MWPVL fact here comes from copies of that page held by the Internet Archive's Wayback Machine. Each fact row keeps its snapshot URL. Only facts are kept (site code, city, state, building type, square feet, opening year, status); MWPVL's prose, analysis and images are not reproduced. MWPVL's figures are its own estimates and can differ from Amazon's.</p>" +
    "<h3>Two eras of the page</h3><ul>" +
    "<li><b>Text era, " + E(textSn[0].snapshot_date) + " to " + E(textSn[textSn.length - 1].snapshot_date) + " (" + textSn.length + " captures).</b> The facility list is an HTML table. It was parsed directly (six columns: site code, address, country, square feet, year opened, description). No capture of the page exists before 2012-06, so 2010 and 2011 cannot be covered. Rows with several codes in one cell are split into one row per code, and each keeps the shared square footage, which is for the whole building. US rows with no site code (Prime Now hubs and unnamed sort sites, 4 to 10 per capture) cannot be joined to the roster and are counted but skipped (" + f("us_rows_no_code") + ").</li>" +
    "<li><b>Image era, " + E(imgSn[0].snapshot_date) + " to " + E(imgSn[imgSn.length - 1].snapshot_date) + " (" + imgSn.length + " captures with tables; " + skipped + " further fetched captures were identical to an earlier one or partial and add no rows).</b> From March 2016 the tables are PNG pictures, so no text can be parsed. They were transcribed by double entry (below). The images dated 2026-01-17 are byte-identical to those of 2025-01-19, so <b>2025-01-19 is the last real data date</b>; a 2026 capture adds no information.</li></ul>" +
    "<h3>Double-entry transcription and adjudication (image era)</h3><ol>" +
    "<li>Two Claude agents transcribed every table image independently (pass A and pass B), reading zoomed tiles.</li>" +
    "<li>The passes were aligned row by row, keyed on site code (or city where a row has no code), and compared after normalising formatting (state name against abbreviation, a dash against a blank, commas, word order in a city).</li>" +
    "<li>Rows where every field matched are <i>agreed</i>. Differences in description wording only, or a city reading that names more places, were settled by fixed rules (keep the union of the descriptions; keep the fuller city).</li>" +
    "<li>Every other disagreement (site code, square feet, year, a city with different words, a description implying a different building type, a row present in only one pass) was adjudicated by an Opus agent against the image itself, using the row crop where possible, or a macOS Vision OCR read of the single cell for city choices. The basis for each decision is stored with the row.</li></ol>" +
    tbl("Table rows and how they were settled (from the build notes)", ["Item", "Count"], [
      ["Images double-entered (140 table images, 24 US maps with dots and no table)", "164"],
      ["Table rows transcribed", "14,828"],
      ["&nbsp;&nbsp;agreed between the two passes", "9,986 (67%)"],
      ["&nbsp;&nbsp;adjudicated (rules and image decisions)", "4,841"],
      ["&nbsp;&nbsp;flagged and left blank (a source typo, Charlton MA)", "1"],
      ["Rows whose content disagreement needed an image decision", "235 (147 city, 53 building type, 11 year, 7 site code, 7 one-pass-only, 5 square feet)"],
      ["Fact rows after splitting multi-code cells", "16,638 (15,072 with a code)"],
      ["Distinct site codes, text and image eras", "1,749 (170 first seen in text, 1,579 in images)"]], 1) +
    srcline("data/notes/mwpvl_wayback.md (counts); data/processed/mwpvl_wayback_image_facts.csv and mwpvl_wayback_sites_all.csv. MWPVL International, archived by the Internet Archive; each row cites its snapshot URL. These counts are not in a data global.") +
    "<p><b>Errors found and removed during reconciliation.</b> Two passes had transcribed the wrong image (the 2020-01 and 2021-01 fulfillment-center tables); the single valid pass was used and checked against a Vision OCR read. Five phantom rows that one pass had copied in from a different capture were confirmed absent from the images and dropped, as were 20 exact duplicate rows inside single images. One correlated error was found: both passes read UCA6 (2026-01) as 37,000 square feet where the image shows 37,800.</p>" +
    "<h3>Local OCR cross-check at 97.1% agreement</h3>" +
    "<p>As an independent third read, a local OCR model (Unlimited-OCR-2-4bit, run on this machine) read 172 of the table images. Its output was aligned to the Claude transcription (16,067 of 16,638 Claude rows matched by site code, else by city, state and square feet) and compared cell by cell.</p>" +
    tbl("Agreement between the local OCR and the Claude transcription on matched rows (from the build notes)", ["Field", "Agreement"], [
      ["Site code", "98.2%"], ["State", "99.6%"], ["Square feet", "98.8%"], ["Year opened", "98.7%"], ["City (mostly address-parsing differences)", "90.5%"], ["<b>All cells (80,335)</b>", "<b>97.1%</b>"]], 1) +
    "<p>The 2,295 disagreeing cells are listed in <span class=\"fld\">mwpvl_ocr_disagreements.csv</span>. The 40 highest-impact cells (32 years, 8 site codes) were checked on crops of the image. In all 30 cells where the row was visible, the Claude value was right and the OCR was wrong (typically a year read from the adjacent row, or a letter and digit swap such as UWA1 read as UVA1); one more was supported by a partial view and 9 could not be settled because the crop missed the row. Limits of this check: only one local model ran (a second model was planned but its server was not up), so it tests agreement, not truth; and about 2,255 disagreeing cells were not reviewed individually.</p>" +
    srcline("data/notes/mwpvl_wayback.md, section Local OCR cross-check; scripts/mwpvl_local_ocr_compare.py. The OCR output is a cross-check, not a published source.") +
    "<h3>From the transcription to sites</h3><ul>" +
    "<li>One row per site code. <b>Opening year.</b> Where the printed year changes between captures and the earlier capture called the site planned, delayed or on hold, the later year wins (" + f("later_year_after_planned") + "). Any other change is flagged as a conflict and resolved to the year MWPVL printed in the most captures, ties to the later one (" + f("conflict_modal_value") + "). A year that was only ever stated for a site not yet open is a projection (" + f("projection") + ").</li>" +
    "<li><b>Status</b> (active, planned, delayed, on hold, sublease, cancelled, closed) and <b>building type</b> come from keyword rules on MWPVL's short description, relative to the snapshot date. They are heuristics. MWPVL never marks a listed Amazon site as closed; closures show up only as rows that disappear from a later capture, which is weak evidence (MWPVL also merged and renamed rows).</li>" +
    "<li><b>Match to the roster</b> is by site code: 1,418 of 1,749 MWPVL codes (81.1%) match the facilities roster. Most of the 331 unmatched are delivery-station, Fresh, Prime Now, third-party and air-hub codes that the OSHA-based roster does not contain.</li>" +
    "<li><b>Outside check.</b> The year and size of BWI2 and DCA1 were checked against trade press and confirmed. The one entry in <span class=\"fld\">mwpvl_corrections.csv</span> is a city spelling (Sparrow's Point to Sparrows Point) and changes no year.</li></ul>");
  A.lineChart(d, {
    title: "US site codes listed in each MWPVL capture", yMin: 0, height: 280,
    series: [{ name: "Text-table captures (parsed)", points: pts(textSn), color: "var(--cat2)" }, { name: "Image-table captures (transcribed)", points: pts(imgSn), color: "var(--cat1)" }],
    xFmt: function (v) { return String(Math.floor(v)); }, yFmt: function (v) { return F(v); },
    caption: "Distinct site codes per capture, summed over the tables on the page (a code on two tables counts twice). MWPVL's list grows because Amazon grew and because the list gained coverage; it is not a count of buildings in operation. Captures that were identical to an earlier one are omitted. The dip in 2022-07 is a partial capture (only part of the delivery-station list), not a real fall. The last real data date is 2025-01-19."
  });
  d.insertAdjacentHTML("beforeend", srcline("AMZ_MWPVL.status_by_snapshot (fields snapshot_date, sites); MWPVL International via the Internet Archive Wayback Machine, 42 captures listed in AMZ_MWPVL.snapshots."));
  var oy = A.rows(MW.openings_by_year).filter(function (r) { return r.year >= 2005; });
  A.barChart(d, {
    title: "Sites by MWPVL opening year (roster-independent, 2005 on)", labelWidth: 60, valFmt: F,
    items: oy.map(function (r) { return { label: String(r.year), value: r.sites, note: F(r.projection) + " projection, " + F(r.conflict_modal_value) + " modal-resolved, " + F(r.later_year_after_planned) + " later year after planned" }; }),
    caption: "Counts distinct site codes by year_opened. Years before 2005 are in the data but not charted. The decline after 2021 is MWPVL's listing, which stopped being updated after 2025-01."
  });
  d.insertAdjacentHTML("beforeend", srcline("AMZ_MWPVL.openings_by_year (fields year, sites, projection, conflict_modal_value, later_year_after_planned); MWPVL International via the Internet Archive."));
})();

/* ================= Year basis ================= */
(function () {
  var cnt = count(fac, "year_basis");
  var flags = { conflict: 0, later: 0, proj: 0, afterosha: 0, pressearly: 0 };
  fac.forEach(function (r) {
    var fl = String(r.year_flag || "").split(";");
    if (fl.indexOf("mwpvl_year_conflict") >= 0) flags.conflict++;
    if (fl.indexOf("mwpvl_later_year_after_planned") >= 0) flags.later++;
    if (fl.indexOf("mwpvl_projection_not_used") >= 0) flags.proj++;
    if (fl.indexOf("year_after_first_osha_filing") >= 0) flags.afterosha++;
    if (fl.indexOf("press_year_well_before_first_osha_filing") >= 0) flags.pressearly++;
  });
  var rows = [
    ["mwpvl_opening_year", "1. MWPVL opening year (text and image eras, corrections applied). Projection years (site still planned or delayed with a future year) are skipped."],
    ["epi_mwpvl2012_opening_year", "2. Opening year from the EPI list or MWPVL's April 2012 table."],
    ["press_event_year", "3. Year of an opening event in trade press or news databases, only for an exact or probable roster match with consistent state and type and a date not in the future."],
    ["first_osha_filing", "4. First year the site filed an OSHA ITA Form 300A: an <i>operating by</i> date, an upper bound on opening."],
    ["undated", "No rule gives a year."]
  ].map(function (x) { return ["<span class=\"fld\">" + x[0] + "</span>", x[1], F(cnt[x[0]] || 0)]; });
  var d = sec("m-year", "Year basis hierarchy",
    "<p>Each roster site gets one year, used for the map slider and for site-count series. The first rule in the list below that gives a year wins, and the rule is recorded per site so that no year looks better sourced than it is.</p>" +
    tbl("Rule order and the number of roster sites each one dated", ["Field value of year_basis", "Rule", "Sites"], rows, 2) +
    srcline("AMZ_FAC.facilities, field <span class=\"fld\">year_basis</span> (" + F(fac.length) + " sites). Years come from MWPVL (Internet Archive), EPI, trade press and news databases (citations only) and OSHA ITA Form 300A.") +
    "<h3>Flags on the year</h3><ul>" +
    "<li>" + F(flags.conflict) + " sites: MWPVL printed different years in different captures; the most common year was used (" + f("mwpvl_year_conflict") + ").</li>" +
    "<li>" + F(flags.later) + " sites: MWPVL moved the year later after first listing the site as planned; the later year was used (" + f("mwpvl_later_year_after_planned") + ").</li>" +
    "<li>" + F(flags.proj) + " sites: the only MWPVL year was a projection, so it was not used and the next rule applied (" + f("mwpvl_projection_not_used") + ").</li>" +
    "<li>" + F(flags.afterosha) + " sites: the MWPVL year is later than a first OSHA filing the site had already made, which cannot be right as an opening date. The MWPVL year is still used and the site is flagged (" + f("year_after_first_osha_filing") + "); the cause is usually a reused code or a rebuilt building.</li>" +
    "<li>" + F(flags.pressearly) + " site: the press year is three or more years before the first OSHA filing, so it is probably an announcement date, not an opening (" + f("press_year_well_before_first_osha_filing") + "). The press year is still used and the site is flagged.</li></ul>" +
    "<p>Also stored per site: " + f("year_used") + ", " + f("year_source") + ", " + f("year_flag") + ", " + f("year_basis_legacy") + " (the basis under the older rule, kept for comparison), " + f("mwpvl_year") + ", " + f("mwpvl_year_resolution") + ", " + f("mwpvl_sq_ft") + " and " + f("mwpvl_status") + ". An opening year says when MWPVL or the press reported the site open, not when Amazon began operating at that address; a first OSHA filing year can be later than the real opening because early filing compliance was low.</p>");
  var order = ["mwpvl_opening_year", "first_osha_filing", "press_event_year", "epi_mwpvl2012_opening_year", "undated"];
  A.barChart(d, {
    title: "Roster sites by year basis", labelWidth: 180, valFmt: F,
    items: order.map(function (k) { return { label: k, value: cnt[k] || 0 }; }),
    caption: "Counts of the " + F(fac.length) + " roster sites."
  });
  d.insertAdjacentHTML("beforeend", srcline("AMZ_FAC.facilities, field year_basis."));
})();

/* ================= Pullback ================= */
(function () {
  var sites = A.rows(PU.sites), agg = A.rows(PU.aggregates);
  var codes = {}; fac.forEach(function (r) { if (r.site_code) codes[r.site_code] = 1; });
  var withCode = sites.filter(function (s) { return s.site_code; });
  var matched = withCode.filter(function (s) { return codes[s.site_code]; });
  var st = count(sites, "status");
  var rost = count(fac.filter(function (r) { return r.pullback_status; }), "pullback_status");
  var nRost = fac.filter(function (r) { return r.pullback_status; }).length;
  var scopes = count(agg, "scope");
  var names = { closed: "closed", closed_temporary: "closed temporarily", closed_partial: "closed in part", cancelled: "cancelled", delayed: "delayed", paused: "paused", sublease: "put up for sublease", removed_from_mwpvl_list: "removed from MWPVL list (weak)" };
  var keys = Object.keys(st).sort(function (a, b) { return st[b] - st[a]; });
  var d = sec("m-pull", "Pullback consolidation",
    "<p>The pullback table collects reports that a US logistics site was closed, cancelled, delayed, paused or put up for sublease. It combines two kinds of evidence and keeps them apart in the " + f("sources") + " and " + f("confidence") + " fields.</p><ul>" +
    "<li><b>News and trade press</b>, from subscription news databases and public trade press. Each fact is reduced to place, building type, size, status and date, with a citation in the form <i>Publication, date (via database)</i>. No quotation, document identifier or database link is kept.</li>" +
    "<li><b>MWPVL captures.</b> A site is given <i>delayed</i>, <i>paused</i> or <i>sublease</i> when a capture's status text says so, with high confidence if two or more captures show it. A code that is present in one capture and missing from the next capture of the same table is <i>removed_from_mwpvl_list</i>, always at low confidence. That is a removal from MWPVL's list, not a confirmed closure: rows were also merged, renamed and reused.</li></ul>" +
    "<h3>Rules</h3><ol>" +
    "<li><b>Status</b> is assigned from the event label of each fact by keyword (sublease, partial closure, cancellation or withdrawal, delay or postponement, pause or hold, closure). A closure whose text says temporary, idled, conversion, retrofit or expansion is <i>closed_temporary</i>. Store, office and data-center items are dropped.</li>" +
    "<li><b>One site, one status per source cluster.</b> Facts are grouped on city, state and status; a fact joins a group only if the building types are compatible, the square feet are compatible, and the site codes do not conflict. A fact attaches only when exactly one group qualifies (or all qualifying groups share one site code), so an ambiguous fact starts its own row rather than being merged wrongly.</li>" +
    "<li><b>Roster join.</b> A row joins the roster on site code. Rows with no code cannot be joined and appear only in the pullback table.</li>" +
    "<li><b>Strongest status wins on the roster.</b> A site with several statuses keeps the strongest in " + f("pullback_status") + " (order: closed, closed_partial, closed_temporary, sublease, paused, cancelled, delayed, removed_from_mwpvl_list) and every status with its date in " + f("pullback_history") + ".</li>" +
    "<li><b>Stated tallies are not summed.</b> Totals printed by a source (for example, a count of facilities closed or delayed by a given date) are kept as <i>stated</i> aggregates exactly as printed, and they can disagree with each other and with the site rows. MWPVL snapshot tallies count flagged codes per capture.</li></ol>" +
    "<p><b>Result.</b> " + F(sites.length) + " pullback rows; " + F(withCode.length) + " have a site code and " + F(matched.length) + " of those match the roster; " + F(sites.length - withCode.length) + " have no code and cannot be joined. " + F(nRost) + " roster sites carry a pullback status. " + F(agg.length) + " aggregate rows (" + F(scopes.stated || 0) + " stated tallies, " + F(scopes.mwpvl_snapshot || 0) + " MWPVL snapshot tallies).</p>");
  A.barChart(d, {
    title: "Pullback rows by status", labelWidth: 190, valFmt: F,
    items: keys.map(function (k) { return { label: names[k] || k, value: st[k], color: k === "removed_from_mwpvl_list" ? "var(--cat6)" : "var(--cat1)", note: F(rost[k] || 0) + " roster sites carry this as their strongest status" }; }),
    caption: "Grey bar: weak evidence (a code that stopped appearing), not a confirmed closure. One site can have several rows; the roster keeps its strongest status."
  });
  d.insertAdjacentHTML("beforeend", srcline("AMZ_PULL.sites (field status; " + F(sites.length) + " rows); roster join via AMZ_FAC.facilities fields pullback_status and site_code. News facts cited as Publication, date, title (via database) in the sources field; MWPVL International via the Internet Archive."));
})();

/* ================= Subsidies ================= */
(function () {
  var tot = A.rows(SU.totals), cls = A.rows(SU.classes), cov = A.rows(SU.coverage), aw = A.rows(SU.awards);
  var classes = ["direct", "infrastructure", "no_incentive_found"], bases = ["announced_max", "estimated_value", "realized", "annual"];
  var rows = [];
  classes.forEach(function (c) {
    bases.forEach(function (b) {
      var v = tot.filter(function (t) { return t.recipient_class === c && t.amount_basis === b && t.verification === "verified"; })[0];
      var a = tot.filter(function (t) { return t.recipient_class === c && t.amount_basis === b && t.verification === "all"; })[0];
      if (!v && !a) return;
      rows.push([c, b, v ? F(v.rows) : "0", v ? usd(v.amount_usd) : "$0", a ? F(a.rows) : "0", a ? usd(a.amount_usd) : "$0", v ? F(v.rows_overlap_flagged) : "0"]);
    });
  });
  var cc = count(cov, "coverage");
  var vl = {}; cls.forEach(function (r) { vl[r.verification_level] = (vl[r.verification_level] || 0) + r.award_rows; });
  var rc = count(aw, "recipient_class"), mixed = aw.filter(function (r) { return r.recipient_mixed; }).length;
  var byRule = count(aw, "recipient_rule");
  sec("m-sub", "Subsidy verification levels and recipient classes",
    "<p>Subsidy rows are public incentives reported for Amazon logistics sites (tax abatements, PILOT agreements, credits, exemptions, grants, tax-increment financing, infrastructure). They were collected state by state from official records first and press second. Facts only are published: amounts, program, year, issuer and a link to a public source. Notes, saved-file paths and secondary sources are not.</p>" +
    "<h3>Verification levels</h3><ul>" +
    "<li><b>primary</b>: an official record states the amount (an agency award list or dataset, an agreement, a council or IDA document, a state report). " + F(vl.primary || 0) + " award rows.</li>" +
    "<li><b>secondary</b>: a news or trade report quotes the amount and names the recipient or program. " + F(vl.secondary || 0) + " rows.</li>" +
    "<li><b>unverified</b>: a lead, request or draft, a figure that may not be a subsidy value (for example a bond size), or an uncertain basis. " + F(vl.unverified || 0) + " rows. They are kept in the table and shown as <i>all</i>, never counted as verified.</li>" +
    "<li><b>Verified</b> in the totals means primary or secondary. Rows that an adversarial check downgraded to unverified (for example a draft tax-increment plan that asked for $6.4 million, and a pilot payment whose basis was unclear) are not verified totals.</li>" +
    "<li>Five rows that rested only on search-result snippets of a subsidy tracker were <b>withheld</b> and are not in the published data.</li></ul>" +
    "<h3>Amount bases are never added</h3><p><span class=\"fld\">announced_max</span> is a stated cap or announced package; <span class=\"fld\">estimated_value</span> is a projected value of an abatement, PILOT or credit; <span class=\"fld\">realized</span> is an amount reported as actually forgone or paid; <span class=\"fld\">annual</span> is a per-year figure. A total is given for one basis at a time. The same award can sit in two bases (a press cap and a later realized figure), and package parts overlap, so rows flagged <span class=\"fld\">overlap_flag</span> stay in each total, with their count and amount shown beside it.</p>" +
    tbl("Verified and all award rows with an amount, by recipient class and amount basis", ["Class", "Basis", "Verified rows", "Verified USD", "All rows", "All USD", "Verified rows flagged as overlapping"], rows, 2) +
    srcline("AMZ_SUB.totals (fields recipient_class, amount_basis, verification, rows, amount_usd, rows_overlap_flagged). Primary records from state and local agencies and IDAs; press reports; row-level links in AMZ_SUB.awards.source_url. Never add rows across bases.") +
    "<h3>Recipient classes</h3><p>A fixed rule, applied in order (first match wins), splits money paid to Amazon or its developer from public infrastructure serving a site. The rule text is stored with the data (" + f("AMZ_SUB.rule") + ") and each row records which step fired (" + f("recipient_rule") + ").</p><ol>" +
    (SU.rule || []).slice(0, 4).map(function (t) { return "<li>" + E(t) + "</li>"; }).join("") + "</ol>" +
    "<p>Result: " + F(rc.direct || 0) + " direct rows, " + F(rc.infrastructure || 0) + " infrastructure rows and " + F(rc.no_incentive_found || 0) + " negative findings among the " + F(aw.length) + " published rows. " + F(mixed) + " direct rows also name roads or utilities and are flagged " + f("recipient_mixed") + " because the package is bundled. The infrastructure-by-type step trusts the recorded subsidy type; one Alabama package typed as infrastructure does not say so in its program text.</p>" +
    "<h3>State coverage</h3><p>A state with no award row is not the same as a state with no subsidy. Each state is labelled by what the search found: " +
    Object.keys(cc).map(function (k) { return F(cc[k]) + " " + f(k); }).join(", ") + ". Search-only marker rows (" + F((SU.excluded_from_totals || {}).partial_search || 0) + " partial searches and " + F((SU.excluded_from_totals || {}).searched_none || 0) + " searches that found nothing) are excluded from every total. Some states were searched only in part, and Good Jobs First's tracker could not be retrieved, so these totals are floors for what was found, not for what exists.</p>" +
    srcline("AMZ_SUB.coverage (field coverage), AMZ_SUB.awards (fields verification_level, recipient_class, recipient_rule, recipient_mixed), AMZ_SUB.excluded_from_totals."));
})();

/* ================= Benchmark matching ================= */
(function () {
  var py = A.rows(BE.injuries_peer_year).filter(function (r) { return r.year === 2024 && r.scope === "headline" && String(r.supplementary) !== "True" && String(r.headline_comparison_ok) === "True" && !/^(group_|ita_)/.test(r.peer); });
  py.sort(function (a, b) { return b.trc - a.trc; });
  var d = sec("m-benchmatch", "Benchmark matching rules",
    "<p>Benchmarks compare Amazon with other logistics operators on the same public source and the same rules. Peers are matched by rule, not by hand, and every matched name is listed in an audit file.</p>" +
    "<h3>Injuries (OSHA ITA Form 300A, same rules as the Amazon series)</h3><ul>" +
    "<li><b>Rates.</b> TRC, DART and DAFW are hours-weighted: cases times 200,000 over hours, summed over valid sites. A site is valid if it has at least 1,000 hours, at least 1 employee, between 300 and 4,500 hours per employee, and every case count present.</li>" +
    "<li><b>Who matches.</b> A row matches a peer if the company name matches an anchored pattern (a contractor filing under its own name never matches), or the company is blank and the establishment name or EIN matches, or the EIN is the peer's and the NAICS is a logistics code (so client-named sites of third-party logistics firms are found).</li>" +
    "<li><b>Scope.</b> NAICS 493 and 492 count for every peer. NAICS 42x counts for third-party logistics and carriers, and for retailers only when the building name reads as a distribution center; other 42x rows are listed outside the headline. Stores, trucking (484), vehicle maintenance and offices are excluded. Where a peer codes its distribution centers to a retail NAICS, a name rule keeps them: for Target, names with DC, fulfillment center, TFC, sortation, return, flow or receive center (added after review, which moved CY2024 from 43 to 65 valid sites, matching the 66 supply-chain facilities in its 10-K).</li>" +
    "<li><b>Duplicates.</b> The Amazon duplicate rule is applied first; a second pass drops re-submitted sites that differ only in punctuation (654 rows over all peers, none Amazon).</li>" +
    "<li><b>Yardstick.</b> The BLS rate for NAICS 493110 is the reference for every peer, so the share of sites above it is one scale for all. BLS 2025 is not yet published.</li>" +
    "<li><b>Partial years are not headlines.</b> FedEx Ground's CY2024 filings cover only about June to December after the 2024 merger, so that year is flagged and kept out of headline comparisons.</li></ul>" +
    tbl("CY2024 headline comparison, by total recordable case rate (TRC) among peers that pass the headline rule", ["Peer", "Valid sites", "TRC"], py.map(function (r) { return [E(r.peer_label), F(r.n_valid), r.trc == null ? "" : r.trc.toFixed(2)]; }), 1) +
    srcline("AMZ_BENCH.injuries_peer_year (scope = headline, year = 2024, headline_comparison_ok = true; fields peer_label, n_valid, trc). Computed from OSHA ITA Form 300A establishment files; BLS SOII reference. Match audit: data/processed/bench_injuries_name_audit.csv and bench_injuries_match_audit.csv.") +
    "<h3>Network, labor, industry and environment</h3><ul>" +
    "<li><b>Network and finance.</b> Facility counts and square feet are from each company's 10-K Item 2 text; revenue, capital spending and net property from SEC XBRL, matched to EDGAR for 21 figures (3 each for 7 companies). Fiscal years are mapped to the calendar year in which most months fall (FedEx fiscal 2025, June 2024 to May 2025, stands for CY2024). FedEx headcount is the company-wide sum, not the Federal Express segment alone. Revenue per square foot is not published as a headline, because it divides company-wide revenue by narrower network space.</li>" +
    "<li><b>Labor.</b> Employee counts are from 10-Ks; NLRB counts are case filings by employer name, shown as rank order, not exact totals.</li>" +
    "<li><b>Industry share.</b> Amazon's share of NAICS 493 is OSHA ITA average employees at Amazon 493110 sites divided by QCEW private NAICS 493 employment. It is an approximation, not a strict bound, and the years 2016, 2019 and 2020 are marked unusable.</li>" +
    "<li><b>Environment.</b> Intensity is emissions per dollar of revenue on each company's own boundary. Scope 3 is not comparable across companies (retailers include use of sold products; UPS and FedEx report it partly; carrier emissions for Amazon parcels appear on both sides), so every intensity row carries a comparability flag set to no.</li></ul>" +
    srcline("data/notes/bench_injuries.md, bench_network_financial.md, bench_labor.md, bench_warehousing_industry.md, bench_environment.md and bench_review.md; AMZ_BENCH tables network_definitions, industry_amazon_share_493, environment_boundaries. SEC EDGAR; BLS QCEW and SOII; OSHA ITA; NLRB."));
})();

/* ================= Database cross-checks ================= */
(function () {
  sec("m-xcheck", "Database cross-checks of the financial series",
    "<p>After the financial series were transcribed from Amazon's 10-K filings, they were compared with the same figures in licensed financial databases reached through the Johns Hopkins University Libraries. This is a check on transcription and definitions, not a source of the published figures. The databases' own values and documents are not redistributed here; only the outcome of each comparison is reported.</p>" +
    tbl("Outcome of each comparison", ["Database (via JHU Libraries)", "Values compared", "Agree", "Differ", "Why they differ"], [
      ["Mergent Market Atlas", "186", "182", "4", "1997 and 1998 operating income and 1997 net income: probably as-originally-reported against our poolings-restated filing (not verified against the filing). 2017 gross PP&E: lease adjustment."],
      ["Hoovers (Avention)", "75", "64", "11", "FY2016 gross capital purchases (cause found, see below) and 10 net or gross PP&E values where the database appears to include operating-lease right-of-use assets."],
      ["Mergent Archives", "54", "53", "1", "One definitional difference, already documented. Six matches are to rounding."],
      ["S&P Capital IQ (as-presented template)", "35", "35", "0", "Agrees with the 10-K. The Standard template reclassifies some items (FY2022 operating income moves a 1,100 asset write-down), so the as-presented view is the one matched."],
      ["S&P Capital IQ (second pull, 2021 to 2025)", "37", "29", "8", "All differences are the Standard template: it adds operating-lease right-of-use assets to net and gross PP&E and reclassifies FY2022 operating income. Described by the database as definitional."],
      ["Value Line", "40", "37", "3", "Three definition disagreements. Ten of the matches are within 1.5% of sales and ten match gross within 1%."]], 2) +
    srcline("Mergent Market Atlas, Hoovers (Avention), Mergent Archives, S&P Capital IQ NetAdvantage and Value Line (all via Johns Hopkins University Libraries), compared with our processed financial files; counts are tallies of the status field in the cross-check extracts (jhu_*_amazon_crosscheck*.csv, which are subscription material and not published). No global holds these counts.") +
    "<p><b>What the checks changed.</b> The Hoovers comparison found that the FY2016 gross capital purchases had been entered as the net-of-proceeds figure. The capital table now carries both: gross 7,804 and net of proceeds 6,737 (USD millions, AMZ_FIN.capex). The PP&E differences from 2019 on are definitional: databases that add operating-lease right-of-use assets show larger net PP&E than the 10-K line the page uses, which is labelled on the financial page.</p>" +
    "<p>The same databases also supplied citations for news facts, market-context rows and pullback rows. Those appear on the <a href=\"sources.html#bibliography\">Sources page</a> as citations only (publication, date, title, database).</p>");
})();

/* ================= Known gaps: moved last and updated ================= */
(function () {
  var g = A.$("#m-gaps");
  if (g) {
    var body = A.$("#m-gaps-body");
    if (body) body.innerHTML = '<div class="md mx"><ul>' +
      "<li>Opening dates for sites MWPVL never listed and no press item covers (the year basis table above shows how many fall back to a first OSHA filing year or have no year); closing dates for almost every site, since MWPVL never marks a closure and a vanished code is only weak evidence; square feet for sites outside MWPVL's list; returns centers and cross-docks that the roster cannot identify.</li>" +
      "<li>MWPVL's list stops changing after 2025-01-19, so openings and removals after that date are not seen.</li>" +
      "<li>Subsidies: some states were searched only in part and Good Jobs First's tracker could not be retrieved, so the subsidy totals are what was found and verified, not a full count. Unverified rows and search-only states are shown as such, never summed.</li>" +
      "<li>Pullback: " + F(A.rows(PU.sites).filter(function (s) { return !s.site_code; }).length) + " rows have no site code and cannot be attached to a roster site; stated tallies from different sources disagree and are not reconciled.</li>" +
      "<li>Truck emissions per site: no primary trip-rate source for fulfillment centers.</li>" +
      "<li>A BLS comparison by establishment size: the size tables needed could not be retrieved. BLS SOII for 2025 and OSHA case-detail (injury type) files are not available; Census ACS demographics need an API key.</li>" +
      "<li>Some subscription databases could not be reached or were blocked mid-run; their absence is not evidence of no coverage.</li>" +
      "<li>Benchmark peers file under their own NAICS codes and names; a peer site filed under an unrelated name is missed, and the injury comparison covers filing sites only, so it is not a measure of all workers.</li></ul></div>";
    app.appendChild(g);
  }
})();
})();
