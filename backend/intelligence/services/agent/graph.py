"""LangGraph state machine for the earnings intelligence agent.

  AgentState (TypedDict):
      ticker, messages, raw_documents, retrieved_context, brief, errors

  Nodes:
      collect_data    — LLM decides which tools in tools.py to call to
                         gather 10-K/10-Q filings, transcripts, analyst
                         reports, and news for `ticker`.
      execute_tools    — runs whatever tool calls collect_data requested,
                         appends results to raw_documents.
      rag              — builds a retriever over raw_documents (see
                         retriever.py) and runs multi-query retrieval to
                         produce retrieved_context.
      generate_brief   — calls llm.with_structured_output(EarningsBrief)
                         (see output_schema.py) against retrieved_context
                         to produce the final structured brief.

  Edges:
      collect_data -> execute_tools -> rag -> generate_brief -> END
      (collect_data -> rag directly if the LLM made no tool calls)

`views.TickerViewSet.analyze` calls `build_graph()` and `.invoke()`s the
compiled graph with an initial AgentState, then persists the returned
`brief` into an `intelligence.models.EarningsBrief` row.
"""

import json
import os
from typing import Annotated, Optional, TypedDict

from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from .output_schema import EarningsBrief
from .retriever import build_retriever, multi_query_retrieve
from .tools import ALL_TOOLS

COLLECT_DATA_SYSTEM_PROMPT = """You are a financial research assistant gathering source \
material to write an earnings brief for the stock ticker {ticker}.

Call tools to collect what you need: recent 10-K/10-Q filings (use get_sec_filings then \
fetch_filing_text on the filing_url it returns), the latest earnings call transcript, \
analyst reports, and recent news. Make as many tool calls as you need, then stop once you \
have enough material to write a thorough brief."""


class AgentState(TypedDict):
    ticker: str
    messages: Annotated[list, add_messages]
    raw_documents: list[str]
    retrieved_context: str
    brief: Optional[dict]
    errors: list[str]


def _get_llm():
    provider = os.getenv("LLM_PROVIDER", "groq").lower()

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest"),
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0,
        )

    from langchain_groq import ChatGroq

    return ChatGroq(
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0,
    )


def collect_data_node(state: AgentState) -> dict:
    llm = _get_llm().bind_tools(ALL_TOOLS)

    messages = state["messages"]
    if not messages:
        messages = [
            {
                "role": "system",
                "content": COLLECT_DATA_SYSTEM_PROMPT.format(ticker=state["ticker"]),
            },
            {
                "role": "user",
                "content": f"Gather source material for an earnings brief on {state['ticker']}.",
            },
        ]

    response = llm.invoke(messages)
    return {"messages": [response]}


MESSAGE_PREVIEW_CHARS = 500


def execute_tools_node(state: AgentState) -> dict:
    tool_node = ToolNode(ALL_TOOLS)
    result = tool_node.invoke(state)

    new_docs = []
    errors = []
    trimmed_messages = []
    for msg in result["messages"]:
        content = msg.content if isinstance(msg.content, str) else json.dumps(msg.content)
        if getattr(msg, "status", None) == "error":
            errors.append(content)
        else:
            new_docs.append(content)

        # Full tool output goes to raw_documents for RAG; only a short preview
        # goes back into the LLM's conversation history, so large fetched
        # documents don't get re-sent (and re-billed) on every collect_data
        # round trip.
        if len(content) > MESSAGE_PREVIEW_CHARS:
            msg.content = content[:MESSAGE_PREVIEW_CHARS] + "... [truncated; full text retained for RAG]"
        trimmed_messages.append(msg)

    return {
        "messages": trimmed_messages,
        "raw_documents": state.get("raw_documents", []) + new_docs,
        "errors": state.get("errors", []) + errors,
    }


def rag_node(state: AgentState) -> dict:
    retriever = build_retriever(state.get("raw_documents", []), state["ticker"])
    context = multi_query_retrieve(retriever, state["ticker"])
    return {"retrieved_context": context}


def generate_brief_node(state: AgentState) -> dict:
    llm = _get_llm().with_structured_output(EarningsBrief)

    prompt = (
        f"Using the research context below, write a complete earnings brief for "
        f"{state['ticker']}.\n\nCONTEXT:\n{state['retrieved_context']}"
    )
    brief: EarningsBrief = llm.invoke(prompt)
    return {"brief": brief.model_dump()}


MAX_COLLECT_ROUNDS = 6


def _has_tool_calls(state: AgentState) -> str:
    last_message = state["messages"][-1]
    ai_rounds = sum(1 for m in state["messages"] if getattr(m, "type", None) == "ai")
    if ai_rounds < MAX_COLLECT_ROUNDS and getattr(last_message, "tool_calls", None):
        return "execute_tools"
    return "rag"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("collect_data", collect_data_node)
    graph.add_node("execute_tools", execute_tools_node)
    graph.add_node("rag", rag_node)
    graph.add_node("generate_brief", generate_brief_node)

    graph.set_entry_point("collect_data")
    graph.add_conditional_edges(
        "collect_data", _has_tool_calls, {"execute_tools": "execute_tools", "rag": "rag"}
    )
    graph.add_edge("execute_tools", "collect_data")
    graph.add_edge("rag", "generate_brief")
    graph.add_edge("generate_brief", END)

    return graph.compile()
