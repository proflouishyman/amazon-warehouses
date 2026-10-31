import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # project root, so scripts run from any checkout
import csv
exec(open('build_financial.py').read().split('# income:')[0].split('# accession by FY')[0]) if False else None
ACC={}
import re
src=open('build_financial.py').read()
ACC=eval(re.search(r'ACC=(\{.*?\})\n',src,re.S).group(1))
R=[] # fy, category, region, tenure, ksf, basis, note
def a(fy,cat,reg,ten,k,note='',basis='reported'): R.append([fy,cat,reg,ten,k,basis,note])
# narrative years (US = United States as the 10-K words it; sq ft converted to thousands)
a(1997,'office','US','leased',88,'Seattle administrative, engineering, marketing, customer service')
a(1997,'fulfillment_warehouse','US','leased',285,'Seattle 85k + New Castle DE 200k'); 
a(1998,'office','US','leased',150,'Seattle; excludes 184k office leased Dec 1998 not yet occupied')
a(1998,'fulfillment_warehouse','US','leased',293,'Seattle 93k + New Castle 200k operating; excludes Fernley NV 323k leased Dec 1998 not yet operating')
a(1998,'fulfillment_warehouse','International','leased',73,'Regensburg DE 32k (HQ and DC) + Slough UK 41k (HQ and DC) combined office/distribution','reported_combined')
a(1999,'office','US','leased',730)
a(1999,'fulfillment_warehouse','US','leased',3800,'Eight distribution centers: Seattle, New Castle, Fernley, Lexington, Campbellsville, McDonough, Coffeyville, Grand Forks')
a(1999,'office','International','leased',121,'Germany and UK')
a(1999,'fulfillment_warehouse','International','leased',690,'Germany + UK; additional 500k Marston Gate UK from April 2000')
a(2000,'office','US','leased',725)
a(2000,'fulfillment_warehouse','US','leased',3210,'Seven fulfillment centers; McDonough GA closure announced Jan 2001')
a(2000,'office','International','leased',150)
a(2000,'fulfillment_warehouse','International','leased',1000,'Germany, France, UK')
a(2001,'office','US','leased',772,'Of which 539k occupied')
a(2001,'fulfillment_warehouse','US','leased',3120,'Six fulfillment centers')
a(2001,'offsite_storage_shipping','US','leased','340-710','Range reported, fluctuates','reported_range')
a(2001,'customer_service','US','leased',76)
a(2001,'data_center','US','leased',120,'Washington and Virginia')
a(2001,'office','International','leased',192,'Of which 141k occupied')
a(2001,'fulfillment_warehouse','International','leased',833)
a(2001,'customer_service','International','leased',54)
a(2001,'fulfillment_warehouse','US','leased',893,'Closed McDonough GA and seasonal Seattle FCs, still under lease; NOT included in 3,120 above','reported_additional')
a(2002,'office','US','leased',517,'Excludes customer service; plus 333k subleased or vacant')
a(2002,'fulfillment_warehouse','US','leased',3100,'Six fulfillment centers')
a(2002,'offsite_storage_shipping','US','leased',1100,'Six facilities near FCs')
a(2002,'customer_service','US','leased',76)
a(2002,'data_center','US','leased',120,'Includes ~40k vacant')
a(2002,'office','International','leased',135)
a(2002,'fulfillment_warehouse','International','leased',845,'Excludes ~200k UK subleased/marketed')
a(2002,'customer_service','International','leased',66)
a(2002,'fulfillment_warehouse','US','leased',520,'McDonough GA lease remaining at 12/31/2002 (closed); not included above','reported_additional')
a(2003,'office','US','leased',577,'Excludes customer service; plus 309k subleased or vacant')
a(2003,'fulfillment_warehouse','US','leased',3200,'Six fulfillment centers')
a(2003,'offsite_storage_shipping','US','leased',1200,'Six facilities')
a(2003,'customer_service','US','leased',77)
a(2003,'data_center','US','leased',120,'Includes ~40k vacant')
a(2003,'office','International','leased',135,'Excludes ~40k vacant Germany')
a(2003,'fulfillment_warehouse','International','leased',1000)
a(2003,'customer_service','International','leased',66)
# FY2004 table
a(2004,'office','North America','leased',707,'Corporate office, incl. ~68k vacant total (all categories)')
a(2004,'office','International','leased',185)
a(2004,'fulfillment_warehouse','North America','leased',4465)
a(2004,'fulfillment_warehouse','International','leased',1483)
a(2004,'customer_service','All (not split)','leased',143)
a(2004,'data_center','All (not split)','leased',129)
# FY2005-2011 tables (thousand sq ft), all leased
T={2005:[(1000,300,7560,2620,None,None,'cs_dc',370,70)],
2006:[(1207,319,8434,3419,416,93)],2007:[(1266,425,8905,4729,368,144)],2008:[(1416,473,11973,5321,368,175)],2009:[(1565,422,11848,5739,553,197)],2010:[(2351,650,15761,10339,775,209)]}
def tab(fy,oNA,oI,fNA,fI,cNA,cI,cat):
    a(fy,'office','North America','leased',oNA); a(fy,'office','International','leased',oI)
    a(fy,'fulfillment_warehouse','North America','leased',fNA); a(fy,'fulfillment_warehouse','International','leased',fI)
    a(fy,cat,'North America','leased',cNA); a(fy,cat,'International','leased',cI)
