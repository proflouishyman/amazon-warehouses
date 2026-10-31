import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # project root, so scripts run from any checkout
import csv
H=['metric','value','period','scope','publisher_and_original','source_url','source_type','caveat','retrieved']
R=[
['annualized turnover of hourly staff','~150%','reported June 2021 (analysis of internal Amazon data; coverage period not confirmed here)','Amazon hourly workforce (US)','New York Times investigation, as summarised by Verdict','https://www.verdict.co.uk/amazon-staff-turnover-rate/','secondary (NYT original not retrieved)','Derived by NYT from ~3% of hourly staff lost per week; figure restated by outlets with little added sourcing; not an Amazon-published number','2026-10-31'],
['warehouse turnover','~100%','reported 2021','Amazon warehouse workers','Wall Street Journal / National Employment Law Project, as summarised by Verdict','https://www.verdict.co.uk/amazon-staff-turnover-rate/','secondary (originals not retrieved)','Reported as about double the industry average; the industry baseline and period were not verified here','2026-10-31'],
['leaked internal document: value of 15% attrition reduction','$726 million per year','leaked document reported by Engadget, c. 2021','Amazon operations','Engadget, picked up by Popular Science','https://www.popsci.com/technology/amazon-employee-turnover/','secondary','Not a turnover rate; context only','2026-10-31'],
]
with open(_ROOT+'/data/processed/amazon_turnover_published_estimates.csv','w',newline='') as o:
    w=csv.writer(o); w.writerow(H); w.writerows(R)
