#!/usr/bin/env python3
"""interp_spend_build.py - category-level channel shift (store -> online) inputs, 2010-2025.

Run:  python3 -I scripts/interp_spend_build.py [--download]

Reads public files saved under data/raw/interp_spend/ (gitignored) and writes
data/processed/interp_spend_*.csv. Standard library only (own minimal .xlsx reader).
--download fetches any missing Census / BEA / Atlanta Fed / paper files first
(BLS CE tables are blocked to scripted clients, HTTP 403; the copies in raw/bls were
saved through the interactive fetch tool. See data/notes/interp_spend.md).

Outputs (all in data/processed/):
  interp_spend_quarterly_ecom_share.csv      Census quarterly e-commerce share of retail, 1999Q4-2026Q2 + annual sums
  interp_spend_arts_merch_line_online.csv    ARTS NAICS 4541 total and e-commerce sales by merchandise line, 1999-2022
  interp_spend_arts_kind_of_business.csv     ARTS total and e-commerce sales by retail kind of business, 1998-2022
  interp_spend_line_denominator_2012.csv     2012 Economic Census all-retail line sales vs ARTS 4541 e-commerce
  interp_spend_pce_goods.csv                 BEA PCE (Table 2.4.5U) goods categories 2010-2025, shares
  interp_spend_line_vs_pce.csv               ARTS 4541 e-commerce / BEA PCE for matched categories (ratio, see caveats)
  interp_spend_dcpc_remote_by_merchant.csv   Diary of Consumer Payment Choice 2020-2025: remote share of purchases by merchant type
  interp_spend_ce_shares.csv                 BLS CE category expenditure shares, selected years
  interp_spend_floorspace.csv                2017 Economic Census floor space (4 industries) + CBECS 2018 floorspace
  interp_spend_trips_nhts.csv                NHTS shopping-and-errand trips per person
  interp_spend_substitution_studies.csv      Literature table: substitution vs complementarity
  interp_spend_store_type_mapping.csv        merchandise line -> store type -> NAICS -> CBECS
"""
import csv
import os
import re
import subprocess
import sys
import zipfile
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw", "interp_spend")
OUT = os.path.join(ROOT, "data", "processed")
RETRIEVED = "2026-11-01"

# --------------------------------------------------------------------------- downloads
UA = {"User-Agent": "Mozilla/5.0 (Macintosh) AppleWebKit/605.1.15"}
CEN = "https://www.census.gov/retail/mrts/www/data/excel/"
ARTS = "https://www2.census.gov/programs-surveys/arts/tables/"
ES = "https://www2.census.gov/programs-surveys/e-stats/tables/2019/historic/"
ECD = "https://www2.census.gov/programs-surveys/economic-census/data/"
ATL = ("https://www.atlantafed.org/-/media/Project/Atlanta/FRBA/Documents/research-and-data/"
       "surveys/consumer-payments/")
DOWNLOADS = [
    (CEN + "tsnotadjustedsales.xlsx", "census/tsnotadjustedsales.xlsx"),
    (CEN + "tsadjustedsales.xlsx", "census/tsadjustedsales.xlsx"),
    (ARTS + "2022benchmarked/ecommerce4541.xlsx", "census/estats/arts2022bm_ecommerce4541.xlsx"),
    (ARTS + "2022benchmarked/ecommerce.xlsx", "census/estats/arts2022bm_ecommerce.xlsx"),
    (ARTS + "2022benchmarked/sales.xlsx", "census/estats/arts2022bm_sales.xlsx"),
    (ARTS + "2022benchmarked/supecommerce4541.xlsx", "census/arts2022bm_supecom4541.xlsx"),
    (ES + "table_5.xlsx", "census/estats/estats2019_historic_table_5.xlsx"),
    (ES + "table_4.xlsx", "census/estats/estats2019_historic_table_4.xlsx"),
    (ECD + "2012/sector44/EC1244SLLS1.zip", "census/ec_EC1244SLLS1/EC1244SLLS1.zip"),
    (ECD + "2017/sector44/EC1744FLSPACE.zip", "census/ec_EC1744FLSPACE/EC1744FLSPACE.zip"),
    ("https://apps.bea.gov/national/Release/XLS/Survey/Section2All_xls.xlsx", "bea/Section2All_xls.xlsx"),
    (ATL + "survey-diary-consumer-payment-choice/2025/dcpc-2025-public-csv.zip", "fed/dcpc-2025-public-csv.zip"),
    (ATL + "survey-diary-consumer-payment-choice/2025/dcpc2025-tables-for-web.xlsx", "fed/dcpc2025-tables-for-web.xlsx"),
    (ATL + "diary-of-consumer-payment-choice/2020/2020-diary-of-consumer-payment-choice.zip", "fed/z2020.zip"),
    (ATL + "survey-diary-consumer-payment-choice/2021/2021-diary-of-consumer-payment-choice.zip", "fed/z2021.zip"),
    (ATL + "survey-diary-consumer-payment-choice/2022/2022-diary-of-consumer-payment-choice.zip", "fed/z2022.zip"),
    (ATL + "survey-diary-consumer-payment-choice/2023/2023-diary-of-consumer-payment-choice.zip", "fed/z2023.zip"),
    (ATL + "survey-diary-consumer-payment-choice/2024/2024-diary-of-consumer-payment-choice.zip", "fed/z2024.zip"),
]


def download_missing():
    for url, rel in DOWNLOADS:
        dest = os.path.join(RAW, rel)
        if os.path.exists(dest) and os.path.getsize(dest) > 0:
            continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
                f.write(r.read())
            print("downloaded", rel)
        except Exception as e:  # not fatal
            print("DOWNLOAD FAILED", url, e)
        if dest.endswith(".zip"):
            try:
                with zipfile.ZipFile(dest) as z:
                    z.extractall(os.path.dirname(dest) if "ec_" in dest else
                                 os.path.join(os.path.dirname(dest), "dcpc" + re.sub(r"\D", "", os.path.basename(dest))[:4])
                                 if "/fed/" in dest else os.path.dirname(dest))
            except Exception as e:
                print("unzip failed", dest, e)


# --------------------------------------------------------------------------- xlsx reader
M = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
RID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"


def _col(ref):
    n = 0
    for c in re.match(r"[A-Z]+", ref).group():
        n = n * 26 + ord(c) - 64
    return n - 1


def read_xlsx(path):
    """Return {sheet_name: [row, ...]} with row = list of str|None."""
    z = zipfile.ZipFile(path)
    ss = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall(M + "si"):
            ss.append("".join(t.text or "" for t in si.iter(M + "t")))
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    out = {}
    for s in wb.find(M + "sheets"):
        t = rels[s.get(RID)].lstrip("/")
        t = t if t.startswith("xl/") else "xl/" + t
        rows = []
        for r in ET.fromstring(z.read(t)).find(M + "sheetData"):
            row = []
            for c in r:
                v = c.find(M + "v")
                i = _col(c.get("r"))
                if c.get("t") == "inlineStr":
                    val = "".join(x.text or "" for x in c.iter(M + "t"))
                elif v is None:
                    continue
                elif c.get("t") == "s":
                    val = ss[int(v.text)]
                else:
                    val = v.text
                row.extend([None] * (i + 1 - len(row)))
                row[i] = val
            rows.append(row)
        out[s.get("name")] = rows
    return out


