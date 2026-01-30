"""
Tool Routing (App-Level) Example
================================

The current Python SDK does not expose built-in tool routing,
so this example demonstrates a lightweight routing layer at
the application level.
"""

from collections import defaultdict, deque


def main():
    print("=== Tool Routing (App-Level) Example ===\n")

    agents = [
        {"id": "code_analyzer", "capabilities": {"code", "search"}, "priority": 100},
        {"id": "db_agent", "capabilities": {"database", "memory"}, "priority": 90},
        {"id": "vector_search", "capabilities": {"vector", "search"}, "priority": 110},
        {"id": "fallback", "capabilities": {"code", "database", "vector", "search"}, "priority": 10},
    ]

    tools = {
        "search_code": {"required": {"code", "search"}},
        "vector_search": {"required": {"vector"}},
        "query_database": {"required": {"database"}},
        "store_memory": {"required": {"memory", "database"}},
    }

    def route_priority(tool_name):
        req = tools[tool_name]["required"]
        candidates = [a for a in agents if req.issubset(a["capabilities"])]
        return sorted(candidates, key=lambda a: a["priority"], reverse=True)[0]["id"]

    print("1. Priority routing")
    print(f"   vector_search -> {route_priority('vector_search')}")
    print(f"   search_code -> {route_priority('search_code')}")

    print("\n2. Round-robin routing")
    rr = deque([a["id"] for a in sorted(agents, key=lambda a: a["priority"], reverse=True)])
    for i in range(4):
        rr.rotate(-1)
        print(f"   Request {i+1}: {rr[0]}")

    print("\n3. Least-loaded routing (simulated)")
    load = {"vector_search": 15, "fallback": 2}
    candidates = [a for a in agents if "vector" in a["capabilities"]]
    chosen = min(candidates, key=lambda a: load.get(a["id"], 0))
    print(f"   vector_search -> {chosen['id']} (load={load.get(chosen['id'], 0)})")

    print("\n=== Tool Routing Example Complete ===")


if __name__ == "__main__":
    main()
