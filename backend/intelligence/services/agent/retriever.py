"""RAG retrieval layer for the earnings intelligence agent.

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

import os

from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

_EMBEDDINGS = None


def _get_embeddings():
    global _EMBEDDINGS
    if _EMBEDDINGS is None:
        _EMBEDDINGS = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return _EMBEDDINGS


def build_retriever(documents: list[str], ticker: str) -> ParentDocumentRetriever:
    """Build a ParentDocumentRetriever over the raw text collected for `ticker`."""
    persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")

    parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    child_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)

    vectorstore = Chroma(
        collection_name=f"earnings_{ticker.lower()}",
        embedding_function=_get_embeddings(),
        persist_directory=persist_dir,
    )
    store = InMemoryStore()

    retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=store,
        child_splitter=child_splitter,
        parent_splitter=parent_splitter,
    )

    docs = [Document(page_content=text, metadata={"ticker": ticker}) for text in documents if text]
    if docs:
        retriever.add_documents(docs)

    return retriever


_QUERY_TEMPLATES = [
    "revenue, margins, and growth rates",
    "competitive and regulatory risks",
    "management outlook and guidance",
    "business model and how the company makes money",
    "year-over-year results compared to prior quarter",
    "analyst consensus and price targets",
    "red flags or concerns disclosed in filings",
]


def multi_query_retrieve(retriever: ParentDocumentRetriever, ticker: str, k: int = 4) -> str:
    """Run several targeted queries against `retriever` and return deduped context."""
    seen: set[str] = set()
    chunks: list[str] = []

    for topic in _QUERY_TEMPLATES:
        query = f"{ticker} {topic}"
        try:
            results = retriever.invoke(query)
        except Exception:
            continue

        for doc in results[:k]:
            content = doc.page_content
            if content not in seen:
                seen.add(content)
                chunks.append(content)

    return "\n\n---\n\n".join(chunks)