def num(x):
    """number or None; returns (value, flag). flag in {'', 'S','D','NA','X','ZZ'}"""
    if x is None:
        return None, "NA"
    s = str(x).strip().replace(",", "")
    if s in ("S", "D", "NA", "X", "ZZ", "N", "(S)", "(D)", "(NA)"):
        return None, s.strip("()")
    try:
        return float(s), ""
    except ValueError:
        return None, s[:6]


def clean_label(s):
    s = (s or "").replace("…", "").replace(".", " ")
    s = re.sub(r"[\d\s]*$", "", re.sub(r"\s+", " ", s)).strip()
    s = re.sub(r"\s*\d$", "", s)
    return s


def write_csv(name, header, rows):
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, name)
    with open(p, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"wrote {name}: {len(rows)} rows")
    return p


def fmt(x, nd=4):
    return "" if x is None else (f"{x:.{nd}f}" if isinstance(x, float) else x)


# --------------------------------------------------------------------------- 1. quarterly
def parse_quarterly(path, adj):
    rows = list(read_xlsx(path).values())[0]
    out = []
    for r in rows:
        if not r or not r[1]:
            continue
        m = re.match(r"(\d)(?:st|nd|rd|th) quarter (\d{4})", r[1].strip())
        if not m:
            continue
        tot, _ = num(r[2])
        ec, _ = num(r[3])
        pct, _ = num(r[4])
        out.append((int(m.group(2)), int(m.group(1)), adj, tot, ec, pct, r[1].strip()))
    return out


def build_quarterly():
    d = os.path.join(RAW, "census")
    q = parse_quarterly(os.path.join(d, "tsadjustedsales.xlsx"), "adjusted")
    q += parse_quarterly(os.path.join(d, "tsnotadjustedsales.xlsx"), "not_adjusted")
    rows = []
    for y, qq, adj, tot, ec, pct, lab in sorted(q):
        share = 100 * ec / tot if tot else None
        rows.append(["quarter", f"{y}Q{qq}", adj, tot, ec, fmt(share, 2), pct, lab])
    # annual from not-adjusted quarters (complete years only)
    ann = defaultdict(lambda: [0, 0, 0])
    for y, qq, adj, tot, ec, pct, lab in q:
        if adj == "not_adjusted":
            a = ann[y]
            a[0] += tot
            a[1] += ec
            a[2] += 1
    for y in sorted(ann):
        if ann[y][2] == 4:
            rows.append(["annual_sum_of_NSA_quarters", str(y), "not_adjusted", ann[y][0], ann[y][1],
                         fmt(100 * ann[y][1] / ann[y][0], 2), "", "sum of four not-adjusted quarters"])
    write_csv("interp_spend_quarterly_ecom_share.csv",
              ["period_type", "period", "adjustment", "total_retail_sales_musd", "ecommerce_sales_musd",
               "ecom_share_pct_computed", "ecom_share_pct_census_printed", "source_label"], rows)
    return {r[1]: r for r in rows}


# --------------------------------------------------------------------------- 2. ARTS merchandise lines
def parse_pairs_table(path, label_header):
    """ARTS tables: header row with years in alternating Total/E-commerce column pairs.
    Returns (years[(label, col_total, col_ecom)], data_rows[(label_raw, row)])"""
    rows = list(read_xlsx(path).values())[0]
    yr_row = None
    for i, r in enumerate(rows):
        cells = [c for c in r if c]
        if sum(1 for c in cells if re.fullmatch(r"\d{4}r?", c.strip())) >= 5:
            yr_row = i
            break
    years = []
    for j, c in enumerate(rows[yr_row]):
        if c and re.fullmatch(r"\d{4}r?", c.strip()):
            years.append((int(c.strip()[:4]), c.strip().endswith("r"), j))
    start = yr_row + 2
    data = []
    for r in rows[start:]:
        if not r or not r[0] and (len(r) < 2 or not r[1]):
            continue
        if r[0] and re.match(r"(D|NA|S|ZZ|Footnotes|Note|r)\b", r[0].strip()):
            break
        data.append(r)
    return years, data


def build_merch_lines():
    """1999-2022 benchmarked vintage (primary) and 2019 vintage (1999-2019) for comparison."""
    rows_out = []
    # 2022 benchmarked: columns [label, (Total, Ecom) per year...]; year header sits above the first col of pair
    p = os.path.join(RAW, "census", "estats", "arts2022bm_ecommerce4541.xlsx")
    table = list(read_xlsx(p).values())[0]
    yr_i = next(i for i, r in enumerate(table) if sum(1 for c in r if c and re.fullmatch(r"\d{4}r?", c.strip())) >= 5)
    yrs = [(int(c.strip()[:4]), j) for j, c in enumerate(table[yr_i]) if c and re.fullmatch(r"\d{4}r?", c.strip())]
    data_start = yr_i + 2
    for r in table[data_start:]:
        if not r or not r[0]:
            continue
        if re.match(r"(NA -|S -|\s*Footnotes|\d?[A-Za-z]*Includes|Note|r)", r[0].strip()) and not r[0].strip().startswith("Total"):
            break
        lab = clean_label(r[0])
        for y, j in yrs:
            tot, ft = num(r[j] if j < len(r) else None)
            ec, fe = num(r[j + 1] if j + 1 < len(r) else None)
            share = 100 * ec / tot if tot and ec is not None else None
            rows_out.append(["2022_benchmarked", y, lab, fmt(tot, 0), ft, fmt(ec, 0), fe, fmt(share, 1)])
    # 2019 vintage: [label, (Total, Ecom) per year ...], year above Total col
    p2 = os.path.join(RAW, "census", "estats", "estats2019_historic_table_5.xlsx")
    table = list(read_xlsx(p2).values())[0]
    yr_i = next(i for i, r in enumerate(table) if sum(1 for c in r if c and re.fullmatch(r"\d{4}r?", c.strip())) >= 5)
    yrs2 = [(int(c.strip()[:4]), j) for j, c in enumerate(table[yr_i]) if c and re.fullmatch(r"\d{4}r?", c.strip())]
    for r in table[yr_i + 2:]:
        if not r or not r[0]:
            continue
        if re.match(r"(NA -|S -|\s*Footnotes|\d?[A-Za-z]*Includes|Note|r)", r[0].strip()) and not r[0].strip().startswith("Total"):
            break
        lab = clean_label(r[0])
        for y, j in yrs2:
            tot, ft = num(r[j] if j < len(r) else None)
            ec, fe = num(r[j + 1] if j + 1 < len(r) else None)
            share = 100 * ec / tot if tot and ec is not None else None
            rows_out.append(["2019_vintage", y, lab, fmt(tot, 0), ft, fmt(ec, 0), fe, fmt(share, 1)])
    rows_out.sort(key=lambda r: (r[0], r[2], r[1]))
    write_csv("interp_spend_arts_merch_line_online.csv",
              ["vintage", "year", "merchandise_line", "line_sales_4541_musd", "flag_total", "line_ecom_4541_musd",
               "flag_ecom", "ecom_pct_of_4541_line_sales"], rows_out)
    return rows_out


