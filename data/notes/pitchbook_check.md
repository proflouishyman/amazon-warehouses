# Logistics deals: adverse source check (2026-10-31)

Scope: every row of `data/processed/logistics_deals_public.csv` (52 rows before the check). I opened each row's
`source_url` on 2026-10-31 and read it for the deal year, the parties (buyer or investor, target or seller) and, where shown,
the amount. All 52 pages loaded. The Business Wire URL for ATSG redirected to the Business Wire newsroom, so it was dead.

Result: 52 rows checked. 39 were confirmed as published. 3 were removed and 10 were changed. **49 rows remain** (32 Amazon, 17 Walmart
and Target), and 12 of them show an amount. All fixes are in `scripts/make_public_deals.py` (`DROP` and `FIX`), so rerunning the
script reproduces the table. Backups: `*.pre_check.*` (gitignored).

## Removed (3)

| Row | Reason |
|---|---|
| Amazon (via Industrial Innovation Fund), Physical Intelligence, 2024, $400M | The CNBC article names Jeff Bezos personally, along with OpenAI, Thrive, Lux and Bond. It does not name Amazon or its fund. None of the other search results name Amazon either. |
| Amazon, BETA Technologies, 2026, investment | The article (Feb 2026) reports a Schedule 13G disclosure of an existing 5.3% holding, not a new transaction. That holding most likely comes from the 2021 Climate Pledge Fund investment, which stays as a row. |
| Target, property purchase, 2025 | The source (Charlotte Business Journal, Feb 2026) describes 15 acres near Rock Hill for a retail development, not a logistics site, and gives no 2025 date. |

## Source replaced (4)

| Row | Old source | New source (read 2026-10-31) |
|---|---|---|
| Amazon, Air Transport Services Group, 2016 | businesswire.com: the link is dead and redirects to the newsroom | ATSG release on airtransport.cc, March 9, 2016: "Amazon granted rights to purchase ATSG equity" |
| Walmart, Symbotic, 2022 | Symbotic release, May 2022, about an expanded commercial agreement that does not mention an investment | Supply Chain Dive, June 2022: "Walmart has taken a stake in Symbotic Inc." (11.1% of common stock) |
| Walmart, "Walmart Advanced Systems & Robotics", 2022 | Symbotic release, Jan 2025, about Symbotic buying the unit *from* Walmart, which does not support a 2022 Walmart acquisition | Walmart corporate news, Oct 6, 2022: "Walmart has agreed to acquire Alert Innovation". The target is renamed **Alert Innovation**. |
| Target, Inspectorio, 2018, $10M | Twin Cities Business Journal: the readable text names Techstars and Ecolab but not Target | Star Tribune, July 12, 2018: "Among the investors are Target", $10 million round |

## Corrected (6)

| Row | Change | Evidence |
|---|---|---|
| Rivian Automotive, 2019, $700M | Actor changed from "Amazon (via Climate Pledge Fund)" to "Amazon" | The Climate Pledge Fund launched in 2020 (Amazon's own BETA release says so). The WSJ says Amazon.com led the round. |
| Rivian Automotive, 2020, $2.5B | Actor changed from "Amazon (via Climate Pledge Fund)" to "Amazon" | SiliconANGLE names "Amazon.com Inc." as a participant. The fund is not mentioned. |
| Amazon, Rightbot acquisition | Year changed from 2025 to 2026 | Automated Warehouse article dated JAN 6, 2026. It also refers to ProMat 2025 as past. |
| Walmart, Ninjacart ($145M round) | Year changed from 2022 to 2021 | Times of India (PTI) dated Dec 13, 2021: "have invested USD 145 million" |
| Amazon, $95M West Jefferson warehouse, 2026 | "Property purchase from West Jefferson Mega Warehouse" changed to "Property purchase (see source)" | The database name is the property, not the seller. The article names the developer (Pizzuti) but no seller. |
| Walmart, Buckeye AZ land, 2026 | "Property purchase from Cardinal Capital" changed to "Property purchase (see source)" | The readable article text does not name the seller. |

I also changed the wording of the amount note from "not necessarily Amazon's share" to "not necessarily the buyer's or investor's
share", because it also appears on Walmart and Target rows. I updated the Methods paragraph in `methods.html` to give the new counts
and to describe this check.

## Confirmed as published (39)

The cited page supports the year, the parties and any amount shown:
BETA 2021 (Climate Pledge Fund, May 18 2021); Colis Privé 2014 (25% stake); Yodel 2014 (an option on a 4.2% stake, see the note below);
Dispatch (TechCrunch 2019 says it was acquired in 2017); Total Express 2022; Caribou Industries 2020 (Santa Ana, $63.2M stated, amount
left blank); Central Steel & Wire 2021 $35M; Owens Corning 2023 $237.8M; Fort Myers 2024 (CoStar, Nov 25 2024); Covington Group 2024
$162M; Hillwood Communities 2024 (Daytona Beach); Olathe 2025; Stephens Land holdings 2025 (Fort Smith, June 13); Hermon 2026 $1.9M;
West Town Chicago 2026; Ashley Furniture 2026 (Frederickson); Forever 21 2026 (Lincoln Heights); Kiva 2012; Balyo 2019 (warrants
under a 7-year deal); Canvas 2019; Vimaan 2022 (PR Newswire, April 26 2022); Rightbot 2023 (Industrial Innovation Fund); Veo
2023 $29M; Fauna 2026; RIVR 2026; Aurora 2019 (Wired, Feb 7 2019); Zoox 2020; Parcel 2017; Shipt 2017 $550M; Deliv 2020; Ninjacart
2020 (Oct 12 2020); DroneUp 2021; Delivery Drivers Inc. 2022; Walmart Glendale 2025 $152.2M; The Keith Corporation 2025 (Kings
Mountain); Core5 Industrial Partners 2026 (Lebanon OH, Feb 6 2026); Fox Robotics 2024 (minority stake); Grand Junction 2017;
Inspectorio 2017 $3.7M.

## Notes, not changed

- Yodel 2014 is shown as an "investment", but the Guardian describes an *option* to buy 4.2%. Balyo 2019 is also warrants tied to
  purchases. Both are kept because the table has no "option or warrant" type.
- Several real amounts are still blank because the strict snippet rule did not match them, though the article states them:
  Caribou $63.2M, Hillwood $393.9M, Fort Myers $66.5M, Ashley $219.5M, Forever 21 $146.2M, Keith Corp $121.5M, West Town $195M and
  Ninjacart $145M. This is a choice of presentation. None of them is an error.
- The pages for Vimaan, Rivian 2019 and 2020, and Dispatch were the ones flagged for a spot check. They are now checked (see above).
