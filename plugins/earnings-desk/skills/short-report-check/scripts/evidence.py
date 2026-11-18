#!/usr/bin/env python3
"""Filing evidence finder for testing allegations against SEC filings. Stdlib only.

Commands
  search TICKER --terms "related party,Customer A|largest customer" [--forms 10-K,10-Q] [--n 3]
                [--context 280] [--max-hits 6]
      Finds each term (comma-separated; use | for synonyms within one term) in the
      n most recent filings of each form. Returns, per term, cited snippets and a
      mention count per filing so you can see whether disclosure grew or shrank.
  events TICKER [--since 2024-01-01] [--limit 400]
      Lists filing events that matter when testing allegations: auditor changes
      (8-K 4.01), non-reliance/restatements (4.02), officer/director changes (5.02),
      material agreements (1.01/1.02), impairments (2.06), listing notices (3.01),
      late filings (NT 10-K/10-Q) and amended reports (10-K/A, 10-Q/A).

All output is JSON with accession numbers and URLs for citation. Full filing text is
cached under ./.earnings-desk/cache/text/ (paths returned as saved_to).
Depends on ../../sec-edgar/scripts/edgar.py (sibling skill or bundled vendor/ copy).
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _base in (os.path.join(HERE, "..", ".."), os.path.join(HERE, "..", "vendor")):  # sibling skill, or bundled copy
    sys.path.insert(0, os.path.join(_base, "sec-edgar", "scripts"))
import edgar  # noqa: E402

ITEMS = {
    "1.01": "material definitive agreement", "1.02": "termination of a material agreement",
    "2.06": "material impairment", "3.01": "delisting / listing-standard notice",
    "4.01": "change in auditor", "4.02": "non-reliance on prior financials (restatement)",
    "5.02": "director or officer departure / appointment", "5.05": "code-of-ethics change or waiver",
    "8.01": "other events",
}


def term_regex(term):
    alts = [a.strip() for a in term.split("|") if a.strip()]
    return re.compile("|".join(r"(?<!\w)" + re.escape(a).replace(r"\ ", r"\s+") + r"(?!\w)" for a in alts), re.I)


def snippet(text, start, end, width):
    a, b = max(0, start - width), min(len(text), end + width)
    s = re.sub(r"\s+", " ", text[a:b]).strip()
    return ("…" if a > 0 else "") + s + ("…" if b < len(text) else "")


def search(cik, terms, forms, n, width, max_hits):
    filings = []
    for form in forms:
        rows = edgar.recent_filings(cik, {form}, limit=n)
        for row in rows:
            try:
                ft = edgar.filing_text(cik, form, 0, None, max_chars=10, accession=row["accession"])
                text = open(ft["saved_to"]).read()
            except SystemExit:
                continue
            filings.append((row, text, ft["saved_to"]))
    out = {}
    for term in terms:
        rx = term_regex(term)
        counts, hits = [], []
        for row, text, path in filings:
            ms = list(rx.finditer(text))
            counts.append({"form": row["form"], "filed": row["filed"], "period": row["period"], "accession": row["accession"], "mentions": len(ms)})
            for m in ms[:max(1, max_hits // max(len(filings), 1) + 1)]:
                if len(hits) >= max_hits:
                    break
                hits.append({"form": row["form"], "filed": row["filed"], "period": row["period"], "accession": row["accession"],
                             "url": row["url"], "saved_to": path, "snippet": snippet(text, m.start(), m.end(), width)})
        total = sum(c["mentions"] for c in counts)
        out[term] = {"total_mentions": total, "per_filing": counts, "hits": hits,
                     "read": ("not found in the filings searched; absence is evidence only if the filings would normally disclose it" if total == 0 else None)}
    return {"filings_searched": [{"form": r["form"], "filed": r["filed"], "period": r["period"], "accession": r["accession"], "url": r["url"]} for r, _, _ in filings],
            "terms": out}


def events(cik, since, limit):
    rows = [r for r in edgar.recent_filings(cik, None, limit=limit) if r["filed"] >= since]
    ev = []
    for r in rows:
        f = r["form"]
        if f in ("8-K", "8-K/A"):
            items = [i.strip() for i in (r.get("items") or "").split(",") if i.strip()]
            flagged = [i for i in items if i in ITEMS and i != "8.01"]
            if flagged:
                ev.append({"filed": r["filed"], "form": f, "items": flagged, "meaning": [ITEMS[i] for i in flagged], "accession": r["accession"], "url": r["url"]})
        elif f.startswith("NT ") or f in ("10-K/A", "10-Q/A", "20-F/A"):
            ev.append({"filed": r["filed"], "form": f, "items": [], "meaning": ["late filing notice" if f.startswith("NT ") else "amended periodic report"],
                       "accession": r["accession"], "url": r["url"]})
    serious = [e for e in ev if any(i in ("4.01", "4.02", "3.01") for i in e["items"]) or e["form"].startswith("NT ")]
    return {"since": since, "filings_scanned": len(rows), "window": [rows[-1]["filed"], rows[0]["filed"]] if rows else None,
            "events": ev, "serious_events": serious,
            "note": "No 4.01/4.02/3.01 or NT filings in the window is itself a finding; state the window you checked."}


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd")
    s = sp.add_parser("search"); s.add_argument("ticker"); s.add_argument("--terms", required=True)
    s.add_argument("--forms", default="10-K,10-Q"); s.add_argument("--n", type=int, default=3)
    s.add_argument("--context", type=int, default=280); s.add_argument("--max-hits", type=int, default=6)
    e = sp.add_parser("events"); e.add_argument("ticker"); e.add_argument("--since", default="2023-01-01"); e.add_argument("--limit", type=int, default=400)
    a = p.parse_args()
    if not a.cmd:
        p.print_help(); return
    co = edgar.resolve(a.ticker)
    if a.cmd == "search":
        terms = [t.strip() for t in a.terms.split(",") if t.strip()]
        forms = [f.strip() for f in a.forms.split(",") if f.strip()]
        out = dict(co, **search(co["cik"], terms, forms, a.n, a.context, a.max_hits))
    else:
        out = dict(co, **events(co["cik"], a.since, a.limit))
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
