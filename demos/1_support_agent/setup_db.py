"""Setup database with schema, sample data, and policy documents."""

import os
import sys
import glob
from pathlib import Path

# Add parent directory to path to import shared utilities
sys.path.insert(0, str(Path(__file__).parent.parent))

from sochdb import Database
import sochdb
from shared.embeddings import EmbeddingClient


def setup_database(db_path: str = "./shop_db"):
    """Initialize SochDB with schema, sample data, and vector collection."""

    if not os.environ.get("SOCHDB_LIB_PATH"):
        lib_root = os.path.join(os.path.dirname(sochdb.__file__), "lib")
        candidates = glob.glob(os.path.join(lib_root, "*", "libsochdb_index.*"))
        if candidates:
            os.environ["SOCHDB_LIB_PATH"] = candidates[0]
    
    print(f"Setting up database at {db_path}...")
    
    with Database.open(db_path) as db:
        # 1. Create SQL schema
        print("Creating SQL schema...")
        
        db.execute_sql("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                eta TEXT,
                destination TEXT NOT NULL,
                total REAL NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        db.execute_sql("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                reason TEXT NOT NULL,
                resolution TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id)
            )
        """)
        
        db.execute_sql("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_type TEXT NOT NULL,
                entity_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                timestamp TEXT NOT NULL
            )
        """)
        
        # 2. Insert sample order data
        print("Inserting sample orders...")
        
        sample_orders = [
            (1001, 123, "IN_TRANSIT", "2026-01-02", "123 Main St Seattle WA 98101", 149.99, "2025-12-28"),
            (1002, 123, "DELIVERED", "2025-12-30", "123 Main St Seattle WA 98101", 79.99, "2025-12-20"),
            (1003, 456, "PROCESSING", "2026-01-10", "456 Oak Ave Portland OR 97201", 299.99, "2026-01-03"),
            (1004, 123, "LATE", "2025-12-31", "123 Main St Seattle WA 98101", 199.99, "2025-12-22"),
            (1005, 789, "IN_TRANSIT", "2026-01-06", "789 Pine Rd San Francisco CA 94102", 549.99, "2026-01-01"),
        ]
        
        for order in sample_orders:
            db.execute_sql(f"DELETE FROM orders WHERE id = {order[0]}")
            db.execute_sql(f"""
                INSERT INTO orders (id, user_id, status, eta, destination, total, created_at)
                VALUES ({order[0]}, {order[1]}, '{order[2]}', '{order[3]}', '{order[4]}', {order[5]}, '{order[6]}')
            """)
        
        # 3. Store user preferences in KV
        print("Storing user preferences...")
        
        db.put(b"users/123/prefs/replacements_over_refunds", b"true")
        db.put(b"users/123/prefs/expedited_shipping_only", b"false")
        db.put(b"users/123/name", b"Alice Johnson")
        db.put(b"users/123/email", b"alice@example.com")
        
        db.put(b"users/456/prefs/replacements_over_refunds", b"false")
        db.put(b"users/456/name", b"Bob Smith")
        
        db.put(b"users/789/prefs/eco_friendly", b"true")
        db.put(b"users/789/name", b"Carol Davis")
        
        # 4. Set up vector collection for policies
        print("Setting up vector collection...")
        
        embedding_client = EmbeddingClient()
        dimension = embedding_client.dimension
        
        ns = db.get_or_create_namespace("support_system")
        
        # Create collection for policy documents
        try:
            collection = ns.get_collection("policies")
            if not collection.config.enable_hybrid_search:
                ns.delete_collection("policies")
                collection = ns.create_collection(
                    "policies",
                    dimension=dimension,
                    enable_hybrid_search=True,
                )
        except Exception:
            collection = ns.create_collection(
                "policies",
                dimension=dimension,
                enable_hybrid_search=True,
            )
        
        # Load and embed policy documents
        policies_dir = Path(__file__).parent / "policies"
        
        for policy_file in policies_dir.glob("*.txt"):
            print(f"  Indexing {policy_file.name}...")
            
            with open(policy_file, "r") as f:
                content = f.read()
            
            # Create chunks (simple split by paragraph)
            chunks = [chunk.strip() for chunk in content.split("\n\n") if chunk.strip()]
            
            for i, chunk in enumerate(chunks):
                if len(chunk) < 50:  # Skip very short chunks
                    continue
                
                embedding = embedding_client.embed(chunk)
                
                doc_id = f"{policy_file.stem}_chunk_{i}"
                metadata = {
                    "source": policy_file.name,
                    "type": "policy",
                    "chunk_index": i
                }
                
                collection.insert(
                    id=doc_id,
                    vector=embedding,
                    metadata=metadata,
                    content=chunk,
                )
        
    print(f"\n✓ Database setup complete at {db_path}")
    print(f"  - Created 3 SQL tables (orders, tickets, audit_logs)")
    print(f"  - Inserted {len(sample_orders)} sample orders")
    print(f"  - Stored preferences for 3 users")
    print(f"  - Indexed policy documents into vector collection")


if __name__ == "__main__":
    setup_database()
