# Interpretation page: arguments about Amazon warehouse safety and environmental effects

Compiled 2026-11-01. Public sources only. Saved copies are in `data/raw/interp_arguments/` (gitignored via `data/raw/`). All paths below are relative to that directory.

Conventions
- "Page" means the printed page number unless "PDF p." is given.
- "SNIPPET ONLY" means I saw the claim only in a search-result summary and did not open the document. Do not quote these without opening the source.
- "NOT SAVED" means I read it through a fetch tool but the file is not on disk.
- Last column "Our data can say": left as "TBD by manager" where unsure; otherwise a suggested check, marked as a suggestion.

---------------------------------------------------------------------

## PART A. SAFETY

### A0. Number cross-check table (all from OSHA ITA 300A data unless stated)

| Year | Amazon total recordable rate per 100 FTE | Source | Comparator numbers |
|---|---|---|---|
| 2019 | 9.01 (Senate, Amazon warehouses) | HELP report p.19 fn 52 | BLS large warehouses (1,000+) 5.8 |
| 2020 | 6.59 (Senate); 6.6 (SOC) | HELP p.19 fn 52; SOC 2025 p.1 | BLS large 5.5 |
| 2021 | 7.64 (Senate); 7.9 (SOC) | HELP p.19 fn 52; SOC 2025 p.2 | BLS large 6.7 |
| 2022 | 6.97 (Senate); 6.9 (SOC) | HELP p.19 fn 52; SOC 2025 p.2 | BLS large 6.8 |
| 2023 | 6.54 (Senate); 6.5 (SOC); 6.5 (Amazon, GWS only) | HELP p.19; SOC 2025 p.2; Amazon blog 2024-03-08 | BLS large 5.4; BLS all warehousing 4.8 |
| 2024 | 6.0 (SOC, all warehouse+logistics) | SOC 2025 p.1-2 | Non-Amazon warehouses: SOC says Amazon warehouses are 66% higher (p.3) |

Why the Senate and SOC series differ slightly: the Senate figure is for NAICS 493110 only ("warehouses"); SOC pools Amazon's 493110 and 492110 (couriers) facilities and, for 2021-22, re-pools 393 facilities Amazon moved from 493110 to 492110 (SOC 2025 App. A p.9). Both sum cases and hours before dividing (HELP p.20 fn 56; SOC 2025 App. A p.8).

Two definitional traps for the interpretation page:
1. SOC's "serious injury rate" = any case with days away, restricted or transferred (DART) (SOC 2024 App. A p.21: "Serious Injury Rate (defined as any case involving DART)"). Amazon's "lost time incident rate" counts only days-away cases ("the most serious injuries"). SOC 2024 serious rate 5.9 per 100 vs Amazon's own 2023 GWS LTIR 1.1 are NOT comparable measures.
2. Amazon's March 2024 post compared its 2023 rate (6.5) with the **2022** BLS large-warehouse average (6.8) because 2023 BLS averages were not yet out. The 2023 BLS large-warehouse figure, cited by the Senate in Dec 2024, is 5.4, i.e. below Amazon's 6.5. (Derived by comparing the two documents; both are saved.)

Our data: suggested check (manager to confirm): rebuild the Amazon total recordable rate by year from our OSHA ITA file with the sum-then-divide method and compare with the table above; the series should match to about +/-0.1.

---

### A1. US Senate HELP Committee majority staff report (Sanders)

- Publisher: US Senate Committee on Health, Education, Labor and Pensions, Chairman Bernard Sanders, Majority Staff Report
- Title: "The 'Injury-Productivity Trade-off': How Amazon's Obsession with Speed Creates Uniquely Dangerous Warehouses"
- Date: December 2024 (PDF created 15 Dec 2024; Sanders press release 16 Dec 2024). 160 pages.
- URL: https://www.help.senate.gov/imo/media/doc/amazon_investigation.pdf (the senate.gov host returns 403 to scripted fetches; the saved copy came from a Wayback snapshot of that URL and matches a second copy at assets.ctfassets.net, https://assets.ctfassets.net/3kqcuzntcg31/3rFi4lwYQRDFeZrv6Xb9v8/29fefe97db69c87a26ab4222e9ef5ca5/amazon_investigation.pdf)
- Saved: `help_amazon_investigation.pdf`, `help_amazon_cdn_copy.pdf` (duplicate), `help_report.txt` (full text)
- Interim report (July 15 2024, "Peak Seasons, Peak Injuries", 9 pp): `help_interim_report_july2024.pdf`, URL https://www.help.senate.gov/imo/media/doc/help_committee_amazon_interim_report.pdf
- Evidence base: public OSHA ITA 300A data plus BLS industry averages (HELP p.17 fn 41); 135 worker interviews and about 500 worker submissions with 1,400 documents; only 285 documents produced by Amazon (p.4-5); Amazon internal documents (Project Soteria, Project Elderwand, an October 2020 internal injury-rate report AMAZON_00004101). The report states it "had to rely heavily on evidence from workers" (p.5).

