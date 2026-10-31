"""Air, DSP, parcel-volume and timeline tables. Run: python3 -I logistics_03_build_tables.py
Values transcribed from the sources named in each row (see data/notes/logistics.md). No interpolation."""
import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # project root, so scripts run from any checkout
import csv
P=_ROOT+'/data/processed'; R='2026-10-31'
def write(name,header,rows):
    with open(f'{P}/{name}','w',newline='',encoding='utf8') as f:
        w=csv.writer(f); w.writerow(header); w.writerows(rows)
    print(name,len(rows))
WP='https://en.wikipedia.org/wiki/Amazon_Air'
# ---- Amazon Air fleet (aircraft counts as reported; definitions differ)
A=[
('2016-03','Amazon Air scheduled operations begin with 20 Boeing 767s',20,'Wikipedia (Amazon Air), citing ATSG/press',WP,'Wikipedia','low-medium','Secondary; check cited refs before publication'),
('2017-12','Fleet of 767-300ER freighters',21,'Wikipedia (Amazon Air)',WP,'Wikipedia','low-medium','Secondary'),
('2018-12','Fleet reported at 50 after ATSG 767-300 leases',50,'Wikipedia (Amazon Air)',WP,'Wikipedia','low','Article itself notes 2018 and 2019-20 lease counts may overlap; the 33 in June 2018 had no citation and is NOT used'),
('2021-01','Purchased 11 aircraft from Delta Air Lines and WestJet (first-ever owned fleet additions began 2020-09 with 4 WestJet 767-300s)',11,'Wikipedia (Amazon Air)',WP,'Wikipedia','low-medium','This is purchases, not fleet total'),
('2024-02','Approx fleet of 90 leased aircraft (majority 767s)',90,'Search-result summary of secondary sources; primary not retrieved','https://www.freightwaves.com/news/amazon-airs-new-reliance-on-hub-airports-increases-efficiency','FreightWaves (headline page; figure not confirmed from page text)','low','Verify against the page before use'),
('2024-12','Fleet comprises 104 aircraft operated by nine carriers',104,'Cargo Facts Consulting (as quoted in search result)','https://cargofacts.com/consulting/amazon-air-routes-capacities-and-new-strategies','Cargo Facts Consulting','low-medium','Page returned HTTP 403 for fetch; figure from search snippet only'),
('2025-01','Total fleet listed in Wikipedia fleet table',101,'Wikipedia (Amazon Air)',WP,'Wikipedia','low-medium','Differs from Cargo Facts 104 (Dec 2024): definitions/dates differ'),
]
write('logistics_air_fleet.csv',['as_of','description','aircraft_count','reported_by','source_url','publisher','confidence','caveats','retrieved'],[[*a,R] for a in A])
H=[
('2015-late','Wilmington Air Park OH','trial cargo runs (Project Aerosmith) begin','Wikipedia (Amazon Air)'),
('2017-01-31','Cincinnati/Northern Kentucky (CVG, KY)','Amazon names CVG its principal air hub; flight operations began 2017-04-30 from interim facility','Wikipedia (Amazon Air)'),
('2019-10-02','Fort Worth Alliance TX','regional hub begins operating','Wikipedia (Amazon Air)'),
('2021-04-28','San Bernardino KSBD CA','new Southern California hub begins operations (Apr 28-29)','Wikipedia (Amazon Air)'),
('2021-08-11','CVG Amazon Air Hub (KY)','new ~$1.5 billion purpose-built hub begins operations; soft-open domestic day-shift; planned 24/7 and international by Mar 2022; widely reported ~2,000 jobs','Wikipedia (Amazon Air) / news coverage (Routes, Fox19, Spectrum News); date 2021-08-11 from a trade report in search results'),
]
write('logistics_air_hubs.csv',['date','location','event','source_basis','source_url','confidence','caveats','retrieved'],
 [[d,l,e,b,WP if 'Wikipedia' in b else 'https://www.fox19.com/2021/08/11/amazon-launches-amazon-air-hub-cvg','low-medium','Secondary sources; month/day vary across outlets (Aug vs Sept 2021 reported by some). Official Amazon release not retrieved',R] for d,l,e,b in H])

