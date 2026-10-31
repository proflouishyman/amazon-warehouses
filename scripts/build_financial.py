import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # project root, so scripts run from any checkout
import csv,os
P=_ROOT+'/data/processed/'
def w(name,hdr,rows):
    with open(P+name,'w',newline='') as f:
        c=csv.writer(f); c.writerow(hdr); c.writerows(rows)
    print(name,len(rows))
# accession by FY (10-K used)
ACC={1997:'0000891020-98-000448',1998:'0000891020-99-000375',1999:'0000891020-00-000622',2000:'0001032210-01-500087',2001:'0001032210-02-000059',2002:'0000950149-03-000355',2003:'0001193125-04-029488',2004:'0001193125-05-047032',2005:'0001193125-06-034166',2006:'0001193125-07-034081',2007:'0001193125-08-024707',2008:'0001193125-09-014406',2009:'0001193125-10-016098',2010:'0001193125-11-016253',2011:'0001193125-12-032846',2012:'0001193125-13-028520',2013:'0001018724-14-000006',2014:'0001018724-15-000006',2015:'0001018724-16-000172',2016:'0001018724-17-000011',2017:'0001018724-18-000005',2018:'0001018724-19-000004',2019:'0001018724-20-000004',2020:'0001018724-21-000004',2021:'0001018724-22-000005',2022:'0001018724-23-000004',2023:'0001018724-24-000008',2024:'0001018724-25-000004',2025:'0001018724-26-000004'}
# window source: FY -> 10-K FY whose 3-year statements supply it
def src(fy):
    for k in (1998,2001,2004,2007,2010,2013,2016,2019,2022,2025):
        if k-2<=fy<=k: return k
    return 1997
# income: fy: (net_sales, fulfillment, op_income, net_income) in USD millions
I={
1997:(147.787,12.1,-32.595,-31.020,1999),1998:(609.819,50.3,-109.055,-124.546,1999),
1999:(1639.839,237.312,-605.755,-719.968,2001),2000:(2761.983,414.509,-863.880,-1411.273,2001),2001:(3122.433,374.250,-412.257,-567.277,2001),
2002:(3932.936,392.467,64.124,-149.132,2004),2003:(5263.699,477.032,270.595,35.282,2004),2004:(6921.124,590.397,440.425,588.451,2004),
2005:(8490,745,432,359,2007),2006:(10711,937,389,190,2007),2007:(14835,1292,655,476,2007),
2008:(19166,1658,842,645,2010),2009:(24509,2052,1129,902,2010),2010:(34204,2898,1406,1152,2010),
2011:(48077,4576,862,631,2013),2012:(61093,6419,676,-39,2013),2013:(74452,8585,745,274,2013),
2014:(88988,10766,178,-241,2016),2015:(107006,13410,2233,596,2016),2016:(135987,17619,4186,2371,2016),
2017:(177866,25249,4106,3033,2019),2018:(232887,34027,12421,10073,2019),2019:(280522,40232,14541,11588,2019),
2020:(386064,58517,22899,21331,2022),2021:(469822,75111,24879,33364,2022),2022:(513983,84299,12248,-2722,2022),
2023:(574785,90619,36852,30425,2025),2024:(637959,98505,68593,59248,2025),2025:(716924,109074,79975,77670,2025)}
rows=[]
for fy,(s,f,o,n,k) in I.items():
    note=''
    if fy in(1997,1998): note='Fulfillment not a separate income-statement line; figure is fulfillment costs embedded in Marketing and sales, per FY1999 10-K MD&A. Sales/OI/NI as restated for poolings in FY1999 10-K.'
    if fy==1999: note='Fulfillment per FY2001 10-K (restated definition, includes credit card fees, bad debt, customer service); FY1999 10-K showed 188.4 under narrower definition.'
    if fy>=2002 and fy<=2004: note='Source statements in USD thousands, converted to millions.'
    if fy==2025: note='Technology and infrastructure label replaces Technology and content from FY2024.'
    rows.append([fy,round(s,3),round(f,3),round(f/s*100,2),round(o,3),round(n,3),ACC[k],note])
