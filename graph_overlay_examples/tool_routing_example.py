"""
ToonDB Tool Routing Example
===========================

Demonstrates the Tool Routing feature for multi-agent systems,
providing context-driven dynamic binding with multiple routing strategies.

Features shown:
- Agent registration with capabilities
- Tool registration with categories
- Multiple routing strategies (PRIORITY, ROUND_ROBIN, LEAST_LOADED)
- Context-based routing with sticky sessions
- Automatic failover
"""

import toondb
from toondb.routing import (
    AgentRegistry, ToolRouter, ToolDispatcher,
    Agent, Tool, ToolCategory, RoutingStrategy,
    RouteContext, RouteResult
)

def main():
    # Open database and create routing infrastructure
    db = toondb.open("./routing_example_db")
    registry = AgentRegistry(db)
    router = ToolRouter(registry, default_strategy=RoutingStrategy.PRIORITY)
    dispatcher = ToolDispatcher(router)
    
    print("=== ToonDB Tool Routing Example ===\n")
    
    # -------------------------------------------------------
    # 1. Register agents with capabilities
    # -------------------------------------------------------
    print("1. Registering agents...")
    
    # Code analysis agent
    code_agent = registry.register(
        agent_id="code_analyzer",
        capabilities=[ToolCategory.CODE, ToolCategory.SEARCH],
        endpoint="http://localhost:8001",
        priority=100,
        max_concurrent=5,
        metadata={"version": "1.0", "model": "gpt-4"}
    )
    print(f"   Registered: {code_agent.agent_id} with {code_agent.capabilities}")
    
    # Database agent
    db_agent = registry.register(
        agent_id="db_agent",
        capabilities=[ToolCategory.DATABASE, ToolCategory.MEMORY],
        endpoint="http://localhost:8002",
        priority=90,
        max_concurrent=10
    )
    print(f"   Registered: {db_agent.agent_id} with {db_agent.capabilities}")
    
    # Vector search agent (high priority)
    vector_agent = registry.register(
        agent_id="vector_search",
        capabilities=[ToolCategory.VECTOR, ToolCategory.SEARCH],
        endpoint="http://localhost:8003",
        priority=110,  # Highest priority
        max_concurrent=20
    )
    print(f"   Registered: {vector_agent.agent_id} with {vector_agent.capabilities}")
    
    # Backup/fallback agent (low priority)
    fallback_agent = registry.register(
        agent_id="fallback",
        capabilities=[
            ToolCategory.CODE, ToolCategory.DATABASE,
            ToolCategory.VECTOR, ToolCategory.SEARCH
        ],
        endpoint="http://localhost:9000",
        priority=10,  # Lowest priority, used as fallback
        max_concurrent=100
    )
    print(f"   Registered: {fallback_agent.agent_id} (fallback)")
    
    # -------------------------------------------------------
    # 2. Register tools
    # -------------------------------------------------------
    print("\n2. Registering tools...")
    
    tools = [
        Tool(
            name="search_code",
            description="Search codebase for patterns",
            category=ToolCategory.CODE,
            required_capabilities=[ToolCategory.CODE, ToolCategory.SEARCH],
            timeout_seconds=30,
            retries=2
        ),
        Tool(
            name="vector_search",
            description="Semantic search using embeddings",
            category=ToolCategory.VECTOR,
            required_capabilities=[ToolCategory.VECTOR],
            timeout_seconds=10,
            retries=3
        ),
        Tool(
            name="query_database",
            description="Execute SQL queries",
            category=ToolCategory.DATABASE,
            required_capabilities=[ToolCategory.DATABASE],
            timeout_seconds=60,
            retries=1
        ),
        Tool(
            name="store_memory",
            description="Store agent memory",
            category=ToolCategory.MEMORY,
            required_capabilities=[ToolCategory.MEMORY, ToolCategory.DATABASE],
            timeout_seconds=5,
            retries=3
        ),
    ]
    
    for tool in tools:
        router.register_tool(tool)
        print(f"   Registered tool: {tool.name} ({tool.category})")
    
    # -------------------------------------------------------
    # 3. Priority-based routing
    # -------------------------------------------------------
    print("\n3. Priority-based routing...")
    
    # Route a vector search request
    ctx = RouteContext(
        tool_name="vector_search",
        session_id="session_123",
        user_id="user_alice"
    )
    result = router.route(ctx)
    print(f"   Tool: vector_search -> Agent: {result.agent_id} (priority: {result.priority})")
    
    # Route a code search request  
    ctx = RouteContext(
        tool_name="search_code",
        session_id="session_123"
    )
    result = router.route(ctx)
    print(f"   Tool: search_code -> Agent: {result.agent_id}")
    
    # -------------------------------------------------------
    # 4. Round-robin routing
    # -------------------------------------------------------
    print("\n4. Round-robin routing...")
    
    router_rr = ToolRouter(registry, default_strategy=RoutingStrategy.ROUND_ROBIN)
    for tool in tools:
        router_rr.register_tool(tool)
    
    # Make multiple requests to see round-robin in action
    for i in range(4):
        ctx = RouteContext(tool_name="vector_search")
        result = router_rr.route(ctx)
        print(f"   Request {i+1}: vector_search -> {result.agent_id}")
    
    # -------------------------------------------------------
    # 5. Least-loaded routing
    # -------------------------------------------------------
    print("\n5. Least-loaded routing...")
    
    router_ll = ToolRouter(registry, default_strategy=RoutingStrategy.LEAST_LOADED)
    for tool in tools:
        router_ll.register_tool(tool)
    
    # Simulate load on agents
    registry.record_load("vector_search", 15)  # 15 active requests
    registry.record_load("fallback", 2)        # Only 2 active requests
    
    ctx = RouteContext(tool_name="vector_search")
    result = router_ll.route(ctx)
    print(f"   With load simulation: vector_search -> {result.agent_id}")
    print(f"   (vector_search has 15 active, fallback has 2)")
    
    # -------------------------------------------------------
    # 6. Sticky session routing
    # -------------------------------------------------------
    print("\n6. Sticky session routing...")
    
    router_sticky = ToolRouter(registry, default_strategy=RoutingStrategy.STICKY)
    for tool in tools:
        router_sticky.register_tool(tool)
    
    # Same session should always route to same agent
    for i in range(3):
        ctx = RouteContext(
            tool_name="query_database",
            session_id="sticky_session_abc"
        )
        result = router_sticky.route(ctx)
        print(f"   Request {i+1} (session abc): query_database -> {result.agent_id}")
    
    # Different session gets different routing
    ctx = RouteContext(
        tool_name="query_database",
        session_id="sticky_session_xyz"
    )
    result = router_sticky.route(ctx)
    print(f"   Request (session xyz): query_database -> {result.agent_id}")
    
    # -------------------------------------------------------
    # 7. Finding capable agents
    # -------------------------------------------------------
    print("\n7. Finding capable agents...")
    
    # Find agents capable of CODE + SEARCH
    capable = registry.find_capable([ToolCategory.CODE, ToolCategory.SEARCH])
    print(f"   Agents with CODE + SEARCH: {[a.agent_id for a in capable]}")
    
    # Find agents with VECTOR capability
    capable = registry.find_capable([ToolCategory.VECTOR])
    print(f"   Agents with VECTOR: {[a.agent_id for a in capable]}")
    
    # -------------------------------------------------------
    # 8. Agent statistics
    # -------------------------------------------------------
    print("\n8. Agent statistics...")
    
    # Record some calls
    registry.record_call("vector_search", latency_ms=45, success=True)
    registry.record_call("vector_search", latency_ms=52, success=True)
    registry.record_call("vector_search", latency_ms=38, success=True)
    registry.record_call("db_agent", latency_ms=120, success=True)
    registry.record_call("db_agent", latency_ms=500, success=False)
    
    # Get stats
    for agent_id in ["vector_search", "db_agent"]:
        stats = registry.get_stats(agent_id)
        print(f"   {agent_id}: {stats['total_calls']} calls, "
              f"avg latency: {stats['avg_latency_ms']:.1f}ms, "
              f"success rate: {stats['success_rate']:.1%}")
    
    # -------------------------------------------------------
    # 9. Tool dispatcher (execute with routing)
    # -------------------------------------------------------
    print("\n9. Tool dispatcher demo...")
    
    # Define a simple handler
    async def search_handler(tool: Tool, params: dict) -> dict:
        return {"results": ["file1.py", "file2.py"], "count": 2}
    
    # Register handler for the fallback agent
    dispatcher.register_handler("fallback", "search_code", search_handler)
    
    print("   Registered handler for search_code on fallback agent")
    print("   (In production, handlers would make actual API calls)")
    
    # Cleanup
    db.close()
    print("\n=== Tool Routing Example Complete ===")

if __name__ == "__main__":
    main()
