/* injuries.html: "vs peers" panel. Data: AMZ_BENCH.injuries_peer_year (scope = headline, year 2024). */
(function(){
"use strict";
var A=AMZ, B=window.AMZ_BENCH, app=A.$("#app");
if(!B||!app) return;
var YEAR=2024;
var rows=A.rows(B.injuries_peer_year).filter(function(r){return r.scope==="headline"&&r.year===YEAR;});
var by={}; rows.forEach(function(r){by[r.peer]=r;});
var want=[
 ["amazon","Amazon logistics sites","var(--amz)"],
 ["walmart","Walmart distribution centers","var(--bench)"],
 ["group_retailer_dcs","Retailer DCs combined (Walmart, Target, Home Depot, Lowe's, Costco, Kroger)","var(--bench)"],
 ["ita_493110_ex_amazon_ex_peers","Other 493110 filers excl. peers","var(--bench)"],
 ["ups","UPS (package network)","var(--bench)"]
].filter(function(w){return by[w[0]];});
if(!want.length) return;
var bls=by.amazon.bls_493110_trc;
function f1(v){return v==null?"n/a":Number(v).toFixed(1);}
function f2(v){return v==null?"n/a":Number(v).toFixed(2);}
var host=A.section(app,"peers","Amazon against peer employers, "+YEAR,
 "Same OSHA source and same rule for every employer: total recordable cases per 100 full-time workers, hours-weighted over establishments with valid hours. Amazon against Walmart distribution centers, other filers in the same industry code, and UPS. The full comparison, with more peers and years, is on the <a href=\"benchmark.html\">Benchmark page</a>.");
var sec=host.parentNode; /* move above the Sources block */
var src=A.$(".srcs",app); if(src) app.insertBefore(sec,src);
var ok=want.every(function(w){return by[w[0]].headline_comparison_ok==="True";});
var items=want.map(function(w){var r=by[w[0]];return {label:w[1].length>34?w[1].replace(/ \(.*\)/,""):w[1],value:r.trc,color:w[2],note:A.fmt(r.n_valid)+" establishments; DART "+f1(r.dart)+", days-away "+f2(r.dafw)};});
items.push({label:"BLS warehousing (493110)",value:bls,color:"var(--cat6)",note:"BLS SOII, all private-sector establishments; a different survey"});
A.barChart(host,{title:"Recordable injury rate per 100 full-time workers, "+YEAR,items:items,labelWidth:200,valFmt:f1,
 caption:"Data: AMZ_BENCH.injuries_peer_year (scope headline, year "+YEAR+"; fields peer, trc, dart, dafw, n_valid, bls_493110_trc). Source: OSHA Injury Tracking Application Form 300A establishment data, CY2016-CY2025 (<a href=\"https://www.osha.gov/Establishment-Specific-Injury-and-Illness-Data\" target=\"_blank\" rel=\"noopener\">osha.gov</a>); BLS reference: Survey of Occupational Injuries and Illnesses, NAICS 493110 (<a href=\"https://www.bls.gov/iif/\" target=\"_blank\" rel=\"noopener\">bls.gov/iif</a>). Peer rows are matched by company name and employer ID number, so they are a screen, not a census."});
var a=by.amazon, w=by.walmart;
var tb='<div class="tw"><table><thead><tr><th>Employer</th><th class="n">Establishments (valid)</th><th class="n">Recordable</th><th class="n">DART</th><th class="n">Days away</th></tr></thead><tbody>'+
 want.map(function(x){var r=by[x[0]];return "<tr><td>"+A.esc(r.peer_label)+'</td><td class="n">'+A.fmt(r.n_valid)+'</td><td class="n">'+f2(r.trc)+'</td><td class="n">'+f2(r.dart)+'</td><td class="n">'+f2(r.dafw)+"</td></tr>";}).join("")+
 '<tr><td>BLS warehousing and storage (493110)</td><td class="n"></td><td class="n">'+f2(bls)+'</td><td class="n">'+f2(a.bls_493110_dart)+'</td><td class="n">'+f2(a.bls_493110_dafw)+"</td></tr></tbody></table></div>";
A.mount(host,'<details class="tv"><summary>Table view</summary>'+tb+"</details>");
var txt='Amazon\'s rate is '+(a.trc/w.trc).toFixed(1)+' times Walmart\'s distribution centers ('+f1(a.trc)+' against '+f1(w.trc)+'). '+
 'UPS is higher than Amazon ('+f1(by.ups.trc)+'), so Amazon is neither the lowest nor the highest of the large logistics employers. ';
if(!ok) txt+="One or more rows is flagged as not comparable in the source file. ";
A.mount(host,'<p class="method">'+txt+'Walmart rows cover its 493110 distribution centers only; its private truck fleet and stores are excluded, and Sam\'s Club DCs filed under Walmart names cannot be separated. <a href="benchmark.html">See the Benchmark page for scope, matching rules and caveats.</a></p>');
})();
