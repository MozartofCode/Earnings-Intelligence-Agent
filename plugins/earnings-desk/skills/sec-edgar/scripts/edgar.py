#!/usr/bin/env python3
"""earnings-desk SEC EDGAR client. Python 3.8+, standard library only.

Every command prints JSON to stdout. Responses are cached under
.earnings-desk/cache/ (in the current directory) so repeat runs are fast and
polite to SEC servers.

SEC asks automated tools to identify themselves. Set SEC_USER_AGENT to
"Your Name your@email.com" (see https://www.sec.gov/os/accessing-edgar-data).

Commands
  cik TICKER                       Ticker -> CIK, name, exchange
  profile TICKER                   Company profile from the submissions API
  filings TICKER [--forms 10-K,10-Q] [--limit 20]
  facts TICKER [--periods 12] [--annual N]
                                   Normalized financials: annual + quarterly series
  concept TICKER TAG [--taxonomy us-gaap]
                                   Raw XBRL facts for one tag
  filing-text TICKER [--form 10-K] [--index 0] [--section "1A"] [--max-chars 60000]
                    [--accession 0000320193-26-000024] [--include-amendments]
                                   Download a filing's primary document as plain text
                                   (amendments are skipped in --index unless asked for)
  earnings-release TICKER [--index 0] [--max-chars 150000] [--accession ACCN]
                                   Latest 8-K Item 2.02 press release (Exhibit 99.x) text
  insiders TICKER [--days 180] [--limit 40]
                                   Parsed Form 4 insider transactions
  peers TICKER [--limit 15]        Companies sharing the same SIC code (via EDGAR browse)
"""
import argparse
import gzip
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta

UA = os.environ.get("SEC_USER_AGENT") or os.environ.get("EVAL_SEC_USER_AGENT") or "earnings-desk/1.0 (open-source research tool; https://github.com/MozartofCode/Earnings-Intelligence-Agent)"
CACHE_DIR = os.path.join(os.getcwd(), ".earnings-desk", "cache")
_last_call = [0.0]


def die(msg, code=1, **extra):
    out = {"error": msg}
    out.update(extra)
    print(json.dumps(out, indent=2))
    sys.exit(code)