tab(2005,1000,300,7560,2620,370,70,'customer_service_and_data_center')
tab(2006,1207,319,8434,3419,416,93,'customer_service_and_other')
tab(2007,1266,425,8905,4729,368,144,'customer_service_and_other')
tab(2008,1416,473,11973,5321,368,175,'customer_service_and_other')
tab(2009,1565,422,11848,5739,553,197,'data_center_customer_service_and_other')
tab(2010,2351,650,15761,10339,775,209,'data_center_customer_service_and_other')
a(2011,'office','North America','leased',3416); a(2011,'office','International','leased',837)
a(2011,'fulfillment_data_center_other','North America','leased',26364,'10-K combines fulfillment, data center and other this year'); a(2011,'fulfillment_data_center_other','International','leased',17690)
# FY2012-2025 owned/leased
def own(fy,oNAl,oNAo,oIl,oIo,fNAl,fNAo,fIl,fIo,sNAl=None,sNAo=None,sIl=None,sIo=None):
    for cat,reg,l,o in [('office','North America',oNAl,oNAo),('office','International',oIl,oIo),('fulfillment_data_center_other','North America',fNAl,fNAo),('fulfillment_data_center_other','International',fIl,fIo)]:
        a(fy,cat,reg,'leased',l); a(fy,cat,reg,'owned',o)
    if sNAl is not None:
        for cat,reg,l,o in [('physical_stores','North America',sNAl,sNAo),('physical_stores','International',sIl,sIo)]:
            a(fy,cat,reg,'leased',l); a(fy,cat,reg,'owned',o)
own(2012,3236,1802,1660,0,35261,339,30761,22)
own(2013,4485,1802,3002,0,48013,329,36131,122)
own(2014,5672,1802,3371,0,57898,735,43969,272)
own(2015,7245,2601,4843,0,69890,1765,47976,670)
own(2016,8454,3693,7314,0,97215,2237,59175,1257)
own(2017,12712,3674,7466,0,131419,4406,67832,5190,20349,735,202,0)
own(2018,16642,3901,14738,0,153917,4467,72596,2085,19176,724,173,0)
own(2019,18051,4961,15863,1831,187148,5591,76868,2570,20072,662,169,0)
own(2020,23731,5696,19023,1823,285677,8461,104668,3449,21157,662,169,0)
own(2021,27519,6138,20983,1802,370392,16663,129035,9601,22396,662,235,0)
own(2022,30611,6792,23956,1802,391598,22058,148146,12613,22881,662,291,0)
own(2023,29655,9222,24528,1802,413017,25630,173765,14802,22871,707,255,0)
own(2024,29551,9104,23771,1802,448168,36869,176287,18958,23975,707,222,0)
own(2025,31028,9160,26495,1802,474128,45803,185814,20660,23932,706,148,0)
# fix: FY2012-2014 owned intl office zero is "none listed"
rows=[]
for r in R:
    fy=r[0]
    k={1997:1997,1998:1998}.get(fy,fy)
    rows.append([fy,r[1],r[2],r[3],r[4],r[5],r[6],ACC[fy],'thousand sq ft'])
with open(_ROOT+'/data/processed/amazon_10k_square_footage.csv','w',newline='') as f:
    c=csv.writer(f); c.writerow(['fiscal_year','space_type','region','tenure','square_feet_thousands','value_basis','note','source_10k_accession','unit']); c.writerows(rows)
print(len(rows))
# segment table FY2015-2025: NA, Intl, AWS excl corporate
S={2015:(67103,398,45950,143,4813,1894),2016:(93716,586,57243,218,5431,2690),2017:(147277,2140,66328,4167,6197,4024),2018:(165503,1977,70619,895,9740,4404),2019:(199473,1983,74231,958,10553,5882),2020:(298879,3813,102192,1294,10599,7465),2021:(383660,9863,124246,5103,14152,11960),2022:(403984,13595,140898,6292,18034,15446),2023:(424145,15438,165329,7931,20434,17770),2024:(457104,20741,166673,11741,24875,24052),2025:(481153,25437,174499,13263,28370,28469)}
with open(_ROOT+'/data/processed/amazon_10k_square_footage_by_segment.csv','w',newline='') as f:
    c=csv.writer(f); c.writerow(['fiscal_year','segment','leased_sqft_thousands','owned_sqft_thousands','source_10k_accession','note'])
    for fy,v in S.items():
        for i,s in enumerate(['North America','International','AWS']):
            c.writerow([fy,s,v[2*i],v[2*i+1],ACC[fy],'Excludes corporate facilities; shared facilities allocated by usage. North America segment is the best proxy for the US logistics network (includes Canada and Mexico, and physical stores)'])
