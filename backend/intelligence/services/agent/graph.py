"""LangGraph state machine for the earnings intelligence agent.

STUB — intentionally left unimplemented. This is the part of the project
meant to be built by hand as a learning exercise.

Intended design (see the original build plan):

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

`views.TickerViewSet.analyze` calls `build_graph()` and expects to
`.invoke()`/`.ainvoke()` the compiled graph with an initial AgentState,
then persist the returned `brief` into an `intelligence.models.EarningsBrief`
row. Wire that persistence step here (or back in views.py) once the graph
is implemented.
"""


def build_graph():
    raise NotImplementedError(
        "The LangGraph agent has not been implemented yet. "
        "Build it in intelligence/services/agent/graph.py."
    )
