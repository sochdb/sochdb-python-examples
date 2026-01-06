"""
ToonDB Graph Overlay Example
============================

Demonstrates the Graph Overlay feature for agent memory,
providing lightweight graph operations on top of KV storage.

Features shown:
- Node creation with types and properties
- Edge creation with typed relationships
- BFS/DFS traversal
- Shortest path finding
- Neighbor queries
"""

import toondb
from toondb import GraphOverlay, GraphNode, GraphEdge

def main():
    # Open database and create graph overlay
    db = toondb.open("./graph_example_db")
    graph = GraphOverlay(db, namespace="memory")
    
    print("=== ToonDB Graph Overlay Example ===\n")
    
    # Create nodes representing an AI agent's memory
    print("1. Creating nodes...")
    
    # Create user nodes
    user1 = GraphNode(
        id="user_alice",
        type="person",
        properties={
            "name": "Alice",
            "role": "developer",
            "interests": ["python", "machine learning"]
        }
    )
    user2 = GraphNode(
        id="user_bob",
        type="person",
        properties={
            "name": "Bob",
            "role": "data scientist"
        }
    )
    
    # Create project nodes
    project = GraphNode(
        id="project_toondb",
        type="project",
        properties={
            "name": "ToonDB",
            "status": "active",
            "tech_stack": ["rust", "python", "go"]
        }
    )
    
    # Create concept nodes
    concept = GraphNode(
        id="concept_vector_search",
        type="concept",
        properties={
            "name": "Vector Search",
            "category": "feature"
        }
    )
    
    # Add all nodes
    graph.add_node(user1)
    graph.add_node(user2)
    graph.add_node(project)
    graph.add_node(concept)
    print(f"   Created {4} nodes")
    
    # Create edges
    print("\n2. Creating edges...")
    
    # Alice works on ToonDB
    graph.add_edge(GraphEdge(
        from_id="user_alice",
        edge_type="works_on",
        to_id="project_toondb",
        properties={"role": "lead developer", "since": "2024-01"}
    ))
    
    # Bob works on ToonDB  
    graph.add_edge(GraphEdge(
        from_id="user_bob",
        edge_type="works_on",
        to_id="project_toondb",
        properties={"role": "data engineer"}
    ))
    
    # Alice knows Bob
    graph.add_edge(GraphEdge(
        from_id="user_alice",
        edge_type="knows",
        to_id="user_bob",
        properties={"context": "work colleagues"}
    ))
    
    # ToonDB has vector search feature
    graph.add_edge(GraphEdge(
        from_id="project_toondb",
        edge_type="has_feature",
        to_id="concept_vector_search"
    ))
    
    # Alice is expert in vector search
    graph.add_edge(GraphEdge(
        from_id="user_alice",
        edge_type="expert_in",
        to_id="concept_vector_search",
        properties={"level": "advanced"}
    ))
    
    print("   Created 5 edges")
    
    # Query nodes
    print("\n3. Querying nodes...")
    alice = graph.get_node("user_alice")
    if alice:
        print(f"   Found: {alice.properties.get('name')} ({alice.type})")
        print(f"   Interests: {alice.properties.get('interests')}")
    
    # Get outgoing edges
    print("\n4. Getting outgoing edges...")
    edges = graph.get_edges("user_alice")
    for edge in edges:
        print(f"   {edge.from_id} --[{edge.edge_type}]--> {edge.to_id}")
    
    # Get incoming edges
    print("\n5. Getting incoming edges...")
    incoming = graph.get_incoming_edges("project_toondb")
    for edge in incoming:
        print(f"   {edge.from_id} --[{edge.edge_type}]--> {edge.to_id}")
    
    # BFS traversal
    print("\n6. BFS traversal from Alice (max depth 2)...")
    visited = graph.bfs("user_alice", max_depth=2)
    print(f"   Visited: {visited}")
    
    # DFS traversal
    print("\n7. DFS traversal from Alice...")
    visited_dfs = graph.dfs("user_alice", max_depth=2)
    print(f"   Visited (DFS): {visited_dfs}")
    
    # Get neighbors
    print("\n8. Getting neighbors of ToonDB project...")
    neighbors = graph.get_neighbors("project_toondb", direction="both")
    for n in neighbors:
        print(f"   Neighbor: {n.id} ({n.type})")
    
    # Find nodes by type
    print("\n9. Finding all 'person' nodes...")
    people = graph.get_nodes_by_type("person", limit=10)
    for p in people:
        print(f"   {p.properties.get('name')} - {p.properties.get('role')}")
    
    # Cleanup
    print("\n10. Cleaning up...")
    graph.delete_edge("user_alice", "knows", "user_bob")
    graph.delete_node("concept_vector_search")
    print("    Deleted edge and node")
    
    db.close()
    print("\n=== Graph Overlay Example Complete ===")

if __name__ == "__main__":
    main()