def build_kind_of_business():
    p = os.path.join(RAW, "census", "estats", "arts2022bm_ecommerce.xlsx")
    table = list(read_xlsx(p).values())[0]
    yr_i = next(i for i, r in enumerate(table) if sum(1 for c in r if c and re.fullmatch(r"\d{4}r?", c.strip())) >= 5)
    yrs = [(int(c.strip()[:4]), j) for j, c in enumerate(table[yr_i]) if c and re.fullmatch(r"\d{4}r?", c.strip())]
    out = []
    for r in table[yr_i + 2:]:
        if not r or len(r) < 2 or not (r[1] or r[0]):
            continue
        if r[0] and re.match(r"(D -|NA -|S -|\s*ZZ|Footnotes|\s*Footnotes|rRevised|Note|\d)", r[0].strip()) and not r[0].strip().isdigit():
            break
        naics = (r[0] or "").strip()
        lab = clean_label(r[1])
        for y, j in yrs:
            tot, ft = num(r[j] if j < len(r) else None)
            ec, fe = num(r[j + 1] if j + 1 < len(r) else None)
            share = 100 * ec / tot if tot and ec is not None else None
            out.append([y, naics, lab, fmt(tot, 0), ft, fmt(ec, 0), fe, fmt(share, 2)])
    out.sort(key=lambda r: (r[1], r[2], r[0]))
    write_csv("interp_spend_arts_kind_of_business.csv",
              ["year", "naics", "kind_of_business", "total_sales_musd", "flag_total", "ecom_sales_musd",
               "flag_ecom", "ecom_pct_of_total"], out)
    return out


# --------------------------------------------------------------------------- 3. 2012 denominators
# ARTS 4541 merchandise line  ->  2012 Economic Census product-line codes (PSCODE2012). Approximate crosswalk.
LINE_XWALK = {
    "Books (includes audio books and e-books)": ["20420"],
    "Clothing and clothing accessories (includes footwear)": ["20200", "20220", "20240", "20250", "20260"],
    "Drugs, health aids, and beauty aids": ["20160"],
    "Electronics and appliances": ["20300", "20310", "20320", "20330", "20440"],
    "Food, beer, and wine": ["20100", "20140"],
    "Furniture and home furnishings": ["20340", "20360", "20380", "20280"],
    "Jewelry": ["20400"],
    "Sporting goods": ["20530"],
    "Toys, hobby goods, and games": ["20460"],
    "Computer and peripheral equipment, communications equipment, and computer software": ["20370"],
}


def build_denominator_2012(merch_rows):
    f = os.path.join(RAW, "census", "ec_EC1244SLLS1", "EC1244SLLS1.dat")
    lines = {}
    with open(f, newline="") as fh:
        rd = csv.reader(fh, delimiter="|")
        hdr = next(rd)
        ix = {h: i for i, h in enumerate(hdr)}
        for r in rd:
            if r[ix["GEOTYPE"]] == "01" and r[ix["NAICS2012"]] == "44-45":
                lines[r[ix["PSCODE2012"]]] = (r[ix["PROD_TTL"]], float(r[ix["RCPTOT"]] or 0) / 1000.0)  # $1000 -> $ million
    # ARTS 2012 values (2022 benchmarked vintage)
    arts = {}
    for v, y, lab, tot, ft, ec, fe, sh in merch_rows:
        if v == "2022_benchmarked" and y == 2012:
            arts[lab] = (float(tot) if tot else None, float(ec) if ec else None)
    # computer hardware + software are two ARTS lines against one EC line
    def arts_val(label):
        if label.startswith("Computer and peripheral equipment, communications equipment, and computer software"):
            a = [arts.get(k) for k in arts if k.startswith("Computer and peripheral") or k.startswith("Computer software")]
            if any(x is None or x[1] is None for x in a) or len(a) < 2:
                return (None, None)
            return (sum(x[0] for x in a), sum(x[1] for x in a))
        for k in arts:
            if k.startswith(label[:25]):
                return arts[k]
        return (None, None)
    out = []
    for label, codes in LINE_XWALK.items():
        den = sum(lines[c][1] for c in codes if c in lines)
        tot, ec = arts_val(label)
        out.append([label, "+".join(codes), fmt(den, 0), fmt(tot, 0), fmt(ec, 0),
                    fmt(100 * tot / den if tot and den else None, 1), fmt(100 * ec / den if ec and den else None, 1),
                    "denominator = 2012 Economic Census (EC1244SLLS1, NAICS 44-45 row, RCPTOT) line sales of all retail establishments; "
                    "numerator = ARTS NAICS 4541 line sales / e-commerce (2022 benchmarked vintage, year 2012). "
                    "Excludes e-commerce by store-based retailers (e.g. a department store's own website) so it UNDERSTATES total online share."])
    write_csv("interp_spend_line_denominator_2012.csv",
              ["arts_merchandise_line", "ec2012_pscodes", "all_retail_line_sales_2012_musd",
               "arts_4541_line_sales_2012_musd", "arts_4541_line_ecom_2012_musd",
               "nonstore_4541_pct_of_all_retail_line", "ecom_4541_pct_of_all_retail_line", "note"], out)
    return out, lines


# --------------------------------------------------------------------------- 4. BEA PCE
PCE_CODES = [
    ("DPCERC", "Personal consumption expenditures, total"),
    ("DGDSRC", "Goods"), ("DDURRC", "Durable goods"), ("DNDGRC", "Nondurable goods"),
    ("DFDHRC", "Furnishings and durable household equipment"),
    ("DFFFRC", "Furniture and furnishings"), ("DAPPRC", "Household appliances"),
    ("DUTERC", "Glassware, tableware, and household utensils"), ("DTOORC", "Tools and equipment for house and garden"),
    ("DREQRC", "Recreational goods and vehicles"),
    ("DVAPRC", "Video, audio, photographic, and information processing equipment and media"),
    ("DSPGRC", "Sporting equipment, supplies, guns, and ammunition"), ("DRBKRC", "Recreational books"),
    ("DMSCRC", "Musical instruments"), ("DJRYRC", "Jewelry and watches"), ("DEBKRC", "Educational books"),
    ("DTCERC", "Telephone and related communication equipment"),
    ("DFXARC", "Food and beverages purchased for off-premises consumption"),
    ("DCLORC", "Clothing and footwear"), ("DGOERC", "Gasoline and other energy goods"),
    ("DPHMRC", "Pharmaceutical and other medical products"),
    ("DREIRC", "Recreational items (toys, games, hobbies, pets, flowers etc.)"),
    ("DHOURC", "Household supplies"), ("DOPCRC", "Personal care products"), ("DTOBRC", "Tobacco"),
    ("DNEWRC", "Magazines, newspapers, and stationery"),
    ("DSERRC", "Services"),
]


