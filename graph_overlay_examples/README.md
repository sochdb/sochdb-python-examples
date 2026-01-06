# ToonDB New Features Examples

This directory contains examples demonstrating the new features in ToonDB v0.3.x (currently unreleased).

## Features Demonstrated

### 1. Graph Overlay (`graph_overlay_example.py`)

Lightweight graph layer on KV storage for agent memory:

- **Node Operations**: Create, read, update, delete nodes with types and properties
- **Edge Operations**: Typed edges with bidirectional indexes
- **Traversal**: BFS and DFS traversal algorithms
- **Queries**: Find neighbors, get nodes by type, shortest path

```python
from toondb import GraphOverlay, GraphNode, GraphEdge

db = toondb.open("./db")
graph = GraphOverlay(db, namespace="memory")

# Create nodes
graph.add_node(GraphNode(id="user_1", type="person", properties={"name": "Alice"}))

# Create edges
graph.add_edge(GraphEdge(from_id="user_1", edge_type="knows", to_id="user_2"))

# Traverse
visited = graph.bfs("user_1", max_depth=3)
```

### 2. Policy Hooks (`policy_hooks_example.py`)

Trigger-based guardrails for agent operations:

- **Validation Hooks**: `@before_write` for input validation
- **Redaction Hooks**: `@after_read` for PII masking
- **Access Control**: `@before_delete` for permission checks
- **Audit Logging**: `@after_commit` for compliance
- **Rate Limiting**: Token bucket algorithm per agent/session

```python
from toondb.policy import PolicyEngine, before_write, PolicyAction

engine = PolicyEngine(db)

@before_write(engine, pattern="users/*")
def validate_user(ctx):
    if "email" not in ctx.value:
        return PolicyAction.DENY
    return PolicyAction.ALLOW
```

### 3. Tool Routing (`tool_routing_example.py`)

Context-driven dynamic binding for multi-agent systems:

- **Agent Registry**: Register agents with capabilities
- **Routing Strategies**: PRIORITY, ROUND_ROBIN, LEAST_LOADED, STICKY, RANDOM, FASTEST
- **Tool Categories**: CODE, SEARCH, DATABASE, MEMORY, VECTOR, GRAPH, ANALYTICS, API, FILE, SYSTEM
- **Failover**: Automatic failover to backup agents

```python
from toondb.routing import AgentRegistry, ToolRouter, ToolCategory, RoutingStrategy

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
from toondb.context import ContextQuery, DeduplicationStrategy

query = (ContextQuery(db, collection="docs")
    .with_token_budget(4000)
    .with_query("How does vector search work?")
    .with_deduplication(DeduplicationStrategy.SEMANTIC)
    .with_top_k(10))

result = query.execute()
print(f"Used {result.total_tokens} tokens")
```

## Running the Examples

1. Install the ToonDB Python SDK:
   ```bash
   pip install toondb-client
   ```

2. Run any example:
   ```bash
   python graph_overlay_example.py
   python policy_hooks_example.py
   python tool_routing_example.py
   python context_query_example.py
   ```

## Related Documentation

- [Graph Overlay Guide](../../toondb/docs/guides/graph-overlay.md)
- [Policy Hooks Guide](../../toondb/docs/guides/policy-hooks.md)
- [Tool Routing Guide](../../toondb/docs/guides/tool-routing.md)
- [Context Query Guide](../../toondb/docs/guides/context-query.md)

## Requirements

- Python 3.8+
- ToonDB v0.3.x or later