# ---- DSP program
G='https://channelx.world/2018/09/amazon-forced-to-turn-down-tens-of-thousands-of-delivery-service-partner-applicants/'
D=[
('2018-06','program_launch','Delivery Service Partner program announced (aboutamazon.com article says "In June")',None,'','https://www.aboutamazon.com/news/transportation/amazon-orders-20-000-vans-for-small-businesses','Amazon (aboutamazon.com)','medium','Year not printed in page text I retrieved; 2018 per channelx/Sept 2018 coverage and the project brief'),
('2018-09-19','vans_ordered','Amazon raises Mercedes-Benz Sprinter van order from 5,000 to 20,000 (an order, not a fleet count)',20000,'vans ordered',G,'ChannelX (Chris Dawson), quoting Amazon','medium','Planned order; tens of thousands of applicants; Amazon initially planned "hundreds" of operators'),
('2020-08-13','dsp_count','More than 1,300 DSPs; nearly 85,000 jobs; US, Canada, UK, Spain, Germany',1300,'DSP companies (global)','https://postandparcel.info/125339/news/amazon-claims-remarkable-growth-for-its-delivery-service-partner-programme','Post&Parcel citing Amazon blog post of 2020-08-07','medium','Global, not US-only; jobs figure nearly 85,000'),
('2020-08-13','dsp_jobs','Nearly 85,000 DSP jobs',85000,'jobs (global)','https://postandparcel.info/125339/news/amazon-claims-remarkable-growth-for-its-delivery-service-partner-programme','Post&Parcel citing Amazon','medium',''),
('2023','dsp_count','3,500 DSP firms, 279,000 driving jobs (the prior-year comparator in Amazon 2024 announcement)',3500,'DSP firms (global)','https://www.geekwire.com/2024/amazon-plans-rate-increases-and-routing-technology-improvements-for-delivery-firms/','GeekWire (page not fetchable; figures from search-result summary)','low','Exact date unknown'),
('2023','dsp_jobs','279,000 driving jobs',279000,'jobs (global)','https://www.geekwire.com/2024/amazon-plans-rate-increases-and-routing-technology-improvements-for-delivery-firms/','GeekWire','low',''),
('2024','dsp_count','4,400 DSP firms representing 390,000 driving jobs worldwide; $2.1 billion DSP program investment',4400,'DSP firms (global)','https://www.geekwire.com/2024/amazon-plans-rate-increases-and-routing-technology-improvements-for-delivery-firms/','GeekWire citing Amazon','low','A commenter argues 390k may be cumulative since 2018 (unverified). Month unknown'),
('2024','dsp_jobs','390,000 driving jobs',390000,'jobs (global)','https://www.geekwire.com/2024/amazon-plans-rate-increases-and-routing-technology-improvements-for-delivery-firms/','GeekWire citing Amazon','low','May be cumulative; see above'),
]
write('logistics_dsp.csv',['date','metric','description','value','unit','source_url','publisher','confidence','caveats','retrieved'],[[*d[:3],d[3] if d[3] is not None else '',*d[4:],R] for d in D])

