/* environment.html: benchmark emissions comparison note. Data: AMZ_BENCH.environment_intensity, environment_emissions, environment_boundaries. */
(function(){
"use strict";
var A=AMZ, B=window.AMZ_BENCH, app=A.$("#app");
if(!B||!app) return;
var host=A.section(app,"peers","Scope 1 and 2 emissions against peer companies",
 "Company-wide reported emissions per dollar of revenue, computed the same way for each company. This is a comparison of reported totals, not of warehouses: no company publishes warehouse-level emissions.");
var sec=host.parentNode, src=A.$(".srcs",app); if(src) app.insertBefore(sec,src);
var all=A.rows(B.environment_intensity), latest={};
all.forEach(function(r){if(r.s12_market_g_per_usd==null||/base/.test(r.period))return;var c=latest[r.company];if(!c||r.revenue_fiscal_period_end>c.revenue_fiscal_period_end)latest[r.company]=r;});
var L=Object.keys(latest).map(function(k){return latest[k];}).sort(function(a,b){return a.s12_market_g_per_usd-b.s12_market_g_per_usd;});
A.barChart(host,{title:"Scope 1 + 2 (market-based) emissions per dollar of revenue, latest year each company reports (g CO2e per $)",
 items:L.map(function(r){return {label:r.company+" ("+r.period+")",value:r.s12_market_g_per_usd,color:r.company==="Amazon"?"var(--amz)":"var(--bench)",note:A.fmt(r.s12_market_t/1e6,2)+" Mt CO2e on $"+A.fmt(r.revenue_usd_m/1000,1)+"bn revenue"+(r.note&&/derived/.test(r.note)?"; derived from reported % change":"")};}),
 labelWidth:170,valFmt:function(v){return Number(v).toFixed(1);},
 caption:"Data: AMZ_BENCH.environment_intensity (fields company, period, s12_market_t, revenue_usd_m, s12_market_g_per_usd). Emissions: each company's sustainability report (listed under Sources below). Revenue: Form 10-K, SEC EDGAR. Walmart divides calendar-year emissions by fiscal-year revenue, and so does this chart. Target's Scope 1 + 2 is derived from a reported percentage change."});
var am=latest.Amazon, wm=latest.Walmart;
var t='';
if(am&&wm) t+="Amazon's Scope 1 + 2 emissions were "+A.fmt(am.s12_market_t/1e6,1)+" Mt CO2e ("+am.period+") against Walmart's "+A.fmt(wm.s12_market_t/1e6,1)+" Mt ("+wm.period+"). Per dollar of revenue Amazon is at "+Number(am.s12_market_g_per_usd).toFixed(1)+" g and Walmart at "+Number(wm.s12_market_g_per_usd).toFixed(1)+" g. The two carriers, UPS and FedEx, are several times higher because they fly aircraft and run large truck fleets. ";
t+="<b>Scope 3 is not compared.</b> Companies draw the boundary differently (Walmart and Home Depot count the goods they buy and sell; Amazon's boundary does not cover third-party seller merchandise), and Amazon's Scope 3 includes delivery bought from carriers that also appear in their own Scope 1. Amazon's own reported intensity (Scope 1+2+3 per dollar) is a different quantity from the chart above.";
A.mount(host,'<div class="find cav">'+t+' See the <a href="benchmark.html">Benchmark page</a> for boundaries and sources by company.</div>');
/* sources: distinct reports behind the emissions rows shown */
var seen={}, list=[], iu={};
all.forEach(function(r){if(r.source_url&&/^https?:/.test(r.source_url))iu[r.company]=r.source_url;});
B.environment_emissions&&A.rows(B.environment_emissions).forEach(function(r){
 if(!latest[r.company]||!r.source_doc)return; var k=r.company+"|"+r.source_doc; if(seen[k])return; seen[k]=1;
 list.push({label:r.company+": "+r.source_doc,url:r.source_url&&/^https?:/.test(r.source_url)&&!/proxy/i.test(r.source_url)?r.source_url:(/2025 Sustainability Report|FY2025|FY25|2025 GRI|2026 Corporate/.test(r.source_doc)?(iu[r.company]||""):"")});});
A.sources(host,list.concat([{label:"Annual reports on Form 10-K (revenue)",url:"https://www.sec.gov/edgar/search/",publisher:"SEC EDGAR"}]));
})();