Quotes
- Injury rates (p.6, Key Finding 1, "Page 17"): "An analysis of the company's data shows that Amazon warehouses recorded over 30 percent more injuries than the warehousing industry average in 2023. The Committee also found that in each of the past seven years, Amazon workers were nearly twice as likely to be injured as workers in warehouses operated by the rest of the warehousing industry. ... more than two-thirds of Amazon's warehouses have injury rates that exceed the industry average."
- Comparator critique (p.19-20): "Amazon has repeatedly compared the injury rate for its warehouses of all sizes to the industry average for large warehouses (those with 1,000 or more employees). But only 40 percent of Amazon warehouses have 1,000 or more employees." and "In 2023, Amazon had 168 of the country's 255 total warehouses with more than 1,000 employees, and employed nearly 80 percent of all of the workers who work in facilities of that size. ... the reason the average injury rate for that subcategory is closer to Amazon's injury rate is because Amazon dominates the subcategory."
- Same page: "even using this misleading comparison, Amazon's injury rate has still been higher than the average injury rate for large warehouses in each of the past five years." (footnote 52 gives the yearly numbers in table A0.)
- 31 percent figure (p.20): "in 2023, Amazon warehouses recorded and disclosed 31 percent more injuries than the average warehouse."
- Boast vs outlier base year (p.18): "Amazon's statement is only true because the company's 2019 data represented a 24 percent increase from two years earlier, and a 16 percent increase from 2018."
- Worst sites (p.21): Spokane "27 injuries per every 100 workers"; "The ten Amazon warehouses with the highest injury rates all exceeded 17 injuries per 100 workers."
- AmCare / underrecording (p.117-123): "Amazon deflates the injury numbers it records for federal regulators" (Key Finding 10, p.8). "the Committee is concerned that AMCARE's reluctance to make external referrals may be part of an effort to treat workers' injuries 'in house' in order to prevent those injuries from being classified as recordable." (p.119). OSHA Texas site finding: "out of 476 total injuries, only seven percent were listed as 'recordable.'" (p.122). Committee caveat, which the page should repeat: "not every injury reflected in the 'total injury rate' is a serious injury" (p.120).
- Internal total-injury rate (interim report, p.1 and p.3-4; also HELP p.119-120): recordable rate "over 10 injuries per 100 workers" during Prime Day 2019 week; total injury rate "just under 45 injuries per 100 workers". Amazon declined to supply later-year totals (HELP p.119 fn 691).
- Quotas (p.23-24): Amazon "does not utilize quota requirements" (2020 letter) is "semantic, not substantive"; Amazon's 2023 claim that it does "not require employees to meet specific productivity speeds or targets" is "demonstrably false."
- Project Soteria (p.7, Key Finding 6; detail pp.71-82): Soteria "found evidence of a connection between speed and injuries"; senior leaders cited concern about "negatively impacting rate/productivity and the ability to deliver on time to customers"; leadership redirected the team to "maximize rates/productivity" without raising injuries, "the 'injury-productivity trade-off'" (p.77); an audit team attributed injuries to "frailty" and "intrinsic likelihood of injury" (p.82).
- Project Elderwand (p.8; detail p.90): Amazon determined a maximum repetition count per shift for one role, then "decided not to implement the change."
- Penalty context (p.6): OSHA proposed penalties "for more than 50 violations ... over a two-year period totaled less than $300,000."

Caveats for the page: this is a majority-staff (Sanders) document, not a bipartisan one; its causal claim (speed causes injury) rests largely on worker testimony and an internal study Amazon disputes (see A3).

Our data: TBD by manager. Suggested: the 2019-2023 Amazon vs non-Amazon vs large-warehouse comparison, and the share of Amazon sites above the industry average, can be recomputed from OSHA ITA.

---

### A2. Strategic Organizing Center (SOC) reports

SOC is a coalition of unions (SEIU, CWA, UFW; Teamsters until about 2023). It is an advocacy organisation; it labels its own analysis as union research. The method is the same public OSHA ITA 300A data. Reports saved:

| Report | Date | File | Data year | Headline |
|---|---|---|---|---|
| Primed for Pain | May 2021 (press 1 June 2021) | `soc_2023_primed_for_pain.pdf` (filename says 2023 by mistake; it is the 2021 report) | 2017-2020 | Amazon injury rate "more than double the injury rate in the ... general warehousing industry" (p.1); total rose 2017 to 2019 to 9.0 per 100 (Fig. 3) |
| The Injury Machine | April 2022 | `soc_2022_injury_machine.pdf` | 2021 | Overall rate "increased by 20 percent from 2020 to 2021"; "serious injury rate at Amazon warehouses was 6.8 per 100 workers ... more than double ... non-Amazon warehouses (3.3 per 100)"; Amazon 33% of warehouse workers, "49% of all injuries" (p.1) |
| In Denial | April 2023 | `soc_2023_in_denial.pdf` | 2022 | Serious rate "6.6 per 100 workers ... more than double ... non-Amazon warehouses (3.2 per 100)"; 36% of workers, 53% of serious injuries (p.2) |
| Same Day Injury | May 2024 | `soc_2024_same_day_injury.pdf` | 2023 | Overall 6.5 per 100 (vs 6.6 in 2020, "less than two percent" improvement); serious rate "6.1 per 100 ... more than double ... (3.0 per 100)"; 35% of workers, 53% of serious injuries; injuries spiked "as much as 59 percent" around peak periods (p.3) |
| Failure to Deliver | 16 May 2025 | `soc_2025_failure_to_deliver.pdf` | 2024 | Overall 6.0 per 100 (down 7.4% from 6.5); "reducing its overall injury rate by only 10%" since 2020; Amazon warehouse serious rate "5.9 per 100 workers--almost double ... non-Amazon warehouses (3.0 per 100)"; 39% of warehouse workers, 56% of serious injuries (p.1); 396 facilities with 38% of FTEs saw rate increases (p.3) |

URLs: https://thesoc.org/wp-content/uploads/2025/05/May-2025_Strategic-Organizing-Center_Report-x-Failure-To-Deliver.pdf ; https://thesoc.org/wp-content/uploads/sites/342/SOC_Same-Day-Injury-Report-May-2024.pdf ; https://thesoc.org/wp-content/uploads/sites/342/SOC_In-Denial_Amazon-Injury-Report-April-2023.pdf ; https://thesoc.org/wp-content/uploads/sites/342/The-Injury-Machine_How-Amazons-Production-System-Hurts-Workers.pdf ; https://thesoc.org/wp-content/uploads/sites/342/PrimedForPain.pdf . Press page for the 2025 report dated 16 May 2025: https://thesoc.org/resources/failure-to-deliver-amazon-falls-short-on-safety/ . I found no 2026 SOC injury report.