def fetch(url, ttl_hours=12, binary=False):
    """GET with caching, SEC rate limiting (<10 req/s) and gzip support."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    key = hashlib.sha1(url.encode()).hexdigest()
    path = os.path.join(CACHE_DIR, key)
    if os.path.exists(path) and (time.time() - os.path.getmtime(path)) < ttl_hours * 3600:
        with open(path, "rb") as f:
            raw = f.read()
        return raw if binary else raw.decode("utf-8", "replace")
    wait = 0.15 - (time.time() - _last_call[0])
    if wait > 0:
        time.sleep(wait)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip, deflate", "Accept": "*/*"})
    last_err = None
    for attempt in range(3):
        try:
            _last_call[0] = time.time()
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read()
                if resp.headers.get("Content-Encoding") == "gzip":
                    raw = gzip.decompress(raw)
            with open(path, "wb") as f:
                f.write(raw)
            return raw if binary else raw.decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code in (400, 404):
                raise
            if e.code == 403:
                die("SEC returned 403 Forbidden. Set SEC_USER_AGENT to 'Your Name your@email.com' and retry.", url=url)
            time.sleep(1.5 * (attempt + 1))
        except urllib.error.URLError as e:
            last_err = e
            time.sleep(1.5 * (attempt + 1))
    die("Network error fetching %s: %s" % (url, last_err))


def fetch_json(url, ttl_hours=12):
    return json.loads(fetch(url, ttl_hours))


# ---------------------------------------------------------------- tickers

def ticker_map():
    data = fetch_json("https://www.sec.gov/files/company_tickers_exchange.json", ttl_hours=24 * 7)
    fields = data["fields"]
    out = {}
    for row in data["data"]:
        rec = dict(zip(fields, row))
        out.setdefault(str(rec["ticker"]).upper(), rec)
    return out


def resolve(ticker):
    t = ticker.upper().strip().replace(".", "-")
    m = ticker_map()
    rec = m.get(t) or m.get(t.replace("-", ""))
    if not rec and t.isdigit():
        return {"cik": int(t), "ticker": t, "name": None, "exchange": None}
    if not rec:
        close = [k for k in m if k.startswith(t[:2])][:8]
        die("Unknown ticker '%s'. EDGAR only covers SEC registrants (US-listed companies)." % ticker, suggestions=close)
    return {"cik": int(rec["cik"]), "ticker": rec["ticker"], "name": rec["name"], "exchange": rec["exchange"]}


def cik10(cik):
    return str(cik).zfill(10)


def submissions(cik):
    return fetch_json("https://data.sec.gov/submissions/CIK%s.json" % cik10(cik), ttl_hours=6)


def _rows_from(block, cik, forms, rows, limit):
    for i in range(len(block["accessionNumber"])):
        form = block["form"][i]
        if forms and form not in forms:
            continue
        acc = block["accessionNumber"][i]
        doc = block["primaryDocument"][i]
        rows.append({
            "form": form,
            "filed": block["filingDate"][i],
            "period": block["reportDate"][i],
            "accession": acc,
            "items": (block.get("items") or [""] * len(block["form"]))[i],
            "primary_doc": doc,
            "url": "https://www.sec.gov/Archives/edgar/data/%d/%s/%s" % (int(cik), acc.replace("-", ""), doc),
            "index_url": "https://www.sec.gov/Archives/edgar/data/%d/%s/" % (int(cik), acc.replace("-", "")),
        })
        if len(rows) >= limit:
            return True
    return False


def recent_filings(cik, forms=None, limit=20):
    """Newest-first filings. EDGAR's 'recent' block holds ~1,000 filings, which
    covers only months for heavy filers (big banks), so older pages listed in
    filings.files are read too until `limit` matches are found."""
    sub = submissions(cik)
    rows = []
    if _rows_from(sub["filings"]["recent"], cik, forms, rows, limit):
        return rows
    for page in sub["filings"].get("files", []):
        try:
            block = fetch_json("https://data.sec.gov/submissions/" + page["name"], ttl_hours=24 * 7)
        except urllib.error.HTTPError:
            break
        if _rows_from(block, cik, forms, rows, limit):
            break
    return rows


# ---------------------------------------------------------------- XBRL facts

# Each metric lists candidate tags in priority order. The first tag with data
# for a period wins, so companies that switched tags over time still get one
# continuous series.
METRICS = {
    "revenue": (["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues", "SalesRevenueNet",
                 "RevenueFromContractWithCustomerIncludingAssessedTax", "SalesRevenueGoodsNet", "RevenuesNetOfInterestExpense"], "flow"),
    "cost_of_revenue": (["CostOfRevenue", "CostOfGoodsAndServicesSold", "CostOfGoodsSold", "CostOfServices"], "flow"),
    "gross_profit": (["GrossProfit"], "flow"),
    "rnd": (["ResearchAndDevelopmentExpense", "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost"], "flow"),
    "sga": (["SellingGeneralAndAdministrativeExpense"], "flow"),
    "operating_income": (["OperatingIncomeLoss"], "flow"),
    "interest_expense": (["InterestExpense", "InterestExpenseNonoperating", "InterestExpenseDebt"], "flow"),
    "pretax_income": (["IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
                       "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments"], "flow"),
    "income_tax": (["IncomeTaxExpenseBenefit"], "flow"),
    "net_income": (["NetIncomeLoss", "ProfitLoss", "NetIncomeLossAvailableToCommonStockholdersBasic"], "flow"),
    "eps_diluted": (["EarningsPerShareDiluted", "EarningsPerShareBasicAndDiluted"], "flow"),
    "shares_diluted": (["WeightedAverageNumberOfDilutedSharesOutstanding"], "flow"),
    "da": (["DepreciationDepletionAndAmortization", "DepreciationAndAmortization", "DepreciationAmortizationAndAccretionNet", "Depreciation"], "flow"),
    "sbc": (["ShareBasedCompensation", "AllocatedShareBasedCompensationExpense"], "flow"),
    "operating_cash_flow": (["NetCashProvidedByUsedInOperatingActivities", "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"], "flow"),
    "capex": (["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets"], "flow"),
    "acquisitions": (["PaymentsToAcquireBusinessesNetOfCashAcquired"], "flow"),
    "buybacks": (["PaymentsForRepurchaseOfCommonStock"], "flow"),
    "dividends_paid": (["PaymentsOfDividends", "PaymentsOfDividendsCommonStock"], "flow"),
    "cash": (["CashAndCashEquivalentsAtCarryingValue", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"], "instant"),
    "short_term_investments": (["ShortTermInvestments", "AvailableForSaleSecuritiesDebtSecuritiesCurrent", "MarketableSecuritiesCurrent", "DebtSecuritiesCurrent", "AvailableForSaleSecuritiesCurrent"], "instant"),
    "receivables": (["AccountsReceivableNetCurrent", "ReceivablesNetCurrent"], "instant"),
    "inventory": (["InventoryNet"], "instant"),
    "current_assets": (["AssetsCurrent"], "instant"),
    "ppe_net": (["PropertyPlantAndEquipmentNet", "PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization", "PropertyPlantAndEquipmentNetIncludingEquipmentOnOperatingLeases"], "instant"),
    "goodwill": (["Goodwill"], "instant"),
    "total_assets": (["Assets"], "instant"),
    "accounts_payable": (["AccountsPayableCurrent"], "instant"),
    "current_liabilities": (["LiabilitiesCurrent"], "instant"),
    "long_term_debt": (["LongTermDebtNoncurrent", "LongTermDebt", "LongTermDebtAndCapitalLeaseObligations"], "instant"),
    "short_term_debt": (["LongTermDebtCurrent", "DebtCurrent", "ShortTermBorrowings", "CommercialPaper"], "instant"),
    "total_liabilities": (["Liabilities"], "instant"),
    "retained_earnings": (["RetainedEarningsAccumulatedDeficit"], "instant"),
    "equity": (["StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"], "instant"),
    "shares_outstanding": (["CommonStockSharesOutstanding", "dei:EntityCommonStockSharesOutstanding"], "instant"),
}


def _days(a, b):
    return (datetime.strptime(b, "%Y-%m-%d") - datetime.strptime(a, "%Y-%m-%d")).days


def _units(fact):
    u = fact.get("units", {})
    for k in ("USD", "USD/shares", "shares", "pure"):
        if k in u:
            return u[k], k
    if u:
        k = next(iter(u))
        return u[k], k
    return [], None


# Weighted-average share counts are not additive, so quarters can't be
# derived by subtracting year-to-date periods. EPS derivation is kept but is
# an approximation (flagged derived=True).
NON_ADDITIVE = {"WeightedAverageNumberOfDilutedSharesOutstanding"}


def _series_for_tag(facts, tag, kind):
    tax = "us-gaap"
    if ":" in tag:
        tax, tag = tag.split(":", 1)
    fact = facts.get("facts", {}).get(tax, {}).get(tag)
    if not fact:
        return None, None
    rows, unit = _units(fact)
    durations, instants = {}, {}
    for r in rows:
        if r.get("form") not in ("10-K", "10-Q", "10-K/A", "10-Q/A", "20-F", "40-F", "6-K"):
            continue
        end = r["end"]
        rec = {"end": end, "val": r["val"], "fy": r.get("fy"), "fp": r.get("fp"), "form": r.get("form"), "filed": r.get("filed"), "accn": r.get("accn")}
        if kind == "instant" or "start" not in r:
            prev = instants.get(end)
            if not prev or r.get("filed", "") > prev.get("filed", ""):
                instants[end] = rec
            continue
        rec["start"] = r["start"]
        key = (r["start"], end)
        prev = durations.get(key)
        if not prev or r.get("filed", "") > prev.get("filed", ""):
            durations[key] = rec
    annual, quarterly = {}, {}
    for (st, en), rec in durations.items():
        d = _days(st, en)
        if 340 <= d <= 380:
            annual[en] = rec
        elif 80 <= d <= 100:
            quarterly[en] = rec
    # Cash-flow statements (and some income statements) are reported year-to-date
    # in 10-Qs. Derive each missing quarter as the difference between consecutive
    # cumulative periods that share a start date (Q2 = 6M - 3M, Q4 = FY - 9M).
    by_start = {}
    for (st, en), rec in (durations.items() if tag not in NON_ADDITIVE else []):
        by_start.setdefault(st, []).append(rec)
    for st, recs in by_start.items():
        recs.sort(key=lambda r: r["end"])
        for prev, cur in zip(recs, recs[1:]):
            gap = _days(prev["end"], cur["end"])
            if 80 <= gap <= 100 and cur["end"] not in quarterly:
                val = cur["val"] - prev["val"]
                if isinstance(val, float):
                    val = round(val, 4)
                quarterly[cur["end"]] = dict(cur, start=prev["end"], val=val, derived=True)
    return (annual, quarterly, instants), unit


def build_facts(cik, n_quarters=12, n_years=6):
    facts = fetch_json("https://data.sec.gov/api/xbrl/companyfacts/CIK%s.json" % cik10(cik), ttl_hours=12)
    out = {"entity": facts.get("entityName"), "cik": cik, "annual": {}, "quarterly": {}, "tags_used": {}, "units": {}}
    for metric, (tags, kind) in METRICS.items():
        merged_a, merged_q, used = {}, {}, []
        for tag in tags:
            parsed, unit = _series_for_tag(facts, tag, kind)
            if not parsed:
                continue
            annual, quarterly, instants = parsed
            if kind == "instant":
                annual = {k: v for k, v in instants.items()}
                quarterly = dict(annual)
            added = False
            for k, v in annual.items():
                if k not in merged_a:
                    merged_a[k] = v
                    added = True
            for k, v in quarterly.items():
                if k not in merged_q:
                    merged_q[k] = v
                    added = True
            if added:
                used.append(tag)
                out["units"][metric] = unit
        if not used:
            continue
        out["tags_used"][metric] = used
        a = sorted(merged_a.values(), key=lambda r: r["end"])
        q = sorted(merged_q.values(), key=lambda r: r["end"])
        if kind == "instant":
            # annual balance-sheet points = fiscal year ends, matched to revenue/NI year ends later
            out["annual"][metric] = [{"end": r["end"], "val": r["val"], "accn": r["accn"]} for r in a]
            out["quarterly"][metric] = [{"end": r["end"], "val": r["val"], "accn": r["accn"]} for r in q][-n_quarters:]
        else:
            out["annual"][metric] = [{"end": r["end"], "fy": int(r["end"][:4]), "val": r["val"], "accn": r["accn"]} for r in a][-n_years:]
            out["quarterly"][metric] = [{"end": r["end"], "val": r["val"], "accn": r["accn"], "derived": bool(r.get("derived"))} for r in q][-n_quarters:]
    # Trim instant annual series to fiscal-year-end dates seen in flow metrics
    fy_ends = set()
    for m in ("revenue", "net_income", "operating_cash_flow"):
        for r in out["annual"].get(m, []):
            fy_ends.add(r["end"])
    if fy_ends:
        for metric, (tags, kind) in METRICS.items():
            if kind == "instant" and metric in out["annual"]:
                out["annual"][metric] = [r for r in out["annual"][metric] if r["end"] in fy_ends][-n_years:]
    return out


# ---------------------------------------------------------------- filing text

class _Strip(object):
    BLOCK = re.compile(r"</?(p|div|br|tr|li|h[1-6]|table|section)[^>]*>", re.I)

    @staticmethod
    def text(raw):
        raw = re.sub(r"(?is)<(script|style|head)[^>]*>.*?</\1>", " ", raw)
        raw = re.sub(r"(?is)<ix:header>.*?</ix:header>", " ", raw)
        raw = re.sub(r"(?i)</t[dh]>", " | ", raw)
        raw = _Strip.BLOCK.sub("\n", raw)
        raw = re.sub(r"(?s)<[^>]+>", " ", raw)
        raw = html.unescape(raw)
        raw = raw.replace("\xa0", " ")
        raw = re.sub(r"[ \t]+", " ", raw)
        raw = re.sub(r"\n\s*\n+", "\n\n", raw)
        return raw.strip()


def _loose(words):
    """Regex that tolerates stray whitespace inside words (EDGAR HTML often splits spans)."""
    return r"\s*".join(r"\s*".join(re.escape(ch) for ch in w) for w in words.split())


SECTION_ALIASES = {
    "1": (r"1", "business"),
    "1a": (r"1a", "risk factors"),
    "1c": (r"1c", "cybersecurity"),
    "3": (r"3", "legal proceedings"),
    "7": (r"7", "management"),
    "7a": (r"7a", "quantitative"),
    "8": (r"8", "financial statements"),
    "9a": (r"9a", "controls and procedures"),
    "mdna": (r"[27]", "management"),
    "risk": (r"1a", "risk factors"),
}


def extract_section(text, section):
    key = section.lower().replace("item", "").strip().replace(" ", "")
    if key in SECTION_ALIASES:
        num, title = SECTION_ALIASES[key]
        pat = r"item\s*" + num + r"\s*[.:\-\u2014]?\s*" + _loose(title)
    else:
        pat = _loose(section)
    hits = [m.start() for m in re.finditer(pat, text, re.I)]
    if not hits:
        return None
    # Skip table-of-contents hits: keep the occurrence with the longest run of
    # text before the next "ITEM n." heading.
    best, best_len = None, -1
    for h in hits:
        nxt = re.search(r"\n\s*item\s*\d+[a-c]?\s*[.:\u2014]\s*[A-Z]", text[h + 80:], re.I)
        end = h + 80 + nxt.start() if nxt else len(text)
        if end - h > best_len:
            best, best_len = (h, end), end - h
    return text[best[0]:best[1]].strip()


def filing_text(cik, form, index, section=None, max_chars=60000, accession=None, include_amendments=False):
    """Plain text of one filing. Amendments (e.g. Part III-only 10-K/A) are
    excluded from the index count unless include_amendments=True or the form
    itself ends in /A. Pass accession to pick an exact filing."""
    if accession:
        rows = [r for r in recent_filings(cik, None, limit=1000) if r["accession"] == accession]
        if not rows:
            die("Accession %s not found in this company's recent filings" % accession)
        row = rows[0]
    else:
        forms = [form, form + "/A"] if include_amendments and not form.endswith("/A") else [form]
        rows = recent_filings(cik, set(forms), limit=index + 1)
        if len(rows) <= index:
            die("No %s filing at index %d for CIK %s" % (form, index, cik))
        row = rows[index]
    form = row["form"]
    raw = fetch(row["url"], ttl_hours=24 * 30)
    text = _Strip.text(raw)
    os.makedirs(os.path.join(CACHE_DIR, "text"), exist_ok=True)
    fname = "%s-%s-%s.txt" % (cik, form.replace("/", ""), row["accession"])
    path = os.path.join(CACHE_DIR, "text", fname)
    with open(path, "w") as f:
        f.write(text)
    body = extract_section(text, section) if section else text
    return {
        "filing": row,
        "saved_to": path,
        "total_chars": len(text),
        "section": section,
        "section_found": body is not None,
        "truncated": bool(body and len(body) > max_chars),
        "text": (body or "")[:max_chars],
    }


def filing_index(cik, accession):
    url = "https://www.sec.gov/Archives/edgar/data/%d/%s/index.json" % (int(cik), accession.replace("-", ""))
    return fetch_json(url, ttl_hours=24 * 30)


def exhibit_docs(cik, row, type_prefix):
    """Documents in a filing whose EDGAR exhibit type starts with type_prefix (e.g. EX-99)."""
    url = row["index_url"] + row["accession"] + "-index.html"
    try:
        page = fetch(url, ttl_hours=24 * 30)
    except urllib.error.HTTPError:
        page = ""
    docs = []
    for tr in re.findall(r"(?is)<tr[^>]*>(.*?)</tr>", page):
        cells = re.findall(r"(?is)<td[^>]*>(.*?)</td>", tr)
        href = re.search(r'href="([^"]+)"', tr)
        if not href or len(cells) < 4:
            continue
        ftype = re.sub(r"<[^>]+>", "", cells[3]).strip().upper()
        name = href.group(1).split("/")[-1]
        if ftype.startswith(type_prefix.upper()) and name.lower().endswith((".htm", ".html", ".txt")):
            docs.append(name)
    if not docs:  # fall back to any non-primary HTML document in the folder
        idx = filing_index(cik, row["accession"])
        docs = [i["name"] for i in idx.get("directory", {}).get("item", [])
                if i["name"].lower().endswith(".htm") and i["name"] != row["primary_doc"]
                and not re.match(r"(?i)^r\d+\.htm$", i["name"]) and "index" not in i["name"]]
    return docs


def earnings_release(cik, index=0, max_chars=150000, accession=None):
    if accession:
        rows = [r for r in recent_filings(cik, {"8-K", "8-K/A"}, limit=1000) if r["accession"] == accession]
        if not rows:
            die("8-K %s not found for this company" % accession)
        index = 0
    else:
        rows = [r for r in recent_filings(cik, {"8-K"}, limit=200) if "2.02" in (r.get("items") or "")]
    if len(rows) <= index:
        die("No 8-K with Item 2.02 (results of operations) found at index %d" % index)
    row = rows[index]
    docs = exhibit_docs(cik, row, r"EX-99")
    docs = docs or [row["primary_doc"]]
    texts = []
    for name in docs[:2]:
        url = row["index_url"] + name
        texts.append({"doc": name, "url": url, "text": _Strip.text(fetch(url, ttl_hours=24 * 30))})
    joined = "\n\n".join("===== EXHIBIT: %s =====\n%s" % (t["doc"], t["text"]) for t in texts)
    return {"filing": row, "exhibits": [{"doc": t["doc"], "url": t["url"]} for t in texts], "truncated": len(joined) > max_chars, "text": joined[:max_chars]}


# ---------------------------------------------------------------- Form 4

TX_CODES = {"P": "open-market buy", "S": "open-market sale", "A": "grant/award", "M": "option exercise", "F": "tax withholding",
            "G": "gift", "D": "disposition to issuer", "C": "conversion", "X": "option exercise (in-the-money)", "J": "other"}


def _t(node, path):
    el = node.find(path)
    return el.text.strip() if el is not None and el.text else None


def insiders(cik, days=180, limit=40):
    cutoff = (date.today() - timedelta(days=days)).isoformat()
    rows = [r for r in recent_filings(cik, {"4", "4/A"}, limit=400) if r["filed"] >= cutoff][:limit]
    txs, errors = [], 0
    for r in rows:
        try:
            idx = filing_index(cik, r["accession"])
            xmls = [i["name"] for i in idx.get("directory", {}).get("item", []) if i["name"].lower().endswith(".xml")]
            if not xmls:
                continue
            root = ET.fromstring(fetch(r["index_url"] + xmls[0], ttl_hours=24 * 365))
        except Exception:
            errors += 1
            continue
        owner = _t(root, "reportingOwner/reportingOwnerId/rptOwnerName")
        rel = root.find("reportingOwner/reportingOwnerRelationship")
        role = []
        if rel is not None:
            if _t(rel, "isDirector") in ("1", "true"):
                role.append("Director")
            if _t(rel, "isOfficer") in ("1", "true"):
                role.append(_t(rel, "officerTitle") or "Officer")
            if _t(rel, "isTenPercentOwner") in ("1", "true"):
                role.append("10% owner")
        plan = "10b5-1" in ET.tostring(root, encoding="unicode").lower() or _t(root, "aff10b5One") in ("1", "true")
        for tx in root.findall("nonDerivativeTable/nonDerivativeTransaction"):
            code = _t(tx, "transactionCoding/transactionCode")
            shares = _t(tx, "transactionAmounts/transactionShares/value")
            price = _t(tx, "transactionAmounts/transactionPricePerShare/value")
            ad = _t(tx, "transactionAmounts/transactionAcquiredDisposedCode/value")
            after = _t(tx, "postTransactionAmounts/sharesOwnedFollowingTransaction/value")
            try:
                sh = float(shares) if shares else None
                px = float(price) if price else None
            except ValueError:
                sh, px = None, None
            txs.append({
                "filed": r["filed"], "date": _t(tx, "transactionDate/value"), "insider": owner, "role": ", ".join(role),
                "code": code, "type": TX_CODES.get(code, code), "acquired_disposed": ad, "shares": sh, "price": px,
                "value": round(sh * px, 2) if sh and px else None, "shares_after": float(after) if after else None,
                "10b5_1_plan": plan, "url": r["index_url"],
            })
    buys = [t for t in txs if t["code"] == "P"]
    sells = [t for t in txs if t["code"] == "S"]
    return {
        "window_days": days, "filings_scanned": len(rows), "parse_errors": errors,
        "summary": {
            "open_market_buys": len(buys), "buy_value": round(sum(t["value"] or 0 for t in buys), 2),
            "open_market_sales": len(sells), "sale_value": round(sum(t["value"] or 0 for t in sells), 2),
            "unique_buyers": sorted(set(t["insider"] for t in buys if t["insider"])),
            "sales_under_10b5_1": sum(1 for t in sells if t["10b5_1_plan"]),
        },
        "transactions": txs,
    }


# ---------------------------------------------------------------- peers

def peers(cik, limit=15):
    sub = submissions(cik)
    sic = sub.get("sic")
    if not sic:
        die("No SIC code on file for this company")
    url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&SIC=%s&type=10-K&dateb=&owner=include&count=100&output=atom" % sic
    try:
        xml = fetch(url, ttl_hours=24 * 7)
    except urllib.error.HTTPError:
        xml = ""
    ciks = re.findall(r"<cik>(\d+)</cik>", xml, re.I)
    names = re.findall(r"<name>([^<]+)</name>", xml, re.I)
    by_cik = {}
    m = ticker_map()
    rev = {}
    for t, rec in m.items():
        rev.setdefault(int(rec["cik"]), t)
    for c, n in zip(ciks, names[1:] if len(names) > len(ciks) else names):
        c = int(c)
        if c != int(cik) and c in rev and str(m[rev[c]].get("exchange")) in ("Nasdaq", "NYSE", "NYSE American"):
            by_cik[c] = {"cik": c, "name": html.unescape(n), "ticker": rev[c]}
    return {"sic": sic, "sic_description": sub.get("sicDescription"), "peers": list(by_cik.values())[:limit],
            "note": "SIC peers are a starting point only; refine by business model, size and end market."}


# ---------------------------------------------------------------- CLI

def main(argv=None):
    p = argparse.ArgumentParser(description="earnings-desk SEC EDGAR client (JSON output).", formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    sp = p.add_subparsers(dest="cmd")
    sp.add_parser("cik").add_argument("ticker")
    sp.add_parser("profile").add_argument("ticker")
    f = sp.add_parser("filings"); f.add_argument("ticker"); f.add_argument("--forms", default=""); f.add_argument("--limit", type=int, default=20)
    fa = sp.add_parser("facts"); fa.add_argument("ticker"); fa.add_argument("--periods", type=int, default=12); fa.add_argument("--annual", type=int, default=6)
    c = sp.add_parser("concept"); c.add_argument("ticker"); c.add_argument("tag"); c.add_argument("--taxonomy", default="us-gaap")
    t = sp.add_parser("filing-text"); t.add_argument("ticker"); t.add_argument("--form", default="10-K"); t.add_argument("--index", type=int, default=0)
    t.add_argument("--section"); t.add_argument("--max-chars", type=int, default=60000)
    t.add_argument("--accession", help="exact accession number (overrides --form/--index)")
    t.add_argument("--include-amendments", action="store_true", help="count 10-K/A, 10-Q/A in --index")
    e = sp.add_parser("earnings-release"); e.add_argument("ticker"); e.add_argument("--index", type=int, default=0); e.add_argument("--max-chars", type=int, default=150000); e.add_argument("--accession", help="a specific 8-K by accession number (any item, e.g. a guarantee or exhibit-only 8-K)")
    i = sp.add_parser("insiders"); i.add_argument("ticker"); i.add_argument("--days", type=int, default=180); i.add_argument("--limit", type=int, default=40)
    pe = sp.add_parser("peers"); pe.add_argument("ticker"); pe.add_argument("--limit", type=int, default=15)
    a = p.parse_args(argv)
    if not a.cmd:
        p.print_help()
        return
    co = resolve(a.ticker)
    cik = co["cik"]
    if a.cmd == "cik":
        out = co
    elif a.cmd == "profile":
        s = submissions(cik)
        out = dict(co, **{k: s.get(k) for k in ("sic", "sicDescription", "category", "fiscalYearEnd", "stateOfIncorporation", "website", "investorWebsite", "description", "exchanges", "tickers", "formerNames")})
        out["addresses"] = s.get("addresses", {}).get("business")
        out["latest_filings"] = recent_filings(cik, {"10-K", "10-Q", "8-K", "DEF 14A", "20-F"}, limit=8)
    elif a.cmd == "filings":
        forms = set(x.strip() for x in a.forms.split(",") if x.strip()) or None
        out = dict(co, filings=recent_filings(cik, forms, a.limit))
    elif a.cmd == "facts":
        out = dict(co, **build_facts(cik, a.periods, a.annual))
    elif a.cmd == "concept":
        try:
            out = fetch_json("https://data.sec.gov/api/xbrl/companyconcept/CIK%s/%s/%s.json" % (cik10(cik), a.taxonomy, a.tag))
        except urllib.error.HTTPError:
            die("Tag %s:%s not reported by %s" % (a.taxonomy, a.tag, co["ticker"]))
    elif a.cmd == "filing-text":
        out = dict(co, **filing_text(cik, a.form, a.index, a.section, a.max_chars, a.accession, a.include_amendments))
    elif a.cmd == "earnings-release":
        out = dict(co, **earnings_release(cik, a.index, a.max_chars, a.accession))
    elif a.cmd == "insiders":
        out = dict(co, **insiders(cik, a.days, a.limit))
    elif a.cmd == "peers":
        out = dict(co, **peers(cik, a.limit))
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
