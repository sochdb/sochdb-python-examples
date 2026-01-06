"""Simple Graph Overlay Example - v0.3.3"""
import sys
sys.path.insert(0, '/Users/sushanth/toondb_v2/toondb-python-sdk/src')

from toondb.database import Database
from toondb.graph import GraphOverlay

print("=== ToonDB Graph Overlay Example (Python) v0.3.3 ===\n")

# Open database
db = Database.open("./test_graph_db")
print("✓ Database opened")

# Create graph
graph = GraphOverlay(db, namespace="demo")
print("✓ Graph overlay created")

# Add nodes
graph.add_node("alice", "person", {"name": "Alice", "role": "developer"})
graph.add_node("bob", "person", {"name": "Bob", "role": "engineer"})
graph.add_node("toondb", "project", {"name": "ToonDB"})
print("✓ 3 nodes added")

# Add edges
graph.add_edge("alice", "works_on", "toondb")
graph.add_edge("bob", "works_on", "toondb")
graph.add_edge("alice", "knows", "bob")
print("✓ 3 edges added")

# Query
node = graph.get_node("alice")
print(f"✓ Retrieved node: {node.properties['name']}")

edges = graph.get_edges("alice")
print(f"✓ Alice has {len(edges)} edges")

# Traverse
visited = graph.bfs("alice", max_depth=2)
print(f"✓ BFS visited: {visited}")

db.close()
print("\n✓✓✓ SUCCESS: Graph Overlay works perfectly! ✓✓✓")