w('amazon_income_statement_annual.csv',['fiscal_year','net_sales_usd_m','fulfillment_expense_usd_m','fulfillment_pct_of_sales','operating_income_usd_m','net_income_usd_m','source_10k_accession','note'],rows)
# shipping
S=[ # fy, metric, usd_m, basis, note
(1997,'gross_profit_from_shipping',4.4,'FY1999 10-K','Shipping revenue less outbound shipping costs; positive'),
(1998,'gross_profit_from_shipping',18.2,'FY1999 10-K',''),
(1999,'gross_profit_from_shipping',11.7,'FY1999 10-K','FY2001 10-K rounds to 12'),
(1999,'shipping_revenue',239,'FY2001 10-K',''),(2000,'shipping_revenue',339,'FY2001 10-K',''),(2001,'shipping_revenue',357,'FY2001 10-K',''),
(2000,'gross_profit_from_shipping',-1,'FY2000 10-K','shipping gross loss'),(2001,'gross_profit_from_shipping',-19,'FY2001 10-K','shipping gross loss'),
(2002,'shipping_revenue',365,'FY2003 10-K',''),(2003,'shipping_revenue',372,'FY2005 10-K',''),(2004,'shipping_revenue',420,'FY2005 10-K',''),(2005,'shipping_revenue',511,'FY2007 10-K',''),(2006,'shipping_revenue',567,'FY2007 10-K',''),(2007,'shipping_revenue',740,'FY2007 10-K',''),(2008,'shipping_revenue',835,'FY2008 10-K',''),(2009,'shipping_revenue',924,'FY2010 10-K',''),(2010,'shipping_revenue',1193,'FY2010 10-K',''),(2011,'shipping_revenue',1552,'FY2012 10-K',''),(2012,'shipping_revenue',2280,'FY2012 10-K',''),
(2002,'outbound_shipping_cost',404,'FY2004 10-K','Early years: shipping plus packaging supplies per FY2003 10-K wording'),(2003,'outbound_shipping_cost',508,'FY2005 10-K',''),(2004,'outbound_shipping_cost',617,'FY2005 10-K',''),(2005,'outbound_shipping_cost',750,'FY2007 10-K',''),(2006,'outbound_shipping_cost',884,'FY2007 10-K',''),(2007,'outbound_shipping_cost',1200,'FY2008 10-K','Reported only as $1.2 billion (rounded)'),
(2008,'outbound_shipping_cost',1465,'FY2010 10-K',''),(2009,'outbound_shipping_cost',1773,'FY2010 10-K',''),(2010,'outbound_shipping_cost',2579,'FY2010 10-K',''),(2011,'outbound_shipping_cost',3989,'FY2012 10-K',''),(2012,'outbound_shipping_cost',5134,'FY2013 10-K',''),(2013,'outbound_shipping_cost',6635,'FY2014 10-K',''),(2014,'outbound_shipping_cost',8709,'FY2015 10-K',''),(2015,'outbound_shipping_cost',11539,'FY2015 10-K','Definition expanded to include sortation and delivery centers and transportation costs'),(2016,'outbound_shipping_cost',16167,'FY2017 10-K',''),
(2017,'outbound_shipping_cost',21700,'FY2019 10-K','Reported in $ billions (rounded to 0.1)'),(2018,'outbound_shipping_cost',27700,'FY2019 10-K','rounded'),(2019,'outbound_shipping_cost',37900,'FY2020 10-K','rounded'),(2020,'outbound_shipping_cost',61100,'FY2021 10-K','rounded'),(2021,'outbound_shipping_cost',76700,'FY2022 10-K','rounded'),(2022,'outbound_shipping_cost',83500,'FY2023 10-K','rounded'),(2023,'outbound_shipping_cost',89500,'FY2024 10-K','rounded'),(2024,'outbound_shipping_cost',95800,'FY2025 10-K','rounded'),(2025,'outbound_shipping_cost',102700,'FY2025 10-K','rounded'),
(2003,'net_shipping_cost',136,'FY2005 10-K',''),(2004,'net_shipping_cost',197,'FY2005 10-K',''),(2005,'net_shipping_cost',239,'FY2007 10-K',''),(2006,'net_shipping_cost',317,'FY2007 10-K',''),(2007,'net_shipping_cost',434,'FY2008 10-K',''),(2008,'net_shipping_cost',630,'FY2010 10-K',''),(2009,'net_shipping_cost',849,'FY2010 10-K',''),(2010,'net_shipping_cost',1386,'FY2010 10-K',''),(2011,'net_shipping_cost',2437,'FY2012 10-K',''),(2012,'net_shipping_cost',2854,'FY2013 10-K',''),(2013,'net_shipping_cost',3538,'FY2014 10-K',''),(2014,'net_shipping_cost',4223,'FY2015 10-K',''),(2015,'net_shipping_cost',5019,'FY2015 10-K',''),(2016,'net_shipping_cost',7191,'FY2016 10-K','Net shipping cost line last reported in FY2016 10-K'),
]
w('amazon_shipping_costs_annual.csv',['fiscal_year','metric','usd_millions','source','note'],[list(r) for r in sorted(S,key=lambda r:(r[1],r[0]))])
# capex
K={ # fy:(gross, net_of_incentives, fin_lease_adds, btsl)
1996:(1.335,None,None,None),1997:(7.603,None,None,None),1998:(28.333,None,None,None),1999:(287.055,None,None,None),2000:(134.758,None,None,None),2001:(50.321,None,None,None),2002:(39.163,None,None,None),2003:(45.963,None,None,None),2004:(89.133,None,None,None),
2005:(204,None,None,None),2006:(216,None,None,None),2007:(224,None,None,None),2008:(333,None,148,72),2009:(373,None,147,188),2010:(979,None,405,172),
2011:(1811,None,753,259),2012:(3785,None,802,29),2013:(3444,None,1867,877),
2014:(4893,None,4008,920),2015:(5387,4589,4717,544),2016:(7804,6737,5704,1209),
2017:(11955,10058,9637,3541),2018:(13427,11323,10615,3641),2019:(16861,12689,13723,1362),
2020:(40140,35044,11588,2267),2021:(61053,55396,7061,5846),2022:(63645,58321,675,3187),
2023:(52729,48133,642,None),2024:(82999,77658,854,None),2025:(131819,128320,2911,None)}
rows=[]
for fy,(g,n,l,b) in K.items():
    note=''
    if fy<2015: note='Purchases of fixed assets/PP&E incl. internal-use software, as reported in the cash flow statement (proceeds from sales and incentives were not shown separately, so no net measure is available).'
    if fy==2014: note+=' The FY2016 10-K labels this same figure net; gross is not disclosed.'
    if fy in (2015,2016): note='Gross = purchases line in the FY2017 10-K comparative cash flow statement; net = that figure less proceeds from property and equipment incentives, which is the single line (labelled net) in the original FY%d 10-K (FY2016 10-K accession 0001018724-17-000011; FY2017 10-K 0001018724-18-000005).'%fy
    if fy in (2008,2009,2010): note+=' Finance-lease column is capital leases (fixed assets acquired under capital leases).'
    rows.append([fy,g,n if n is not None else '',l if l is not None else '',b if b is not None else '',note.strip()])
