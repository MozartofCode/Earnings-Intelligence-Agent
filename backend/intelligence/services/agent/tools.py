"""LangChain tools available to the earnings intelligence agent.

Implements:
  get_sec_filings(ticker, form_type="10-K", count=2)
      Resolve ticker -> CIK via https://www.sec.gov/files/company_tickers.json,
      then list recent filings from
      https://data.sec.gov/submissions/CIK{cik}.json.

  fetch_filing_text(filing_url)
      Fetch and extract text from a filing index URL.

  search_earnings_transcript(ticker, quarter="latest")
  search_analyst_reports(ticker)
  search_company_news(ticker)
      Provider-agnostic web search tools, switched via SEARCH_PROVIDER
      ("duckduckgo" needs no key; "tavily" needs TAVILY_API_KEY).

Export an ALL_TOOLS list here for graph.py to bind to the LLM via
`llm.bind_tools(ALL_TOOLS)`.
"""

import os
from typing import Optional

import requests
from bs4 import BeautifulSoup
from langchain_core.tools import tool

SEC_USER_AGENT = os.getenv(
    "EDGAR_USER_AGENT", "Earnings Intelligence Agent (set EDGAR_USER_AGENT in .env)"
)
SEC_HEADERS = {"User-Agent": SEC_USER_AGENT}

_TICKER_CACHE: Optional[dict] = None


def _load_ticker_map() -> dict:
    """Fetch and cache the SEC ticker -> CIK map."""
    global _TICKER_CACHE
    if _TICKER_CACHE is not None:
        return _TICKER_CACHE

    resp = requests.get(
        "https://www.sec.gov/files/company_tickers.json", headers=SEC_HEADERS, timeout=15
    )
    resp.raise_for_status()
    data = resp.json()

    _TICKER_CACHE = {
        entry["ticker"].upper(): {
            "cik": str(entry["cik_str"]).zfill(10),
            "title": entry["title"],
        }
        for entry in data.values()
    }
    return _TICKER_CACHE


def _resolve_cik(ticker: str) -> dict:
    ticker_map = _load_ticker_map()
    entry = ticker_map.get(ticker.upper())
    if not entry:
        raise ValueError(f"Could not resolve ticker '{ticker}' to a SEC CIK.")
    return entry


@tool
def get_sec_filings(ticker: str, form_type: str = "10-K", count: int = 2) -> list[dict]:
    """List the most recent SEC filings of a given form type for a ticker.

    Returns a list of dicts with accession_number, filing_date, form,
    primary_document, and filing_url (the index page for that filing).
    """
    entry = _resolve_cik(ticker)
    cik = entry["cik"]

    resp = requests.get(
        f"https://data.sec.gov/submissions/CIK{cik}.json", headers=SEC_HEADERS, timeout=15
    )
    resp.raise_for_status()
    recent = resp.json().get("filings", {}).get("recent", {})

    results = []
    forms = recent.get("form", [])
    for i, form in enumerate(forms):
        if form != form_type:
            continue
        accession = recent["accessionNumber"][i]
        accession_nodash = accession.replace("-", "")
        primary_doc = recent["primaryDocument"][i]
        results.append(
            {
                "accession_number": accession,
                "filing_date": recent["filingDate"][i],
                "form": form,
                "primary_document": primary_doc,
                "filing_url": (
                    f"https://www.sec.gov/Archives/edgar/data/"
                    f"{int(cik)}/{accession_nodash}/{primary_doc}"
                ),
            }
        )
        if len(results) >= count:
            break

    return results


@tool
def fetch_filing_text(filing_url: str, max_chars: int = 20000) -> str:
    """Fetch a SEC filing document and return its plain text, truncated to max_chars."""
    resp = requests.get(filing_url, headers=SEC_HEADERS, timeout=20)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.content, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()

    text = " ".join(soup.get_text(separator=" ").split())
    return text[:max_chars]


def _web_search(query: str, max_results: int = 5) -> list[dict]:
    provider = os.getenv("SEARCH_PROVIDER", "duckduckgo").lower()

    if provider == "tavily":
        from tavily import TavilyClient

        client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        response = client.search(query=query, max_results=max_results)
        return [
            {"title": r.get("title", ""), "href": r.get("url", ""), "body": r.get("content", "")}
            for r in response.get("results", [])
        ]

    from ddgs import DDGS

    with DDGS() as ddgs:
        return list(ddgs.text(query, max_results=max_results))


@tool
def search_earnings_transcript(ticker: str, quarter: str = "latest") -> list[dict]:
    """Search the web for the most recent earnings call transcript for a ticker."""
    return _web_search(f"{ticker} {quarter} earnings call transcript")


@tool
def search_analyst_reports(ticker: str) -> list[dict]:
    """Search the web for recent analyst ratings, price targets, and consensus for a ticker."""
    return _web_search(f"{ticker} stock analyst rating price target consensus")


@tool
def search_company_news(ticker: str) -> list[dict]:
    """Search the web for recent news about a company's ticker."""
    return _web_search(f"{ticker} stock news")


ALL_TOOLS: list = [
    get_sec_filings,
    fetch_filing_text,
    search_earnings_transcript,
    search_analyst_reports,
    search_company_news,
]
