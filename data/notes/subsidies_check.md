# Subsidies check: top 30 primary/secondary rows (2026-10-31)

Scope: the 30 largest `amount_usd` rows with `verification_level` primary or secondary in
`data/processed/subsidies_verified.csv`, as they stood after the 217-row merge. For each row I opened the saved
`local_file` (all 30 exist under `data/raw/subsidies/<STATE>/`; some `local_file` values are bare
filenames or omit the `data/` prefix) and checked amount, recipient, locality, year, basis, and that the facility is
logistics. I also checked for double counting. The check was done inline. No web fetches were made.

Backups made before any edit:
- `data/processed/subsidies_verified.pre_check.csv`
- `data/processed/subsidies_verified_summary.pre_check.csv`
- `data/notes/financial.pre_check.md`

## Changes

| # | Row | Field | Old | New | Reason |
|---|---|---|---|---|---|
| 1 | NJ, Robbinsville Township, 2013, 13,755,000, KTR NJ Urban Renewal LLC PILOT | verification_level | secondary | unverified | Area Development says Robbinsville offered KTR a 20-year PILOT "worth $13.755 million" but does not say whether that is foregone tax or the PILOT payments. The other saved sources use PILOT "value" to mean payments to the township. Princeton Magazine (`princetonmag_robbinsville_amazon.html`) says "The total value of the PILOT is $22 million", about $1M a year. The Trentonian, via `hamilton_in_focus_robbinsville_pilot_2013.html`, gives $600,000 a year. So the figure is not established as a subsidy value, and the row is kept but taken out of the verified totals. A note was appended to the row. |

Knock-on updates:
- `data/processed/subsidies_verified_summary.csv` was rebuilt with a short script. The script was first checked to reproduce the existing summary byte for byte. The only difference is that `NJ,2013,estimated_value,secondary` (1 row, 13,755,000) became `NJ,2013,estimated_value,unverified`. The file still has 140 groups.
- Totals now: 48 primary, 128 secondary and 29 unverified award rows. For primary and secondary rows with an amount, `estimated_value` is 38 rows totalling $964,628,154 (was 39 rows, $978,383,154). `announced_max`, `realized` and `annual` are unchanged.
- In `data/notes/financial.md`, the coverage line was updated to these figures, with NJ now 0/2/2.

## Confirmed rows (29 of 30, no change)

In each case the local file states the amount, and the recipient, locality, year and basis match within the row's own caveats.

