# SochDB New Features Examples

This directory contains examples demonstrating graph-related workflows in the current SDK.
Some previously documented features (GraphOverlay, Policy Hooks, Tool Routing) are not
exposed in the Python SDK yet, so those examples show app-level equivalents.

## Features Demonstrated

### 1. Graph API (`graph_overlay_example.py`)

Lightweight graph layer on KV storage for agent memory:

- **Node Operations**: Create, read, update, delete nodes with types and properties
- **Edge Operations**: Typed edges with bidirectional indexes
- **Traversal**: BFS and DFS traversal algorithms
- **Queries**: Find neighbors, get nodes by type, shortest path

```python
from sochdb import GraphOverlay, GraphNode, GraphEdge

db = sochdb.open("./db")
graph = GraphOverlay(db, namespace="memory")

# Create nodes
graph.add_node(GraphNode(id="user_1", type="person", properties={"name": "Alice"}))

# Create edges
graph.add_edge(GraphEdge(from_id="user_1", edge_type="knows", to_id="user_2"))

# Traverse
visited = graph.bfs("user_1", max_depth=3)
```

### 2. Policy Hooks (App-Level) (`policy_hooks_example.py`)

Trigger-based guardrails for agent operations:

- **Validation Hooks**: `@before_write` for input validation
- **Redaction Hooks**: `@after_read` for PII masking
- **Access Control**: `@before_delete` for permission checks
- **Audit Logging**: `@after_commit` for compliance
- **Rate Limiting**: Token bucket algorithm per agent/session

```python
from sochdb.policy import PolicyEngine, before_write, PolicyAction

engine = PolicyEngine(db)

@before_write(engine, pattern="users/*")
def validate_user(ctx):
    if "email" not in ctx.value:
        return PolicyAction.DENY
    return PolicyAction.ALLOW
```

### 3. Tool Routing (App-Level) (`tool_routing_example.py`)

Context-driven dynamic binding for multi-agent systems:

- **Agent Registry**: Register agents with capabilities
- **Routing Strategies**: PRIORITY, ROUND_ROBIN, LEAST_LOADED, STICKY, RANDOM, FASTEST
- **Tool Categories**: CODE, SEARCH, DATABASE, MEMORY, VECTOR, GRAPH, ANALYTICS, API, FILE, SYSTEM
- **Failover**: Automatic failover to backup agents

```python
from sochdb.routing import AgentRegistry, ToolRouter, ToolCategory, RoutingStrategy

registry = AgentRegistry(db)
router = ToolRouter(registry, default_strategy=RoutingStrategy.PRIORITY)

# Register agent
registry.register(
    agent_id="code_analyzer",
    capabilities=[ToolCategory.CODE, ToolCategory.SEARCH],
    priority=100
)

# Route tool call
result = router.route(RouteContext(tool_name="search_code"))
```

### 4. Context Query (`context_query_example.py`)

Token-aware retrieval for LLM applications:

- **Token Budgeting**: Fit context within LLM token limits
- **Deduplication**: Semantic and exact deduplication
- **Hybrid Search**: Vector + keyword with RRF fusion
- **Provenance**: Track source of each chunk
- **Token Estimators**: GPT-4, Claude, or custom

```python
from sochdb.context import ContextQuery, DeduplicationStrategy

query = (ContextQuery(db, collection="docs")
    .with_token_budget(4000)
    .with_query("How does vector search work?")
    .with_deduplication(DeduplicationStrategy.SEMANTIC)
    .with_top_k(10))

result = query.execute()
print(f"Used {result.total_tokens} tokens")
```

## Running the Examples

1. Install the SochDB Python SDK (venv in this repo):
   ```bash
   ./../venv/bin/pip install sochdb
   ```

2. Run any example:
   ```bash
   ./../venv/bin/python graph_overlay_example.py
   ./../venv/bin/python policy_hooks_example.py
   ./../venv/bin/python tool_routing_example.py
   ./../venv/bin/python context_query_example.py
   ```

## Related Documentation

- [Graph Overlay Guide](../../sochdb/docs/guides/graph-overlay.md)
- [Policy Hooks Guide](../../sochdb/docs/guides/policy-hooks.md)
- [Tool Routing Guide](../../sochdb/docs/guides/tool-routing.md)
- [Context Query Guide](../../sochdb/docs/guides/context-query.md)

## Requirements

- Python 3.8+
- SochDB v0.3.x or later