# ---- US parcel volume (Pitney Bowes Parcel Shipping Index), billions
PB={'2020':'https://s203.q4cdn.com/910716257/files/doc_news/2020/10/News-Release-1698772536964440.pdf','2021':'https://s203.q4cdn.com/910716257/files/doc_news/2021/09/News-Release-1698772315506235.pdf',
'2023':'https://s203.q4cdn.com/910716257/files/doc_news/2023/03/News-Release-1698771911420130.pdf','2024':'https://s203.q4cdn.com/910716257/files/doc_news/Pitney-Bowes-Parcel-Shipping-Index-Consumer-Demand-for-Real-Time-Retail-Shakes-Carrier-Market-Share-2024.pdf',
'2025':'https://www.nasdaq.com/press-release/pitney-bowes-parcel-shipping-index-us-carrier-disruption-increasing-and-thats-good'}
V=[ # year, carrier, volume_bn, share_pct, revenue_bn, edition, note, status
(2018,'US total',13.2,'','', '2020','As restated in 2020 release (14.7 for 2019 incl Amazon Logistics)','primary'),
(2019,'US total',14.7,'',130,'2020','Revenue $130bn','primary'),
(2019,'Amazon Logistics',1.9,'','','2020','Amazon-delivered parcels via in-house network; +155% y/y per release; later edition (2024) rounds 2019 as 2B','primary'),
(2020,'US total',20.2,'','171.4','2021','+37% y/y; parcels per capita 61','primary'),
(2020,'Amazon Logistics','','', '','2021','Release gives +127% volume and +109% revenue y/y but no level; 4.2bn / shares USPS38 UPS24 AMZL21 FedEx16 appear only in a secondary summary and are NOT recorded','primary-growth-only'),
(2021,'US total',21.7,'',186,'2023','2022 edition first printed 21.5; 2023 edition restates 21.7','primary'),
(2021,'USPS',7.0,'','','2023','','primary'),(2021,'UPS',5.3,'','','2023','','primary'),(2021,'FedEx',4.3,'','','2023','','primary'),(2021,'Amazon Logistics',4.8,22,'','2023','Share 22% stated as prior-year comparator','primary'),
(2022,'US total',21.2,'',198,'2023','Later restated to 21.5 (2024 release); carrier revenue total $198bn (restated 198.4)','primary'),
(2022,'USPS',6.7,32,31,'2023','Share from secondary report of same release; 6.7bn and revenue primary','primary (volume), secondary (share)'),
(2022,'UPS',5.2,24,73,'2023','','primary (volume), secondary (share)'),
(2022,'FedEx',4.1,19,65,'2023','','primary (volume), secondary (share)'),
(2022,'Amazon Logistics',4.8,23,24,'2023','Share 23% primary','primary'),
(2023,'US total',21.7,'',197.9,'2024','+0.5% y/y','primary'),
(2023,'USPS',6.6,31,31.7,'2024','','primary'),
(2023,'Amazon Logistics',5.9,27,28.6,'2024','+15.7% y/y; first year above UPS; nearly tripled from 2B in 2019','primary'),
(2023,'UPS',4.6,21,68.9,'2024','-10.3% y/y','primary'),
(2023,'FedEx',3.9,'',63.2,'2024','-6.1% y/y','primary'),
(2023,'Others',0.6,'',5.6,'2024','','primary'),
(2024,'US total',22.4,'','', '2025','+3.4% y/y; revenue +2.7%','primary'),
(2024,'Amazon Logistics',6.3,'','','2025','Share computed 28.1% = 6.3/22.4 (computed here, not printed in release text I retrieved; a secondary summary also says 28%)','primary (volume)'),
(2024,'USPS',6.9,'','','2025','Computed share 30.8%','primary (volume)'),
(2024,'Others',0.8,'','','2025','+23% y/y','primary'),
]
rows=[]
for y,c,v,sh,rev,ed,note,st in V:
    if c in('Amazon Logistics','USPS') and y==2024 and v!='': sh=round(v/22.4*100,1); sh_basis='computed (volume / US total)'
    else: sh_basis='as published' if sh!='' else ''
    rows.append([y,c,v,sh,sh_basis,rev,ed,PB.get(ed,PB['2020']) if ed in PB else PB['2020'],'Pitney Bowes Inc. Parcel Shipping Index press release',st,note,R])
write('logistics_us_parcel_volume.csv',['year','carrier','volume_billion_parcels','share_of_volume_pct','share_basis','revenue_billion_usd','index_edition_release_year','source_url','publisher','status','notes','retrieved'],rows)

