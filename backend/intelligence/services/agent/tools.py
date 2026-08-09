"""LangChain tools available to the earnings intelligence agent.

STUB — intentionally left unimplemented. This is the part of the project
meant to be built by hand as a learning exercise.

Intended tools (see the original build plan):

  get_sec_filings(ticker, form_type="10-K", count=2)
      Resolve ticker -> CIK via https://www.sec.gov/files/company_tickers.json,
      then list recent filings from
      https://data.sec.gov/submissions/CIK{cik}.json.
      Requires a SEC-compliant User-Agent header — see config.SEC_HEADERS
      pattern from the original plan.

  fetch_filing_text(filing_url)
      Fetch and extract text from a filing index URL.

  search_earnings_transcript(ticker, quarter="latest")
  search_analyst_reports(ticker)
  search_company_news(ticker)
      Provider-agnostic web search tools. Swap providers (DuckDuckGo /
      Tavily / Brave / Serper) via a config toggle, per the original plan's
      `get_search_tool()` pattern.

Export an ALL_TOOLS list here once implemented, and bind it to the LLM in
graph.py via `llm.bind_tools(ALL_TOOLS)`.
"""

ALL_TOOLS: list = []
