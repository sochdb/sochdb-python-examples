# Analytics Copilot Demo

Demo-grade analytics copilot showcasing SochDB's SQL, TOON encoding, vector search, and token-optimized context assembly for spreadsheet data analysis.

## What This Demo Shows

1. **CSV to SQL**: Load spreadsheet data into SQL tables for querying
2. **TOON Encoding**: Convert query results to compact TOON format (40-67% token savings)
3. **Vector Search**: Semantic search over customer notes/text fields
4. **Token Budgeting**: Pack relevant context under strict token limits (app-level)
5. **Unified Storage**: SQL + vectors in one database (no separate systems)
6. **Token Comparison**: Measure actual savings with tiktoken

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

## Usage

### Run Token Comparison

See TOON vs JSON token savings:

```bash
cd demos/3_analytics_copilot
./../../venv/bin/python token_comparison.py
```

**Expected Output**:
```
TOKEN COMPARISON: JSON vs TOON
==================================

JSON FORMAT:
[
  {"id": 1, "name": "Alice", "email": "alice@example.com", "age": 28},
  {"id": 2, "name": "Bob", "email": "bob@example.com", "age": 34},
  ...
]
Tokens: 120

TOONFORMAT:
users[3]{id,name,email,age}:
1,Alice,alice@example.com,28
2,Bob,bob@example.com,34
3,Carol,carol@example.com,42
Tokens: 55

RESULTS:
  Tokens saved:     65
  Percent saved:    54.2%
```

### Run Analytics Copilot

Interactive churn analysis:

```bash
./../../venv/bin/python run_demo.py
```

Non-interactive runs (CI) default to query 1.

Or programmatically:

```python
from copilot import AnalyticsCopilot

copilot = AnalyticsCopilot()
copilot.setup_database("sample_data/customers.csv")

result = copilot.analyze_churn_risk(
    "Which customers are most at risk of churn?"
)
print(result["response"])
```

## Demo Flow

### 1. Data Ingestion

Loads `customers.csv` into SQL table:

```
📥 Loading data from sample_data/customers.csv...
  ✓ Loaded 15 customers into SQL table
  
🔍 Indexing customer notes for semantic search...
  ✓ Indexed 15 customer notes

✅ Database setup complete!
```

### 2. SQL Query

Finds at-risk customers using SQL:

```sql
SELECT id, name, account_value, contract_end,
       monthly_active_days, support_tickets_30d,
       last_login_days_ago, feature_usage_score
FROM customers
WHERE (
    monthly_active_days < 15
    OR support_tickets_30d > 5
    OR last_login_days_ago > 7
    OR feature_usage_score < 50
)
ORDER BY feature_usage_score ASC
```

### 3. TOON Encoding

Converts results to compact format:

```
🔧 Encoding to TOON format...
  TOON tokens: 245 | JSON tokens: 580
  Saved: 335 tokens (57.8%)
```

**JSON (verbose)**:
```json
[
  {
    "id": 6,
    "name": "StartupXYZ",
    "account_value": 8000,
    "contract_end": "2026-01-30",
    "monthly_active_days": 4,
    "support_tickets_30d": 12,
    "last_login_days_ago": 18,
    "feature_usage_score": 22
  },
  ...
]
```

**TOON (compact)**:
```
at_risk_customers[8]{id,name,account_value,contract_end,monthly_active_days,support_tickets_30d,last_login_days_ago,feature_usage_score}:
6,StartupXYZ,8000,2026-01-30,4,12,18,22
10,MarketingGenius,35000,2026-05-18,6,10,15,28
...
```

### 4. Vector Search

Semantic search over customer notes:

```
🔍 Searching customer notes (vector semantic search)...
  Retrieved 5 relevant notes
  Token budget used: ~850 tokens
```

Finds notes about:
- Low engagement warnings
- Support ticket patterns
- Churn risk indicators

### 5. AI Analysis

LLM generates insights:

```
ANALYSIS RESULTS
================

Top Churn Risks:
1. StartupXYZ (#6) - CRITICAL: Contract ending Jan 30, very low engagement (22%)
2. MarketingGenius (#10) - High support load + low activity
3. TechStart Inc (#2) - Performance complaints + contract ending soon

Common Patterns:
- High support ticket volume (>5 in 30 days)
- Low monthly active days (<15)
- Declining feature usage scores

Recommended Interventions:
1. IMMEDIATE: Contact #6 (StartupXYZ) - contract expires in 26 days
2. Schedule retention calls with #10, #2
3. Offer performance optimization consultation to ticket-heavy accounts
```

## Sample Data

`sample_data/customers.csv` contains 15 customers with:
- Account metadata (value, contract end)
- Usage metrics (active days, feature usage score)
- Support indicators (ticket count, last login)
- Free-text notes (indexed for vector search)

Example row:
```csv
6,StartupXYZ,dev@startupxyz.io,8000,2026-01-30,4,12,18,22,"CRITICAL: Contract ending soon. Very low engagement. Many unresolved tickets. High churn risk."
```

## Key Highlights

### TOON Saves 40-67% Tokens

Actual measurements from this demo:
- 5 customers: 57.8% savings (335 tokens)
- 15 customers: 62.3% savings (1,245 tokens)

**Impact**:
- Fit more data in prompts
- Reduce API costs
- Faster model processing

### No Separate Vector DB

Everything in one SochDB instance:
- SQL tables for structured data
- Vector collection for text search
- No ETL between systems
- ACID consistency across both

### Token-Budgeted Retrieval

This demo uses a simple token-budgeted selection step after hybrid search:

```python
results = collection.hybrid_search(
    vector=query_embedding,
    text_query="churn risk",
    k=6,
    alpha=0.8,
)

# Keep adding chunks until token budget is reached
picked = token_budget_pick(chunks, budget=1000)
```

This keeps context under a strict limit even with many matches.

## Files

- `copilot.py`: Main analytics copilot implementation
- `token_comparison.py`: TOON vs JSON token measurement utility
- `run_demo.py`: Interactive demo runner
- `sample_data/customers.csv`: Example customer dataset

## Requirements

```
sochdb>=0.3.3
openai>=1.0.0
tiktoken>=0.5.0
```

## Use Cases

This pattern works for:
- Customer analytics (churn, expansion, health scores)
- Sales pipeline analysis
- Financial data exploration
- Product usage analytics
- Support ticket analysis
- Any spreadsheet → AI analysis workflow