def build_pce():
    p = os.path.join(RAW, "bea", "Section2All_xls.xlsx")
    rows = read_xlsx(p)["T20405-A"]
    hdr = next(r for r in rows if r and r[0] == "Line")
    years = {j: int(c) for j, c in enumerate(hdr) if c and re.fullmatch(r"\d{4}", c)}
    data = {}
    for r in rows:
        if len(r) > 3 and r[2] and re.fullmatch(r"D[A-Z]{3}RC", r[2].strip()):
            data[r[2].strip()] = {years[j]: fnum(r[j]) for j in years if j < len(r) and fnum(r[j]) is not None}
    tot = data["DPCERC"]
    goods = data["DGDSRC"]
    out = []
    for code, lab in PCE_CODES:
        if code not in data:
            continue
        for y in range(2010, 2026):
            v = data[code].get(y)
            if v is None:
                continue
            out.append([y, code, lab, fmt(v, 0), fmt(100 * v / tot[y], 3), fmt(100 * v / goods[y], 2) if code not in ("DSERRC", "DPCERC") else ""])
    write_csv("interp_spend_pce_goods.csv",
              ["year", "bea_series_code", "category", "pce_musd_current", "pct_of_total_pce", "pct_of_goods_pce"], out)
    return data


# --------------------------------------------------------------------------- 5. line vs PCE
LINE_TO_PCE = {
    "Books (includes audio books and e-books)": ["DRBKRC", "DEBKRC"],
    "Clothing and clothing accessories (includes footwear)": ["DCLORC"],
    "Drugs, health aids, and beauty aids": ["DPHMRC", "DOPCRC"],
    "Food, beer, and wine": ["DFXARC"],
    "Furniture and home furnishings": ["DFFFRC", "DUTERC"],
    "Jewelry": ["DJRYRC"],
    "Sporting goods": ["DSPGRC"],
    "Toys, hobby goods, and games": ["DREIRC"],
    "Electronics and appliances": ["DVAPRC", "DAPPRC", "DTCERC"],
}


def build_line_vs_pce(merch_rows, pce):
    arts = {}
    for v, y, lab, tot, ft, ec, fe, sh in merch_rows:
        if v == "2022_benchmarked" and ec:
            arts[(lab, y)] = float(ec)
    cav = {
        "Books": "ARTS line includes e-books/audio books; PCE book series are narrower: upper bound, not a share",
        "Furniture": "PCE denominator (furniture + glassware/utensils) is narrower than the ARTS line (home furnishings, rugs, bedding, housewares): ratio overstates",
        "Sporting": "PCE sporting equipment excludes some items in the ARTS line (e.g. apparel-like athletic goods): treat as upper bound",
        "Toys": "PCE 'recreational items' also holds pets, pet food, flowers: ratio understates",
        "Drugs": "ARTS line includes mail-order pharmacy sales; PCE pharmaceuticals are net of insurer-paid amounts differently: rough",
        "Electronics": "three PCE lines summed; ARTS computer lines are suppressed so the numerator omits computers: understates",
        "Clothing": "closest match of the set",
        "Food": "closest match; grocery e-commerce by store-based retailers is NOT in the numerator",
        "Jewelry": "PCE jewelry and watches; ARTS line similar",
    }
    out = []
    for line, codes in LINE_TO_PCE.items():
        key = next((k[0] for k in arts if k[0].startswith(line[:25])), None)
        if not key:
            continue
        for y in range(2010, 2023):
            ec = arts.get((key, y))
            den = sum(pce[c].get(y, 0) for c in codes)
            if ec is None or not den:
                out.append([line, y, "", fmt(den, 0), "", "+".join(codes), ""])
                continue
            out.append([line, y, fmt(ec, 0), fmt(den, 0), fmt(100 * ec / den, 1), "+".join(codes),
                        next(v for k, v in cav.items() if line.startswith(k))])
    write_csv("interp_spend_line_vs_pce.csv",
              ["arts_merchandise_line", "year", "arts_4541_line_ecom_musd", "bea_pce_matched_musd",
               "ratio_pct", "bea_codes", "caveat"], out)
    return out


# --------------------------------------------------------------------------- 6. DCPC
MERCH = {
    1: "Grocery, convenience (no gas), pharmacies", 2: "Gas stations", 3: "Sit-down restaurants and bars",
    4: "Fast food, coffee, cafeterias, food trucks",
    5: "General merchandise, department stores, other stores, ONLINE SHOPPING (not separable)",
    6: "General services", 7: "Arts, entertainment, recreation", 8: "Utilities", 9: "Taxis, airlines, delivery",
    10: "Telephone, internet, cable, streaming", 11: "Building contractors etc", 12: "Professional services",
    13: "Hotels, motels", 14: "Rent", 15: "Mortgage, cards, banks, insurance", 16: "Person-to-person / small job",
    17: "Donations", 18: "Medical", 19: "Government taxes or fees", 20: "Schools, childcare", 21: "Public transport, tolls",
}
DCPC_FILES = {
    2020: ("dcpc2020/dcpc_2020_tranlevel_public_csv.csv", "dcpc2020/dcpc_2020_daylevel_public_csv.csv"),
    2021: ("dcpc2021/dcpc_2021_tranlevel_public_xls.csv", "dcpc2021/dcpc_2021_daylevel_public_xls.csv"),
    2022: ("dcpc2022/dcpc_2022_tranlevel_public_xls.csv", "dcpc2022/dcpc_2022_daylevel_public_xls.csv"),
    2023: ("dcpc2023/dcpc_2023_tranlevel_public_xls.csv", "dcpc2023/dcpc_2023_daylevel_public_xls.csv"),
    2024: ("dcpc2024/zip content/dcpc_2024_tranlevel_public.csv", "dcpc2024/zip content/dcpc_2024_daylevel_public.csv"),
    2025: ("dcpc2025/dcpc_2025_tranlevel_public.csv", "dcpc2025/dcpc_2025_daylevel_public.csv"),
}


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def build_dcpc():
    fed = os.path.join(RAW, "fed")
    out = []
    overall = {}
    for y, (tf, df) in DCPC_FILES.items():
        tp, dp = os.path.join(fed, tf), os.path.join(fed, df)
        if not (os.path.exists(tp) and os.path.exists(dp)):
            print("DCPC", y, "missing files, skipped")
            continue
        w = {}
        with open(dp, newline="") as fh:
            for r in csv.DictReader(fh):
                wt = fnum(r.get("dow_weight"))
                if wt is not None:
                    w[(r["id"], r["diary_day"])] = wt
        agg = defaultdict(lambda: [0.0, 0.0, 0.0, 0.0, 0])  # w_n, w_n_remote, w_amt, w_amt_remote, n_raw
        dropped = 0
        with open(tp, newline="") as fh:
            for r in csv.DictReader(fh):
                if r.get("bill") != "0" or r.get("payment") != "1" or r.get("diary_day") in ("0", "NA", ""):
                    continue  # purchases only (non-bill, a payment was made); diary day 0 excluded per Atlanta Fed guidance
                ip = r.get("in_person")
                if ip not in ("0", "1"):
                    continue
                wt = w.get((r["id"], r["diary_day"]))
                if wt is None:
                    dropped += 1
                    continue
                amt = fnum(r.get("amnt")) or 0.0
                m = int(r["merch"]) if r.get("merch", "").isdigit() else 0
                for key in (m, "ALL"):
                    a = agg[key]
                    a[0] += wt
                    a[2] += wt * amt
                    if ip == "0":
                        a[1] += wt
                        a[3] += wt * amt
                    a[4] += 1
        for key, a in agg.items():
            lab = "All purchases (all merchant types)" if key == "ALL" else MERCH.get(key, "unknown merch code")
            out.append([y, key, lab, a[4], fmt(100 * a[1] / a[0], 1) if a[0] else "",
                        fmt(100 * a[3] / a[2], 1) if a[2] else "", dropped])
        overall[y] = agg["ALL"]
        print(f"DCPC {y}: weighted remote share of purchases by count {100*agg['ALL'][1]/agg['ALL'][0]:.1f}%, by value {100*agg['ALL'][3]/agg['ALL'][2]:.1f}% (n={agg['ALL'][4]}, unmatched weights {dropped})")
    out.sort(key=lambda r: (str(r[1]) != "ALL", str(r[1]).zfill(3), r[0]))
    write_csv("interp_spend_dcpc_remote_by_merchant.csv",
              ["year", "merch_code", "merchant_type", "n_purchases_unweighted", "remote_pct_of_purchases_by_count",
               "remote_pct_of_purchases_by_value", "n_dropped_no_weight"], out)
    return out