Method (SOC 2025 App. A p.8-9; same text in SOC 2024 App. A p.21-22):
- "annual summary data from OSHA Form 300A and ... detailed case ... submitted by Amazon to OSHA through OSHA's Injury Tracking Application".
- "Injury counts and hours worked were summed before calculating rates to ensure that rates were properly weighted and not skewed by smaller facilities."
- 2,000 hours = one FTE; rates per 100 FTE.
- Excludes Amazon facilities reported under manufacturing and retail NAICS codes; keeps warehouse (493110) and couriers (492110).
- Drops records where hours / average employees exceeds 8,760 (OSHA validation rule).
- Reclassification handling: Amazon moved 393 facilities from 493110 to 492110 in 2021; SOC keeps them in the "warehouse" group for Amazon trend lines.
- The 2025 report notes 2023 figures were revised because "three Amazon delivery service partner (DSP) facilities ... were erroneously included" (App. B note, p.10).

Evidence base: OSHA public data only; no internal Amazon documents. Amazon calls the "serious injury" label misleading (see A3). 

Our data: suggested check (manager to confirm): our Amazon total rate by year versus SOC's 6.6, 7.9, 6.9, 6.5, 6.0; our non-Amazon 493110 comparator versus SOC's 3.3, 3.2, 3.0, 3.0 DART rates. A difference above 0.2 would indicate a NAICS-grouping or hours-filter difference.

---

### A3. Amazon's own position

Saved: `amazon_blog_safety_performance_2024-03-08.html/.txt`, `amazon_blog_safety_performance_2025.html/.txt`, `amazon_blog_safety_injury_reduction_2026.html/.txt`, `amazon_response_sanders_2024.html/.txt`.

1. Sarah Rhoads (VP Global Workplace Health and Safety), "Amazon's Safety Performance Continues to Improve Year over Year", aboutamazon.com, 8 Mar 2024. https://www.aboutamazon.com/news/workplace/amazon-workplace-safety-post-2023
 - Claim: "Our Recordable Incident Rate (RIR) ... has improved 30% over the past four years and 8% year over year" (global); Lost Time Incident Rate "improved 60% over the past four years" (global).
 - US General Warehousing and Storage: "Our RIR improved 24% over the past four years. Amazon's 2023 rate is 6.5, which is better than the latest BLS average of 6.8 for employers our size (>1,000 employees)." LTIR "1.1, which is better than the latest BLS average of 2.6".
 - Courier and Express Delivery: RIR 2023 "6.3, which is better than the latest BLS average of 11.5 for employers our size (250-999 employees)".
 - Comparator: BLS averages "based on employers' size". Amazon's goal text: "Our goal is to be the safest workplace within the industries in which we operate."
 - Evidence: Amazon's own OSHA-reportable data; the BLS comparator was the 2022 average ("the 2022 averages published in November 2023 are the most recent").
2. Same author, 13 Mar 2025 (2024 data). https://www.aboutamazon.com/news/workplace/amazon-workplace-safety-performance-2024 . Global RIR "improved 34% over the past five years and over 6% year over year"; US warehousing RIR "improved 27% over the past five years and 5% YoY"; LTIR "79% over the past five years". Comparison graphs against 2023 BLS averages (graph values are images, not in saved text; SNIPPET ONLY for the plotted numbers).
3. Same author, 12 Mar 2026 (2025 data). https://www.aboutamazon.com/news/workplace/amazon-workplace-safety-2025-injury-reduction . Global RIR "improved 43% over the past six years and 14% year-over-year"; US warehousing RIR "improved 39% over the past six years and 16% YoY"; warehousing LTIR "was flat YoY". Notable shift in wording: "Comparing safety performance across companies isn't straightforward given reporting methodologies vary and very few companies proactively publish detailed data." Goal is now "set the benchmark for safety excellence across every industry", not "safest workplace".
4. Amazon Staff, "Senator Bernie Sanders continues to mislead the American public on workplace safety at Amazon", aboutamazon.com, 16 Dec 2024. https://www.aboutamazon.com/news/policy-news-views/amazon-response-to-senator-bernie-sanders-report-on-workplace-safety (saved as `amazon_response_sanders_2024.*`)
 - Speed vs injury: "we've increased our delivery speeds, while decreasing the injury rates across our network. ... speedy delivery doesn't come from pushing people harder - it comes from getting products closer to customers and reducing the number of steps".
 - "from 2019-2023, we reduced our recordable incident rate ... in the U.S. by 28%, and we reduced our lost time incident rate ... by 75%."
 - Comparator defence: "we compare ourselves against the average for employers with over 1,000 employees. ... we have on average 1,400 employees at the buildings that are included in this particular comparison."
 - Delivery: "Amazon's Courier and Express Delivery RIR rates for 2023 were 6.3, while the industry average (regardless of number of employees) was 9.7."
 - Soteria: "analytically unsound"; "evaluated by expert economists at Amazon, and they determined that the project was flawed and inaccurate"; "never used".
 - Washington: "a Washington judge ruled in Amazon's favor and vacated the citations ... the judge ruled that L&I did not establish that pace of work at Amazon was hazardous."
 - Total injury rate: "'Total injury rate' claims are a red herring."
 - AmCare: "These centers are for first aid and first aid only"; OSHA's recordkeeping probe found "small clerical errors".
 - Anecdotes: 135 interviews is "about 0.018% of our current frontline employee population".
 - Footnote 1: "All numbers and comparisons in this letter are based on the rates we have reported to applicable regulators".
 - Amazon's direct criticism is of the Senate report; I did not find a document in which Amazon responds to SOC's method line by line. SOC's 2025 page has no Amazon response (checked). Treat "Amazon's criticism of SOC's method" as not found in a primary document; the large-site-benchmark rebuttal above is aimed at the Senate. Press quotes of Amazon on SOC ("serious injury" label misleading) were SNIPPET ONLY.
 - Note the discrepancy: Amazon's 2024-03-08 post says RIR improved 24% (GWS, 4 yrs); Senate calls 2019 an outlier base year (HELP p.18).

Our data: TBD by manager. Suggested: compute the share of Amazon employees in 1,000+ employee sites and the share of 1,000+ sites that are Amazon (Senate says 168 of 255 sites, nearly 80% of workers in such sites) to test the "Amazon dominates its own comparator" argument.

---

### A4. Government enforcement

