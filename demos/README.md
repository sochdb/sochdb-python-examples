# SochDB Demo Use Cases

Three demo-grade, agentic use cases showcasing SochDB's capabilities:

1. **"Real database stuff"**: SQL, KV, transactions (ACID/MVCC/WAL/SSI)
2. **"Agent memory + retrieval"**: Vectors, ContextQuery, TOON, token budgeting

Each demo maps directly to SochDB features: TOON encoding, ContextQuery, HNSW vectors, ACID transactions, Embedded + IPC modes, hybrid search, and multi-vector documents.

---

## Demos

### 1. [Support Agent](./1_support_agent/) - "Where's my order?"

**RAG + SQL + Transactional Writes**

An AI support agent that handles customer order inquiries using SQL queries, KV preferences, vector-retrieved policies, TOON-encoded context, and ACID transactions.

**Showcases**:
- ✅ SQL queries (`execute_sql`) for order data
- ✅ KV storage for user preferences
- ✅ Vector RAG with `ContextQuery` and token budgeting
- ✅ TOON encoding (40-67% token savings vs JSON)
- ✅ ACID transactions (update order + create ticket + audit log)
- ✅ Hybrid storage: SQL + KV + vectors in one DB

**Key Highlight**: TOON reduces prompt tokens by ~67% compared to JSON for tabular data.

[→ See Demo 1 README](./1_support_agent/README.md)

---

### 2. [Incident Response](./2_incident_response/) - Multi-Agent IPC

**Shared Memory + Retrieval Across Processes**

Three concurrent processes share a single SochDB instance via IPC (Unix socket) to detect, analyze, and mitigate production incidents using hybrid retrieval.

**Showcases**:
- ✅ IPC mode: multiple processes, one shared DB
- ✅ Namespace isolation (`incident_ops`)
- ✅ Hybrid retrieval: vector + keyword with RRF
- ✅ ACID state transitions (OPEN → MITIGATING → RESOLVED)
- ✅ Concurrent writes without conflicts
- ✅ Token-budgeted runbook retrieval

**Key Highlight**: In this repo, the demo runs sequentially in embedded mode for repeatable CLI output. IPC server mode is documented but not exposed in the current Python SDK.

[→ See Demo 2 README](./2_incident_response/README.md)

---

### 3. [Analytics Copilot](./3_analytics_copilot/) - Spreadsheet to Agent Memory

**TOON for Tabular Data + Vector Search**

Upload a CSV, run SQL analytics, encode results in TOON, search notes semantically, and get AI-powered churn analysis—all under strict token budgets.

**Showcases**:
- ✅ CSV ingestion to SQL tables
- ✅ TOON encoding (40-67% token savings)
- ✅ Vector search over text fields (customer notes)
- ✅ Token-budgeted context assembly via `ContextQuery`
- ✅ SQL + vectors in one database (no ETL)
- ✅ Actual token count measurements with `tiktoken`

**Key Highlight**: Proves TOON savings with concrete measurements (e.g., 156 → 52 tokens = 67% reduction).

[→ See Demo 3 README](./3_analytics_copilot/README.md)

---

## Feature Matrix

| Feature | Demo 1 | Demo 2 | Demo 3 |
|---------|--------|--------|--------|
| **SQL (execute_sql)** | ✅ Orders, tickets, audit logs | ✅ State tracking | ✅ Customer analytics |
| **KV Storage** | ✅ User preferences | ✅ Metrics, incidents | ✅ - |
| **Vector Search (HNSW)** | ✅ Policy retrieval | ✅ Runbook retrieval | ✅ Customer notes |
| **TOON Encoding** | ✅ Order rows | - | ✅ Analytics results |
| **ContextQuery + Token Budget** | ✅ 1200 token limit | ✅ 2000 token limit | ✅ 1000 token limit |
| **Hybrid Search (vector+keyword)** | ✅ RRF for policies | ✅ RRF for runbooks | ✅ RRF for notes |
| **ACID Transactions** | ✅ Multi-table writes | ✅ State transitions | ✅ - |
| **IPC Mode** | - | ✅ 3 processes | - |
| **Namespace Isolation** | ✅ `support_system` | ✅ `incident_ops` | ✅ `analytics` |

---

## Quick Start

### Prerequisites

