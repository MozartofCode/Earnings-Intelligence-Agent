#!/usr/bin/env python3
"""Redline a 10-K/10-Q section against the prior filing. Stdlib only.

Usage
  python3 diff_sections.py TICKER [--form 10-K] [--section 1A] [--new 0] [--old 1] [--max-items 40]
  python3 diff_sections.py --files old.txt new.txt

Sections: 1A (risk factors), 7 / mdna (MD&A), 1 (business), 3 (legal), 7a, 9a, or any heading text.
For 10-Q MD&A use --form 10-Q --section mdna. Indexes count only filings of that form (plus its /A
amendments), and a fiscal year has three 10-Qs (Q4 is in the 10-K), so --old 3 is the same
quarter last year (--old 1 is the prior quarter). Check `edgar.py filings` first if amendments exist.

Output JSON:
  stats       paragraph counts, % of text changed, word-count delta
  added[]     new paragraphs (most important first: longest + risk-keyword hits)
  removed[]   deleted paragraphs
  changed[]   edited paragraphs with inline [-old-]{+new+} word diff
  lexicon     change in hedging / risk / litigation / AI / tariff vocabulary per 10k words
"""
import argparse
import difflib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "sec-edgar", "scripts"))

LEXICON = {
    "hedging": ["may", "might", "could", "possibly", "uncertain", "uncertainty", "no assurance", "cannot assure", "unpredictable"],
    "negative": ["decline", "decrease", "adverse", "adversely", "loss", "impairment", "weak", "headwind", "deteriorat"],
    "litigation": ["lawsuit", "litigation", "investigation", "subpoena", "settlement", "class action", "regulator", "doj", "ftc", "sec "],
    "liquidity": ["going concern", "covenant", "liquidity", "refinanc", "default", "credit facility"],
    "supply_chain": ["supply", "shortage", "supplier", "tariff", "export control", "sanction"],
    "ai": ["artificial intelligence", " ai ", "generative", "machine learning"],
    "cyber": ["cyber", "breach", "ransomware", "security incident"],
}
PRIORITY = re.compile(r"(material weakness|going concern|restat|investigation|subpoena|covenant|impairment|customer concentration|single source|export control|tariff|class action|default|downgrade|cybersecurity incident|layoff|restructur)", re.I)


def paragraphs(text):
    paras = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", text)]
    # drop page numbers, running headers and table-of-contents fragments
    return [p for p in paras if len(p) > 60 and not re.fullmatch(r"[\d\s|.\-]+", p)]


def norm(p):
    return re.sub(r"[^a-z0-9 ]", "", p.lower())


def word_diff(a, b, limit=1200):
    aw, bw = a.split(), b.split()
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, aw, bw, autojunk=False).get_opcodes():
        if op == "equal":
            seg = aw[i1:i2]
            out.append(" ".join(seg if len(seg) < 16 else seg[:6] + ["…"] + seg[-6:]))
        if op in ("delete", "replace"):
            out.append("[-" + " ".join(aw[i1:i2]) + "-]")
        if op in ("insert", "replace"):
            out.append("{+" + " ".join(bw[j1:j2]) + "+}")
    s = " ".join(out)
    return s[:limit] + ("…" if len(s) > limit else "")


def lex_rates(text):
    t = " " + text.lower() + " "
    words = max(len(t.split()), 1)
    return {k: round(sum(t.count(w) for w in ws) / words * 10000, 1) for k, ws in LEXICON.items()}


def score(p):
    return len(PRIORITY.findall(p)) * 1000 + len(p)


def diff(old_text, new_text, max_items=40):
    old_p, new_p = paragraphs(old_text), paragraphs(new_text)
    old_n = {norm(p): p for p in old_p}
    new_n = {norm(p): p for p in new_p}
    only_new = [p for k, p in new_n.items() if k not in old_n]
    only_old = [p for k, p in old_n.items() if k not in new_n]
    changed, added = [], []
    used_old = set()
    old_sets = {q: set(norm(q).split()) for q in only_old}
    for p in only_new:
        best, best_r = None, 0.0
        pset = set(norm(p).split())
        for q in only_old:
            if q in used_old:
                continue
            qs = old_sets[q]
            if len(pset & qs) / float(max(len(pset | qs), 1)) < 0.35:  # cheap Jaccard prefilter
                continue
            sm = difflib.SequenceMatcher(None, norm(q), norm(p), autojunk=False)
            if sm.real_quick_ratio() < 0.5 or sm.quick_ratio() < 0.5:
                continue
            r = sm.ratio()
            if r > best_r:
                best, best_r = q, r
        if best is not None and best_r >= 0.55:
            used_old.add(best)
            changed.append({"similarity": round(best_r, 2), "redline": word_diff(best, p), "new": p[:600], "priority_terms": sorted(set(m.lower() for m in PRIORITY.findall(p)))})
        else:
            added.append(p)
    removed = [q for q in only_old if q not in used_old]
    added.sort(key=score, reverse=True)
    removed.sort(key=score, reverse=True)
    changed.sort(key=lambda c: (len(c["priority_terms"]), 1 - c["similarity"]), reverse=True)
    ow, nw = len(old_text.split()), len(new_text.split())
    lo, ln = lex_rates(old_text), lex_rates(new_text)
    return {
        "stats": {"old_paragraphs": len(old_p), "new_paragraphs": len(new_p), "added": len(added), "removed": len(removed), "changed": len(changed),
                  "unchanged": len(new_p) - len(added) - len(changed), "old_words": ow, "new_words": nw, "word_delta_pct": round((nw / ow - 1) * 100, 1) if ow else None},
        "added": [{"text": p[:1500], "priority_terms": sorted(set(m.lower() for m in PRIORITY.findall(p)))} for p in added[:max_items]],
        "removed": [{"text": p[:1500], "priority_terms": sorted(set(m.lower() for m in PRIORITY.findall(p)))} for p in removed[:max_items]],
        "changed": changed[:max_items],
        "lexicon_per_10k_words": {k: {"old": lo[k], "new": ln[k], "delta": round(ln[k] - lo[k], 1)} for k in lo},
        "truncated": max(len(added), len(removed), len(changed)) > max_items,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("ticker", nargs="?")
    p.add_argument("--form", default="10-K")
    p.add_argument("--section", default="1A")
    p.add_argument("--new", type=int, default=0, help="index of the newer filing (0 = latest)")
    p.add_argument("--old", type=int, default=1, help="index of the older filing")
    p.add_argument("--max-items", type=int, default=40)
    p.add_argument("--files", nargs=2, metavar=("OLD", "NEW"))
    a = p.parse_args()
    if a.files:
        old, new = (open(f).read() for f in a.files)
        meta = {"old": a.files[0], "new": a.files[1]}
    else:
        if not a.ticker:
            p.error("TICKER or --files required")
        import edgar
        co = edgar.resolve(a.ticker)
        n = edgar.filing_text(co["cik"], a.form, a.new, a.section, max_chars=10 ** 7)
        o = edgar.filing_text(co["cik"], a.form, a.old, a.section, max_chars=10 ** 7)
        if not n["section_found"] or not o["section_found"]:
            edgar.die("Section '%s' not found in one of the filings. Try --section with the exact heading text, or read saved_to files directly." % a.section,
                      new_saved_to=n["saved_to"], old_saved_to=o["saved_to"])
        new, old = n["text"], o["text"]
        meta = dict(co, form=a.form, section=a.section, new_filing=n["filing"], old_filing=o["filing"])
    out = dict(meta, **diff(old, new, a.max_items))
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
