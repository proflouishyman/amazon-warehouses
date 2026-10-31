"""ENVIRONMENT domain: EPA ECHO air-permit (CAA / ICIS-Air) facilities whose name contains AMAZON.
Source: https://echodata.epa.gov/echo/air_rest_services.get_facilities?output=JSON&p_fn=AMAZON  then get_qid pages.
Raw pages are saved in data/raw/environment/echo_air_amazon_p*.json (retrieved 2026-10-31). This script parses them.
Run: python3 -I env_05_echo_air_permits_amazon.py
Classification heuristic (name based, ESTIMATE): data_center if the name has DATA SERVICES/DATA SVCS/DEDC or SIC 7374/7379/3571;
amazon_logistics if the name contains AMAZON.COM/AMAZON COM/AMAZON LOGISTICS/AMAZON INC/AMAZON SERVICES; others excluded
(name collisions: Amazonia MO quarries, oil wells, other companies listed because of shared addresses/IDs).
"""
import csv, json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data/raw/environment'); OUT = os.path.join(ROOT, 'data/processed')
rows = []
for p in (1, 2):
    rows += json.load(open(os.path.join(RAW, 'echo_air_amazon_p%d.json' % p)))['Results']['Facilities']
out = []
for x in rows:
    n = (x['AIRName'] or '').upper()
    if re.search(r'DATA SERVICES|DATA SVCS|DEDC|DATA SERVICE', n) and 'AMAZON' in n: kind = 'data_center'
    elif re.search(r'AMAZON\.?COM|AMAZON COM|AMAZON LOGISTICS|AMAZON INC|AMAZON SERVICES', n): kind = 'amazon_logistics'
    else: continue
    out.append(dict(name=x['AIRName'], city=x['AIRCity'], state=x['AIRState'], zip=x['AIRZip'], county=x['AIRCounty'],
                    lat=x['FacLat'], lon=x['FacLong'], kind_heuristic=kind, air_ids=x['AIRIDs'], registry_id=x['RegistryID'],
                    classification=x['AIRClassification'], operating_status=x['AIRStatus'], programs=x['AIRPrograms'],
                    sic=x['FacSICCodes'], recent_violation_count=x['AIRRecentViolCnt'], evaluations=x['AIREvalCnt'],
                    last_eval_date=x['AIRLastEvalDate'], full_compliance_evals=x['AIRFceCnt'], source='EPA ECHO ICIS-Air; retrieved 2026-10-31'))
with open(os.path.join(OUT, 'epa_echo_air_permits_amazon_facilities.csv'), 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
from collections import Counter
print(len(rows), 'ECHO rows;', len(out), 'kept'); print(Counter((o['kind_heuristic'], o['operating_status']) for o in out))
