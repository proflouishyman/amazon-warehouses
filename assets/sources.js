/* sources.html: dataset catalog, public source-file manifest (grouped by domain and publisher),
   subscription bibliography (citations only) and a statement of what is withheld.
   The manifest and the bibliography are read from their public CSV files at load time because no data global
   holds them (they are 4,899 and 2,584 rows). If the CSVs cannot be fetched (for example the page was opened
   from a file:// path), the page says so and links to them. */
(function () {
"use strict";
var A = window.AMZ, E = A.esc, F = A.fmt, S = window.AMZ_SOURCES;
var MANIFEST = "data/sources_manifest_public.csv", BIB = "data/processed/bibliography_subscription.csv";
var LIC = '<span class="lic">JHU-licensed; not redistributed</span>';

A.page({ title: "Sources", sub: "Every dataset used, with publisher, URL, retrieval date, coverage and caveats; every public source file grouped by domain and publisher; and the citations of the licensed databases consulted. Retrieved " + E(S.retrieved) + "." });
var app = A.$("#app");
app.classList.add("sx");

var names = { facilities: "Facilities roster", financial: "Financial", labor: "Labor", injuries: "Workplace injuries", environment: "Environment", logistics: "Logistics", industry: "Industry sources (parcel volume, early openings, robots)", population: "Population access" };
var order = ["facilities", "financial", "labor", "injuries", "environment", "logistics", "industry", "population"];

function srcline(h) { return '<p class="srcline"><b>Source.</b> ' + h + "</p>"; }
function link(u, text) {
  if (/^https?:\/\//i.test(u) && !/ezprox[y]|\.proxy\.|\/login/i.test(u)) return '<a href="' + E(u) + '" target="_blank" rel="noopener">' + text + "</a>";
  return text;
}
function parseCSV(t) {
  var rows = [], row = [], f = "", q = false, i = 0, n = t.length, c;
  while (i < n) {
    c = t.charAt(i);
    if (q) { if (c === '"') { if (t.charAt(i + 1) === '"') { f += '"'; i++; } else q = false; } else f += c; }
    else if (c === '"') q = true;
    else if (c === ",") { row.push(f); f = ""; }
    else if (c === "\n" || c === "\r") { if (c === "\r" && t.charAt(i + 1) === "\n") i++; row.push(f); f = ""; if (row.length > 1 || row[0] !== "") rows.push(row); row = []; }
    else f += c;
    i++;
  }
  if (f !== "" || row.length) { row.push(f); rows.push(row); }
  var h = rows.shift() || [];
  return rows.map(function (r) { var o = {}; h.forEach(function (k, j) { o[k] = r[j] == null ? "" : r[j]; }); return o; });
}
function load(url) {
  return fetch(url).then(function (r) { if (!r.ok) throw new Error(r.status); return r.text(); }).then(parseCSV);
}
function failMsg(host, url) {
  A.mount(host, '<p class="loadmsg">This table is read from <a href="' + E(url) + '">' + E(url) + "</a> when the page is served over http(s). It could not be loaded here (for example the page was opened as a local file). The CSV holds the same rows.</p>");
}
function count(arr, key) { var o = {}; arr.forEach(function (x) { var k = typeof key === "function" ? key(x) : x[key]; o[k] = (o[k] || 0) + 1; }); return o; }

/* ---------------- 1. What is public and what is withheld ---------------- */
(function () {
  var b = A.section(app, "withheld", "What is published and what is withheld");
  A.mount(b,
    '<div class="stmt"><p><b>Published:</b> facts (place, date, size, amount, status), each with a citation or a public link; derived tables; and, for licensed databases, citations only (publication, date, title, database).</p>' +
    "<p><b>Withheld:</b></p><ul>" +
    "<li>The text of articles, reports and records saved from subscription databases, and any quotation longer than 15 words from them. Licence terms for the Johns Hopkins University Libraries databases allow research use, not redistribution, and the publishers' copyright covers the text.</li>" +
    "<li>Document identifiers, database URLs and library proxy links, which would point to licensed content or to a personal login.</li>" +
    "<li>The extracts made from those databases and from Statista (kept locally, not in this repository), and the full local file manifest, which lists every saved subscription file. Only the public-access rows are published here.</li>" +
    "<li>PitchBook (read through the Johns Hopkins University Libraries subscription): its deal records, descriptions and identifiers. The deal tables here (data/processed/logistics_deals_public.csv) cite a public source first and name PitchBook second, include only deals a public page confirms, and show amounts only where that page states them. PitchBook is not redistributed.</li>" +
    "<li>MWPVL's own prose, analysis and images. Only the facts read from its archived list are used, each with the archive URL.</li>" +
    "<li>Subsidy rows that rested only on search-result snippets of a subsidy tracker (not verified), and the working notes, saved-file paths and secondary links behind each subsidy row.</li>" +
    "<li>Any data about individual workers. Injury figures are establishment totals from public OSHA filings.</li></ul>" +
    "<p>Raw downloads are kept locally, not published. Where a page shows a number that comes from a licensed database, it is a fact, cited as <i>Publication, date, title (via database)</i>.</p></div>");
})();

/* ---------------- 2. Dataset catalog ---------------- */
(function () {
  var b0 = A.section(app, "datasets", "Datasets used", S.catalog.length + " processed datasets with publisher, URL, coverage and caveats, grouped by domain.");
  order.forEach(function (d) {
    var rows = S.catalog.filter(function (c) { return c.domain === d; });
    if (!rows.length) return;
    A.mount(b0, '<h3 id="s-' + d + '" style="font-size:15px;margin:16px 0 4px">' + E(names[d]) + " (" + rows.length + ' datasets)</h3><div class="tw"><table><thead><tr><th>Dataset (data/processed)</th><th>What it is</th><th>Publisher</th><th>URL</th><th>Coverage</th><th>Caveats</th></tr></thead><tbody>' + rows.map(function (c) {
      var us = String(c.url).split(" ; ").map(function (u) { return /^https?:/.test(u) ? link(u, E(u.replace(/^https?:\/\/(www\.)?/, "").slice(0, 48))) : E(u); }).join("<br>");
      return '<tr class="srcrow"><td class="mono">' + E(c.file) + "</td><td>" + E(c.what) + "</td><td>" + E(c.publisher) + "</td><td>" + us + "</td><td>" + E(c.coverage) + "</td><td>" + E(c.caveats) + "</td></tr>";
    }).join("") + "</tbody></table></div>");
  });
  A.mount(b0, srcline("AMZ_SOURCES.catalog (fields domain, file, what, publisher, url, coverage, caveats), built by scripts/dataset_catalog.py. Retrieval date " + E(S.retrieved) + "."));
})();

/* ---------------- 3. Public manifest ---------------- */
(function () {
  var b = A.section(app, "manifest", "Public source files, by domain and publisher", "Every file saved from a public-access source and used or kept for this project. Subscription files are not listed here. Open a domain, then a publisher, to see its files.");
  var host = document.createElement("div"); b.appendChild(host);
  host.innerHTML = '<p class="loadmsg">Loading the public manifest...</p>';
  load(MANIFEST).then(function (rows) {
    host.innerHTML = "";
    var pubs = {}; rows.forEach(function (r) { pubs[r.publisher] = 1; });
    var byDom = count(rows, "domain"), doms = Object.keys(byDom).sort(function (a, c) { return byDom[c] - byDom[a]; });
    A.tiles(host, [{ value: F(rows.length), label: "public source files", context: "public access only" }, { value: F(Object.keys(pubs).length), label: "publishers" }, { value: F(doms.length), label: "domains" }]);
    host.insertAdjacentHTML("beforeend", '<div class="ctl"><input type="search" id="mq" placeholder="Search title or publisher" aria-label="Search the public manifest"><span class="muted" id="mqn"></span></div><div id="mres"></div><div id="mdoms"></div>');
    var fileRows = function (arr, from, to, showPub) {
      return arr.slice(from, to).map(function (r) {
        return "<tr><td>" + link(r.url_or_doc_id, E(r.title || "(untitled)")) + (showPub ? '<br><span class="muted">' + E(r.publisher) + " (" + E(r.domain) + ")</span>" : "") + '</td><td class="n">' + E(r.publication_date) + "</td><td>" + E(r.role) + '</td><td class="n">' + E(r.retrieved_date) + "</td></tr>";
      }).join("");
    };
    var head = "<thead><tr><th>Title</th><th>Published</th><th>Role</th><th>Retrieved</th></tr></thead>";
    function filesBox(arr, showPub) {
      var shown = 0, step = 100, box = document.createElement("div");
      box.className = "files";
      box.innerHTML = '<div class="tw"><table>' + head + "<tbody></tbody></table></div>";
      var tb = box.querySelector("tbody");
      function more() {
        tb.insertAdjacentHTML("beforeend", fileRows(arr, shown, shown + step, showPub)); shown = Math.min(arr.length, shown + step);
        var btn = box.querySelector("button.more");
        if (btn) btn.remove();
        if (shown < arr.length) { box.insertAdjacentHTML("beforeend", '<button class="btn ghost more" type="button">Show ' + Math.min(step, arr.length - shown) + " more (" + F(arr.length - shown) + " not shown)</button>"); box.querySelector("button.more").addEventListener("click", more); }
      }
      more();
      return box;
    }
    var dh = A.$("#mdoms");
    doms.forEach(function (d) {
      var dr = rows.filter(function (r) { return r.domain === d; }), bp = {};
      dr.forEach(function (r) { (bp[r.publisher] = bp[r.publisher] || []).push(r); });
      var pn = Object.keys(bp).sort(function (a, c) { return bp[c].length - bp[a].length || (a < c ? -1 : 1); });
      var det = document.createElement("details"); det.className = "dom";
      det.innerHTML = "<summary>" + E(names[d] || d) + ' <span class="muted">(' + F(dr.length) + " files, " + F(pn.length) + ' publishers)</span></summary><div class="in"></div>';
      var built = false;
      det.addEventListener("toggle", function () {
        if (!det.open || built) return; built = true;
        var inn = det.querySelector(".in");
        pn.forEach(function (p) {
          var pd = document.createElement("details"); pd.className = "pub";
          pd.innerHTML = '<summary><span class="nm">' + E(p) + '</span><span class="ct">' + F(bp[p].length) + " file" + (bp[p].length === 1 ? "" : "s") + "</span></summary>";
          var done = false;
          pd.addEventListener("toggle", function (e) { e.stopPropagation(); if (pd.open && !done) { done = true; pd.appendChild(filesBox(bp[p], false)); } });
          inn.appendChild(pd);
        });
      });
      dh.appendChild(det);
    });
    var q = A.$("#mq"), res = A.$("#mres"), nn = A.$("#mqn"), tm;
    q.addEventListener("input", function () {
      clearTimeout(tm);
      tm = setTimeout(function () {
        var v = q.value.trim().toLowerCase();
        res.innerHTML = ""; nn.textContent = "";
        dh.style.display = v ? "none" : "";
        if (!v) return;
        var hit = rows.filter(function (r) { return (r.title + " " + r.publisher).toLowerCase().indexOf(v) >= 0; });
        nn.textContent = F(hit.length) + " matching files";
        if (hit.length) res.appendChild(filesBox(hit, true));
      }, 150);
    });
    host.insertAdjacentHTML("beforeend", srcline("data/sources_manifest_public.csv (" + F(rows.length) + " rows; fields source_id, title, publisher, publication_date, url_or_doc_id, access, domain, role, retrieved_date). Built by scripts/build_sources_public.py from the local manifest by keeping access = public and removing references to private files. Titles and publishers are as recorded when each file was saved; the \"Role\" column says whether a file is a source, a derived extract, an image or code."));
  }).catch(function () { host.innerHTML = ""; failMsg(host, MANIFEST); });
})();

/* ---------------- 4. Subscription bibliography ---------------- */
(function () {
  var b = A.section(app, "bibliography", "Licensed databases: citations only", "Publication, date, title and database for each item consulted in the Johns Hopkins University Libraries subscriptions. " + LIC);
  var host = document.createElement("div"); b.appendChild(host);
  host.innerHTML = '<p class="loadmsg">Loading the bibliography...</p>';
  load(BIB).then(function (rows) {
    host.innerHTML = "";
    var byDb = count(rows, "database"), dbs = Object.keys(byDb).sort(function (a, c) { return byDb[c] - byDb[a]; });
    var cited = rows.filter(function (r) { return r.cited_in_public_data && r.cited_in_public_data !== "no"; });
    host.insertAdjacentHTML("beforeend", '<div class="stmt"><p>' + LIC + " The items below are the publisher, date and title of material read in licensed databases. The text of the items, their document identifiers and their library links are not published, and no quotation over 15 words is used on any page. Items marked as cited in the public data support a fact in one of the published tables (facility events, pullback or market context); the rest were read but not used.</p></div>");
    A.tiles(host, [{ value: F(rows.length), label: "citations" }, { value: F(dbs.length), label: "databases" }, { value: F(cited.length), label: "cited in a published table" }]);
    var tb = '<div class="tw"><table><thead><tr><th>Database</th><th class="n">Citations</th><th class="n">Cited in a published table</th></tr></thead><tbody>' + dbs.map(function (d) {
      var c = rows.filter(function (r) { return r.database === d && r.cited_in_public_data !== "no" && r.cited_in_public_data; }).length;
      return "<tr><td>" + E(d) + '</td><td class="n">' + F(byDb[d]) + '</td><td class="n">' + F(c) + "</td></tr>";
    }).join("") + "</tbody></table></div>";
    host.insertAdjacentHTML("beforeend", '<div class="twrap"><p class="cap"><b>Citations by database.</b> ' + LIC + "</p>" + tb + "</div>");
    var uses = {}; rows.forEach(function (r) { if (r.cited_in_public_data && r.cited_in_public_data !== "no") r.cited_in_public_data.split(";").forEach(function (u) { uses[u] = 1; }); });
    host.insertAdjacentHTML("beforeend", '<div class="ctl"><input type="search" id="bq" placeholder="Search publication or title" aria-label="Search citations"><label>Database <select id="bdb"><option value="">All</option>' + dbs.map(function (d) { return '<option value="' + E(d) + '">' + E(d) + "</option>"; }).join("") + '</select></label><label>Cited in <select id="buse"><option value="">Any</option><option value="__yes">Any published table</option>' + Object.keys(uses).sort().map(function (u) { return '<option value="' + E(u) + '">' + E(u.replace(/_/g, " ")) + "</option>"; }).join("") + '</select></label></div><p class="cap"><b>Citations.</b> ' + LIC + '</p><div id="btab"></div>');
    var t = A.table("#btab", {
      rows: rows, pageSize: 25, sort: "date", dir: -1,
      cols: [{ key: "publication", label: "Publication" }, { key: "date", label: "Date" }, { key: "title", label: "Title" }, { key: "database", label: "Database" }, { key: "cited_in_public_data", label: "Cited in", fmt: function (v) { return v === "no" ? "" : String(v).replace(/_/g, " ").replace(/;/g, ", "); } }]
    });
    function refilter() {
      var v = A.$("#bq").value.trim().toLowerCase(), db = A.$("#bdb").value, u = A.$("#buse").value;
      t.setRows(rows.filter(function (r) {
        if (db && r.database !== db) return false;
        if (u === "__yes" && (r.cited_in_public_data === "no" || !r.cited_in_public_data)) return false;
        if (u && u !== "__yes" && String(r.cited_in_public_data).split(";").indexOf(u) < 0) return false;
        return !v || (r.publication + " " + r.title).toLowerCase().indexOf(v) >= 0;
      }));
    }
    ["#bq", "#bdb", "#buse"].forEach(function (s) { A.$(s).addEventListener("input", refilter); A.$(s).addEventListener("change", refilter); });
    host.insertAdjacentHTML("beforeend", srcline("data/processed/bibliography_subscription.csv (" + F(rows.length) + " rows; fields publication, date, title, database, cited_in_public_data), built by scripts/build_bibliography.py, which fails the build if a quotation, document id or proxy link is present. Databases via Johns Hopkins University Libraries; " + LIC + "."));
  }).catch(function () { host.innerHTML = ""; failMsg(host, BIB); });
})();

/* ---------------- 5. Domain notes ---------------- */
(function () {
  var nb = A.section(app, "notes", "Domain notes (from data/notes)", "These are the working notes written while collecting each dataset, shown unedited apart from local paths.");
  order.forEach(function (d) { if (S.notes[d]) A.mount(nb, '<details class="card" style="margin:8px 0"><summary><b>' + E(names[d]) + '</b></summary><div class="md">' + A.md(S.notes[d]) + "</div></details>"); });
})();
})();
