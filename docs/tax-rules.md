# Tax classification rules

Generated from `sovereign_books/tax_classifier.py`. Every expense the agents see is assigned one of these classes. The percentage is the federal deductible share; the reference is the Internal Revenue Code section or regulation the rule rests on; the line is where it lands on the return. Figures reflect tax years 2026 onward unless the notes say otherwise. These are planning estimates for a tax professional to confirm.

## The meal question

When a charge looks like a restaurant and nobody has said who attended, the approval card asks **Who was this meal with?** The answer decides the class:

| Answer | Class | Deductible |
| --- | --- | --- |
| Client or prospect was there | Business meal (client or employee present) | 50% |
| One or a few employees | Business meal (client or employee present) | 50% |
| Whole company event | Company-wide event (party, offsite, picnic) | 100% |
| I was traveling for work | Meal while traveling for business | 50% |
| Food for the office | Meals furnished for the employer's convenience | 0% |
| Just me, in town | Solo meal, not traveling | 0% |
| Personal | Personal | 0% |

Before tax year 2026, food furnished for the employer's convenience was still 50% deductible; from 2026 it is 0% under IRC 274(o).

Equipment at or under $2,500 per item is expensed under the de minimis safe harbor; above that it is capitalized and eligible for Section 179.

## All classes

| Class | Deductible | Reference | Return line | Notes |
| --- | --- | --- | --- | --- |
| Business meal (client or employee present) | 50% | IRC 274(n)(1), 274(k) | Schedule C line 24b / Form 1120 line 26 | Food or drink with a client, prospect, or employee where business is discussed; not lavish; taxpayer present. |
| Company-wide event (party, offsite, picnic) | 100% | IRC 274(e)(4), 274(n)(2)(A) | Schedule C line 24b / Form 1120 line 26 | Recreational or social activity primarily for employees who are not highly compensated: holiday party, team offsite, picnic. Fully deductible. |
| Meal while traveling for business | 50% | IRC 274(n)(1), 162(a)(2) | Schedule C line 24b | Meals away from the tax home overnight. 50% of actual cost or the federal per diem. |
| Meals furnished for the employer's convenience | 0% | IRC 274(o) (tax years after 2025) | Not deductible | Office lunches, snacks, and on-premises cafeterias became nondeductible for tax years beginning after December 31, 2025. |
| Solo meal, not traveling | 0% | IRC 262 | Not deductible | A meal by yourself in town is a personal expense. |
| Entertainment (tickets, golf, club dues) | 0% | IRC 274(a) | Not deductible | No deduction for entertainment, amusement, or recreation since 2018. Food bought separately at the event can still be a 50% meal. |
| Travel: airfare, rail, rideshare, car rental | 100% | IRC 162(a)(2) | Schedule C line 24a | Transportation for business away from home, and local transportation between work locations. Commuting is not deductible. |
| Lodging while traveling | 100% | IRC 162(a)(2) | Schedule C line 24a | Hotel or short-term rental on an overnight business trip. |
| Vehicle: fuel, parking, tolls | 100% | IRC 162, 274(d); Rev. Proc. standard mileage | Schedule C line 9 | Deduct actual business-use share or the standard mileage rate. Keep a mileage log; commuting miles are personal. |
| Business gift | 100% (per-recipient cap) | IRC 274(b) | Schedule C line 27a | Deductible up to $25 per recipient per year. The excess is not deductible. |
| Software and subscriptions | 100% | IRC 162; Rev. Proc. 2000-50 | Schedule C line 18 / 27a | Off-the-shelf software and SaaS subscriptions are currently deductible. |
| Cloud hosting and compute | 100% | IRC 162; IRC 41(b)(2)(A)(iii) for research use | Schedule C line 27a | Fully deductible. Compute used for development can also count as a qualified research expense. Counts toward research credit QRE. |
| Advertising and marketing | 100% | IRC 162; Reg. 1.162-1(a) | Schedule C line 8 | Ads, sponsorships, promotional materials. |
| Utilities and telecom | 100% | IRC 162 | Schedule C line 25 | Internet, phone, power for the business. Home-office share only if a home office qualifies. |
| Office supplies | 100% | IRC 162 | Schedule C line 18 | Consumables used within the year. |
| Equipment expensed under the de minimis safe harbor | 100% | Reg. 1.263(a)-1(f) | Schedule C line 22 / 27a | Items costing $2,500 or less per invoice or item can be expensed in the year of purchase with an annual election statement. |
| Equipment: capitalize, Section 179 or bonus depreciation | 100% | IRC 179, 168(k) | Form 4562 | Over $2,500. Elect Section 179 to expense in year one (subject to annual limits and taxable income) or depreciate. |
| Legal, accounting, consulting | 100% | IRC 162 | Schedule C line 17 | Fees for services to the business. |
| Business insurance | 100% | IRC 162 | Schedule C line 15 | Liability, E&O, cyber, property. Owner life insurance is not deductible. |
| Rent and coworking | 100% | IRC 162(a)(3) | Schedule C line 20b | Office rent, coworking memberships. |
| Wages and payroll | 100% | IRC 162(a)(1); IRC 41(b)(2)(A)(i) for research wages | Schedule C line 26 / Form 1120 line 13 | Deductible compensation. Engineering wages for development work count toward the research credit. Counts toward research credit QRE. |
| Contractors (1099) | 100% | IRC 162; IRC 41(b)(3) at 65% for research | Schedule C line 11 | Payments to independent contractors. Research contractors count at 65% toward QRE. Counts toward research credit QRE. |
| Training, courses, conferences | 100% | Reg. 1.162-5 | Schedule C line 27a | Education that maintains or improves skills in the current business. |
| Cost of goods sold | 100% | IRC 471; IRC 263A exceptions for small business | Schedule C Part III | Inventory and direct costs of products sold. |
| Bank, payment processing, and interest | 100% | IRC 162, 163 | Schedule C line 16b / 27a | Processing fees, bank charges, business interest (small businesses are exempt from the 163(j) limit). |
| Taxes and licenses | 100% | IRC 164 | Schedule C line 23 | State and local business taxes, licenses, permits. Federal income tax is not deductible. |
| Charitable contribution | 0% | IRC 170 | Owner's return (Schedule A) or Form 1120 line 19 | Not a Schedule C business expense; flows to the owner. C corporations deduct up to 10% of taxable income. |
| Fines and penalties | 0% | IRC 162(f) | Not deductible | Government fines and penalties are never deductible. |
| Political and lobbying | 0% | IRC 162(e) | Not deductible | Contributions and most lobbying are not deductible. |
| Personal | 0% | IRC 262 | Not deductible | Personal, living, or family expense paid from the business account. |
| Income (not an expense) | 0% | IRC 61 | Schedule C Part I | Revenue; not subject to deduction rules. |
| Transfer or owner draw | 0% | n/a | Balance sheet | Moves money; not income and not an expense. |
| Needs review | 0% | n/a | Pending | Not enough information. The deduction is lost if it stays unclassified. |