1. IL Markham 220M (Cook County Class 8 abatement, estimated over 12 years). Confirmed by the WBEZ text. It and row 4 are the two parts of the $322M package (220 + 102), so they are not a duplicate.
2. NY Town of Niagara 123,922,474. Confirmed by the Niagara IDA MRB cost-benefit for Amazon.com Services LLC: 94,374,974 + 26,000,000 + 3,547,500. The present value is 113,063,031. The facility is a "first mile" fulfillment center.
3. IL University Park 108.2M. Matches the BGA table. The text says up to $107M plus about $1M in impact fees, plus 7% interest. The payment goes to the developer (Project Condor, for Amazon).
4. IL Markham TIF 102M. Confirmed by WBEZ ("refund another $102 million").
5. NJ Hamilton Twp about 100M. The figure is derived (about $223M without the PILOT minus about $123M in PILOT payments, per The Digest). The township sheet confirms $123,057,621. It is already labelled as derived.
6. IL Matteson 82M. Confirmed by WBEZ and BGA. It was pending in 2020.
7. IL Joliet 71.5M EDGE. Confirmed: Illinois Policy says "DCEO lists the estimated value ... $71.5 million". The primary Joliet EDGE row has no amount, so there is no double count.
8. IL Waukegan 40M. Confirmed in WBEZ ("city pledged $40 million for redevelopment costs") and BGA ("TIF over 12 years").
9. KY Hebron 40M KBI. The CED 2024 list has "Amazon.com Services, LLC, KBI, Boone, $40,000,000, cost $2,064,435,709, 600 jobs, final 2022/05/26". The facility (the air hub) is inferred from the county; see the concerns below.
10. MD Baltimore 35.3M Enterprise Zone credits. Confirmed by Technical.ly (quoting the Sun). The other parts of the package (5.5M, 1.7M, 1.25M, 0.125M) are separate rows, and there is no package-total row.
11. WA Airway Heights 30.4M. Confirmed: the Spokesman says WSDOT, the county, the city and the PDA "committed $30.4 million". This is a public road, not a payment to Amazon, and the notes say so.
12. CA Fresno 30M. Confirmed by the staff report and the agreement with Golden State FC LLC (an Amazon subsidiary): "maximum total payment of $30,000,000".
13. TN statewide 30M (three counties). Confirmed: the TFP says "$30 million in property tax breaks from three counties".
14. IL Monee 27.8M EDGE. Confirmed by Illinois Policy.
15. MA North Andover 27M. Confirmed: the mass.gov EDIP 2020 page says "10-year TIF valued at approximately $27 million" for Amazon.com Services, LLC.
16. NY Liverpool/Clay 22,232,146 realized. Re-summed from the ABO JSON (project 3101-19-10A, FY2020-24 net_exemptions), and it matches exactly. The recipient is the developer CF Anaconda SYR LLC, at 7211 Morgan Rd.
17. NY Rochester Manitou 20,323,268 realized. Re-summed (2602 21 008 A, FY2021-24) and it matches exactly. The recipient is the developer USRE Manitou LLC.
18. NY Staten Island 18M. Confirmed: the ESD Excelsior JSON lists Amazon Fulfillment Services, Inc. (3), Distribution, NYC, with maximum_tax_credits 18,000,000. The locality and year come from press reports, not the dataset.
19. OH Obetz and Etna 17.54M. Confirmed by Bricker, quoting Business First ("valued at $17.54 million"). There are no separate Obetz or Etna amount rows.
20. GA South Fulton 16,025,034. Confirmed: the DAFC fact sheet of 2026-02-24 for Amazon.com Services LLC at 7055 Campbellton Rd gives "Estimated tax savings over 10 years ... $16,025,034". The facility is a robotics fulfillment center.
21. IN Fort Wayne 16M. Confirmed: IIB says "The city council already awarded Amazon a $16 million tax abatement for the facility's construction". The $7.3M machinery abatement was rejected and is carried as 0.
22. NY Woodmere 16M. Confirmed by Innovate LI ("$16 million tax-abatement deal", Hempstead IDA, 2020). See the recipient concern below.
23. TN Memphis 15,194,936. Confirmed: the EDGE Q2 FY2018 report says "$15,194,936 benefit to Amazon". The recipient is Amazon.com.dedc, LLC, and the facility is a receive center at 3292 Holmes Rd.
24. PA 2016 15M JCTC. Confirmed: the reprinted Governor's release says "$15 million in Job Creation Tax Credits". The other parts of the package (5M PA First, 2.25M WEDnetPA) are separate rows, and there is no total row.
25. TN statewide 14.9M state grants. Confirmed by the TFP.
26. (Changed: NJ Robbinsville. See above.)
27. IL Aurora 12.89M EDGE. Confirmed by Illinois Policy.
28. IL Channahon 12.8M road upgrades. Confirmed by WBEZ and BGA.
29. OH Akron and Rossford 12.1M. Confirmed: WOUB/AP says "could be worth up to $12.1 million", for two fulfillment centers approved by the TCA in July 2019.
30. IL Palatine 11.6M. Confirmed by the BGA table ("Cook County property tax abatement pending").

None of the 30 is a data center, office or HQ2 site. All are fulfillment, sort, receive, distribution or air-hub facilities, or roads serving them.

## Double counting

