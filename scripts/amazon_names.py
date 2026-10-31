"""Shared rule for deciding whether an OSHA ITA 300A row is an Amazon-operated establishment.
Used by extract_amazon_ita.py, build_injury_tables.py, facilities_01/03 and logistics_01.
Import with sys.path.insert(0, scripts dir) because scripts run under python3 -I.
Rules are documented in data/notes/injuries.md. Returns a rule label (truthy) or None.
"""
import re

# EINs filed by Amazon's own operating companies (Amazon.com Inc., Amazon.com Services LLC, Amazon.com LLC,
# Amazon Retail LLC). Used only to confirm rows whose company name is the bare word "Amazon".
AMAZON_EINS = {'911646860', '820544687', '710933087', '912172399'}

# Amazon's internal organisation labels, used in the establishment name ("North America Fulfillment Centers (FCs) : ABE2").
ORG_LABEL = re.compile(r'^\s*(North America Fulfillment Centers[^:]*|Global Specialty Fulfillment|AMZL|Amazon Transportation Services|'
                       r'Physical Stores|Transportation)\s*:\s*(?:[A-Z]{3,4}\d{1,2}|K[A-Z]{3})\b', re.I)
# labels specific enough to trust even when the company field is something else (a typo or a legacy name).
# The bare "Transportation :" label is generic and is trusted only when the company field is blank.
STRICT_LABEL = re.compile(r'^\s*(North America Fulfillment Centers[^:]*|Global Specialty Fulfillment|AMZL|Amazon Transportation Services)\s*:\s*(?:[A-Z]{3,4}\d{1,2}|K[A-Z]{3})\b', re.I)

# false positives: companies whose name contains "Amazon" but are not Amazon.com Inc. entities
FALSE_CO = re.compile(r'^\W*(amazon environmental|amazone)\b', re.I)
FALSE_EST = re.compile(r'amazon environmental|amazone usa', re.I)


def amazon_rule(company, estab, ein='', naics=''):
    c = (company or '').strip()
    e = (estab or '').strip()
    ein = re.sub(r'\D', '', ein or '')
    naics = re.sub(r'\.0+$', '', str(naics or ''))
    if FALSE_CO.match(c) or FALSE_EST.search(e):
        return None
    if re.match(r'^\W*amazon\.com\b', c, re.I):
        return 'company_amazon.com'
    if re.match(r'^\W*amazon retail\b', c, re.I):
        return 'company_amazon_retail'
    if re.match(r'^\W*golden state fc\b', c, re.I):
        return 'company_golden_state_fc'
    if re.match(r'^\W*prime now llc\b', c, re.I):
        return 'company_prime_now'
    if re.match(r'^\W*amazon (leo|kuiper|project kuiper|web services)\b', c, re.I):
        return 'company_amazon_unit'
    if re.match(r'^\W*amazon\W*$', c, re.I):
        # bare "Amazon": delivery-partner filings use this too (Agema, Black Eagle, Lyfeline, Caravan 12th ...).
        # They carry their own EIN, so require a blank or Amazon EIN and a non-courier NAICS unless the name says Amazon.
        if ein in AMAZON_EINS:
            return 'company_amazon_bare_amazon_ein'
        if ein == '' and not (naics.startswith('492') and 'amazon' not in e.lower()):
            return 'company_amazon_bare_blank_ein'
        return None
    if c == '':
        if ORG_LABEL.match(e):
            return 'blank_company_org_label'
        if ein in AMAZON_EINS and re.match(r'^\W*amazon', e, re.I):
            return 'blank_company_amazon_ein'
        return None
    # any other company: only Amazon's own org label in the establishment name counts
    if STRICT_LABEL.match(e) and not re.match(r'^\W*(abm|sizemore|sps|c&w|sbm|compass)', c, re.I):
        return 'org_label_other_company'
    return None