```bash
# Install SochDB + deps (venv already provided in this repo)
./venv/bin/pip install openai tiktoken

# Set LLM credentials (either Azure OpenAI or OpenAI)
# Azure (preferred for this repo)
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_API_KEY="your_api_key"
export AZURE_OPENAI_API_VERSION="2024-12-01-preview"
export AZURE_OPENAI_CHAT_DEPLOYMENT="your-deployment"
export AZURE_OPENAI_EMBEDDING_DEPLOYMENT="text-embedding-3-small"

# Or OpenAI (optional)
export OPENAI_API_KEY="your-openai-key"
```

### Run Demos

```bash
# Demo 1: Support Agent
cd 1_support_agent
./../../venv/bin/python setup_db.py
./../../venv/bin/python run_demo.py

# Demo 2: Incident Response (requires separate terminals)
cd 2_incident_response
PATH=./../../venv/bin:$PATH ./run_demo.sh

# Demo 3: Analytics Copilot
cd 3_analytics_copilot
./../../venv/bin/python token_comparison.py  # See TOON vs JSON savings
./../../venv/bin/python run_demo.py          # Interactive churn analysis
```

---

## Architecture Patterns

### Pattern 1: Single-Process Agent (Demo 1, 3)

```
User Query
    ↓
[SQL Query] → Operational data
    ↓
[KV Lookup] → User preferences
    ↓
[Vector Search] → Knowledge retrieval
    ↓
[ContextQuery] → Token-budgeted context
    ↓
[TOON Encoding] → Compact format
    ↓
[LLM] → Generate response
    ↓
[ACID Transaction] → Atomic writes
```

**Everything in one SochDB instance. No glue code.**

### Pattern 2: Multi-Process IPC (Demo 2)

```
Process A (Collector) ────┐
                          ├──→ SochDB Server (IPC)
Process B (Indexer)   ────┤         ↓
                          │    Shared State
Process C (Commander) ────┘    - KV paths
                               - Vector collection
                               - SQL tables
```

**Multiple agents, one source of truth, Unix socket.**

---

## Why These Demos Matter

### 1. Developer Experience

Traditional stack:
- Postgres (SQL)
- Redis (KV)
- Pinecone/Weaviate (vectors)
- Custom orchestration layer
- ETL pipelines between systems

SochDB stack:
- **SochDB** (SQL + KV + vectors)
- Done.

### 2. Token Efficiency

JSON example (from SochDB README):
```json
[{"id": 1, "name": "Alice", "email": "alice@example.com"}]
```
**156 tokens**

TOON example:
```
users[1]{id,name,email}:
1,Alice,alice@example.com
```
**52 tokens** (67% reduction)

### 3. Production-Ready Features

- **ACID/MVCC/WAL/SSI**: Demo 1 shows atomic multi-table transactions
- **HNSW Vectors**: All demos use efficient vector search
- **Token Budgeting**: `ContextQuery` prevents prompt overflow
- **IPC**: Demo 2 shows multi-process collaboration
- **Hybrid Search**: RRF combines vector + keyword retrieval

---

## Project Structure

```
demos/
├── README.md                         # This file
├── shared/                           # Shared utilities
│   ├── toon_encoder.py              # TOON format encoder
│   ├── llm_client.py                # OpenAI wrapper
│   └── embeddings.py                # Embedding client
├── 1_support_agent/
│   ├── README.md
│   ├── setup_db.py
│   ├── agent.py
│   ├── run_demo.py
│   └── policies/                    # RAG documents
├── 2_incident_response/
│   ├── README.md
│   ├── start_server.sh
│   ├── process_a_collector.py
│   ├── process_b_indexer.py
│   ├── process_c_commander.py
│   ├── run_demo.sh
│   └── runbooks/                    # RAG documents
└── 3_analytics_copilot/
    ├── README.md
    ├── copilot.py
    ├── token_comparison.py
    ├── run_demo.py
    └── sample_data/
        └── customers.csv
```

---

## Requirements

All demos share the same dependencies:

```
sochdb>=0.3.3
openai>=1.0.0
tiktoken>=0.5.0
```

Install globally or use per-demo `requirements.txt`.

---

## Links

- [SochDB Main Repo](https://github.com/sochdb/sochdb)
- [Python SDK](https://github.com/sochdb/sochdb-python-sdk)
- [Node.js SDK](https://github.com/sochdb/sochdb-js)
- [Go SDK](https://github.com/sochdb/sochdb-go)

---

## Credits

These demos showcase SochDB's core capabilities:
- **TOON format** for token-efficient tabular data
- **ContextQuery** for retrieval with budgets
- **HNSW vectors** for fast semantic search
- **ACID/MVCC** for transactional consistency
- **IPC mode** for multi-process agents
- **Hybrid search** with RRF

All features are production-ready and available in SochDB 0.3+.