No row in the top 30 is the same award entered twice at the same level or at two levels. Packages are entered as parts, with no total row on top, for Markham, Maryland's Broening Highway site, PA 2016, IL EDGE (the primary agreement rows have no amount), and NY Woodmere and Syosset (the press figure is `announced_max` and the IDA figure is `realized`, which are different bases). These are open:
- **TN.** The aggregate rows (30M local and 14.9M state, 2017) overlap the Lebanon/Wilson 3.3M secondary row (no year) and the Chattanooga 871,102 unverified row. The notes already say "do not add". They are separate summary groups only because the years differ.
- **KY.** The KBI air-hub award of up to $5.4M (2017 phase 1, secondary, counted in the KY 2017 announced_max total of 10.4M) may be part of the $40M award (2022 primary). The sources do not settle this, so I made no change.

## Remaining concerns (not changed)

- **KY 40M.** The CED list does not name the facility, gives a project cost of $2.06B and 600 jobs (2017 press: $1.49B and 2,700 jobs), and is dated 2022. Treating it as the same award as the 2017 $40M preliminary approval is a plausible inference, not something the document states.
- **IL Joliet year.** The row says 2015 (the agreement date taken from the primary row). Illinois Policy says the first deal was "signed July 22, 2016". The BGA open date is 2016.
- **IL Waukegan 40M.** The only sources are BGA and WBEZ. The row's own note says it may cover the wider Bridge Point North park.
- **NY Woodmere 16M.** The deal went to the speculative developer Wildflower in April 2020. Amazon signed as tenant later (reported May 2021), so "developer acting for Amazon" is loose here. The recipient on the Liverpool, Manitou and Niagara rows is also a developer or SPV, but those IDA records tie the project to Amazon.
- **NY Niagara 123.9M.** This is a pre-approval MRB estimate for a project with 0 FTEs reported in FY2024, and the closing was extended. It may never be realized.
- **Rows that are not payments to Amazon:** WA Geiger 30.4M (a shared road) and IL Channahon 12.8M (roads).
- **IN Fort Wayne 16M.** The row is labelled `announced_max`, but the source does not say whether $16M is a cap or an estimate of tax value.
- **Use of `alt_sources` and `local_file`.** The NJ Hamilton and Fresno rows give bare filenames in `local_file`. Paths are not normalized across states, but every one of them resolved.
- **Outside the top 30.** OH New Albany CRA 2020 (secondary, no amount) is described as a fulfillment center. The row excludes the AWS data-center abatements, but I did not check that site against a source.

# Gap-fill check: 15 largest new primary/secondary rows (2026-10-31)

Scope: the 15 largest `amount_usd` award rows at `verification_level` primary or secondary that the gap-fill merge
added (CO MN MO OR WI SC CT IA KS MS). The merge report's own top-15 list included two unverified rows (MO St. Peters
$75M IRB, MN Shakopee $5.8M road TIF). These were left out, so IA Davenport 3.9M and OR Salem 3.6M were checked in their
place. For each row I opened every saved `local_file` under `data/raw/subsidies/<STATE>/` and checked amount,
recipient, locality, year, basis, logistics use and double counting. The check was done inline, with no web fetches
and no worker agents.

Backups made before any edit:
- `data/processed/subsidies_verified.pre_gapcheck.csv`
- `data/processed/subsidies_verified_summary.pre_gapcheck.csv`
- `data/notes/financial.pre_gapcheck.md`

Script: `scripts/apply_subsidies_gapcheck.py`. It asserts that `subsidies_summary_lib.summarize` reproduces the
current summary before it edits anything, then applies the fix and rebuilds the summary.

## Changes

