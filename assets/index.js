(function(){
var P_=AMZ_META.pages;if(!P_.some(function(x){return x[0]==="benchmark.html";})){var i_=P_.findIndex(function(x){return x[0]==="environment.html";});P_.splice(i_<0?P_.length-2:i_+1,0,["benchmark.html","Benchmark"]);}
var A=AMZ, F=AMZ_FIN, L=AMZ_LOG, I=AMZ_INJ, P=AMZ_POP, E=AMZ_ENV, B=AMZ_LAB, FA=AMZ_FAC;
A.page({title:"Amazon US warehouse network",sub:"Facilities, finance, labor, injuries and environmental estimates for Amazon's US logistics sites, 1997 to today. Every number links to a source on the <a href=\"sources.html\">Sources</a> page."});
var app=A.$("#app");
var inc=A.rows(F.income), last=inc[inc.length-1], emp=A.rows(B.employees), le=emp[emp.length-1];
var sq=A.rows(L.sqft), ls=sq[sq.length-1];
var cmp=A.rows(I.comparison), c24=cmp.filter(function(r){return r.year===2024;})[0];
var car=A.rows(E.carbon).filter(function(r){return r.report_vintage==="2025 report"&&r.metric==="total_footprint"&&r.year===2025;})[0];
var pop=A.rows(P.by_year).filter(function(r){return r.set==="2025"&&r.site_type==="all";})[0];
var fac=A.rows(FA.facilities), nfac=fac.length, mr=FA.match_report;
var basis=A.by(fac,function(r){return r.year_basis||"undated";});
function nb(k){return (basis[k]||[]).length;}
var pb=A.by(fac.filter(function(r){return r.pullback_status;}),function(r){return r.pullback_status;});
function np(k){return (pb[k]||[]).length;}
var npull=fac.filter(function(r){return r.pullback_status;}).length;
var mw=A.rows(AMZ_MWPVL.openings_by_year), peak=mw.reduce(function(a,b){return b.sites>a.sites?b:a;});
function yr(y){var r=mw.filter(function(x){return x.year===y;})[0];return r?r.sites:0;}
var sub={};A.rows(AMZ_SUB.totals).forEach(function(r){if(r.recipient_class==="direct"&&r.verification==="verified")sub[r.amount_basis]=r;});
function fx1(v){return Number(v).toFixed(1);}
function mus(v){return "$"+A.fmt(v/1e6,1)+"m";}
var bh={};A.rows(AMZ_BENCH.injuries_peer_year).forEach(function(r){if(r.scope==="headline"&&r.year===2024)bh[r.peer]=r;});
A.tiles(app,[
 {value:A.fmt(nb("mwpvl_opening_year"))+" of "+A.fmt(nfac),label:"roster sites dated by an MWPVL opening year",context:"Others dated by first OSHA filing ("+A.fmt(nb("first_osha_filing"))+"), press event ("+A.fmt(nb("press_event_year"))+"), EPI list ("+A.fmt(nb("epi_mwpvl2012_opening_year"))+"); "+A.fmt(nb("undated"))+" undated",href:"map.html"},
 {value:A.fmt(peak.sites)+" in "+peak.year,label:"sites in the MWPVL list with this opening year, the peak year",context:A.fmt(yr(peak.year-1))+" in "+(peak.year-1)+", "+A.fmt(yr(peak.year+1))+" in "+(peak.year+1)+"; "+A.fmt(peak.conflict_modal_value)+" of the "+A.fmt(peak.sites)+" had captures that disagreed",href:"logistics.html#mwpvlopen"},
 {value:A.fmt(npull)+" sites",label:"carry a pullback status: closed, delayed, paused or dropped from the MWPVL list",context:A.fmt(np("removed_from_mwpvl_list"))+" removed from list, "+A.fmt(np("delayed"))+" delayed, "+A.fmt(np("closed")+np("closed_temporary")+np("closed_partial"))+" closed in full or part; a status is not a verified closure",href:"logistics.html#pullback"},
 {value:mus(sub.announced_max.amount_usd),label:"announced maximum value of direct state and local incentives, verified awards",context:A.fmt(sub.announced_max.rows)+" awards; a ceiling, not a payment. Never added to the other bases; "+A.fmt(sub.announced_max.rows_overlap_flagged)+" rows overlap others",href:"financial.html#subs"},
 {value:mus(sub.estimated_value.amount_usd),label:"estimated value of direct incentives, verified awards",context:A.fmt(sub.estimated_value.rows)+" awards ("+A.fmt(sub.estimated_value.rows_overlap_flagged)+" overlap other rows, "+mus(sub.estimated_value.amount_overlap_flagged)+"); an agency or press estimate of value over the term. Separate basis",href:"financial.html#subs"},
 {value:mus(sub.realized.amount_usd),label:"realized (actually received) direct incentives, verified awards",context:A.fmt(sub.realized.rows)+" awards with an amount reported as received. Separate basis; infrastructure rows excluded",href:"financial.html#subs"},
 {value:fx1(bh.amazon.trc)+" vs "+fx1(bh.walmart.trc),label:"2024 recordable injuries per 100 FTE: Amazon logistics sites vs Walmart distribution centers",context:"Same OSHA source and rule for both; "+A.fmt(bh.amazon.n_valid)+" and "+A.fmt(bh.walmart.n_valid)+" establishments",href:"injuries.html#peers"},
 {value:A.pct(pop.share20,0),label:"of the US population lives within 20 miles of a site",context:"2020 population, "+A.fmt(pop.n_sites)+" sites with a 2025 OSHA filing (straight-line)",href:"logistics.html#cover"},
 {value:"$"+A.fmt(last.net_sales_usd_m/1000,0)+"bn",label:"FY"+last.fiscal_year+" net sales",context:"Fulfillment expense "+last.fulfillment_pct_of_sales+"% of sales (company-wide)",href:"financial.html"},
 {value:A.fmt(ls.na_fulfil_dc_other_total_ksf/1000,0)+"m sq ft",label:"North America fulfillment, data center and other space, FY"+ls.fiscal_year_end_dec31,context:"10-K Item 2; includes AWS data centers",href:"logistics.html"},
 {value:A.fmt(le.employees/1000,0)+"k",label:"Amazon employees worldwide, FY"+le.fiscal_year_end_dec31,context:"10-K; not US-only or warehouse-only",href:"labor.html"},
 {value:c24.amz_logistics_trc.toFixed(1)+" vs "+c24.bls_493110_trc.toFixed(1),label:"2024 recordable injuries per 100 FTE: Amazon logistics sites vs BLS warehousing",context:"OSHA ITA vs BLS SOII (NAICS 493110); different sources, see caveats",href:"injuries.html"},
 {value:A.fmt(car.value,1)+" Mt",label:"Amazon total carbon footprint 2025 (CO2e)",context:"Company-wide, from Amazon's 2025 sustainability report",href:"environment.html"},
 {value:A.fmt(B.nlrb_cases.rows.length),label:"NLRB cases with Amazon in the name",context:"2009-2026, mostly 2020 onward",href:"labor.html"}
]);
A.mount(app,'<p class="cap">Tile data and original sources. Dating and pullback: AMZ_FAC.facilities (year_basis, pullback_status) and AMZ_MWPVL.openings_by_year, from the MWPVL warehouse list by Marc Wulfraat (captures via the Wayback Machine), EPI, press reports and OSHA Form 300A filings. Subsidies: AMZ_SUB.totals (recipient_class direct, verification verified; fields rows, amount_usd, rows_overlap_flagged) from state and local award records (issuer and source_url per row in AMZ_SUB.awards); primary and secondary verified rows only. Injuries: AMZ_BENCH.injuries_peer_year (scope headline, 2024; trc, n_valid), OSHA Injury Tracking Application. Other tiles: AMZ_POP, AMZ_FIN, AMZ_LOG, AMZ_LAB, AMZ_ENV, AMZ_INJ. Full list on <a href="sources.html">Sources</a>.</p>');
A.caveat(app,"<b>Read before using.</b><ul><li>The facility roster is built from OSHA injury filings and public lists, so it is a lower bound. Opening years come from the MWPVL warehouse list where a site appears there (where its captures disagree the most common year is used) and otherwise from press events or the first OSHA filing, which is only a date by which the site was operating. Pullback statuses are reported statuses, not verified closures. Subsidy amounts are shown by basis (announced maximum, estimated value, realized) and never summed across bases.</li><li>The OSHA roster counts sites that filed, not all sites. Form 300A electronic filing has covered warehousing sites with 20 or more employees since 2016 data (collected late, with low compliance at first), so growth in filers reflects network growth and compliance, not rule changes.</li><li>Environmental figures are screening estimates, not measurements. Amazon publishes no facility-level energy or fuel data.</li><li>Injury rates are self-reported and the Amazon and BLS series come from different surveys.</li></ul>");
var s1=A.section(app,"charts","Two quick views");
A.mount(s1,'<div class="cols2" id="cc"></div>');
A.lineChart("#cc",{title:"North America fulfillment, data-center and other space (million sq ft)",series:[{name:"Total NA",color:"var(--amz)",points:sq.map(function(r){return [r.fiscal_year_end_dec31,r.na_fulfil_dc_other_total_ksf/1000];})}],yFmt:function(v){return A.fmt(v,0);},caption:"Source: Amazon 10-K Item 2 via SEC EDGAR. Definition changes over time; FY2011 onward includes AWS data centers."});
var yrs=cmp.filter(function(r){return r.year>=2017&&r.year<=2024;});
A.lineChart("#cc",{title:"Total recordable injury rate per 100 full-time workers",series:[
 {name:"Amazon logistics sites (OSHA ITA)",color:"var(--amz)",points:yrs.map(function(r){return [r.year,r.amz_logistics_trc];})},
 {name:"BLS warehousing and storage (493110)",color:"var(--bench)",points:yrs.map(function(r){return [r.year,r.bls_493110_trc];})},
 {name:"BLS all private industry",color:"var(--cat6)",dash:"4 3",points:yrs.map(function(r){return [r.year,r.bls_private_trc];})}],yFmt:function(v){return v.toFixed(1);},caption:"2016 omitted (one Amazon site) and CY2025 omitted (partial filing). BLS figures include Amazon."});
var s2=A.section(app,"pages","Pages");
A.mount(s2,'<div class="pages">'+AMZ_META.pages.filter(function(p){return ["index.html","sources.html","methods.html"].indexOf(p[0])<0;}).map(function(p){
 var d={"map.html":"Every located site on a map of the country, by type, with state shading.","logistics.html":"How big the network was and when: site counts, square footage, air, delivery partners, parcel volume, early openings and robots.","financial.html":"Sales, fulfillment expense, shipping cost, capital spending, state and local subsidies by amount basis.","labor.html":"Employees, wages, union activity and the warehousing workforce by state.","injuries.html":"Amazon recordable injury rates against warehousing as an industry, 2016 to 2025.","environment.html":"Company carbon footprint plus facility-level screening estimates (electricity and gas) with low and high ranges.","benchmark.html":"Amazon against Walmart, Target, other warehouse and parcel operators and the industry: injuries, finance, pay, NLRB activity, emissions, workforce share."}[p[0]]||"";
 return '<a class="pagecard" href="'+p[0]+'"><b>'+A.esc(p[1])+'</b><span>'+A.esc(d)+'</span></a>';}).join("")+'<a class="pagecard" href="sources.html"><b>Sources</b><span>Every dataset with publisher, URL, retrieval date and caveats.</span></a><a class="pagecard" href="methods.html"><b>Methods</b><span>Assumptions, match rates and known gaps for each domain.</span></a></div>');
})();