w('amazon_capex_annual.csv',['fiscal_year','purchases_of_ppe_gross_usd_m','purchases_net_of_proceeds_incentives_usd_m','ppe_acquired_under_finance_leases_usd_m','ppe_recognized_build_to_suit_usd_m','note'],rows)
# PPE
PP={1996:0.985,1997:9.726,1998:29.791,1999:317.613,2000:366.416,2001:271.751,2002:239.398,2003:224.285,2004:246.156,2005:348,2006:457,2007:543,2008:854,2009:1290,2010:2414,2011:4417,2012:7060,2013:10949,2014:16967,2015:21838,2016:29114,2017:48866,2018:61797,2019:72705,2020:113114,2021:160281,2022:186715,2023:204177,2024:252665,2025:357025}
GR={2009:1915,2010:3256,2011:5786,2012:9582,2013:14809,2014:22730,2015:30053,2016:42441,2017:72656,2018:95770,2019:119680,2024:394055,2025:534098}
BASIS='10-K property and equipment, net (excludes operating-lease right-of-use assets)'
ROUNOTE=' Database aggregators (Morningstar-standardised, e.g. D&B Hoovers) report a larger PP&E figure from 2019 because they include operating-lease right-of-use assets; this series does not.'
w('amazon_ppe_year_end.csv',['fiscal_year','fixed_assets_net_usd_m','ppe_gross_usd_m','basis','note'],[[y,v,GR.get(y,''),BASIS,('Year-end balance sheet; label "Fixed assets, net" before 2012' if y<2012 else 'Year-end balance sheet')+(ROUNOTE if y>=2019 else '')] for y,v in PP.items()])