| # | Row | Field | Old | New | Reason |
|---|---|---|---|---|---|
| 1 | MN, Shakopee, 2015, 6,400,000, TIF request (MN.csv#2) | verification_level | secondary | unverified | MPR says a draft TIF plan "asks for as much as $6.4 million". Finance & Commerce (2015-05-12) says the Planning Commission approved the plan, that $6.4M is the total new tax increment, that Scott County can take $2.2-4M of road costs off the top, and that Amazon's share had been put at about $3.4M. No saved page shows council approval or an award. The row's own notes say the request was probably withdrawn. It is a request rather than an established award, so it was taken out of the verified totals and a note was appended to the row. |

Knock-on updates:
- Summary: `MN,2015,announced_max,secondary` (1 row, 6.4M) was merged into `MN,2015,announced_max,unverified`, which now has 2 rows and 12.2M (with the overlapping 5.8M road-TIF lead). No other group changed.
- Totals: 56 primary, 151 secondary and 31 unverified award rows. For primary and secondary rows with an amount, `announced_max` is 90 rows and $652,450,708 (was 91 rows and $658.9M). `estimated_value`, `realized` and `annual` are unchanged.
- In `financial.md`, the coverage line was updated to these figures, with MN now 0/0/2.

## Confirmed rows (14 of 15, no change)

1. WI Kenosha TIF, 18M (2013). BizTimes 2013-10-09 says "authorized $18 million in tax incremental financing". The recipient is the developer KTR, which leases to Amazon. Fox6 gives $17M and the later "Amazon Effect" feature gives about $21M, and the row notes both.
2. WI Oak Creek TIF, 16.9M (2018). BizTimes says the "total value of the TIF incentive ... is $16.9 million". This is $13.4M of developer-funded road and utility work (mostly rebuilding S 13th St and Ryan Rd), refunded to Hillwood, plus up to $3.5M of site costs. See the concerns below.
3. CT North Haven URA credits, 15M (2017). TT News says "eligible to earn up to $15 million", plus $5M more if the job targets are exceeded. The basis is announced_max.
4. WI Kenosha WEDC, 10.3M (2013). BizTimes "Amazon Effect" says "up to $10.3 million in state tax credits". BizTimes 2019 says it was awarded in 2013.
5. OR Troutdale EZ, 9.6M (2017). KOIN says a "five-year tax break worth approximately $9.6 million". Troutdale claws back 25% (about $2.4M), so Amazon nets about $7.2M. The row notes say this. See the concerns below.
6. CT North Haven credits issued, 9M (2021, primary). In `full_ihra-gwrn.json`, the FY2021 record for Amazon.com Services, Inc., 409 Washington Ave, URA (CGS 32-9t) has total_tax_credits_issued $9,000,000 and a contract date of 2021-02-19. It matches the row exactly.
7. CT Windsor, 8.78M (2020). HBJ 2020-06-16 says "projected to save a total of $8.78 million" ($7.48M property tax plus $1.3M in permit fees) at 1201 Kennedy Rd. The developer is Scannell.
8. MO St. Peters state sales-tax exemptions, 7.95M (2018). West Newsmagazine quotes DED: "could receive $7.95 million in sales tax exemptions". It is part of the about $11M state package, which has no total row.
9. WI Oak Creek WEDC, 7.5M (2019). The Urban Milwaukee reprint of the WEDC release, the Daily Reporter and BizTimes all date it 2019-03-25 and say "up to $7.5 million".
10. (Changed: MN Shakopee. See above.)
11. MS Byhalia MDA, 6M (2018). The Panattoni item quotes the MDA spokeswoman: "$6 million in public incentives — a $2 million grant for building construction and $4 million for road improvements". The facility is a fulfillment center.
12. CT North Haven sales and use tax exemption, 5M (2017). TT News says "may be eligible for ... up to $5 million". It is a separate component from the URA credits.
13. CT Windsor, 3.9M (2013). Patch 2013-10-21 says the deal "will save Amazon about $3.9 million". It is a 5-year abatement averaging 60%.
14. IA Davenport, 3.9M (2021). KWQC says "applied for a grant to help cover the 3.9 million dollar cost" of public road and intersection work, with the grant covering 60%. The row already says it is not a payment to Amazon.
15. OR Salem EZ, 3.6M (2017). TT News quotes SEDCorp's Chad Freeman: "worth an estimated $3.6 million over the three years". KLCC 2019 gives $3.7M, and the notes say so.

All 15 are fulfillment or distribution centers, or roads serving them. None is a data center or office.

## Double counting

None of these rows is the same award entered twice in the same summary group.
- **CT North Haven.** The 15M announced_max (2017), the 5M exemption (2017) and the 9M realized (2021) differ in basis or year, so they never sum. The notes flag the overlap between the 15M and the 9M.
- **MO.** The three state rows (7.95M, 2.98M and 0.1M) add up to the AP "more than $11M". They are components, and there is no total row.
- **WI.** For Kenosha and Oak Creek, the TIF and the WEDC credits are different programs. Each figure from a different source (17M, 18M or 21M) appears only once.
- **MN Shakopee.** The 6.4M request and the 5.8M road TIF are probably the same district. Both rows are now unverified, and they share a summary group whose note says "rows overlap".

## Remaining concerns (not changed)

- **OR Troutdale, gross or net.** The 9.6M is the gross abatement. Amazon pays back about $2.4M, so it nets about $7.2M. KGW's combined figure of $13.2M (9.6 + 3.6) shows the gross is the figure most often cited. I left it as is because the row notes give the net, but 7.2M would be the figure on the same footing as the NJ Hamilton net row.
- **Rows that are mostly public roads, not payments to Amazon:** WI Oak Creek 16.9M ($13.4M of it is road and utility work reimbursed to the developer), MS Byhalia 6M ($4M is a road grant), and IA Davenport 3.9M (the grant was only applied for, not shown as awarded).
- **The CT 9M "realized" basis.** The dataset says "credits issued", not credits used or sold. That fits `realized` only loosely.
- **Information not captured.** BizTimes 2019 says WEDC had "verified more than $5.2 million in tax credits" for the Kenosha award by 2019. That is a partial realized figure, and no row records it.
- **Developer recipients.** For Kenosha (KTR), Oak Creek (Hillwood) and Windsor 2020 (Scannell), the developer is the recipient or co-recipient. In each source the developer is building specifically for Amazon.
- **Rows just outside this check.** The MO St. Peters $2.6M county road money and $2.98M building-materials abatement are both in the same West Newsmagazine page, which I read. Both figures appear there as stated.

# Browser-pass check: 15 largest new primary/secondary rows (2026-10-31)

Scope: the 15 largest award rows at `verification_level` primary or secondary that the browser-pass merge added
(`scripts/merge_subsidies_browser.py`; the merge report's own top-15 list). For each row I opened every saved
`local_file` under `data/raw/subsidies/<STATE>/` and checked amount, recipient, locality, year, basis, logistics use
and double counting. PDFs were read with `pdftotext`; the Oregon sums were recomputed from the state CSVs (the 2020
Part A file has a different column order, which I allowed for). The check was done inline, with no web fetches, no
worker agents and no OCR. The one image-only PDF (SC Lexington inducement agreement) was not needed, because the SC
amount comes from the Post and Courier page.

Backups made before any edit:
- `data/processed/subsidies_verified.pre_browsercheck.csv`
- `data/processed/subsidies_verified_summary.pre_browsercheck.csv`
- `data/notes/financial.pre_browsercheck.md`

Script: `scripts/apply_subsidies_browsercheck.py`. It asserts that `subsidies_summary_lib.summarize` reproduces the
current summary before it edits anything, then applies the fixes, appends a note to each changed row and rebuilds the
summary.

## Changes

| # | Row | Field | Old | New | Reason |
|---|---|---|---|---|---|
| 1 | SD, Sioux Falls, 2021, 94,371,313, TIF #23 (SD.csv#2) | verification_level | primary | unverified | The project plan never names Amazon. The figure is the TIF requested by the Sioux Falls Development Foundation for the whole 539-acre Foundation Park North. It includes a $30,000,000 off-site competitiveness fund and $30,184,577 of financing costs, against $2.5B of projected tenant investment. The recipient is a park developer, not Amazon or a developer acting for Amazon. |
| 2 | KS, Salina, 2025, 6,000,000, SAA temporary notes (KS.csv#16) | verification_level | primary | unverified | The SAA memo (pp. 3-4) shows the $6M financed streets and utilities for the 80-acre Project 80, where Amazon bought 20 acres. About $1.56M was not spent and is being moved to the airport terminal and MRO hangars. Permanent financing is retired by special assessments on all benefited landowners, Amazon included. This is financing repaid by the landowners, not an established subsidy value. |
| 3 | NM, Albuquerque, 2021, 6,500,000 realized (NM.csv#2) | verification_level | secondary | unverified | The only saved text (a Minuteman Press reprint of KRQE) says the money was county spending on the industrial park and that Amazon did not receive it. It also says "most of that money has been recouped by Bernalillo County in fees Amazon has paid" and that no incentive money was used. The KRQE file is an empty 403 page. A cost mostly recovered from Amazon is not a realized $6.5M subsidy. |
| 4 | WI, Kenosha, 2013, 7,000,000 WEDC (WI.csv#6) | verification_level | secondary | unverified | This is the same WEDC 2013 award as the 10.3M row (WI.csv#3). The $7M was quoted in November 2013 for the first building ($141M, 1,100 jobs). BizTimes later gives up to $10.3M for the two-building project ($155M, 1,250 jobs). BizTimes 2019 says "$10.3 million in credits awarded to Amazon for its Kenosha facilities in 2013". Both rows were in the WI 2013 announced_max secondary group, so the same credits were counted twice (group total 35.3M). |

Knock-on updates:
- Summary: four groups changed. `KS,2025,announced_max`, `NM,2021,realized` and `SD,2021,announced_max` moved from primary or secondary to unverified. `WI,2013,announced_max,secondary` went from 3 rows and 35.3M to 2 rows and 28.3M, and a new `WI,2013,announced_max,unverified` group has 1 row and 7M. The file now has 206 groups plus the header.
- Totals: 290 award rows, of which 90 are primary, 169 secondary and 31 unverified. For primary and secondary rows with an amount: `announced_max` is 110 rows and $718.4M (was 113 and $825.8M), and `realized` is 16 rows and $111.5M (was 17 and $118.0M). `estimated_value` (48 rows, $1,008.0M) and `annual` are unchanged.
- In `financial.md`, the coverage line and the KS, NM, SD and WI rows of the state table were updated, and one sentence names the four changes.

## Confirmed rows (11 of 15, no change)

1. OR Troutdale/Fairview (Columbia Cascade EZ), 11,471,624 realized, 2019. Re-summed from Part A 2020-2026 and it matches exactly. The taxpayer is Amazon.com dedc LLC. It is gross of the Troutdale 25% community service fee.
2. IA Bondurant RISE, 8,565,283, 2020. The Iowa DOT FY2020 RISE table gives "$14,275,472 / $8,565,283, 40%", finalized 2020-01-14, and minutes order PPM-2020-21 is dated 2019-10-08. The company is "TBD" in the DOT record. The Amazon (Ryan Cos., Project Bluejay) link comes from the Des Moines Register of 2019-11-12. The grant goes to the city for roads.
3. KS Kansas City KDOT, 7,000,000, 2016. Three Wyandotte Daily News pages quote UG staff saying a "$7 million grant from the Kansas Department of Transportation" replaced the Riverview CID. The site is RELP Turner LLC, which the UG confirmed as Amazon. The grant goes to the UG for roads.
4. IA Bondurant Project Omega, 6,050,000, 2021. The City FY2024 operating report shows Series 2/21A of $6,050,000, "City Improvements", and its text says the 2021A bonds "were issued to fund the public infrastructure" under the Project Omega development agreement "with Amazon". This is bond principal, so it is an upper bound, as the row says.
5. MN Shakopee road TIF, 5,698,326 estimated_value, 2015. The cooperative agreement names the developer as Amazon.com.NVDC / Amazon.com.dedc and says it "agreed to forego any tax increment". The budgets are $2,319,076 for the city and $3,379,250 for the county. Finance & Commerce gives about $5.8M and Pioneer Press about $5.7M, with a 4-1 vote. The money goes to public roads.
6. LA Shreveport, 5,000,000, 2021. The LED release of 2021-05-07 says "eligible for a $5 million performance-based grant payable in two installments during 2022 and 2023". It is a robotics fulfillment center.
7. LA Baton Rouge, 5,000,000, 2021. The LED release of 2021-06-16 uses the same wording. The site is the former Cortana Mall, and it is a separate site from Shreveport.
8. SC Lexington land, 5,000,000 estimated_value, 2010. The Post and Courier of 2010-12-06 says "90 acres that county officials value at slightly more than $5 million". ABC Columbia says "2.5 million dollars worth of land". The row notes both figures.
9. OR Salem EZ, 4,709,846 realized, 2020. Re-summed from Part A 2021-2024 (1,540,513 + 1,544,196 + 1,619,414 + 5,723) and it matches. The taxpayer is Amazon.com dedc LLC s.
10. OR Portland EZ, 4,606,013 realized, 2020. Re-summed from Part A 2021-2026 and it matches. The taxpayer is Amazon.com dedc LLC p. The site is unresolved, as the row says.
11. KS Coffeyville, 4,500,000 announced_max, 1999. The Wichita Eagle of 2014-12-03 quotes the interim city manager: "$1.2 million in infrastructure improvements and $3.3 million in cash incentives". The Eagle of 2014-10-01 gives "about $4.5 million". It was an Amazon distribution center, and the state $500,000 loan is a separate row.

All 15 rows are fulfillment, sort, distribution or delivery sites, or roads and parks serving them. None is a data center or an office. The Oregon taxpayer is the distribution-center entity (dedc).

## Double counting

- **WI Kenosha.** The 7M and 10.3M WEDC rows were summed. This is fixed above.
- **SC Lexington.** The $5M land row (estimated_value, secondary) and the $2.5M state grant row (announced_max, primary) overlap, because the grant reimburses the county for the land. They use different bases, so they never sum.
- **MN Shakopee.** The 5.7M road TIF (estimated_value) and the 1.2M declined Amazon share (announced_max) use different bases, so they never sum. Finance & Commerce says the 1.2M went to the city instead, so it is probably inside the city's $2.32M road budget.
- **OR.** The realized rows (Troutdale 2019, Salem 2020, Portland 2020) are in different zones. The 2017 estimate rows for Troutdale and Salem use a different basis.
- **IA Bondurant.** RISE (2020) and Omega (2021) are in different summary groups. See the concerns below.
- **LA.** Shreveport and Baton Rouge are both in `LA,2021,announced_max,primary` (10M), but they are different sites.
- **KS.** Coffeyville's 4.5M local package and the 0.5M state loan are separate programs in the same 1999 group. Nothing else overlaps.

## Remaining concerns (not changed)

- **IA Omega bonds may be the Bluejay road balance.** The Register (2019) said the city would bond the rest of the $15.9M Bluejay road project after the DOT grant, which comes to about $6.4M. Series 2021A ($6.05M, Feb 2021) is close to that, but the city's own disclosure ties 2021A to Omega. If it is the Bluejay balance, it overlaps the RISE row's project and not the Omega sort station.
- **Public road money, not payments to Amazon, still counted:** IA RISE 8.57M, KS Kansas City KDOT 7M and MN Shakopee 5.7M. These are consistent with the earlier treatment of WA Geiger and IL Channahon.
- **MN 1.2M declined share.** The row is still a secondary `announced_max` award of 1.2M, although Amazon declined it before the vote and $0 was realized. It is outside this check's 15, and I left it.
- **OR gross versus net.** Troutdale 11.47M is gross. The 25% community service fee makes the net about 8.6M. The row notes say this.
- **LA grants are eligibility, not payment records.**
- **SD 1.9M federal EDA grant** (secondary, outside the 15) is still in the totals, although `financial.md` excludes federal grants.
- **SC agreement.** The inducement agreement PDF has no text layer (91 characters from pdftotext), and no OCR text is saved beside it. The row notes cite a local OCR of pages 1-14 that I could not find on disk. If the section 3.1.1 wording matters, re-OCR it with the local model setup (see the dean project) rather than an API model.
