"""Process B: Runbook indexer.

Indexes runbook documents into vector collection via IPC.
"""

import sys
import time
import argparse
import os
import glob
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sochdb import Database
import sochdb
from shared.embeddings import EmbeddingClient


def index_runbooks(db: Database):
    """Index runbook documents into vector collection."""
    print("📚 Indexing runbooks into vector collection...\n")
    
    embedding_client = EmbeddingClient()
    dimension = embedding_client.dimension
    
    # Get or create namespace
    ns = db.get_or_create_namespace("incident_ops")
    
    # Create collection for runbooks
    try:
        collection = ns.create_collection(
            "runbooks",
            dimension=dimension,
            enable_hybrid_search=True,
        )
        print(f"  ✓ Created 'runbooks' collection (dimension={dimension})")
    except Exception:
        collection = ns.get_collection("runbooks")
        print("  ✓ Using existing 'runbooks' collection")
    
    # Index runbook files
    runbooks_dir = Path(__file__).parent / "runbooks"
    
    for runbook_file in sorted(runbooks_dir.glob("*.txt")):
        print(f"\n  Indexing: {runbook_file.name}")
        
        with open(runbook_file, "r") as f:
            content = f.read()
        
        # Split into chunks (by section)
        chunks = [chunk.strip() for chunk in content.split("\n\n") if chunk.strip()]
        
        for i, chunk in enumerate(chunks):
            if len(chunk) < 50:  # Skip very short chunks
                continue
            
            # Generate embedding
            embedding = embedding_client.embed(chunk)
            
            doc_id = f"{runbook_file.stem}_chunk_{i}"
            metadata = {
                "source": runbook_file.name,
                "type": "runbook",
                "chunk_index": i
            }
            
            # Add to collection
            collection.insert(
                id=doc_id,
                vector=embedding,
                metadata=metadata,
                content=chunk,
            )
            
            print(f"    ✓ Indexed chunk {i+1}: {chunk[:60]}...")
    
    print(f"\n✅ Runbook indexing complete!")
    return collection


def main():
    """Run runbook indexer."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--db-path", default="./ops_db")
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    
    print("="*60)
    print("PROCESS B: RUNBOOK INDEXER")
    print("="*60)
    print(f"Opening SochDB database: {args.db_path}\n")
    
    try:
        if not os.environ.get("SOCHDB_LIB_PATH"):
            lib_root = os.path.join(os.path.dirname(sochdb.__file__), "lib")
            candidates = glob.glob(os.path.join(lib_root, "*", "libsochdb_index.*"))
            if candidates:
                os.environ["SOCHDB_LIB_PATH"] = candidates[0]

        db = Database.open(args.db_path)
        print("✅ Opened shared SochDB!\n")
        
        # Index runbooks
        index_runbooks(db)
        
        # Keep process running to maintain connection
        if args.once:
            db.close()
            return

        print("\n👀 Watching for runbook updates (Ctrl+C to stop)...\n")
        while True:
            time.sleep(60)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Runbook indexer stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