## Opportunities the advisor can raise

`sovereign_books/tax_advisor.py` ranks these nearest-first against the classified ledger and the research credit estimate:

- **Hold a company-wide event** (IRC 274(e)(4), 274(n)(2)(A)): 100% versus 50% for business meals; deadline December 31
- **Answer open meal questions** (IRC 274(d)): unanswered meals are provisionally 50% and flagged
- **Separate food from entertainment** (IRC 274(a); Reg. 1.274-11): entertainment is 0%; separately invoiced food is a 50% meal
- **Redirect office meal spend** (IRC 274(o)): office food is 0% from 2026
- **Claim the research credit** (IRC 41; 41(h)): 14% alternative simplified credit; payroll offset up to $500,000 for young companies
- **Claim the state research credit** (state statute): same QRE as federal
- **Amortize development costs correctly** (IRC 174): five-year domestic amortization
- **Expense equipment in year one** (IRC 179; 168(k)): buy and place in service before December 31
- **Attach the de minimis safe harbor election** (Reg. 1.263(a)-1(f)): annual statement with the return
- **Start a retirement plan** (IRC 45E, 45T): up to $5,000 startup credit for three years plus $500 auto-enrollment
- **Screen new hires for the Work Opportunity credit** (IRC 51; Form 5884): $2,400 to $9,600 per qualifying hire; Form 8850 within 28 days
- **Claim the small employer health credit** (IRC 45R; Form 8941): fewer than 25 FTEs, SHOP plan, up to 50% of premiums
- **Take the home office deduction** (IRC 280A; Rev. Proc. 2013-13): $5 per square foot up to 300 square feet
- **Keep a mileage log** (IRC 274(d)): standard mileage rate often beats actual fuel cost
- **Keep business gifts at $25 per person** (IRC 274(b)): excess is nondeductible
- **Classify unknown spend** (IRC 162; 6001): unclassified spend is treated as nondeductible