a) OSHA ergonomic citations (inspections from July 2022, SDNY referral)
 - Date of citations: announced 18 Jan 2023 for Deltona FL, Waukegan IL, New Windsor NY: proposed penalties $60,269 (SNIPPET ONLY; the osha.gov page for 18 Jan 2023 returned 404 to my fetch; news sources cited it). The Dec 2022 citations of Amazon facilities for recordkeeping failures are cited by the Senate (HELP p.120-121, citing OSHA20222343, e.g. Albany ALB1: "failed to record 11 injuries ... in just a month and a half").
 - Senate: Amazon violated recordkeeping rules "in at least 20 facilities since 2022" (p.120).
b) OSHA / DOL corporate-wide settlement, 19 Dec 2024. Saved: `osha_20241219_settlement_release.html/.txt`. URL https://www.osha.gov/news/newsreleases/osha-national-news-release/20241219
 - Headline: "US Department of Labor announces settlement with Amazon requiring corporate-wide ergonomic measures at facilities across the country".
 - "The settlement agreement resolves the department's multiple ergonomics cases against Amazon.com Services LLC, in the first major multi-site investigation brought by OSHA in over a decade."
 - "The parties had been scheduled to begin trials in 10 cases ... between January and June 2025 stemming from inspections conducted across 10 Amazon facilities beginning in the summer of 2022."
 - "Amazon will also pay a penalty of $145,000, over 90 percent of the amount assessed by OSHA in the ergonomics citations."
 - "The agreement will apply to all of Amazon's fulfillment centers, sortation centers, and delivery stations ... in federal OSHA's jurisdiction"; "alternative dispute resolution process"; two-year term (per the full release) with biannual meetings on MSD injury trends. Douglas Parker: "The ball is in the company's court."
 - The release does not say how many citations were withdrawn. Amazon's public statement that all but one ergonomic citation was withdrawn was SNIPPET ONLY.
 - Evidence base: OSHA inspections of 10 sites; no admission of liability reported (SNIPPET ONLY).
c) Washington State L&I. 
 - 20 Mar 2022 release #22-08, Kent fulfillment center: "willful serious violation and a $60,000 fine"; "10 of the 12 processes L&I evaluated create a serious hazard for work-related back, shoulder, wrist, and knee injuries"; workers "required to perform these tasks at such a fast pace that it increases the risk of injury". Saved: `lni_22-08_kent_citation.html/.txt`. https://lni.wa.gov/news-events/article/22-08
 - Outcome: July 2024, Board of Industrial Insurance Appeals judge Stephen Pfeifer ruled for Amazon in the consolidated appeals; per Amazon, the state "lacked sufficient evidence to support its allegations that the pace of work in Amazon warehouses is hazardous". L&I said it would appeal. Source saved: `insurancejournal_2024-07-29_wa_ruling.html/.txt` (Bloomberg wire, 29 Jul 2024). The ruling itself was not public when I read it. Later report of the Board denying L&I's petition for review was SNIPPET ONLY.
