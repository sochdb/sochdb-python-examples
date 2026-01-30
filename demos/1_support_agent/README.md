# Support Agent Demo

Demo-grade support agent showcasing SochDB's SQL, KV, vector RAG, TOON encoding, and ACID transactions.

## What This Demo Shows

1. **SQL Queries** (`execute_sql`): Fetch customer orders from relational tables
2. **KV Storage**: Retrieve user preferences from key-value store
3. **Vector RAG**: Hybrid search over embedded policy chunks (vector + keyword)
4. **TOON Encoding**: Convert SQL rows to compact TOON format (40-67% token savings vs JSON)
5. **ACID Transactions**: Atomically update orders + create tickets + log audits
6. **Hybrid Storage**: Single DB for SQL + KV + vectors (no glue code)

## Setup

### 1. Install Dependencies

```bash
./../../venv/bin/pip install openai tiktoken
```

### 2. Set OpenAI API Key

```bash
# Azure OpenAI (preferred)
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_API_KEY="your_api_key"
export AZURE_OPENAI_API_VERSION="2024-12-01-preview"
export AZURE_OPENAI_CHAT_DEPLOYMENT="your-deployment"
export AZURE_OPENAI_EMBEDDING_DEPLOYMENT="text-embedding-3-small"
```

### 3. Initialize Database

```bash
cd demos/1_support_agent
./../../venv/bin/python setup_db.py
```

This creates:
- SQL tables: `orders`, `tickets`, `audit_logs`
- Sample order data (5 orders)
- User preferences in KV store
- Vector-indexed policy documents

## Usage

### Run Interactive Demo

```bash
./../../venv/bin/python run_demo.py
```

Non-interactive runs (CI) default to scenario 1.

Select from predefined scenarios or enter custom queries.

### Run Programmatically

```python
from agent import SupportAgent

agent = SupportAgent()
result = agent.handle_query(
    user_id=123,
    user_question="My order is late. Can you reroute it?"
)
print(result["response"])
```

## Example Session

```
User 123: My order #1004 is late. I'm traveling tomorrow. Can you reroute or replace it?

📊 Fetching order data from SQL...
   Found 3 orders

🔧 Encoding orders to TOON format...
   orders[3]{id,status,eta,destination,total}:
   1004,LATE,2025-12-31,123 Main St\, Seattle\, WA 98101,199.99
   1002,DELIVERED,2025-12-30,123 Main St\, Seattle\, WA 98101,79.99
   1001,IN_TRANSIT,2026-01-02,123 Main St\, Seattle\, WA 98101,149.99

👤 Fetching user preferences from KV...
   User: Alice Johnson
   Preferences: {replacements_over_refunds: true}

🔍 Retrieving relevant policies (vector RAG)...
   Retrieved 5 policy chunks
   Token budget used: ~1150 tokens

💬 Generating LLM response...
   [Agent suggests reroute or replacement based on policies]

⚡ Executing ACID transaction: reroute order...
   ✓ Updated order status
   ✓ Created support ticket
   ✓ Logged audit trail
```

## Key Highlights

### TOON Token Savings

Compare same data in JSON vs TOON:

**JSON (verbose)**:
```json
[
  {"id": 1004, "status": "LATE", "eta": "2025-12-31", ...},
  {"id": 1002, "status": "DELIVERED", "eta": "2025-12-30", ...}
]
```
Tokens: ~120

**TOON (compact)**:
```
orders[2]{id,status,eta,destination,total}:
1004,LATE,2025-12-31,123 Main St\, Seattle\, WA 98101,199.99
1002,DELIVERED,2025-12-30,123 Main St\, Seattle\, WA 98101,79.99
```
Tokens: ~55

**Savings: ~54% (65 fewer tokens)**

### No Glue Code

Everything lives in one SochDB instance:
- SQL: Operational data (orders, tickets)
- KV: User preferences
- Vectors: Policy documents with HNSW index
- Transactions: ACID guarantees across all stores

No need for separate Postgres + Redis + Pinecone + orchestration layer.

## Architecture

```
User Query
    ↓
[SQL Query] → Fetch orders → [TOON Encoder] → Compact representation
    ↓
[KV Lookup] → User prefs
    ↓
[Vector Search] → Policy RAG → [Hybrid Search] → Token-budgeted context
    ↓
[LLM] → Generate response
    ↓
[ACID Transaction] → Update order + Create ticket + Audit log
```

## Files

- `setup_db.py`: Initialize database with schema and sample data
- `agent.py`: Main support agent implementation
- `run_demo.py`: Interactive demo runner
- `policies/`: Policy documents for RAG retrieval
  - `late_shipment.txt`: Late shipment resolution guidelines
  - `replacement_policy.txt`: Replacement eligibility and process
  - `reroute_guidelines.txt`: Reroute validation and fees