# --------------------------------------------------------------------------- 7. BLS CE
CE_ITEMS = ["Food at home", "Food away from home", "Alcoholic beverages", "Housekeeping supplies",
            "Household furnishings and equipment", "Apparel and services", "Entertainment",
            "Personal care products and services", "Reading"]


def _first_num(s):
    """first number on a CE PDF text line; small shares print like '.9' (no leading zero)."""
    tail = s.split("..")[-1] if ".." in s else re.sub(r"^[A-Za-z ]+", "", s)
    m = re.search(r"-?\$?(?:\d[\d,]*\.?\d*|\.\d+)", tail)
    return float(m.group().replace("$", "").replace(",", "")) if m else None


def ce_from_pdf(path_txt):
    lines = open(path_txt, errors="ignore").read().split("\n")
    start = next(i for i, l in enumerate(lines) if l.strip() == "Average annual expenditures")
    res = {}
    tot = None
    for i in range(start, min(start + 4, len(lines))):
        if lines[i].startswith("Mean"):
            tot = _first_num(lines[i])
            break
    res["Total average annual expenditures"] = (tot, 100.0)
    for item in CE_ITEMS:
        for i in range(start, len(lines)):
            if lines[i].strip() == item:
                mean = share = None
                for l in lines[i + 1:i + 8]:
                    if l.startswith("Mean") and mean is None:
                        mean = _first_num(l)
                    elif l.startswith("Share") and share is None:
                        share = _first_num(l)
                    if mean is not None and share is not None:
                        break
                res[item] = (mean, share)
                break
    return res


def ce_from_xlsx(path):
    rows = list(read_xlsx(path).values())[0]
    start = next(i for i, r in enumerate(rows) if r and r[0] == "Average annual expenditures")
    res = {}
    tot = None
    if rows[start + 1][0] == "Mean":
        tot = fnum(rows[start + 1][1])
    res["Total average annual expenditures"] = (tot, 100.0)
    for item in CE_ITEMS:
        for i in range(start, len(rows)):
            if rows[i] and rows[i][0] == item:
                mean = share = None
                for r in rows[i + 1:i + 6]:
                    if r and r[0] == "Mean" and mean is None:
                        mean = fnum(r[1])
                    if r and r[0] == "Share" and share is None:
                        share = fnum(r[1])
                res[item] = (mean, share)
                break
    return res


def build_ce():
    d = os.path.join(RAW, "bls")
    out = []
    srcs = []
    for y in (2012, 2015, 2019, 2022):
        txt = os.path.join(d, f"r{y}.txt")
        pdf = os.path.join(d, f"ce_{y}_cu_income.pdf")
        if not os.path.exists(txt) and os.path.exists(pdf):
            try:
                subprocess.run(["pdftotext", "-raw", pdf, txt], check=True)  # poppler
            except Exception as e:
                print("pdftotext failed", pdf, e)
        srcs.append((y, ce_from_pdf, txt if os.path.exists(txt) else None, f"ce_{y}_cu_income.pdf"))
    for y in (2024, 2025):
        srcs.append((y, ce_from_xlsx, os.path.join(d, f"ce_{y}_cu_income.xlsx"), f"ce_{y}_cu_income.xlsx"))
    for y, fn, p, name in srcs:
        if p is None or not os.path.exists(p):
            print("CE", y, "missing", name)
            continue
        res = fn(p)
        for item, (mean, share) in res.items():
            out.append([y, item, fmt(mean, 0), fmt(share, 1), "All consumer units column, 'Income before taxes' table (Table 1202/1203), " + name])
    write_csv("interp_spend_ce_shares.csv",
              ["year", "item", "mean_annual_expenditure_usd", "share_of_total_pct", "source"], out)
    return out


# --------------------------------------------------------------------------- 8. floor space, trips
def build_floorspace():
    rows = []
    f = os.path.join(RAW, "census", "ec_EC1744FLSPACE", "EC1744FLSPACE.dat")
    with open(f, newline="") as fh:
        rd = csv.reader(fh, delimiter="|")
        hdr = next(rd)
        ix = {h: i for i, h in enumerate(hdr)}
        for r in rd:
            if r[ix["GEO_ID"]] == "0100000US":
                rows.append(["2017 Economic Census, Retail Trade Floor Space (EC1744FLSPACE)", 2017,
                             r[ix["NAICS2017"]] + " " + r[ix["NAICS2017_TTL"]], r[ix["ESTAB"]],
                             fmt(float(r[ix["FSTOT"]]) / 1000, 1), fmt(float(r[ix["FSSELL"]]) / 1000, 1),
                             fmt(float(r[ix["RCPTOT"]]) / 1000, 0),
                             r[ix["RCPTOTPSQ"]], "total and selling floor space in million sq ft; sales in $ million; $ per sq ft of total under-roof space"])
    c1 = os.path.join(ROOT, "data", "raw", "retail_context", "cbecs2018_c1.xlsx")
    if os.path.exists(c1):
        rows_c = read_xlsx(c1)["data"]
        for r in rows_c:
            if r and r[0] and r[0].strip() in ("Food sales", "Mercantile", "Retail (other than mall)", "Enclosed and strip malls",
                                                 "Warehouse and storage", "Food service"):
                rows.append(["CBECS 2018 Table C1 (data/raw/retail_context/cbecs2018_c1.xlsx)", 2018, r[0].strip(),
                             fmt(float(r[1]) * 1000, 0), fmt(float(r[2]), 0), "", "", "",
                             "buildings = thousand x1000; floorspace million sq ft (all floorspace, not selling space)"])
    write_csv("interp_spend_floorspace.csv",
              ["source", "year", "category", "establishments_or_buildings", "total_floorspace_msf",
               "selling_floorspace_msf", "sales_musd", "sales_per_sqft_usd", "note"], rows)


