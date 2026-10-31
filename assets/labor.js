/* labor.html: benchmark panels. Data: AMZ_BENCH.labor_announced_vs_qcew493 and labor_nlrb_counts_by_year. */
(function(){
"use strict";
var A=AMZ, B=window.AMZ_BENCH, app=A.$("#app");
if(!B||!app) return;
var host=A.section(app,"peers","Pay and NLRB activity against peer employers",
 "Two comparisons from the <a href=\"benchmark.html\">Benchmark page</a>: announced warehouse pay set against the BLS average wage for warehousing, and NLRB charge volume against company size. Both are indicators with large caveats, not measures of working conditions.");
var sec=host.parentNode, src=A.$(".srcs",app); if(src) app.insertBefore(sec,src);
function usd(v){return v==null?"":"$"+Number(v).toFixed(2).replace(/\.00$/,"");}

/* ---- wages ---- */
var w=A.rows(B.labor_announced_vs_qcew493).filter(function(r){return /^yes/.test(r.warehouse_dc_specific)&&!/total compensation/.test(r.metric);});
w.sort(function(a,b){return a.company===b.company?(a.announce_date<b.announce_date?-1:1):(a.company==="Amazon"?-1:b.company==="Amazon"?1:a.company<b.company?-1:1);});
A.mount(host,'<h3 class="cap" style="font-size:13px;margin-top:6px">Announced warehouse pay as a share of the BLS warehousing average</h3>');
A.mount(host,'<div class="tw"><table><thead><tr><th>Employer</th><th>Announced</th><th>What was announced</th><th class="n">USD per hour</th><th class="n">QCEW 493 average per hour (weekly wage / 40)</th><th class="n">Announced as % of QCEW</th><th>Source</th></tr></thead><tbody>'+
 w.map(function(r){var rng=r.announced_usd_hr_high!=null?usd(r.announced_usd_hr_low)+" to "+usd(r.announced_usd_hr_high):usd(r.announced_usd_hr_low);
  var pc=r.announced_high_as_pct_of_qcew_493!=null?Number(r.announced_low_as_pct_of_qcew_493).toFixed(0)+" to "+Number(r.announced_high_as_pct_of_qcew_493).toFixed(0):Number(r.announced_low_as_pct_of_qcew_493).toFixed(0);
  return "<tr><td>"+A.esc(r.company)+"</td><td>"+A.esc(r.announce_date)+"</td><td class=\"t\">"+A.esc(r.metric)+'</td><td class="n">'+rng+'</td><td class="n">'+usd(r.qcew_493_hourly_equiv_40h)+" ("+r.qcew_year+')</td><td class="n">'+pc+"</td><td>"+(r.announced_source_url&&/^https?:/.test(r.announced_source_url)?'<a href="'+A.esc(r.announced_source_url)+'" target="_blank" rel="noopener">link</a>':"")+"</td></tr>";}).join("")+
 "</tbody></table></div>");
A.mount(host,'<p class="srcline">Data: <code>AMZ_BENCH.labor_announced_vs_qcew493</code> (fields company, announce_date, metric, announced_usd_hr_low/high, qcew_year, qcew_493_hourly_equiv_40h, announced_low_as_pct_of_qcew_493). Sources: each employer announcement (linked); BLS Quarterly Census of Employment and Wages, national NAICS 493, private ownership (<a href="https://www.bls.gov/cew/" target="_blank" rel="noopener">bls.gov/cew</a>). Only rows marked as warehouse or distribution specific are shown; total-compensation claims are left out.</p>');
A.estimate(host,"The QCEW figure is an average for every job in warehousing, including supervisors, overtime and bonuses, divided by 40 hours (hours are not reported). A starting rate or a floor compared with an average is not like-for-like: it shows how an entry rate relates to the industry mean, not whether workers earn less. Amazon's figures are \"more than\" floors from its own announcements.");

/* ---- NLRB ---- */
var n=A.rows(B.labor_nlrb_counts_by_year), YEAR=2024;
var y=n.filter(function(r){return r.year_filed===YEAR&&r.ca_per_10k_employees!=null;}).sort(function(a,b){return b.ca_per_10k_employees-a.ca_per_10k_employees;});
var skipped=n.filter(function(r){return r.year_filed===YEAR&&r.ca_per_10k_employees==null;}).map(function(r){return r.company;});
A.barChart(host,{title:"NLRB unfair-labor-practice charges against the employer per 10,000 employees, filed "+YEAR,
 items:y.map(function(r){return {label:r.company,value:r.ca_per_10k_employees,color:r.company==="Amazon"?"var(--amz)":"var(--bench)",note:A.fmt(r.ca_ulp_charges_vs_employer)+" CA charges; "+A.fmt(r.all_cases)+" cases of all types; "+A.fmt(r.employees_total_10k)+" employees (10-K)"};}),
 labelWidth:110,valFmt:function(v){return Number(v).toFixed(2);},
 caption:"Data: AMZ_BENCH.labor_nlrb_counts_by_year (fields company, year_filed, ca_ulp_charges_vs_employer, employees_total_10k, ca_per_10k_employees). Source: NLRB public case search by company name (<a href=\"https://www.nlrb.gov/search/case\" target=\"_blank\" rel=\"noopener\">nlrb.gov</a>); employees from each company's Form 10-K (SEC EDGAR), worldwide headcount."+(skipped.length?" "+skipped.join(", ")+" omitted: no usable 10-K headcount.":"")});
var cos=y.map(function(r){return r.company;}), yrs=[2022,2023,2024];
A.mount(host,'<details class="tv"><summary>Table view: charges per 10,000 employees, and charge counts</summary><div class="tw"><table><thead><tr><th>Employer</th>'+yrs.map(function(v){return '<th class="n">'+v+" per 10k</th>";}).join("")+yrs.map(function(v){return '<th class="n">'+v+" CA charges</th>";}).join("")+"</tr></thead><tbody>"+
 cos.map(function(c){var m={};n.forEach(function(r){if(r.company===c)m[r.year_filed]=r;});
  return "<tr><td>"+A.esc(c)+"</td>"+yrs.map(function(v){return '<td class="n">'+(m[v]&&m[v].ca_per_10k_employees!=null?Number(m[v].ca_per_10k_employees).toFixed(2):"")+"</td>";}).join("")+yrs.map(function(v){return '<td class="n">'+(m[v]?A.fmt(m[v].ca_ulp_charges_vs_employer):"")+"</td>";}).join("")+"</tr>";}).join("")+"</tbody></table></div></details>");
A.estimate(host,"A charge is an allegation, not a finding, and volume also reflects union presence and organizing activity. UPS, with most of its US workforce under Teamsters agreements, has the highest rate. Employee counts are worldwide, so rates per US worker would be higher for every company. Cases are matched by name, so cases filed under subsidiary or contractor names are missed.");
})();
