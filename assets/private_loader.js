/* Local private layer loader. Committed and harmless: it holds code only, no data.
   Public site: assets/private_index.js does not exist, the probe fails silently and nothing is added to the page.
   Local machine (ces-server): `scripts/build_data.py --private` writes assets/private_*.js (gitignored); this file
   then loads them and runs the hooks registered in window.AMZ_PRIVATE_HOOKS (keyed by the page's data-page id,
   "*" for every page) to add collapsible "Local only" sections and "local file" links.
   Pages may register their own hook:  (window.AMZ_PRIVATE_HOOKS = window.AMZ_PRIVATE_HOOKS || {}).fin = [function (P) {...}]; */
(function () {
"use strict";
var HOOKS = window.AMZ_PRIVATE_HOOKS = window.AMZ_PRIVATE_HOOKS || {};
function on(page, fn) { (HOOKS[page] = HOOKS[page] || []).push(fn); }
window.AMZ_PRIVATE = window.AMZ_PRIVATE || { on: on };

function load(src, done) {
  var s = document.createElement("script"), fin = false;
  function end(ok) { if (fin) return; fin = true; try { done(ok); } catch (e) { } }
  s.src = src; s.onload = function () { end(true); }; s.onerror = function () { end(false); };
  try { document.head.appendChild(s); } catch (e) { end(false); }
}

/* ---------- small helpers (own copies, so nothing depends on page code) ---------- */
function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
function fmt(n) { return n == null || n === "" || isNaN(n) ? "" : Number(n).toLocaleString("en-US", { maximumFractionDigits: 0 }); }
function rows(t) { if (!t) return []; return t.rows.map(function (r) { var o = {}; t.cols.forEach(function (c, i) { o[c] = r[i]; }); return o; }); }
function isUrl(u) { return /^https?:\/\//i.test(String(u || "")); }
function ext(u, label) { return isUrl(u) ? '<a href="' + esc(u) + '" target="_blank" rel="noopener">' + esc(label || "link") + "</a>" : ""; }
function loc(p, label) { return p ? '<a class="lf" href="' + esc(encodeURI(p)) + '" target="_blank" title="' + esc(p) + ' (local file, this machine only)">' + esc(label || "local file") + "</a>" : ""; }
function trunc(s, n) { s = String(s == null ? "" : s); return s.length > n ? '<span title="' + esc(s) + '">' + esc(s.slice(0, n)) + "&hellip;</span>" : esc(s); }
function day(r) { return r.event_date || r.article_date || ""; }
function openAll() { return /[?&]open=1\b/.test(location.search); }

/* ---------- styles (injected only in local mode) ---------- */
function css() {
  var st = document.createElement("style");
  st.textContent =
    ".lo-wrap{margin:34px 0 10px;padding:10px 14px 14px;border:2px dashed var(--warn-ink,#5c4608);border-radius:8px;background:var(--surface,#f8f9f9)}" +
    ".lo-wrap>h2{margin-top:4px}.lo-badge{display:inline-block;font:700 10.5px/1 ui-monospace,Menlo,monospace;letter-spacing:.06em;padding:3px 6px;border-radius:3px;background:var(--warn-ink,#5c4608);color:var(--warn-bg,#f4e9c9);vertical-align:middle;margin-right:6px}" +
    "details.lo{margin:10px 0;border:1px solid var(--rule,#c8cfd1);border-radius:6px;background:var(--bg,#eceeee)}details.lo>summary{cursor:pointer;padding:9px 12px;font-weight:600;font-size:14px}" +
    "details.lo>.lo-body{padding:4px 12px 12px}details.lo .lo-n{font-weight:400;color:var(--ink-3,#6e7a7f);font-size:12.5px;margin-left:6px}" +
    ".lo-tools{display:flex;flex-wrap:wrap;gap:8px 14px;align-items:center;margin:6px 0}.lo-tools input{padding:5px 8px;border:1px solid var(--rule,#c8cfd1);border-radius:4px;min-width:260px;background:var(--surface,#fff)}" +
    ".lo-tools button{padding:4px 10px;border:1px solid var(--rule,#c8cfd1);border-radius:4px;background:var(--surface-2,#e2e5e6);cursor:pointer}" +
    ".lo-wrap .tw{max-height:640px;overflow:auto}.lo-wrap td.q{min-width:280px;max-width:520px;overflow-wrap:anywhere}.lo-wrap td{font-size:12.5px}" +
    "a.lf{font-size:10.5px;margin-left:5px;padding:0 5px;border:1px solid var(--warn-ink,#5c4608);border-radius:8px;color:var(--warn-ink,#5c4608);text-decoration:none;white-space:nowrap;background:var(--warn-bg,#f4e9c9)}" +
    ".pill.ok{background:var(--accent-soft,#d3e4ea);color:var(--ink,#1f2629)}.lo-sum{font-size:13px;color:var(--ink-2,#4b575c);margin:4px 0}" +
    "#lo-flag{position:fixed;right:10px;bottom:10px;z-index:20;font:700 11px/1 ui-monospace,Menlo,monospace;letter-spacing:.06em;padding:6px 9px;border-radius:4px;background:var(--warn-ink,#5c4608);color:var(--warn-bg,#f4e9c9);opacity:.92;text-decoration:none}" +
    ".lo-log h2,.lo-log h3,.lo-log h4{margin:14px 0 6px}.lo-log{font-size:13.5px;max-width:110ch}.lo-log code{font-size:12px}";
  document.head.appendChild(st);
}

/* ---------- widgets ---------- */
function wrapper(host, intro) {
  var id = "local-only";
  var el = document.getElementById(id);
  if (!el) {
    host.insertAdjacentHTML("beforeend", '<section class="gsec lo-wrap" id="' + id + '"><h2><span class="lo-badge">LOCAL ONLY</span>Local-only sections</h2><p class="method">' + intro +
      " These sections are built from subscription extracts and raw files on this machine. They do not exist on the public site and are never committed.</p></section>");
    el = document.getElementById(id);
  }
  return el;
}
function section(wrap, id, title, count, build) {
  wrap.insertAdjacentHTML("beforeend", '<details class="lo" id="' + id + '"><summary><span class="lo-badge">LOCAL ONLY</span>' + esc(title) + (count != null ? '<span class="lo-n">' + esc(count) + "</span>" : "") + '</summary><div class="lo-body"></div></details>');
  var d = document.getElementById(id), body = d.querySelector(".lo-body"), built = false;
  function go() { if (!built && d.open) { built = true; try { build(body); } catch (e) { body.textContent = "Could not render: " + e.message; } } }
  d.addEventListener("toggle", go);
  if (openAll()) { d.open = true; go(); }
  return d;
}
/* cols: [{label, key, num, cls, html(r)}]; opts: {page, text(r) override for the filter} */
function table(host, cols, data, opts) {
  opts = opts || {}; var size = opts.page || 150, shown = 0, view = data, hay = null;
  host.insertAdjacentHTML("beforeend", '<div class="lo-tools"><input type="search" placeholder="Filter rows (all columns)" aria-label="Filter rows"><span class="lo-cnt muted"></span></div>' +
    '<div class="tw"><table><thead><tr>' + cols.map(function (c) { return "<th" + (c.num ? ' class="n"' : "") + ">" + esc(c.label) + "</th>"; }).join("") + '</tr></thead><tbody></tbody></table></div><div class="lo-tools"><button type="button" hidden>Show more</button></div>');
  var inp = host.querySelector("input"), cnt = host.querySelector(".lo-cnt"), tb = host.querySelector("tbody"), btn = host.querySelector("button");
  function line(r) { return "<tr>" + cols.map(function (c) { var v = c.html ? c.html(r) : esc(r[c.key] == null ? "" : (c.fmt ? c.fmt(r[c.key]) : r[c.key])); return "<td" + (c.num || c.cls ? ' class="' + (c.num ? "n " : "") + (c.cls || "") + '"' : "") + ">" + v + "</td>"; }).join("") + "</tr>"; }
  function more() { var n = Math.min(view.length, shown + size), h = ""; for (var i = shown; i < n; i++) h += line(view[i]); tb.insertAdjacentHTML("beforeend", h); shown = n; stat(); }
  function stat() { cnt.textContent = fmt(shown) + " of " + fmt(view.length) + " rows" + (view.length !== data.length ? " (filtered from " + fmt(data.length) + ")" : ""); btn.hidden = shown >= view.length; btn.textContent = "Show " + Math.min(size, view.length - shown) + " more"; }
  function refilter() {
    var q = inp.value.trim().toLowerCase();
    if (q && !hay) hay = data.map(function (r) { return (opts.text ? opts.text(r) : Object.keys(r).map(function (k) { return r[k]; }).join(" ")).toLowerCase(); });
    var words = q.split(/\s+/).filter(Boolean);
    view = !words.length ? data : data.filter(function (r, i) { return words.every(function (w) { return hay[i].indexOf(w) >= 0; }); });
    tb.innerHTML = ""; shown = 0; more();
  }
  inp.addEventListener("input", function () { clearTimeout(inp._t); inp._t = setTimeout(refilter, 160); });
  btn.addEventListener("click", more);
  more();
}

/* ---------- logistics + map: events, PitchBook deals, pullback ---------- */
function logHook(P) {
  var app = document.getElementById("app"); if (!app) return;
  var ev = P.AMZ_PRIVATE_EVENTS, pb = P.AMZ_PRIVATE_PITCHBOOK;
  if (!ev && !pb) return;
  var w = wrapper(app, "Facility events and openings from the subscription extracts, every PitchBook deal (confirmed or not) and the pullback rows with their quotes.");
  function evCols() {
    return [{ label: "Date", html: function (r) { return esc(day(r)); } }, { label: "Publication", key: "publication" }, { label: "Event", key: "event" },
      { label: "Place", html: function (r) { return esc([r.city, r.state].filter(Boolean).join(", ")); } }, { label: "Type", key: "facility_type" },
      { label: "Sq ft", num: true, key: "sq_ft", fmt: fmt },
      { label: "Title", cls: "q", html: function (r) { return isUrl(r.url) ? ext(r.url, r.title || "article") : esc(r.title); } },
      { label: "Database", key: "database" }, { label: "Short quote", cls: "q", html: function (r) { return esc(r.quote); } }];
  }
  if (ev) {
    var E = rows(ev.events), srcs = {}; E.forEach(function (r) { srcs[r.source] = 1; });
    section(w, "lo-events", "Facility events and openings (subscription extracts)", fmt(E.length) + " rows, " + Object.keys(srcs).length + " extracts", function (b) {
      b.insertAdjacentHTML("beforeend", '<p class="lo-sum">Every announced, opened, delayed or cancelled facility event in the extracts, with publication, date, title, database and the short quote the extract holds. Type a state, city, publication or word to filter.</p>');
      table(b, evCols(), E);
    });
    var Pu = rows(ev.pullback);
    section(w, "lo-pullback", "Pullback rows with their quotes", fmt(Pu.length) + " rows", function (b) {
      b.insertAdjacentHTML("beforeend", '<p class="lo-sum">Closures, cancellations, delays and aggregate pullback statements from the subscription extracts. The public pullback table shows the derived status only.</p>');
      table(b, evCols(), Pu);
    });
  }
  if (pb) {
    var D = rows(pb.deals), conf = D.filter(function (r) { return r.public_confirmed === "yes"; }).length;
    section(w, "lo-pitchbook", "PitchBook deals (all rows)", D.length + " deals, " + conf + " confirmed, " + (D.length - conf) + " unconfirmed", function (b) {
      b.insertAdjacentHTML("beforeend", '<p class="lo-sum">Unconfirmed means no public source was found for the deal. Amounts are the PitchBook figures; amount_basis says whether PitchBook marks them disclosed or estimated. The public site shows only confirmed rows.</p>');
      table(b, [{ label: "Date", key: "date" }, { label: "Acquirer or investor", key: "acquirer_or_investor" }, { label: "Target", key: "target" }, { label: "Deal type", key: "deal_type" },
        { label: "PitchBook amount (USD)", num: true, key: "amount_usd", fmt: fmt }, { label: "Basis", key: "amount_basis" }, { label: "Category", key: "category" }, { label: "Logistics", key: "logistics_relevance" },
        { label: "Status", html: function (r) { return r.public_confirmed === "yes" ? '<span class="pill ok">confirmed</span>' : '<span class="pill no">unconfirmed</span>'; } },
        { label: "Public source", html: function (r) { return ext(r.public_source_url, r.public_source_type || "source"); } }, { label: "PitchBook id", cls: "mono", key: "pitchbook_id" }], D, { page: 100 });
    });
  }
}

/* ---------- financial: subsidy leads, GJF, partial search, Statista ---------- */
function finHook(P) {
  var f = P.AMZ_PRIVATE_FIN, app = document.getElementById("app"); if (!f || !app) return;
  var w = wrapper(app, "Unverified subsidy leads, withheld Good Jobs First figures, notes from partial searches and the Statista tables.");
  var subCols = [{ label: "Status", html: function (r) { return '<span class="pill no">' + esc(r.lead_status) + "</span>"; } }, { label: "State", key: "state" }, { label: "Locality", key: "locality" }, { label: "Program", cls: "q", key: "program" },
    { label: "Year", key: "award_year" }, { label: "Amount (USD)", num: true, key: "amount_usd", fmt: fmt }, { label: "Basis", key: "amount_basis" }, { label: "Level", key: "verification_level" },
    { label: "Notes", cls: "q", html: function (r) { return trunc(r.notes, 420); } }, { label: "Found in", key: "from_file" },
    { label: "Source", html: function (r) { return ext(r.source_url, "link") + (r.local_file ? " " + loc(r.local_file) : ""); } }];
  var L = rows(f.leads);
  section(w, "lo-leads", "Unverified subsidy leads", fmt(L.length) + " rows", function (b) {
    b.insertAdjacentHTML("beforeend", '<p class="lo-sum">Rows that are unverified, were dropped from the published file or exist only in an earlier backup (subsidies_verified.pre_*.csv), plus the Good Jobs First rows withheld from the public site. They are leads to check, not findings.</p>');
    table(b, subCols, L, { page: 100 });
  });
  var G = rows(f.gjf);
  section(w, "lo-gjf", "Withheld Good Jobs First rows", fmt(G.length) + " rows", function (b) {
    b.insertAdjacentHTML("beforeend", '<p class="lo-sum">Snippet-only figures from the Good Jobs First subsidy tracker (data/processed/amazon_subsidies_gjf_unverified.csv). The page itself was not fetched, so none of this is verified.</p>');
    table(b, [{ label: "Record", key: "record_type" }, { label: "State", key: "state" }, { label: "Location", key: "location" }, { label: "Program", cls: "q", key: "program" }, { label: "Amount (USD)", num: true, key: "amount_usd", fmt: fmt },
      { label: "Year", key: "year" }, { label: "Jobs or investment", key: "jobs_or_investment" }, { label: "Verification", cls: "q", key: "verification" }, { label: "Source", html: function (r) { return ext(r.source_url, "link"); } }], G);
  });
  var Pa = rows(f.partial);
  section(w, "lo-partial", "Partial-search and searched-none notes", fmt(Pa.length) + " rows", function (b) {
    b.insertAdjacentHTML("beforeend", '<p class="lo-sum">The notes behind the states marked partial search only or searched, none found on the coverage map. Not a proven zero.</p>');
    table(b, subCols.filter(function (c) { return c.label !== "Amount (USD)" && c.label !== "Basis" && c.label !== "Year"; }), Pa);
  });
  var T = f.statista || [], SF = rows(f.statista_facts);
  section(w, "lo-statista", "Statista tables", T.length + " tables, " + fmt(SF.length) + " citable facts", function (b) {
    b.insertAdjacentHTML("beforeend", '<p class="lo-sum">Licensed Statista data (data/private/statista). Only the short cited facts may ever be published; the full tables stay local.</p>');
    b.insertAdjacentHTML("beforeend", "<h3>Citable facts</h3>"); var h1 = document.createElement("div"); b.appendChild(h1);
    table(h1, [{ label: "Year", key: "year" }, { label: "Metric", cls: "q", key: "metric" }, { label: "Value", key: "value" }, { label: "Unit", key: "unit" }, { label: "Statista id", key: "statista_id" }, { label: "Original source", cls: "q", key: "original_source" }], SF);
    b.insertAdjacentHTML("beforeend", "<h3>Full tables</h3>");
    T.forEach(function (t) {
      var d = document.createElement("details"); d.className = "lo"; d.innerHTML = "<summary>" + esc(t.title || ("Statista " + t.id)) + '<span class="lo-n">' + esc(t.id) + ", " + t.rows.length + " rows</span></summary>";
      var inner = document.createElement("div"); inner.className = "lo-body"; d.appendChild(inner); b.appendChild(d);
      var built = false; d.addEventListener("toggle", function () {
        if (!d.open || built) return; built = true;
        inner.insertAdjacentHTML("beforeend", "<p class='lo-sum'>" + loc(t.file, "csv") + (t.html ? " " + loc(t.html, "saved page") : "") + "</p>");
        inner.insertAdjacentHTML("beforeend", '<div class="tw"><table><thead><tr>' + t.cols.map(function (c) { return "<th>" + esc(c) + "</th>"; }).join("") + "</tr></thead><tbody>" +
          t.rows.map(function (r) { return "<tr>" + r.map(function (c) { return "<td>" + esc(c) + "</td>"; }).join("") + "</tr>"; }).join("") + "</tbody></table></div>");
      });
    });
  });
}

/* ---------- methods: MWPVL transcription disagreements ---------- */
function metHook(P) {
  var m = P.AMZ_PRIVATE_MWPVL, app = document.getElementById("app"); if (!m || !app) return;
  var w = wrapper(app, "Where the two readings of the MWPVL table images disagreed, and how each case was settled.");
  var S = m.adj_summary || {}, Dr = rows(m.disagreements), Ar = rows(m.adjudications);
  function imgLink(r) { return r.image_path ? loc(r.image_path, "image") : '<span class="muted">image not found</span>'; }
  section(w, "lo-mwpvl-adj", "MWPVL adjudications (summary and cases)", fmt(S.cases) + " cases", function (b) {
    function list(pairs) { return pairs.map(function (p) { return esc(p[0]) + " <b>" + p[1] + "</b>"; }).join(" &middot; "); }
    b.insertAdjacentHTML("beforeend", '<p class="lo-sum"><b>' + fmt(S.cases) + "</b> adjudicated cases, " + fmt(S.unresolved_cases) + " with an unresolved field. By field in dispute: " + list(S.by_why || []) + ".</p><p class=\"lo-sum\">By basis: " + list(S.by_basis || []) + ".</p>");
    table(b, [{ label: "Case", key: "case" }, { label: "Row", key: "idx" }, { label: "Disputed", key: "why" }, { label: "Code A", key: "a_code" }, { label: "Code B", key: "b_code" }, { label: "Decision", cls: "q mono", key: "decision" },
      { label: "Basis", key: "basis" }, { label: "Unresolved", key: "unresolved" }, { label: "OCR evidence", cls: "q", html: function (r) { return trunc(r.ocr_loc, 160); } }, { label: "Image", html: imgLink }], Ar);
  });
  section(w, "lo-mwpvl-dis", "MWPVL transcription disagreements (every row)", fmt(Dr.length) + " rows, " + fmt(S.images_linked) + " with a local image", function (b) {
    b.insertAdjacentHTML("beforeend", '<p class="lo-sum">One row per disputed field: the vision transcription (claude) against the local OCR model, the decision taken and a link to the table image.</p>');
    table(b, [{ label: "Site", key: "site_code" }, { label: "City", html: function (r) { return esc([r.city, r.state].filter(Boolean).join(", ")); } }, { label: "Field", key: "field" }, { label: "Transcription", key: "claude" }, { label: "OCR", key: "ocr" },
      { label: "Year text", key: "raw_year_text" }, { label: "Status", key: "claude_transcription" }, { label: "Models agree", key: "models_agree" }, { label: "Decision", key: "decision" },
      { label: "Row", key: "row_in_image" }, { label: "Image", html: imgLink }], Dr, { page: 150, text: function (r) { return [r.image, r.site_code, r.city, r.state, r.field, r.claude, r.ocr, r.decision].join(" "); } });
  });
}

/* ---------- sources: the full manifest and the logbook ---------- */
function srcHook(P) {
  var s = P.AMZ_PRIVATE_SOURCES, app = document.getElementById("app"); if (!s || !app) return;
  var w = wrapper(app, "The complete source manifest (public and subscription files) with a link to every local file, and the working logbook.");
  var M = rows(s.manifest);
  section(w, "lo-manifest", "Full source manifest", fmt(M.length) + " files", function (b) {
    b.insertAdjacentHTML("beforeend", '<p class="lo-sum">Every file under data/raw and data/private. Click a path to open the file from this machine. ' + fmt(s.manifest_missing_files) + " listed files are missing on disk. Filter by publisher, domain, role, access or any word in the title.</p>");
    table(b, [{ label: "Title", cls: "q", key: "title" }, { label: "Publisher", key: "publisher" }, { label: "Date", key: "publication_date" }, { label: "Access", html: function (r) { return '<span class="pill' + (r.access === "public" ? "" : " no") + '">' + esc(r.access) + "</span>"; } },
      { label: "Domain", key: "domain" }, { label: "Role", key: "role" }, { label: "Size (bytes)", num: true, key: "size_bytes", fmt: fmt },
      { label: "Original URL or id", cls: "q", html: function (r) { return isUrl(r.url_or_doc_id) ? ext(r.url_or_doc_id, trunc(r.url_or_doc_id, 60).replace(/<[^>]+>/g, "")) : trunc(r.url_or_doc_id, 60); } },
      { label: "Local file", cls: "q", html: function (r) { return r.missing ? '<span class="muted">' + esc(r.local_path) + " (missing)</span>" : loc(r.local_path, r.local_path); } },
      { label: "Flags", key: "flags" }, { label: "Used by", cls: "q", html: function (r) { return trunc(r.used_by, 140); } }], M, { page: 200, text: function (r) { return [r.title, r.publisher, r.domain, r.role, r.access, r.local_path, r.url_or_doc_id, r.flags].join(" "); } });
  });
  section(w, "lo-logbook", "Working logbook (LOGBOOK.md)", null, function (b) { b.insertAdjacentHTML("beforeend", '<div class="lo-log">' + (s.logbook_html || "") + "</div>"); });
}

/* ---------- click-through: add a small "local file" link next to public source links ---------- */
function linksHook(P) {
  var L = P.AMZ_PRIVATE_LINKS; if (!L || !L.by_url) return;
  var app = document.body, busy = false, t = null;
  function pass() {
    busy = true;
    try {
      var as = document.querySelectorAll('a[href^="http"]:not(.lf)');
      for (var i = 0; i < as.length; i++) {
        var a = as[i];
        if (a.closest(".lo-wrap") || a.getAttribute("data-lf")) continue;
        a.setAttribute("data-lf", "1");
        var ps = L.by_url[a.getAttribute("href")] || L.by_url[a.href]; if (!ps || !ps.length) continue;
        var h = "", n = Math.min(ps.length, 3);
        for (var k = 0; k < n; k++) h += loc(ps[k], ps.length > 1 ? "local file " + (k + 1) : "local file").replace(' class="lf"', ' class="lf"');
        if (ps.length > n) h += '<span class="lf muted"> +' + (ps.length - n) + " more</span>";
        a.insertAdjacentHTML("afterend", h);
      }
      /* MWPVL snapshot dates in public table cells -> the saved Wayback snapshot */
      var sd = L.snapshots_by_date || {}, cells = document.querySelectorAll("td:not([data-lf])");
      for (var j = 0; j < cells.length; j++) {
        var c = cells[j]; c.setAttribute("data-lf", "1");
        if (c.closest(".lo-wrap") || c.children.length) continue;
        var tx = c.textContent.trim(); if (sd[tx]) c.insertAdjacentHTML("beforeend", loc(sd[tx], "local snapshot"));
      }
    } catch (e) { }
    busy = false;
  }
  pass();
  try { new MutationObserver(function () { if (busy) return; clearTimeout(t); t = setTimeout(pass, 200); }).observe(app, { childList: true, subtree: true }); } catch (e) { }
}

on("log", logHook); on("map", logHook); on("fin", finHook); on("met", metHook); on("src", srcHook); on("*", linksHook);

/* ---------- boot ---------- */
function run() {
  var P = window, page = (document.getElementById("app") || {}).getAttribute ? document.getElementById("app").getAttribute("data-page") : "";
  css();
  document.body.insertAdjacentHTML("beforeend", '<a id="lo-flag" href="#local-only" title="Local-only layer is on. Built ' + esc(window.AMZ_PRIVATE_BUILT || "") + '">LOCAL ONLY</a>');
  ["*", page].forEach(function (k) {
    (HOOKS[k] || []).forEach(function (fn) { try { fn(P); } catch (e) { if (window.console) console.warn("private hook failed", k, e); } });
  });
  if (location.hash && document.querySelector(location.hash.replace(/[^#\w-]/g, ""))) { try { document.querySelector(location.hash).scrollIntoView(); } catch (e) { } }
}
function boot() {
  /* Under file:// a missing script cannot be probed silently (the browser logs it), so the layer is off there unless the URL has ?local=1.
     Over http(s) (scripts/serve_local.sh) the probe is always made; on the public site it is one expected 404. */
  if (location.protocol === "file:" && !/[?&]local=1\b/.test(location.search)) return;
  load("assets/private_index.js", function (ok) {
    if (!ok || !window.AMZ_PRIVATE_FILES) return;            /* public site, or no private build here: do nothing */
    var files = window.AMZ_PRIVATE_FILES, left = files.length;
    if (!left) return run();
    files.forEach(function (f) { load("assets/" + f, function () { if (--left === 0) run(); }); });
  });
}
if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
