"""
SochDB Context Retrieval Example
================================

Demonstrates a simple token-budgeted retrieval flow using the
built-in collection search APIs (vector, keyword, hybrid).
"""

import os
import glob
import sys
from pathlib import Path
from typing import List

from sochdb import Database
sys.path.insert(0, str(Path(__file__).parent.parent))

from demos.shared.embeddings import EmbeddingClient
import tiktoken
import sochdb


def ensure_lib_path():
    if os.environ.get("SOCHDB_LIB_PATH"):
        return
    lib_root = os.path.join(os.path.dirname(sochdb.__file__), "lib")
    candidates = glob.glob(os.path.join(lib_root, "*", "libsochdb_index.*"))
    if candidates:
        os.environ["SOCHDB_LIB_PATH"] = candidates[0]


def token_budget_pick(chunks: List[str], budget: int) -> List[str]:
    enc = tiktoken.encoding_for_model("gpt-4")
    picked = []
    used = 0
    for chunk in chunks:
        count = len(enc.encode(chunk))
        if used + count > budget:
            break
        picked.append(chunk)
        used += count
    return picked


def main():
    ensure_lib_path()

    print("=== SochDB Context Retrieval Example ===\n")

    db = Database.open("./context_example_db")
    ns = db.get_or_create_namespace("docs")

    # Create collection with hybrid search enabled
    try:
        collection = ns.create_collection("docs", dimension=1536, enable_hybrid_search=True)
    except Exception:
        collection = ns.get_collection("docs")

    embedding_client = EmbeddingClient()

    documents = [
        {
            "id": "doc1",
            "text": "SochDB is an AI-native database designed for LLM applications. It features vector search and durable transactions.",
            "metadata": {"source": "readme", "category": "overview"},
        },
        {
            "id": "doc2",
            "text": "Vector search in SochDB uses HNSW indexes for fast approximate nearest neighbor search.",
            "metadata": {"source": "docs", "category": "features"},
        },
        {
            "id": "doc3",
            "text": "Graph operations allow typed nodes and edges with BFS/DFS traversal.",
            "metadata": {"source": "docs", "category": "features"},
        },
        {
            "id": "doc4",
            "text": "SochDB supports embedded mode and server mode for flexible deployment.",
            "metadata": {"source": "docs", "category": "deployment"},
        },
    ]

    print("1. Storing documents...")
    for doc in documents:
        embedding = embedding_client.embed(doc["text"])
        collection.insert(
            id=doc["id"],
            vector=embedding,
            metadata=doc["metadata"],
            content=doc["text"],
        )
    print(f"   Stored {len(documents)} documents")

    print("\n2. Vector search with token budget...")
    query = "How does vector search work?"
    query_embedding = embedding_client.embed(query)
    results = collection.vector_search(vector=query_embedding, k=5)

    chunks = [r.metadata.get("_content", "") for r in results.results if r.metadata]
    picked = token_budget_pick(chunks, budget=120)

    print(f"   Query: {query}")
    print(f"   Token budget: 120")
    print(f"   Selected {len(picked)} chunks")
    for chunk in picked:
        print(f"   - {chunk[:60]}...")

    print("\n3. Keyword search...")
    kw_results = collection.keyword_search(query="deployment", k=3)
    for r in kw_results.results:
        content = (r.metadata or {}).get("_content", "")
        print(f"   - {content[:60]}...")

    print("\n4. Hybrid search (vector + keyword)...")
    hybrid = collection.hybrid_search(vector=query_embedding, text_query="vector search HNSW", k=3, alpha=0.7)
    for r in hybrid.results:
        content = (r.metadata or {}).get("_content", "")
        print(f"   - {content[:60]}...")

    db.close()
    print("\n=== Context Retrieval Example Complete ===")


if __name__ == "__main__":
    main()
