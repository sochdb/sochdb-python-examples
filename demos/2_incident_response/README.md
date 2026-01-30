# Multi-Agent Incident Response Demo

Demo-grade incident response system showcasing SochDB's IPC mode, namespace isolation, hybrid retrieval, and ACID state transitions.

## What This Demo Shows

1. **Embedded Mode (Sequential)**: In this repo, the demo runs sequentially in embedded mode for repeatable output
2. **Namespace Isolation**: Separate namespaces for `incident_ops` data
3. **Hybrid Retrieval**: Vector + keyword search with Reciprocal Rank Fusion (RRF)
4. **ACID State Transitions**: Incident states (OPEN → MITIGATING → RESOLVED)
5. **Concurrent Writes**: Three processes writing simultaneously without conflicts
6. **Token-Budgeted Context**: Runbook retrieval under strict token limits

## Architecture

```
Process A (Collector)  ────┐
                           ├──→ SochDB Server (IPC)
Process B (Indexer)    ────┤         ↓
                           │    Shared State:
Process C (Commander)  ────┘    - Metrics (KV)
                                - Runbooks (Vectors)
                                - Incident State (KV)
```

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

### 3. Run Demo (Embedded Mode)

```bash
cd demos/2_incident_response
PATH=./../../venv/bin:$PATH ./run_demo.sh
```

## Usage

### Run All Processes

```bash
./run_demo.sh
```

This runs:
- **Process B**: Runbook indexer (indexes runbooks into vector collection)
- **Process A**: Metrics collector (writes metrics for a few iterations)
- **Process C**: Incident commander (monitors metrics for a few iterations)

### Run Processes Manually

In separate terminals:

```bash
# Terminal 1: Start server
./start_server.sh

# Terminal 2: Index runbooks
python process_b_indexer.py

# Terminal 3: Collect metrics
python process_a_collector.py

# Terminal 4: Monitor incidents
python process_c_commander.py
```

## Demo Flow

### 1. Normal Operation
Process A writes metrics every 5 seconds:
```
[2026-01-04T18:00:00] Latency P99: 350ms | Error Rate: 1.2% | CPU: 45.3%
```

Process C monitors and shows "OK" status.

### 2. Incident Trigger
When latency > 1000ms AND error rate > 5%:
```
🚨🚨🚨 INCIDENT DETECTED! 🚨🚨🚨

📊 Incident Details:
   Latency P99: 1450ms
   Error Rate: 6.8%
   Triggered: 2026-01-04T18:05:23

📝 State transition: NONE → OPEN
```

### 3. Runbook Retrieval
Process C retrieves relevant runbooks using hybrid search:
```
🔍 Retrieving relevant runbooks (hybrid search)...
   Retrieved 8 runbook chunks
   Token budget used: ~1850 tokens
```

Combines:
- **Vector search**: Semantic similarity to incident symptoms
- **Keyword search**: "latency spike deployment rollback database"
- **RRF**: Fuses results from both methods

### 4. Mitigation Plan
LLM generates actionable plan:
```
MITIGATION PLAN
===============
Most Likely Root Cause: Recent deployment causing database overload

Immediate Actions:
1. Check recent deployments (last 30 min)
2. Review database slow query log
3. Consider deployment rollback if spike coincides with deploy

Next Steps:
1. Monitor metrics for 5 minutes after mitigation
2. Document incident timeline
3. Schedule postmortem
```

### 5. State Transition
```
📝 State transition: OPEN → MITIGATING
⚡ Executing mitigation actions...
🔬 Checking metrics...
📝 State transition: MITIGATING → RESOLVED
✅ Incident resolved!
```

## Key Highlights

### IPC: Shared DB Across Processes

All three processes connect to the same SochDB instance:

```python
from sochdb import IpcClient

client = IpcClient.connect("./ops_db/sochdb.sock")

# Process A writes metrics
client.put(b"metrics/latest/latency_p99", b"1450")

# Process C reads metrics
latency = client.get(b"metrics/latest/latency_p99")
```

### Hybrid Search with RRF

Combines vector and keyword search:

```python
ctx = (
    ContextQuery(collection)
    .add_vector_query(embedding, weight=0.6)    # Semantic
    .add_keyword_query("latency spike", weight=0.4)  # Keyword
    .with_token_budget(2000)
    .with_deduplication(DeduplicationStrategy.SEMANTIC)
    .execute()
)
```

### ACID State Machine

Incident transitions are atomic:
```
NONE → OPEN → MITIGATING → RESOLVED
```

Each transition writes:
- Current state
- Timestamp
- Historical record

All operations are consistent across processes.

## Files

- `start_server.sh`: Start SochDB in IPC mode
- `process_a_collector.py`: Metrics collector (writes to KV)
- `process_b_indexer.py`: Runbook indexer (writes to vectors)
- `process_c_commander.py`: Incident commander (reads KV + vectors, writes state)
- `run_demo.sh`: Orchestrate all processes
- `runbooks/`: Runbook documents
  - `latency_spike.txt`: Latency troubleshooting guide
  - `deployment_rollback.txt`: Rollback procedures
  - `database_recovery.txt`: Database recovery steps

## Troubleshooting

### Server Won't Start

```bash
# Check if server is already running
sochdb-server status --db ./ops_db

# Stop existing server
sochdb-server stop --db ./ops_db

# Start fresh
./start_server.sh
```

### Process Can't Connect

Ensure server is running first:
```bash
./start_server.sh
# Wait for "✅ SochDB server is running!" message
```

### No Incident Triggered

Incidents trigger when BOTH conditions are met:
- Latency P99 > 1000ms
- Error Rate > 5%

Process A increases these values after ~20 iterations (100 seconds).
