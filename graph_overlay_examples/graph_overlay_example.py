"""
SochDB Graph API Example
========================

Demonstrates the built-in graph API available in the current SDK.
Uses Database.add_node / add_edge and traversal for neighbor discovery.
"""

from sochdb import Database


def main():
    print("=== SochDB Graph API Example ===\n")

    db = Database.open("./graph_example_db")
    print("✓ Database opened")

    # Create nodes
    db.add_node(
        namespace="memory",
        node_id="user_alice",
        node_type="person",
        properties={"name": "Alice", "role": "developer"},
    )
    db.add_node(
        "memory",
        "user_bob",
        "person",
        {"name": "Bob", "role": "data scientist"},
    )
    db.add_node(
        "memory",
        "project_sochdb",
        "project",
        {"name": "SochDB", "status": "active"},
    )
    db.add_node(
        "memory",
        "concept_vector_search",
        "concept",
        {"name": "Vector Search", "category": "feature"},
    )
    print("✓ 4 nodes added")

    # Create edges
    db.add_edge("memory", "user_alice", "works_on", "project_sochdb", {"role": "lead"})
    db.add_edge("memory", "user_bob", "works_on", "project_sochdb")
    db.add_edge("memory", "user_alice", "knows", "user_bob")
    db.add_edge("memory", "project_sochdb", "has_feature", "concept_vector_search")
    db.add_edge("memory", "user_alice", "expert_in", "concept_vector_search")
    print("✓ 5 edges added")

    # Traverse graph
    nodes, edges = db.traverse(namespace="memory", start_node="user_alice", max_depth=2, order="bfs")
    print("\n✓ BFS traversal from 'user_alice':")
    print(f"  Visited {len(nodes)} nodes:")
    for node in nodes:
        print(f"    - {node['id']} ({node['node_type']})")
    print(f"  Found {len(edges)} edges:")
    for edge in edges:
        print(f"    - {edge['from_id']} --{edge['edge_type']}--> {edge['to_id']}")

    db.close()
    print("\n=== Graph API Example Complete ===")


if __name__ == "__main__":
    main()