def build_trips():
    p = os.path.join(RAW, "papers", "nhts.txt")
    vals = None
    if os.path.exists(p):
        for l in open(p, errors="ignore"):
            if re.match(r"\s*Shopping and Errands\s+579\s+668", l):
                vals = [int(x) for x in re.findall(r"\b\d{3}\b", l)][:4]
                vals = [579, 668, 608, 588, 473] if vals[:2] == [579, 668] else vals
                break
    if vals is None:
        vals = [579, 668, 608, 588, 473]  # printed values, 2017 NHTS Summary of Travel Trends, Table 10a (all persons)
    yrs = [1990, 1995, 2001, 2009, 2017]
    rows = [[y, v, "Annual person trips per person for shopping and errands, all persons",
             "FHWA Summary of Travel Trends: 2017 NHTS, Table 10a (p.32)",
             "Report cautions: catch-all category; methods changed (2017 address-based web sample may under-report incidental stops); decline 'may be affected by increases in online shopping' (not measured)"]
            for y, v in zip(yrs, vals)]
    write_csv("interp_spend_trips_nhts.csv", ["year", "shopping_errand_trips_per_person_per_year", "definition", "source", "caveat"], rows)


# --------------------------------------------------------------------------- 9. literature + mapping (hand-curated)
STUDIES = [
    # id, citation, data, access, status, finding, direction, numbers, categories, caveats
    ["Dolfen et al. 2019/2023", "Dolfen, Einav, Klenow, Klopack, Levin, Levin, Best. Assessing the Gains from E-Commerce. NBER WP 25610 (Feb 2019); AEJ: Macroeconomics 15(1):342-370 (2023). (This is the Einav/Klenow paper and the Dolfen paper - one paper.)",
     "Visa credit/debit transactions 2007-2017 (avg 380M cards, 35.9B transactions, $1.93T/yr); card-present vs card-not-present flag", "Visa data restricted; paper public",
     "OPENED (NBER WP full text, saved data/raw/interp_spend/papers/dolfen_nber_w25610.pdf)",
     "Online share of Visa spending in NAICS category rose 2007 -> 2017 (Table 2): electronics 42->51%, furniture 35->43%, clothing 22->37%, general merchandise 8->15%, food 5->6%, nonstore retailers 90->96%. Online = ~5% of all consumption 2007 -> ~8% 2017 (retail-only ~3.5% -> ~5%).",
     "substitution (mostly across merchants)", "Convenience gain <=0.4% of consumption; most gain is variety (switching to online-only merchants). Within-merchant: moving 10 -> 20 miles from nearest store raises online share of purchases ~3 pts (Table/Sec 4). Elasticity of substitution online vs offline merchants 4.3 overall; 3.4 electronics to 7.7 building materials (Table 9).",
     "furniture, electronics, clothing, sporting/hobby/books, misc, general merchandise, food (Table 2, Table 3, Table 9)",
     "WP version, not the published AEJ text. Share is of Visa card spend, scaled to consumption; assumes Visa online share representative. Does not measure trips or floor space; the 'trip' cost is a distance proxy."],
    ["Relihan 2022", "Relihan, L.E. Is online retail killing coffee shops? Estimating the winners and losers of online retail using customer transaction microdata. CEP Discussion Paper 1836 (Mar 2022).",
     "JPMorgan Chase Institute de-identified daily card transactions, 69M customers Oct 2012-May 2017; panel of ~7.7M; early adopters of online grocery platforms vs matched non-users", "JPMCI data restricted (data-use agreement); paper public",
     "OPENED (CEP PDF saved data/raw/interp_spend/papers/relihan_cep_dp1836.pdf)",
     "Early online-grocery adopters cut grocery-store trips by 0.5 days/month (6.8 -> 6.3, -7.4%) but spend 12.3% more on local ground transport and take more trips to coffee shops (+1.3 days/yr), leisure, personal care, restaurants (+2.3), and pharmacies (+0.9). No increase in trips for clothing, general goods, home goods.",
     "partial substitution for the replaced store (grocery); complementarity for time-intensive services; no new goods trips", "Counterfactual: platform adoption 1.7% -> 9.2% would cut mean zip-code grocery trip frequency 2.0% and raise coffee-shop frequency 3.4%.",
     "grocery (online grocery platforms, not Amazon-specific)", "Trip = card-transaction day, so trips without card payment are invisible; early adopters not representative; groceries only."],
    ["Chava et al. 2022/2024", "Chava, Oettl, Singh, Zeng. Creative Destruction? Impact of E-Commerce on the Retail Sector. NBER WP 30077 (May 2022); Management Science 70(4):2168-2187 (2024).",
     "Staggered rollout of a major e-commerce firm's fulfillment centers (firm not named in the text: first center 1997, over 90 by end-2016, which matches Amazon; Amazon appears only in cited news URLs and references) vs payroll data for 2.6M retail workers and data on 3.2M stores", "Payroll and store data are commercial/restricted; paper public",
     "OPENED (NBER full text searched for categories and firm name, saved data/raw/interp_spend/papers/chava_nber_w30077.pdf)",
     "A new fulfillment center lowers sales at proximate stores by 4% (employment -2.1%); store exit probability rises ~3 pts, entry falls; retail sector loses 938 jobs per county-quarter.",
     "substitution (store sales, store exits)", "Sales -4% and employment -2.1% at stores near a fulfillment center; classified retail 3-digit NAICS 442, 444, 448, 451 etc. in the exposure definition.",
     "NAICS 442, 444, 448, 451 and others (retail categories that compete with the catalog)", "Effect on stores near a center, not total spend shifted; category breakdown not used for the headline; counts store exits, not floor space."],
    ["Pozzi 2013", "Pozzi, A. The effect of Internet distribution on brick-and-mortar sales. RAND Journal of Economics 44(3):569-583 (2013); Oct 2012 working paper.",
     "Household scanner data (almost 10,000 households) from one large supermarket chain that added online shopping", "Chain data restricted (not Nielsen Homescan); WP public",
     "OPENED (Oct 2012 working paper, saved data/raw/interp_spend/papers/pozzi_wp.pdf)",
     "Online grocery sales are mostly incremental: each $1 online crowds out less than 40 cents of the chain's own store spend (WP abstract; a search snippet of another version says 45 cents - published figure not verified). Store revenues up 13% in the zip code once the service launches.",
     "mostly complementary for the retailer; crowd-out low and shrinks with distance from stores", "Crowd-out <$0.40 per $1 online; +13% zip-level chain revenue.",
     "grocery", "One chain; share-stealing from rivals is part of the 'incremental' revenue, so it is not net household-level complementarity."],
    ["Forman, Ghose, Goldfarb 2009", "Forman, Ghose, Goldfarb. Competition between local and electronic markets: how the benefit of buying online depends on where you live. Management Science 55(1):47-57.",
     "Amazon book sales ranks for 1,497 US locations, ~10 months to Jan 2006; local store openings (Barnes & Noble, Borders, Wal-Mart, Target)", "Public rank data scraped by authors; paper public",
     "SNIPPET ONLY (abstract via search result)",
     "Online book purchasing falls when a physical store opens nearby: online and local stores are substitutes at the margin; offline entry also lowers sensitivity to online price discounts.",
     "substitution", "Effects 'economically large' (no number captured).", "books", "Books only, 2005-06; snippet only."],
    ["Zhou and Wang 2014", "Zhou, Y. and Wang, X. Explore the relationship between online shopping and shopping trips: an analysis with the 2009 NHTS data. Transportation Research Part A 70:1-9.",
     "2009 National Household Travel Survey (public use), structural equation model", "NHTS public",
     "SNIPPET ONLY (abstract via search result)",
     "Online shopping increases the number of shopping trips (complementarity); shopping trips lower online-shopping propensity (store shopping substitutes for online).",
     "complementarity (online -> trips), with reverse substitution", "no magnitudes captured", "all shopping", "Cross-section, self-reported online shopping on a points scale; causality is not identified."],
    ["Atlanta/Boston Fed DCPC (Diary)", "Atlanta Fed Diary of Consumer Payment Choice 2020-2025 public microdata (this build); earlier years via Boston Fed",
     "3-day payment diary, ~3,000-5,000 US consumers/yr, October of each year", "Public microdata", "OPENED and computed (see interp_spend_dcpc_remote_by_merchant.csv)",
     "Remote (online, mail, phone) share of purchases about 20% 2020-2022 (double 2019 per Atlanta Fed text) and 24% of purchases by number in 2025 (report text). Category cut is coarse: merchant code 5 lumps general merchandise, department, other stores AND online shopping.",
     "records channel but not trips", "see CSV", "grocery/pharmacy, general+other stores+online, restaurants, etc.", "Payments, not trips; no category detail within stores; remote includes bills-like prepayments only for purchases."],
    ["FHWA NHTS 2017", "McGuckin and Fucci. Summary of Travel Trends: 2017 NHTS, Table 10a", "NHTS 1990-2017", "Public", "OPENED (saved data/raw/interp_spend/papers/nhts2017_summary.pdf)",
     "Shopping-and-errand person trips per person per year: 668 (1995), 608 (2001), 588 (2009), 473 (2017). Report attributes part of the drop to online shopping but does not measure it and warns about method changes.",
     "consistent with substitution, not identified", "-20% 2009 -> 2017", "all shopping and errands", "2017 sample is address-based/web; catch-all purpose."],
    ["NielsenIQ Homescan (Kilts)", "NielsenIQ Consumer Panel (Homescan) via Kilts Center, University of Chicago", "~40-60k US households scanning UPC purchases incl. online retailers", "RESTRICTED (Kilts data-use agreement); not downloaded",
     "SNIPPET ONLY",
     "No public category-level online share found. A search-result summary of an AEA working paper says the panel shows a growing online share over time, and a Fed discussion deck notes weak compliance for frequent small online purchases and ~4.9% of consumption coverage (Baker and Kueng figure).",
     "n/a", "n/a", "CPG/grocery-like barcoded goods", "Do not cite these as measured shares."],
    ["Numerator", "Numerator Total Commerce Panel / OmniPanel (receipt-based, ~200,000 households per company statements)", "Receipt capture across store and online", "RESTRICTED (commercial)",
     "SNIPPET ONLY",
     "Company survey report 'State of Commerce 2026' (survey of 2,000+ consumers, not the panel) says online share of 1-2 item baskets rose from 16% to 32% and of stock-up baskets from 3% to 12% since 2019. Not verified against the report.",
     "n/a", "n/a", "baskets", "Survey, self-reported, vendor press release."],
    ["US Financial Diaries", "Morduch and Schneider. The Financial Diaries (Princeton UP 2017); US Financial Diaries 2012-13", "235 households in 4 communities, every financial transaction for a year", "Public summaries; household data on request",
     "SNIPPET ONLY",
     "Not usable here: tiny, non-representative, 2012-13 only, built for income volatility and borrowing. Search results show no channel (online vs store) field and no category-level spending breakdown.",
     "n/a", "n/a", "n/a", "Say 'no evidence of a channel field', not 'confirmed absent'."],
    ["BLS CE outlet test", "BLS Division of CE Surveys, Lee and Abdirizak, AAPOR 2019 slides", "CE Interview final wave Jul 2017-Mar 2018, 1,100 test households (4,517 completed interviews)", "Test only; not a public time series",
     "OPENED (saved data/raw/interp_spend/bls/lee_outlet.pdf)",
     "A 'Purchase mode: online or in-person' question was tested in 10 CE Interview sections, along with store name and location. Only 224 households answered the purchase-mode question. No findings on online share in the deck.",
     "n/a", "n/a", "10 CE sections", "Production CE public-use files: no outlet or online variable found (see notes)."],
]

