# Allowed-source register

Accessed 6 November 2026. Only the assignment's permitted tax authorities and
NYC 311 dataset supply domain facts/data. No commercial tax blogs or external
geographic/name datasets are used. Gemini REST is an implementation service,
not an additional tax authority.

| ID | Authority | Use |
|---|---|---|
| ITD-2024 | https://www.incometax.gov.in/iec/foportal/help/individual/return-applicable-3 | AY 2025-26 slabs, surcharge, cess, deductions, senior treatment |
| ITD-2025 | https://www.incometax.gov.in/iec/foportal/help/individual/return-applicable-1 | AY 2026-27 rates and deductions |
| ACT-2024 | https://incometaxindia.gov.in/news/finance-no.2-act-2024.pdf | Finance (No.2) Act 2024; primary document endpoint returned access error in this environment |
| ACT-2025 | https://incometaxindia.gov.in/Documents/Act/Finance-Act-2025.pdf | Finance Act 2025, amendments to 87A and 115BAC; full PDF endpoint returned access error |
| ACT-2025-S20 | https://wmstatic-prd.incometaxindia.gov.in/web/guest/w/section-20-111 | Official section 20 extract (87A); live page includes later Finance Act 2026 annotation: do not apply that later change |
| ACT-2025-S25 | https://wm.incometaxindia.gov.in/w/section-25-125 | Official Finance Act 2025 section 25 extract, new 115BAC slabs |
| HRA | https://www.incometaxindia.gov.in/w/section-10-8 | HRA qualifying salary and rented period; 10(13A), Rule 2A |
| ROUND-PAYABLE | https://www.incometaxindia.gov.in/w/section-288b-59 | Final payable: discard paise, nearest ten, ties upward |
| HEALTH | https://www.incometaxindia.gov.in/w/section-80d-53 | Separate group limits and combined preventive-checkup sublimit |
| ROUND-INCOME | https://www.incometaxindia.gov.in/w/section-288a-58 | Discard paise, nearest ten, ties upward |
| ITD-DEDUCTIONS | https://wm.incometaxindia.gov.in/w/deductions/allowances-allowed-to-a-salaried-employee | 16(ia), HRA and deduction interpretation; page is current, historical rules pinned separately |
| NYC311 | https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9/ | Named public dataset; 2023 records only |
| NYC311-API | https://data.cityofnewyork.us/resource/erm2-nwe9.json | Reproducible filtered download; exact queries and SHA-256 in data manifest |
| NYC311-UPDATE | https://www.nyc.gov/opendata/news/all-news/311-Service-Requests-Updates | Display names changed; API fields complaint_type/descriptor unchanged |

## Important distinctions

`project_a/rules/*.md` are normalized operational extracts written during this
implementation, with clause references. They are not archived originals or
verbatim statutes. The official guidance pages are not exhaustive. The full Act
PDF access failures and outstanding official-calculator checks are a real legal
verification gap, not a completed source audit.

FY 2024-25 is AY 2025-26. FY 2025-26 is AY 2026-27. The year of an Act, the FY
and the AY must not be substituted for one another. Current pages may include
post-2025 amendments: the engine deliberately pins the two requested years.

The new-regime statutory 87A ceiling in FY 2024-25 is Rs 25,000, but actual tax
at taxable income Rs 700,000 under that year's revised slabs is Rs 20,000.
Rebate is capped by actual tax: using Rs 25,000 as an unconditional subtraction
would be wrong.

## Official-calculator validation procedure (pending)

Use the Income Tax Department's official calculator from its portal, not a blog.
`project_a/fixtures/official_checks.csv` lists 30 distinct taxpayer cases, with
one line for each regime (60 checks). Enter the fixture's assessment year,
residency, age, salary/deductions and regime. Record the official final payable,
UTC verification date and a repository-relative screenshot/export evidence path.
Compare final rounded payable, not only base income-tax or the TDS balance.
Mark VERIFIED only after an actual check. `reproduce.py --strict` requires 30
cases with both regimes verified and evidence files present. CSV evidence is
not automatically proof of source authenticity and should be reviewed manually.

No official-calculator observation has been invented. Source URLs are retained
for review even where direct full-document retrieval failed.
