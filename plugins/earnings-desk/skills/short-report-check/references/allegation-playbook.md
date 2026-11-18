# Allegation playbook: where to test each kind of claim

Short reports recycle a small set of claim types. For each, here's what a filing can and can't show, and the commands to run (`$S` = the plugin's `skills/` folder, `E` = `python3 $S/short-report-check/scripts/evidence.py`).

| Claim type | What filings can show | Where to look | Commands |
|---|---|---|---|
| **Related-party dealings** (sales to, purchases from, or loans to entities tied to insiders) | Whether the relationship and amounts are disclosed; how they changed | 10-K related-party note, Item 13 (often incorporated from the proxy), DEF 14A "Certain Relationships" | `E search T --terms "related party\|related parties,<entity name>,<person name>" --forms 10-K,10-Q,DEF 14A --n 4` |
| **Revenue recognition / inflated sales** (channel stuffing, round-tripping, bill-and-hold) | Receivables vs revenue (DSO), deferred revenue, returns reserves, revenue-policy wording, customer concentration | Revenue note, MD&A, balance sheet | `statements.py T --years 6 --quarters 8` (dso, receivables, revenue growth); `E search T --terms "bill-and-hold,channel,returns reserve\|right of return"`; `diff_sections.py T --section "Revenue Recognition"` |
| **Inventory problems** (obsolete stock, fake inventory) | DIO trend, inventory reserves, write-downs, critical audit matters | Inventory note, auditor's report | `scores.py T` (dio trend); `E search T --terms "inventory reserve\|excess and obsolete,critical audit matter"` |
| **Cash / balance-sheet doubts** (cash doesn't exist, hidden debt) | Cash flow vs earnings, interest income vs cash balance, guarantees, off-balance-sheet items | Cash-flow statement, commitments and contingencies note | `statements.py` (ocf_to_ni); `E search T --terms "guarantee,variable interest entit,off-balance"` |
| **Controls and auditor** (weak controls, conflicted or small auditor) | Material weakness disclosures, auditor changes and stated reasons, tenure, CAMs | Item 9A, auditor's report, 8-K Item 4.01 (+ auditor's Ex.16 letter) | `E events T --since <date>`; `E search T --terms "material weakness,Exhibit 16\|disagreements"` |
| **Restatements / misstated periods** | Non-reliance notices, amended reports | 8-K Item 4.02, 10-K/A, 10-Q/A | `E events T` (4.02, amendments); read the 8-K by `--accession` |
| **Export controls / sanctions / regulatory** | Risk-factor language, investigations disclosed, subpoenas | Item 1A, legal proceedings (Item 3), contingencies note | `E search T --terms "export control,subpoena,investigation,Department of Justice\|DOJ,SEC"`; `diff_sections.py T --section 1A` |
| **Insider selling / governance** | Form 4 sales, 10b5-1 plans, executive departures, rehiring of people tied to past issues | Form 4, 8-K Item 5.02, proxy | `edgar.py insiders T --days 365 --limit 150`; `E events T` (5.02); `E search T --terms "<person name>"` |
| **Undisclosed customers / suppliers** | Concentration disclosures (customer A = x%), named counterparties | Business section, concentration note | `E search T --terms "customer concentration\|largest customer,accounted for"` |
| **Unit economics / KPI claims** (store counts, users, pricing) | Company-reported KPIs over time; definition changes | Earnings releases, MD&A | `edgar.py earnings-release T --index 0..7`; kpi-tracker skill |
| **Valuation / "worth $X"** | Nothing: this is Opinion | n/a | Label Opinion |
| **Channel checks, interviews, private records** | Usually nothing directly | n/a | Label Not verifiable; say what would settle it (e.g. a regulator finding, a restatement) |

## Serious events and what they do (and don't) establish
| Event | Supports | Does not by itself establish |
|---|---|---|
| Auditor resigns (8-K 4.01) citing disagreements or lost confidence | Concerns about controls, management representations or governance | Any specific fraud allegation |
| Non-reliance / restatement (8-K 4.02) | That prior statements were wrong in the areas named | Intent |
| Late filing (NT 10-K/10-Q) | Unresolved accounting or audit issues at that date | The nature of the issues (read the NT text) |
| Exchange listing notice (3.01) | Filing deficiencies or other listing breaches | Wrongdoing |
| Special committee report clears management | That the committee found no misconduct in its scope | That every allegation was false (check the scope) |
| DOJ/SEC investigation disclosed | That regulators are looking | Guilt |

## Writing allegations neutrally
- "The report alleges…", "the filings confirm the relationship but not the alleged pricing", "consistent with the allegation", "not addressed in filings".
- Avoid "fraud", "scam", "cooked the books" unless quoting the report, a court or a regulator, and attribute the quote.