MAPPING = [
    # merchandise line (ARTS 4541), store type used by model, NAICS store kind (ARTS/CBP), CBECS PBA, EC 2012 PSCODEs, confidence, notes
    ["Clothing and clothing accessories (includes footwear)", "clothing", "448 Clothing and clothing accessories stores (also share of 452 department stores)", "Retail (other than mall): retail store; Enclosed and strip malls", "20200,20220,20240,20250,20260", "medium", "Clothing is the one line sold in both mall-anchor and strip formats; share between the two is not published."],
    ["Electronics and appliances; Computer and peripheral equipment; Computer software; Audio and video recordings", "electronics", "443 Electronics and appliance stores", "Retail (other than mall): retail store", "20300,20310,20320,20330,20370,20440", "medium", "ARTS computer lines are suppressed (S) in several years; 2017 Economic Census floor space has no 443 row."],
    ["Books (includes audio books and e-books); Sporting goods; Toys, hobby goods, and games", "books_hobby", "451 Sporting goods, hobby, musical instrument and book stores (+ part of 453)", "Retail (other than mall): retail store; strip centers", "20420,20530,20460", "medium", "ARTS publishes lines separately but NAICS 451 is a single store type."],
    ["Furniture and home furnishings", "furniture_home (not one of the six requested; add if model wants it)", "442 Furniture and home furnishings stores", "Retail (other than mall): retail store; Mercantile", "20340,20360,20380,20280", "medium", "Furniture shows the highest nonstore growth in dollars after clothing."],
    ["Drugs, health aids, and beauty aids", "grocery_pharmacy (drug stores) - map to 'grocery' bucket or add 'pharmacy'", "446 Health and personal care stores; part of 445/452", "Food sales (grocery/convenience) or Retail store", "20160", "low", "4541 nonstore line includes mail-order pharmacy: large and not a shift from store trips in the same way."],
    ["Food, beer, and wine", "grocery", "445 Food and beverage stores", "Food sales (CBECS PBA) - grocery store/food market, convenience store", "20100,20140", "high", "Online share is small (1-3% of line in 2012; Visa food online share 5 -> 6% 2007-2017)."],
    ["Other merchandise; Office equipment and supplies; Nonmerchandise receipts", "general_merchandise", "452 General merchandise stores (department, warehouse clubs, supercenters); 453 miscellaneous", "Retail (other than mall): retail store, dealership/showroom (big box); Enclosed mall (department store anchors)", "20850,29810", "low", "'Other merchandise' is a residual; ARTS gives no breakdown. General-merchandise stores' own e-commerce is suppressed (D) in ARTS 2020-2022."],
    ["(all lines; department-store specific)", "department", "4522/452210 Department stores (2017 NAICS)", "Enclosed mall anchors or retail store; 2017 floor space: 494 million sq ft total, 388 million selling (EC1744FLSPACE)", "none (line-level)", "low", "No ARTS line is 'department store goods'; department stores sell clothing, home goods, cosmetics, jewelry. Use department-store sales decline as the store-type signal."],
]


