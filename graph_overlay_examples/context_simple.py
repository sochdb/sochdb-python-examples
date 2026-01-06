"""Simple Context Query Example - v0.3.3"""
import sys
sys.path.insert(0, '/Users/sushanth/toondb_v2/toondb-python-sdk/src')

from toondb.database import Database

print("=== ToonDB Context Query Example (Python) v0.3.3 ===\n")

db = Database.open("./test_context_db")
print("✓ Database opened")

# Store documents
docs = [
    ("doc1", "ToonDB is an AI-native database with vector search"),
    ("doc2", "Graph overlay provides agent memory capabilities"),
    ("doc3", "Policy hooks enable validation and access control"),
]

for doc_id, text in docs:
    db.put(f"docs/{doc_id}".encode(), text.encode())
print(f"✓ Stored {len(docs)} documents")

# Retrieve
value = db.get(b"docs/doc1")
print(f"✓ Retrieved: {value.decode()[:50]}...")

# Scan with prefix
count = 0
for key, value in db.scan_prefix(b"docs/"):
    count += 1
    print(f"  - {key.decode()}: {value.decode()[:40]}...")

print(f"✓ Scanned {count} documents")

db.close()
print("\n✓✓✓ SUCCESS: Context operations work perfectly! ✓✓✓")
