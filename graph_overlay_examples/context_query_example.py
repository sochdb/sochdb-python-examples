"""
ToonDB Context Query Example
============================

Demonstrates the Context Query Engine for token-aware retrieval
in LLM applications.

Features shown:
- Token budgeting for context windows
- Semantic deduplication
- Provenance tracking
- Vector + keyword hybrid search
- Priority-ordered selection
"""

import toondb
from toondb.context import (
    ContextQuery, ContextChunk, ContextResult,
    DeduplicationStrategy, TokenEstimator,
    FusionStrategy
)

def main():
    # Open database and create context query engine
    db = toondb.open("./context_example_db")
    
    print("=== ToonDB Context Query Example ===\n")
    
    # -------------------------------------------------------
    # 1. Store some documents for retrieval
    # -------------------------------------------------------
    print("1. Storing documents...")
    
    documents = [
        {
            "id": "doc1",
            "text": "ToonDB is an AI-native database designed for LLM applications. "
                    "It features token-optimized output, O(|path|) lookups, built-in "
                    "vector search, and durable transactions.",
            "metadata": {"source": "readme", "category": "overview"}
        },
        {
            "id": "doc2", 
            "text": "Vector search in ToonDB uses HNSW indexes for fast approximate "
                    "nearest neighbor search. The index supports both cosine and "
                    "euclidean distance metrics.",
            "metadata": {"source": "docs", "category": "features"}
        },
        {
            "id": "doc3",
            "text": "The Graph Overlay feature allows building lightweight graph "
                    "structures on top of ToonDB's key-value storage. It supports "
                    "typed edges, BFS/DFS traversal, and property storage.",
            "metadata": {"source": "docs", "category": "features"}
        },
        {
            "id": "doc4",
            "text": "Policy hooks provide trigger-based guardrails for agent operations. "
                    "Use @before_write, @after_read, and @before_delete decorators "
                    "to implement validation, redaction, and access control.",
            "metadata": {"source": "docs", "category": "security"}
        },
        {
            "id": "doc5",
            "text": "ToonDB supports multiple deployment surfaces including embedded mode, "
                    "IPC sockets, and gRPC. Use the unified connect() API with URI "
                    "patterns like file://, ipc://, or grpc://.",
            "metadata": {"source": "docs", "category": "deployment"}
        },
    ]
    
    for doc in documents:
        db.put(f"docs/{doc['id']}", doc)
    print(f"   Stored {len(documents)} documents")
    
    # -------------------------------------------------------
    # 2. Basic context query with token budget
    # -------------------------------------------------------
    print("\n2. Basic context query with token budget...")
    
    query = (ContextQuery(db, collection="docs")
        .with_token_budget(500)  # Max 500 tokens
        .with_query("How does vector search work?")
        .with_top_k(3))
    
    result = query.execute()
    
    print(f"   Query: 'How does vector search work?'")
    print(f"   Token budget: 500")
    print(f"   Results: {len(result.chunks)} chunks")
    print(f"   Total tokens used: {result.total_tokens}")
    
    for chunk in result.chunks:
        print(f"   - [{chunk.score:.2f}] {chunk.text[:60]}...")
    
    # -------------------------------------------------------
    # 3. Token estimator configuration
    # -------------------------------------------------------
    print("\n3. Token estimator configuration...")
    
    # Use different token estimators
    estimators = {
        "gpt4": TokenEstimator.gpt4(),      # GPT-4 tokenizer (cl100k_base)
        "claude": TokenEstimator.claude(),   # Claude tokenizer
        "simple": TokenEstimator.simple(),   # Simple word-based (~4 chars/token)
    }
    
    sample_text = "This is a sample text to demonstrate token counting differences."
    
    for name, estimator in estimators.items():
        tokens = estimator.estimate(sample_text)
        print(f"   {name}: {tokens} tokens")
    
    # -------------------------------------------------------
    # 4. Semantic deduplication
    # -------------------------------------------------------
    print("\n4. Semantic deduplication...")
    
    # Store some similar documents
    similar_docs = [
        {"id": "dup1", "text": "ToonDB supports vector search using HNSW indexes."},
        {"id": "dup2", "text": "Vector search in ToonDB uses HNSW indexes."},  # Similar
        {"id": "dup3", "text": "HNSW indexes power ToonDB's vector search."},   # Similar
        {"id": "unique", "text": "Policy hooks enable validation and access control."},
    ]
    for doc in similar_docs:
        db.put(f"similar/{doc['id']}", doc)
    
    # Without deduplication
    query_no_dedup = (ContextQuery(db, collection="similar")
        .with_query("vector search")
        .with_deduplication(DeduplicationStrategy.NONE)
        .with_top_k(10))
    result1 = query_no_dedup.execute()
    print(f"   Without dedup: {len(result1.chunks)} chunks")
    
    # With semantic deduplication
    query_with_dedup = (ContextQuery(db, collection="similar")
        .with_query("vector search")
        .with_deduplication(DeduplicationStrategy.SEMANTIC)
        .with_top_k(10))
    result2 = query_with_dedup.execute()
    print(f"   With semantic dedup: {len(result2.chunks)} chunks")
    
    # -------------------------------------------------------
    # 5. Provenance tracking
    # -------------------------------------------------------
    print("\n5. Provenance tracking...")
    
    query = (ContextQuery(db, collection="docs")
        .with_query("deployment options")
        .with_provenance(True)
        .with_top_k(2))
    
    result = query.execute()
    
    for chunk in result.chunks:
        print(f"   Chunk: {chunk.id}")
        print(f"   - Source: {chunk.provenance.get('source', 'unknown')}")
        print(f"   - Category: {chunk.provenance.get('category', 'unknown')}")
        print(f"   - Retrieved at: {chunk.provenance.get('timestamp', 'unknown')}")
    
    # -------------------------------------------------------
    # 6. Hybrid search (vector + keyword)
    # -------------------------------------------------------
    print("\n6. Hybrid search (vector + keyword)...")
    
    # Configure hybrid search with RRF fusion
    query = (ContextQuery(db, collection="docs")
        .with_query("graph traversal BFS DFS")
        .with_vector_search(enabled=True, weight=0.7)
        .with_keyword_search(enabled=True, weight=0.3)
        .with_fusion(FusionStrategy.RRF, k=60)
        .with_top_k(3))
    
    result = query.execute()
    
    print(f"   Hybrid query: 'graph traversal BFS DFS'")
    print(f"   Vector weight: 0.7, Keyword weight: 0.3")
    print(f"   Fusion: RRF (k=60)")
    print(f"   Results: {len(result.chunks)} chunks")
    
    # -------------------------------------------------------
    # 7. Priority-ordered selection
    # -------------------------------------------------------
    print("\n7. Priority-ordered selection...")
    
    # Store documents with priorities
    priority_docs = [
        {"id": "p1", "text": "Low priority doc about databases", "priority": 1},
        {"id": "p2", "text": "Medium priority doc about features", "priority": 5},
        {"id": "p3", "text": "High priority doc about security", "priority": 10},
    ]
    for doc in priority_docs:
        db.put(f"priority/{doc['id']}", doc)
    
    query = (ContextQuery(db, collection="priority")
        .with_query("doc")
        .with_priority_field("priority")  # Sort by priority
        .with_top_k(3))
    
    result = query.execute()
    
    print("   Documents ordered by priority:")
    for chunk in result.chunks:
        print(f"   - {chunk.id}: priority={chunk.metadata.get('priority')}")
    
    # -------------------------------------------------------
    # 8. Context for different LLM windows
    # -------------------------------------------------------
    print("\n8. Context for different LLM windows...")
    
    windows = {
        "GPT-3.5": 4096,
        "GPT-4": 8192,
        "GPT-4-Turbo": 128000,
        "Claude-3": 200000,
    }
    
    for model, max_tokens in windows.items():
        # Reserve 1000 tokens for response, 500 for system prompt
        available = max_tokens - 1500
        
        query = (ContextQuery(db, collection="docs")
            .with_token_budget(available)
            .with_query("all features")
            .with_top_k(20))
        
        result = query.execute()
        print(f"   {model} ({max_tokens} tokens): "
              f"{len(result.chunks)} chunks, {result.total_tokens} tokens used")
    
    # -------------------------------------------------------
    # 9. Building context string
    # -------------------------------------------------------
    print("\n9. Building context string...")
    
    query = (ContextQuery(db, collection="docs")
        .with_token_budget(300)
        .with_query("ToonDB features")
        .with_top_k(2))
    
    result = query.execute()
    
    # Build a formatted context string for LLM
    context_str = result.to_context_string(
        format="markdown",
        include_metadata=True,
        separator="\n---\n"
    )
    
    print("   Generated context:")
    print("   " + context_str[:200].replace("\n", "\n   ") + "...")
    
    # Cleanup
    db.close()
    print("\n=== Context Query Example Complete ===")

if __name__ == "__main__":
    main()