COMBINED = [
    # model store type, ARTS 4541 lines (prefix match), ARTS kind-of-business NAICS, BEA PCE codes, caveat
    ("clothing", ["Clothing and clothing accessories"], "448", ["DCLORC"],
     "448 own-website sales are mostly clothing; department-store (452) clothing online is suppressed so the all-channel share is understated"),
    ("furniture_home", ["Furniture and home furnishings"], "442", ["DFFFRC", "DUTERC"],
     "PCE denominator narrower than the ARTS line, so the percentage is overstated"),
    ("grocery_food", ["Food, beer, and wine"], "445", ["DFXARC"],
     "445 e-commerce includes some non-food; large grocers' (452 supercenter) online grocery is suppressed in ARTS, so understated"),
    ("electronics", ["Electronics and appliances"], "443", ["DVAPRC", "DAPPRC", "DTCERC"],
     "computer lines suppressed in the ARTS 4541 table; PCE series wider than the line: shown for completeness, unreliable"),
    ("books_hobby", ["Books", "Sporting goods", "Toys, hobby"], "451", ["DRBKRC", "DEBKRC", "DSPGRC", "DREIRC"],
     "451 own-website sales cover books, sporting goods, hobby; PCE 'recreational items' also holds pets and flowers: understated"),
]


def build_combined(merch_rows, kob_rows, pce):
    arts = {}
    for v, y, lab, tot, ft, ec, fe, sh in merch_rows:
        if v == "2022_benchmarked" and ec:
            arts[(lab, y)] = float(ec)
    kob = {}
    for y, naics, lab, tot, ft, ec, fe, sh in kob_rows:
        if ec:
            kob[(naics, y)] = float(ec)
    out = []
    for stype, prefixes, naics, codes, cav in COMBINED:
        for y in (2010, 2012, 2015, 2017, 2019, 2020, 2022):
            a = []
            for pre in prefixes:
                k = next((kk[0] for kk in arts if kk[0].startswith(pre) and kk[1] == y), None)
                a.append(arts.get((k, y)) if k else None)
            ec41 = sum(a) if all(x is not None for x in a) else None
            ecst = kob.get((naics, y))
            den = sum(pce[c].get(y, 0) for c in codes)
            comb = (ec41 + ecst) if ec41 is not None and ecst is not None else None
            out.append([stype, y, fmt(ec41, 0), fmt(ecst, 0), fmt(comb, 0), fmt(den, 0),
                        fmt(100 * ec41 / den, 1) if ec41 is not None and den else "",
                        fmt(100 * comb / den, 1) if comb is not None and den else "", cav])
    write_csv("interp_spend_online_share_combined_est.csv",
              ["model_store_type", "year", "arts_4541_line_ecom_musd", "store_based_kind_ecom_musd", "sum_musd",
               "bea_pce_denominator_musd", "pct_4541_only", "pct_4541_plus_store_based", "caveat"], out)
    return out


def build_visa():
    """Hand-typed from Dolfen et al., NBER WP 25610 (Feb 2019): Table 2 (p.9), Table 3, Table 9. Opened full text."""
    t2 = [("Nonstore Retailers", 90, 96), ("Air Transport", 87, 97), ("Electronics", 42, 51), ("Furniture", 35, 43),
          ("Clothing", 22, 37), ("General Merchandise", 8, 15), ("Food", 5, 6)]
    t3 = {"Furniture (442)": (0.168, 0.244), "Electronics (443)": (0.474, 0.295), "Clothing (448)": (0.265, 0.302),
          "Sporting goods, hobby, music, books (451)": (0.253, 0.238), "Misc. stores (453)": (0.220, 0.393)}
    t9 = {"Building Material, Garden Supplies": 7.7, "Motor Vehicle and Parts Dealers": 7.5,
          "Furniture and Home Furnishings Stores": 7.4, "General Merchandise Stores": 5.8,
          "Health and Personal Care Stores": 5.5, "Clothing and Clothing Accessories Stores": 5.2,
          "Miscellaneous Store Retailers": 5.2, "Sporting Goods, Hobby, Music, Book Stores": 4.2,
          "Food and Beverage Stores": 3.6, "Electronics and Appliance Stores": 3.4}
    rows = []
    for n, a, b in t2:
        rows.append(["Table 2", n, "online % of Visa card spending in NAICS category", "2007", a, "2017", b])
    for n, (tr, sp) in t3.items():
        rows.append(["Table 3", n, "online share (card-not-present e-commerce) within category merchants that sell both ways; transactions, spending (period 2007-2017 pooled, estimation sample)", "transactions", tr, "spending", sp])
    for n, v in t9.items():
        rows.append(["Table 9", n, "elasticity of substitution sigma between offline and online merchants (higher = more substitutable)", "sigma", v, "", ""])
    rows.append(["Fig 2 / text p.9", "All consumption", "estimated online share of US consumption", "2007", "about 5", "2017", "almost 8 (retail-only about 3.5 -> 5)"])
    write_csv("interp_spend_visa_online_share_by_naics.csv",
              ["table", "category", "measure", "col1_label", "col1", "col2_label", "col2"], rows)


def build_studies_and_mapping():
    write_csv("interp_spend_substitution_studies.csv",
              ["study", "citation", "data", "data_access", "verification_status", "finding", "substitution_vs_complementarity",
               "key_numbers", "categories_covered", "caveats"], STUDIES)
    write_csv("interp_spend_store_type_mapping.csv",
              ["arts_merchandise_lines", "model_store_type", "naics_store_kind", "cbecs_pba_candidate", "ec2012_pscodes",
               "mapping_confidence", "note"], MAPPING)


# --------------------------------------------------------------------------- main
def main():
    if "--download" in sys.argv:
        download_missing()
    os.makedirs(OUT, exist_ok=True)
    build_quarterly()
    merch = build_merch_lines()
    kob = build_kind_of_business()
    build_denominator_2012(merch)
    pce = build_pce()
    build_line_vs_pce(merch, pce)
    build_combined(merch, kob, pce)
    build_dcpc()
    build_ce()
    build_floorspace()
    build_trips()
    build_visa()
    build_studies_and_mapping()
    print("retrieved", RETRIEVED)


if __name__ == "__main__":
    main()