# ---- Timeline
ST='https://www.supplychaindive.com/news/amazon-fastest-prime-fulfillment-speeds-ever-q2-doug-herrington/689415/'
AS='https://www.amazon.science/news-and-features/how-amazon-reworked-its-fulfillment-network-to-meet-customer-demand'
SEC='https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001018724&type=10-K'
RW='https://www.freightwaves.com/?p=540523'
TL=[
('1997','year','network','Fulfillment centers in Seattle WA and New Castle DE (the two original FCs, per MWPVL narrative)',2,'fulfillment centers','https://www.mwpvl.com/html/amazon_com.html','MWPVL International','medium'),
('1999','year','network','Fulfillment centers added at Fernley NV, Coffeyville KS, McDonough GA, Campbellsville KY, Lexington KY (MWPVL narrative)',5,'fulfillment centers added','https://www.mwpvl.com/html/amazon_com.html','MWPVL International','medium'),
('2001-01','month','network','Amazon announces closure of McDonough GA FC and seasonal-only operation of Seattle FC; six US FCs listed in FY2001 10-K',6,'US FCs','https://www.sec.gov/Archives/edgar/data/1018724/000103221002000059/d10k405.htm','Amazon.com 10-K FY2001 (EDGAR)','high'),
('2005-02-02','day','speed','Amazon Prime launches in the US: free two-day shipping on eligible items for an annual fee ($79 per secondary sources)',2,'days','https://www.pattern.com/blog/amazon-prime-timeline-from-2005-to-today','Pattern (secondary); verify against Amazon press release','low-medium'),
('2014','year','network','FY2014 10-K properties text newly lists sortation and delivery facilities (absent from the FY2013 text)',None,'','https://www.sec.gov/Archives/edgar/data/1018724/000101872415000006/amzn-20141231x10k.htm','Amazon.com 10-K FY2014 (EDGAR)','high'),
('2015-05','month','speed','Free Same-Day delivery for Prime members in 14 US metros (secondary sources)',14,'metros','https://www.pattern.com/blog/amazon-prime-timeline-from-2005-to-today','Pattern (secondary)','low-medium'),
('2015-late','month','air','Trial cargo runs from Wilmington Air Park OH (Project Aerosmith); Dec 2015 plan for own cargo airline reported',None,'',WP,'Wikipedia (Amazon Air)','low-medium'),
('2016-03','month','air','Amazon Air operations begin with 20 Boeing 767s',20,'aircraft',WP,'Wikipedia (Amazon Air)','low-medium'),
('2017-01-31','day','air','CVG named principal hub; operations began 2017-04-30',None,'',WP,'Wikipedia (Amazon Air)','low-medium'),
('2018-06','month','dsp','Delivery Service Partner (DSP) program announced',None,'','https://www.aboutamazon.com/news/transportation/amazon-orders-20-000-vans-for-small-businesses','Amazon (aboutamazon.com)','medium'),
('2018-09-19','day','dsp','Amazon increases Sprinter van order from 5,000 to 20,000 for DSP operators',20000,'vans ordered',G,'ChannelX','medium'),
('2019-04','month','speed','Amazon says it will spend $800 million in Q2 2019 to move Prime from two-day to one-day shipping (secondary summary of Q1 2019 earnings)',800,'million USD','https://www.pymnts.com/amazon/2019/amazon-one-day-shipping-no-minimum-purchase/','PYMNTS (secondary); Amazon Q1 2019 earnings release is the primary','low-medium'),
('2019-06','month','speed','Prime Free One-Day delivery available on more than 10 million products with no minimum purchase (secondary)',10000000,'products','https://www.pymnts.com/amazon/2019/amazon-one-day-shipping-no-minimum-purchase/','PYMNTS (secondary)','low-medium'),
('2019-10-02','day','air','Fort Worth Alliance (TX) regional air hub begins operating',None,'',WP,'Wikipedia (Amazon Air)','low-medium'),
('2020-03-03','day','speed','Amazon installs mini fulfillment centers in cities incl. Dallas, Orlando, Philadelphia, Phoenix to cut same-day times (secondary)',None,'','https://www.retailtouchpoints.com/news/amazon-nearly-quadruples-same-and-next-day-prime-delivery-volume-over-2019/135974/','Retail TouchPoints (search summary)','low'),
('2020-08-07','day','dsp','Amazon blog: more than 1,300 DSPs, nearly 85,000 jobs, five countries',1300,'DSPs','https://postandparcel.info/125339/news/amazon-claims-remarkable-growth-for-its-delivery-service-partner-programme','Post&Parcel citing Amazon','medium'),
('2020-12-31','day','network','FY2020: 285.7 million leased + 8.5 million owned sq ft of North America "fulfillment, data centers, and other" (vs 192.7 million total in FY2019; see logistics_sqft_by_year.csv)',294138,'thousand sq ft','https://www.sec.gov/Archives/edgar/data/1018724/000101872421000004/amzn-20201231.htm','Amazon.com 10-K FY2020','high'),
('2021-04-28','day','air','San Bernardino (KSBD, CA) air hub begins operations',None,'',WP,'Wikipedia (Amazon Air)','low-medium'),
('2021-08-11','day','air','CVG Amazon Air Hub (about $1.5 billion; ~2,000 jobs reported) opens',None,'','https://www.fox19.com/2021/08/11/amazon-launches-amazon-air-hub-cvg','Fox19 (news; date per trade reports)','medium'),
('2022-2023','year','network','MWPVL: over 123 buildings closed, cancelled or delayed (mostly US) as Amazon scaled back after pandemic over-build',123,'buildings','https://www.mwpvl.com/html/amazon_com.html','MWPVL International','medium'),
('2023-01-18','day','speed','Regionalization go-live begins in Northeast and Mid-Atlantic; eight regions; remaining regions activated a month earlier than planned (INFORMS paper: full deployment by March 2023)',8,'regions',AS,'Amazon Science (2023-07-24)','high'),
('2023-07-24','day','speed','Amazon Science: share of orders filled entirely within a region rose from 62% to 76%',76,'percent in-region',AS,'Amazon Science','high'),
('2023-07-31','day','speed','Q2 2023 call: fastest Prime speeds ever; more than half of Prime orders in the 60 largest metros arrive same or next day; >76% of orders fulfilled within customer region; plan to double same-day sites',76,'percent in-region',ST,'Supply Chain Dive (2023-07-31)','high'),
('2024-04-17','day','volume','Pitney Bowes: Amazon Logistics passes UPS in US parcel volume (5.9bn vs 4.6bn) for 2023',5.9,'billion parcels','https://s203.q4cdn.com/910716257/files/doc_news/Pitney-Bowes-Parcel-Shipping-Index-Consumer-Demand-for-Real-Time-Retail-Shakes-Carrier-Market-Share-2024.pdf','Pitney Bowes','high'),
('2024','year','dsp','Amazon: 4,400 DSP firms and 390,000 driving jobs worldwide (possibly cumulative)',4400,'DSPs','https://www.geekwire.com/2024/amazon-plans-rate-increases-and-routing-technology-improvements-for-delivery-firms/','GeekWire (search summary)','low'),
('2025-04/05','month','speed','Amazon announces more than $4 billion to extend same-day and next-day delivery to about 4,000 smaller towns and rural communities by end of 2025; 200+ new rural delivery stations (date: Apr 30 per FreightWaves, May per Chain Store Age)',4000,'communities',RW,'FreightWaves / Chain Store Age (search summaries)','low-medium'),
('2025-12-31','day','network','FY2025: 474.1 million leased + 45.8 million owned sq ft of North America fulfillment, data centers and other',519931,'thousand sq ft','https://www.sec.gov/Archives/edgar/data/1018724/000101872426000004/amzn-20251231.htm','Amazon.com 10-K FY2025','high'),
('2025-06-30','day','volume','Pitney Bowes: Amazon Logistics handled 6.3bn US parcels in 2024, second to USPS 6.9bn; projected to overtake USPS by 2028 (forecast)',6.3,'billion parcels',PB['2025'],'Pitney Bowes (Nasdaq copy)','high'),
('2025-09-30','day','network','Moraine Research counts 1,399 operating US Amazon sites (162 sort centers, 392 delivery stations, 192 rural delivery stations, 115 same-day sites)',1399,'sites','https://morainecre.com/resources/research/amazon-logistics-network-map','Moraine Research (2026-10-04)','medium'),
]
write('logistics_timeline.csv',['date','date_precision','category','event','value','unit','source_url','publisher','confidence','retrieved'],[[*t,R] for t in TL])