d) California AB 701 (warehouse quotas). Saved: `ca_dir_ab701_legislative_report.pdf/.txt` (California Labor Commissioner's Office, report for 2022; 7 pp). https://www.dir.ca.gov/dlse/AB-701-Legislative-Report_DIR_DLSE.pdf
 - Signed 22 Sep 2021, effective 1 Jan 2022 (signing date SNIPPET ONLY; the effective date is stated on p.2 of the report).
 - Covers employers with "100 or more employees at a single warehouse distribution center, or 1,000 or more employees at multiple" (p.2).
 - "an employee cannot be required to meet a quota that prevents compliance with meal or rest periods, use of bathroom facilities ... or occupational health and safety standards" (p.2).
 - As of 19 Dec 2022 the Labor Commissioner had received 168 reports of violations, 93 alleging quotas prevent health and safety compliance (p.3). That is complaints, not findings.
e) New York Warehouse Worker Protection Act: S8922-A, Chapter 722 of 2022, signed 21 Dec 2022 (NOT SAVED; read at https://www.nysenate.gov/legislation/bills/2021/S8922 through a fetch tool). Covers 100+ employees at one warehouse distribution center or 500+ statewide. Requires written quota disclosure; no quota that prevents meal or rest breaks. Effective date: the bill page implies 60 days after signing; widely reported as 19 June 2023 (unverified, SNIPPET ONLY). Ergonomic-evaluation text was in the original S8922 but not in S8922-A (per the fetch result).

Our data: TBD by manager. Suggested: site-level OSHA ITA rates for the cited sites (Kent DLS4 area, Deltona, Waukegan, New Windsor, Albany ALB1) before and after citation dates could be pulled, noting small-n.

---

### A5. Academic / Fed / BLS work on whether Amazon raised or lowered injury rates in local labor markets

Result of searching: I did NOT find any peer-reviewed, Fed, or BLS study that estimates the causal effect of Amazon warehouse openings on local or industry injury rates. Say so on the page rather than imply a literature exists. What I did find:

- GAO-24-106413, "Workplace Safety and Health: OSHA Should Take Steps to Better Identify and Address Ergonomic Hazards at Warehouses and Delivery Companies", 18 Sep 2024 (released 8 Oct 2024). Saved: `gao_24_106413_ergonomic_hazards_warehouses.pdf` (72 pp). https://www.gao.gov/products/GAO-24-106413
 - PDF p.19: "From 2018 through 2022, the estimated serious injury rates in general warehousing and last-mile delivery increased significantly faster than the estimated rate for all private industry ... the serious injury rate for general warehousing rose by 20 percent (from an estimated 4.0 to 4.8 cases per 100 full-time workers), and the serious injury rate for last-mile delivery rose by 23 percent (from an estimated 6.0 to 7.4 ...)."
 - Evidence: BLS SOII; descriptive; GAO says there is no e-commerce NAICS code, so it uses general warehousing as a proxy. Does not attribute the rise to Amazon.
- NELP (advocacy), "Amazon's Outsized Role: The Injury Crisis in U.S. Warehouses and a Policy Roadmap to Protect Workers", May 2024. Saved: `nelp_2024_amazons_outsized_role.pdf` (30 pp). https://www.nelp.org/app/uploads/2024/04/Amazons-Outsized-Role-5-1-24.pdf . Claims Amazon is "37 percent of all U.S. warehouse employment" and its rate is more than 1.5 times other large warehouse employers (the rate text was seen only in a grep excerpt; open before quoting). Descriptive, not causal.
- Chava, Oettl, Singh, Zeng (below, section C3) is about wages and retail, not injuries.
- Robot and injury evidence: SOC "Primed for Pain" (p.6-8) argues injury rates are higher at Amazon's robotics facilities; the Reveal/CIR Tracy CA robot claim was SNIPPET ONLY. Not a causal study.

Our data: this is where our dataset could add something that the literature lacks. TBD by manager (e.g. county-level OSHA ITA rates for 493110 before and after an Amazon site opens; simple event-study of non-Amazon warehouse rates). Flag as exploratory only.

---------------------------------------------------------------------

## PART B. Argument map: SAFETY

| Argument | Who makes it | Evidence they cite | What our data can say |
|---|---|---|---|
| Amazon warehouses are far more dangerous than peers | Senate HELP majority (Sanders); SOC; NELP | OSHA ITA 300A, BLS industry averages; Amazon 6.54 vs non-Amazon about half that; SOC serious (DART) 5.9 vs 3.0 in 2024 | Suggested check: recompute with sum-then-divide; TBD by manager |
| Amazon's own safety record is improving and in line with or better than peers | Amazon (Rhoads posts 2024-2026; Dec 2024 response) | Own RIR/LTIR series from OSHA-reportable data; BLS large-site (1,000+) and courier averages | Suggested check: trend 2019 to 2025 once 2025 ITA is out; TBD by manager |
| The "improvement" is flattering because 2019 was an outlier | Senate HELP (p.18) | Amazon RIR 2017 to 2019 rose; 9.01 in 2019 | Our ITA series covers 2017-2024 so the outlier-year point is directly testable; suggested |
| Amazon's chosen comparator (1,000+ employee warehouses) is biased because Amazon dominates it | Senate HELP (p.19-21) | 168 of 255 large warehouses; about 80% of large-site workers | Suggested: count Amazon share of 1,000+ sites from ITA; TBD by manager |
| Counter: the comparator is fair because Amazon sites average 1,400 employees | Amazon (Dec 2024 response) | Own site-size statistic | Suggested: distribution of Amazon site employment; TBD by manager |
| Measured rates understate true injuries (AmCare, 21-day rule, internal total rate near 45 per 100 in Prime Day 2019) | Senate HELP (interim and final report); SOC (AmCare clinic visits) | Internal Soteria-era chart, OSHA ELP1 Texas letter (476 injuries, 7% recorded), worker interviews | Our data cannot see unrecorded injuries; TBD by manager |
| Counter: total injury rate includes first-aid cuts; no systemic underreporting; OSHA found "clerical errors" | Amazon | Own statement; OSHA recordkeeping probe (cited by Amazon, not seen in primary form) | Cannot say |
| Speed and quotas cause injuries | Senate HELP; SOC; WA L&I (2022 citation); OSHA ergonomic cases | Soteria, worker testimony, L&I ergonomist observation | Cannot test with OSHA ITA |
| Counter: pace not shown hazardous; Soteria flawed; speed up and injuries down | Amazon; WA BIIA judge (2024) | Amazon economists' review; BIIA ruling (ruling text not seen) | Suggested: any link between Amazon site-level growth in hours and rate changes is exploratory only |
| Regulation is needed or working (AB 701, NY WWPA, federal Warehouse Worker Protection Act S.4260) | Senate HELP; state legislators | Quota disclosure; complaints data (168 RLLVs in CA, 2022) | TBD by manager |
| OSHA settlement shows enforcement works / shows weak penalties | OSHA (corporate-wide agreement, $145,000); Senate HELP ("penalties ... far too low") | Settlement terms | Cannot say |

---------------------------------------------------------------------

## PART C. ENVIRONMENT

### C1. Amazon's Climate Pledge claims and methodology critiques

Amazon primary documents (saved):
- Amazon, "Amazon Sustainability Report 2025", released July 2026 (PDF created 14 Jul 2026), 51 pp: `amazon_sustainability_report_2025.pdf/.txt`. https://sustainability.aboutamazon.com/2025-amazon-sustainability-report.pdf
 - Table "Amazon's 2019-2025 Carbon Footprint" (PDF p.46), MMT CO2e: total 51.17 (2019), 60.64, 71.54, 65.37, 65.28, 69.55 (2024), 80.85 (2025) (+16% YoY). Scope 1: 5.76 to 15.37; Scope 2 (market-based): 5.50 to 3.74 (+34% in 2025); Scope 3: 39.91 to 61.74 (+20%). Carbon intensity (g CO2e per $ revenue): 182.4 (2019) to 112.8 (2025), "3%" YoY increase.
 - Text: "From 2024 to 2025, absolute emissions increased 16% and carbon intensity increased 3%. Yet, since 2019, overall carbon intensity has decreased 38%". Scope 3 "76% of our carbon footprint".
 - Comparison: footprint 2019 to 2025 is +58% in absolute terms (51.17 to 80.85, computed here) while intensity fell 38%.
- Amazon, "Carbon Methodology" (8 pp, created 1 Jul 2026): `amazon_carbon_methodology.pdf/.txt`. https://sustainability.aboutamazon.com/carbon-methodology
 - Boundary (p.1): includes "Amazon's last mile delivery fleet", "Amazon-operated freight", "Purchased delivery services (e.g., postal services) and other contracted freight", "Amazon-branded product manufacturing, such as Echo devices, Kindle e-readers, Amazon Basics, Whole Foods Market brands, and other Amazon Private Brands products". It lists no emissions from manufacturing of third-party products sold on the store. (That is the basis for the critique; the document does not itself say the exclusion is 99% of sales.)
 - Scope 2 method (p.1; further detail on later pages): "Amazon reports emissions according to GHGp's market-based method (MBM) in both Scope 2 and Scope 3 (as applicable)", and Scope 1/3 include "certain Environmental Attribute Certificates".
 - 2025 values "independently assured by Ernst & Young LLP" (page not recorded; text near the end of the first section).
- Amazon, "Amazon Sustainability Report 2024": `amazon_sustainability_report_2024.pdf/.txt` (57 pp, created 18 Aug 2025). https://sustainability.aboutamazon.com/2024-amazon-sustainability-report.pdf . Secondary coverage: 2024 total 68.25 vs 64.38 MMT (original release; shown as 69.55 in the 2025 report, whose table carries the note "calculated in accordance with updated Carbon Methodology"; I infer a restatement "calculated in accordance with updated Carbon Methodology"). Restatement note: confirm before citing 2024 as either number.

Critics
- NewClimate Institute, Corporate Climate Responsibility Monitor 2022, Feb 2022, 128 pp: `newclimate_ccrm_2022.pdf` (saved from a Wayback copy; original https://newclimate.org/wp-content/uploads/2022/02/CorporateClimateResponsibilityMonitor2022.pdf). Amazon section p.54-55 (PDF p.55): "Amazon's net-zero carbon 2040 pledge currently remains unsubstantiated"; "no explicit reduction target for the company's own emissions, and with a significant role envisaged for offsets"; "Amazon's pledge is weakened by relying on offset credits from nature-based solutions"; recommends reporting "scope 2 emissions with the location-based accounting method in addition to the market-based method used". The same section also credits Amazon's renewable procurement as "mostly from high-quality" PPAs. Rating: "low" integrity and "low" transparency for Amazon (rating labels SNIPPET ONLY in press; the p.54 text is saved). Amazon's response (press, SNIPPET ONLY): report "lacks understanding of our approach and contains significant inaccuracies". I found no later NewClimate rating of Amazon; check newclimate.org for 2023-2025 editions.
- Amazon Employees for Climate Justice, "Burns Trust: The Amazon Unsustainability Report", July 2024: `aecj_unsustainability_report_2024-07.pdf` https://static1.squarespace.com/static/65681f099d7c3d48feb86a5f/t/668ebf702516716ca72bbf98/1720631157044/unsustainability-report.pdf . I have NOT read it beyond file retrieval. Claims reported by press (SNIPPET ONLY): unbundled RECs are "68%" of Amazon's renewable claims (citing Amazon's 2023 CDP disclosure) and only "22%" of renewable energy used at Amazon's US data center locations comes from local utilities; recommends hourly matching. AECJ is an employee advocacy group; data centers (AWS) are outside the logistics scope of our dashboard.
- Stand.earth (Stand Research Group), "Amazon? Sustainable? Think again.", 29 Jan 2026: `stand_earth_amazon_sustainable_think_again.html/.txt` (Wayback copy). https://stand.earth/insights/amazon-sustainable-think-again/ . Quotes: logistics emissions "increased more than 75% during the period 2019-2023 - from 3.33 million metric tons to ... 5.84 million metric tons" (2024 SRG investigation; the underlying SRG report was not opened); "Amazon is Underreporting Its True Climate Impact: Amazon leaves out pollution from its third-party Delivery Service Providers (DSPs), even though the GHG Protocol requires counting them." Caution: Amazon's methodology document lists a "last mile delivery fleet" and "Purchased delivery services" in its boundary, so the DSP claim is disputed or at least unclear; treat as a contested claim, not fact. Stand.earth also says Amazon does not participate in CDP or SBTi.
- SBTi: August 2023 the Science Based Targets initiative listed Amazon's commitment as expired (SNIPPET ONLY via Bloomberg/DCD coverage; Amazon said submitting a target was "difficult for us to submit in a meaningful and accurate way"). Not opened.
- Reveal / Center for Investigative Reporting: no relevant Reveal climate piece found. The Reveal story that did surface was on robot-related injuries at Tracy CA (SNIPPET ONLY). I did not find a CIR climate-reporting item.
- The "Scope 3 covers only Amazon-branded products, about 1% of sales" figure came from Digital Commerce 360 (SNIPPET ONLY); the 1% number is not in Amazon's methodology document. Do not publish the 1% without the primary source.

Our data: logistics emissions per package or per dollar from our own network data; Amazon's reported Scope 1 fuel and Scope 3 transport lines are comparable aggregates. TBD by manager.

---

### C2. Local air quality and community arguments

- Consumer Reports (with The Guardian), "When Amazon Expands, These Communities Pay the Price", **December 2021** (not 2023; the user prompt's 2023 date appears wrong). Saved: `consumer_reports_2021-12_when_amazon_expands.html` ; methodology PDF `consumer_reports_methodology_2021-12.pdf`. URL https://www.consumerreports.org/cars/corporate-accountability/when-amazon-expands-these-communities-pay-the-price-a2554249208 ; methodology https://article.images.consumerreports.org/prod/content/dam/CRO-Images-2021/Misc/Consumer-Reports-Methodology-for-Amazon-December-2021
 - Quote: "Amazon opens most of its warehouses in neighborhoods with a disproportionately high number of people of color. Nationally, 69 percent of Amazon warehouses have a greater share of people of color living within a mile radius than the median, or typical, neighborhood in their metro areas." Also "Warehouse operators are not generally accountable for air pollution from the trucks and vans they attract, and existing air quality monitoring networks are too spread out to pick up local emissions that can affect neighbors' health."
 - Evidence base: MWPVL facility list (Amazon did not provide one), EPA EJSCREEN and ACS 2014-2018 demographics, 1-mile radius, with Sacoby Wilson (University of Maryland) as method adviser. Methodology notes the demographic data predate many facilities. CR did not measure air pollution; the pollution claim rests on traffic proximity indicators and general epidemiology. The page should say "siting pattern" not "measured pollution".
 - Other points seen: 57% of warehouses in neighborhoods with more low-income residents than typical (SNIPPET ONLY); Amazon's response "committed to being a good community partner" (SNIPPET ONLY).
- Pitzer College Robert Redford Conservancy and coalition, "A Region in Crisis" report and letter to Governor Newsom, December 2022: Pitzer news page saved `pitzer_region_in_crisis.html/.txt`. https://www.pitzer.edu/news/redford-conservancy-seeks-governors-help . Claims (Pitzer page): Inland Empire "is home to a billion square feet of warehouse space with at least another 200 million in the wings"; coalition of more than 60 groups asked Newsom "for a halt on the construction of new warehouses until the health and environmental impact can be better understood". I did not open the report or the Warehouse CITY tool (Redford Conservancy with Radical Research; SNIPPET ONLY). I could not confirm the People's Collective for Environmental Justice report's PM2.5 claims. A public comment (SNIPPET ONLY) argues the 2022 report "omits previous and ongoing regulatory developments". These are not specific to Amazon; the IE argument is about the logistics sector as a whole.
- San Bernardino airport air hub litigation: Center for Community Action and Environmental Justice et al. v. FAA, and State of California v. FAA, Ninth Circuit No. 20-70272 / 20-70464. Saved: `ca9_20-70272_2022-10-11.pdf` (order amending opinion of 18 Nov 2021, 15 pp). https://cdn.ca9.uscourts.gov/datastore/opinions/2022/10/11/20-70272.pdf . The court (2-1) denied the petitions for review of the FAA's finding of no significant impact for a 660,000 sq ft Amazon air cargo facility; a further amendment was issued 24 Feb 2023 (SNIPPET ONLY). The summary says CCA "could not identify any potential cumulative impacts that the FAA failed to consider". The court ruled on NEPA procedure (adequacy of the Environmental Assessment), not on whether harm occurs. California argued the state CEQA review found significant unavoidable air, GHG, and noise impacts (SNIPPET ONLY). Amazon Air hub opened April 2021 (SNIPPET ONLY).
- SCAQMD Rule 2305 (Warehouse Indirect Source Rule), adopted 7 May 2021; 100,000 sq ft and larger warehouses; a federal court rejected a preemption challenge on 14 Dec 2023; EPA approved into the SIP 11 Sep 2024 (all SNIPPET ONLY from law-firm alerts; not opened).

Our data: TBD by manager. Suggested: share of Amazon sites within the Inland Empire counties, and share located in EJSCREEN high-percentile tracts if our facility file has coordinates (we could replicate CR's 1-mile test; it would need EJSCREEN data, which may now be unavailable from EPA).

---

### C3. E-commerce greener versus worse, and retail displacement

Argument that e-commerce is greener
- Oliver Wyman with Logistics Advisory Experts (St Gallen), "Is E-commerce Good For Europe?", April 2021, 120 pp: `oliverwyman_2021_is_ecommerce_good_for_europe.pdf`. https://www.corrierecomunicazioni.it/wp-content/uploads/2021/04/is-ecommerce-good-for-europe.pdf (mirror; original on oliverwyman.com). **Funded by Amazon**: title page states "Independent study commissioned by Amazon" and (p.2) "has been conducted over a 12-week period and was commissioned by Amazon". Findings quoted: "Driving to a store results in between 3 and 6 times the CO2e as ordering a product online"; "offline retail causes 1.5 to 2.9 times the amount of CO2e as online retail" (nominal case is single-product trip, no return). Scope: Europe, books, fashion, consumer electronics; surveys of consumer behaviour by Oliver Wyman in 2020 (France, Germany, Italy, Spain, UK). Not US.
- Amazon's own grocery claim (Jeff Bezos/Whole Foods model; 43% fewer emissions per item; 2020, SNIPPET ONLY from GeekWire; methodology not provided).
- Carnegie Mellon Green Design Institute, 2009 Buy.com flash-drive case study: e-commerce used about 35% less energy and CO2 than traditional retail; "about 65% of the traditional retail model's emissions came from customers traveling" (campustechnology.com summary, read through a fetch tool, NOT SAVED; https://campustechnology.com/Articles/2009/03/16/Shopping-Online-More-Energy-Efficient-Say-Carnegie-Mellon-Researchers.aspx). Funding: Buy.com is a member of the Institute's corporate consortium; no other funder stated. Product: electronics (flash drive), US. This is the study to cite for "Carnegie Mellon 2009". Do NOT conflate with Weber, Koomey, Matthews (2010, J. Industrial Ecology 14(5): 754-769), which is about digital music downloads vs CDs and was supported by Microsoft and Intel (SNIPPET ONLY); it is not about retail logistics.
- MIT Real Estate Innovation Lab, "Retail Carbon Footprints: Measuring Impacts from Real Estate and Technology", January 2021, 25 pp: `mit_realestate_retail_carbon_footprints_2021.pdf`. https://realestateinnovationlab.mit.edu/wp-content/uploads/2021/01/FINAL_Retail-carbon-footprints-report_011221.pdf . **Not MIT CTL.** Funding statement: "We are grateful for the financial support of the MIT Real Estate Innovation Lab partners: ProLogis, JLL, and EY." Prologis is a logistics-real-estate owner with a commercial stake. The report says its findings are "independent of third parties interests". I did not find an MIT CTL e-commerce funding statement; the MIT CTL 2013 thesis (Weideli) is SNIPPET ONLY. I did not open the report's headline comparison; open before quoting a percentage.
- Shahmohammadi et al., "Comparative Greenhouse Gas Footprinting of Online versus Traditional Shopping for Fast-Moving Consumer Goods: A Stochastic Approach", Environmental Science & Technology 54(6): 3499-3509, 2020: `shahmohammadi_2020_est_pmc.html` https://pmc.ncbi.nlm.nih.gov/articles/PMC7081612/ . Funding: EU Horizon 2020 Marie Sklodowska-Curie grant no. 641459 (RELIEF) (Acknowledgments, saved). Key point (SNIPPET ONLY from abstract summary): "bricks and clicks" (store-fulfilled delivery) likely lowers footprints; "pure players with parcel delivery often have higher GHG footprints" than traditional shopping; last mile and basket size dominate. FMCG (groceries) only, NL/SE/UK/CN/US.

Argument that e-commerce is worse or not clearly better
- Jaller and Pahwa, "Evaluating the environmental impacts of online shopping: A behavioral and transportation approach", Transportation Research Part D 80, 102223 (2020), UC Davis (NCST/Caltrans funded; SNIPPET ONLY on funder). Page not saved (UC Davis site returned 403). Per UC Davis summary (SNIPPET ONLY): all-online scenario lowered CO2 by 42-75% depending on consolidation level but with limited real-world savings because too few shoppers substitute; the paper estimates rush deliveries, basket size and consolidation with a breakeven analysis. I did not confirm the same-day delivery number. Do not quote a number without opening the paper.
- Optoro (returns-technology vendor, with its own commercial interest in returns reduction; now part of Blue Yonder): sustainability page saved `optoro_sustainability.html/.txt` https://www.optoro.com/environmental-impact/ . The figures (SNIPPET ONLY): about 15 million (older) to nearly 27 million (current) metric tons CO2 from returns each year; landfill from returns 5.8 to 9.6 billion pounds a year. Its estimates have changed with method; I could not see the figures in my saved text. Treat as vendor estimates.
- Edwards, McKinnon, Cullinane (Heriot-Watt, 2010): "neither home delivery nor conventional shopping ... has an absolute carbon advantage" (SNIPPET ONLY).
- Stand.earth and Amazon's own report: absolute logistics emissions are rising (2019 to 2025 above); Stand.earth blames faster delivery. This is an argument about growth, not about per-item comparisons.

Retail displacement (e-commerce replaces store trips and store buildings)
- Chava, Oettl, Singh, Zeng, "Creative Destruction? Impact of E-Commerce on the Retail Sector", NBER Working Paper 30077, May 2022 (later Management Science 70(4), 2024): `nber_w30077_chava_et_al_ecommerce_retail.pdf`, `nber_w30077.txt`. https://www.nber.org/papers/w30077
 - Abstract: "the staggered rollout of a major e-commerce firm's fulfillment centers reduces traditional retail workers' income in geographically proximate counties by 2.4%"; "sales (employment) at proximate stores decrease by 4% (2.1%). Exits ... increase, and entry decreases. In aggregate, the retail sector loses 938 jobs per county per quarter, and the transportation-warehousing sector (food services sector) gains 256 (143)".
 - The paper says "a major e-commerce firm" (the saved text only names Amazon in references and background); I did not confirm it names Amazon as the firm. Funding: "Kauffman Foundation Junior Faculty Fellowship" (p. acknowledgments). Evidence: administrative payroll data of 2.6 million retail workers, 3.2 million stores, staggered-rollout design. Working paper, not peer reviewed at the NBER stage.
- No source I found quantifies the net carbon effect of closed stores or vacated retail buildings. The MIT and Oliver Wyman reports address trips and delivery, not building stock. Flag as an evidence gap.

Our data: TBD by manager. The Chava et al. design (county-level, staggered rollout of fulfillment centers) can be compared with our own facility opening dates and county employment data: suggested exploratory check of retail versus warehouse employment around openings, labeled exploratory.

---------------------------------------------------------------------

## PART D. Argument map: ENVIRONMENT

| Argument | Who makes it | Evidence they cite | What our data can say |
|---|---|---|---|
| Amazon is on track and efficient (carbon intensity down 38% since 2019, 100% renewable electricity matching) | Amazon | Own footprint table, EY assurance, market-based Scope 2 | Intensity is computable only with Amazon's revenue; TBD by manager |
| Absolute emissions are up 58% since 2019 and rose 16% in 2025 | Amazon's own table; Stand.earth | Same table | Directly checkable from the saved table; suggested |
| Climate Pledge net-zero 2040 is unsubstantiated, leans on offsets | NewClimate Institute (2022) | Amazon's published targets in 2021 | Cannot say |
| Scope 3 omits the products Amazon sells for others; Scope 2 is market-based only; REC quality | Stand.earth; AECJ; NewClimate (location-based recommendation) | Amazon methodology boundary; Amazon CDP disclosure (via AECJ) | Cannot say |
| Warehouses are sited in communities of color and bring diesel traffic | Consumer Reports (2021); Pitzer Redford Conservancy coalition (2022); California AG and CCAEJ (litigation) | EJSCREEN 1-mile test; Inland Empire warehouse counts; CEQA findings | Suggested: replicate the siting test if facility coordinates available; TBD by manager |
| Counter: courts and regulators found the process lawful or the harm unproven at the time | FAA; Ninth Circuit (2-1) | NEPA environmental assessment | Cannot say |
| E-commerce replaces car trips so it is greener | Amazon-commissioned Oliver Wyman (2021); CMU Green Design Institute (2009, Buy.com consortium member); MIT Real Estate Innovation Lab (Prologis, JLL, EY funded) | Single-item trip comparisons, European data | TBD by manager |
| E-commerce is worse once returns, rush delivery and split shipments are counted; pure-player parcel delivery can exceed store trips | Shahmohammadi et al. (EU funded); Jaller and Pahwa (public funded, SNIPPET ONLY); Optoro (vendor, returns) | Last-mile and basket-size drivers | Suggested: our network data has delivery volumes but not returns; TBD by manager |
| E-commerce displaces local retail jobs and stores | Chava et al. (NBER 2022) | Payroll and store data, staggered rollout | Suggested exploratory check; TBD by manager |

---------------------------------------------------------------------

## Items to verify before publishing (summary of weak links)
1. NY WWPA effective date (bill page implies about 19 Feb 2023; press says 19 Jun 2023).
2. OSHA 18 Jan 2023 citation release and the number of ergonomic citations withdrawn in the Dec 2024 settlement (not stated in the DOL release).
3. Washington BIIA ruling text and what happened on L&I's appeal.
4. AECJ report figures (68% unbundled RECs, 22% local renewable) not read directly.
5. Warehouse CITY and the People's Collective report; Jaller and Pahwa results; Optoro numbers: all snippet-only.
6. NewClimate "low" rating labels and any rating after 2022.
7. Amazon's 2024 total emissions: 68.25 (original) versus 69.55 (restated in 2025 report).
8. Any Amazon rebuttal specifically of SOC's method: not found in a primary document.
9. Consumer Reports analysis is December 2021, not 2023.
