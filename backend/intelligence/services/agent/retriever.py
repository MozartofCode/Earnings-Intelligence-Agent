"""RAG retrieval layer for the earnings intelligence agent.

STUB — intentionally left unimplemented. This is the part of the project
meant to be built by hand as a learning exercise.

Intended design (see the original build plan):

  build_retriever(documents, ticker)
      A ParentDocumentRetriever backed by Chroma (persisted under
      CHROMA_PERSIST_DIR) with HuggingFace `all-MiniLM-L6-v2` embeddings.
      Child chunks (~400 tokens) are embedded for precise matches; parent
      chunks (~2000 tokens) are returned for full context.

  multi_query_retrieve(retriever, ticker)
      Runs several targeted queries (revenue/margins, competitive risks,
      management outlook, business model, YoY results, analyst consensus,
      red flags) against the retriever, dedupes results, and returns a
      single formatted context string for generate_brief_node in graph.py.
"""


def build_retriever(documents, ticker):
    raise NotImplementedError(
        "The RAG retriever has not been implemented yet. "
        "Build it in intelligence/services/agent/retriever.py."
    )


def multi_query_retrieve(retriever, ticker):
    raise NotImplementedError(
        "The RAG retriever has not been implemented yet. "
        "Build it in intelligence/services/agent/retriever.py."
    )
