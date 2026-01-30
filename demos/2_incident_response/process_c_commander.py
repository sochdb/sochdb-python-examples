"""Process C: Incident commander agent.

Monitors metrics, retrieves runbooks via hybrid search, and manages incident state.
"""

import sys
import time
import argparse
import os
import glob
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from sochdb import Database
import sochdb
from shared.llm_client import LLMClient
from shared.embeddings import EmbeddingClient


class IncidentCommander:
    """Incident commander agent with hybrid retrieval and state management."""
    
    def __init__(self, db_path: str):
        """Initialize commander."""
        self.db_path = db_path
        self.db = Database.open(db_path)
        self.llm = LLMClient(model="gpt-4-turbo-preview")
        self.embedding_client = EmbeddingClient()
        self.incident_state = "NONE"
        self._runbooks_indexed = False

        if not os.environ.get("SOCHDB_LIB_PATH"):
            lib_root = os.path.join(os.path.dirname(sochdb.__file__), "lib")
            candidates = glob.glob(os.path.join(lib_root, "*", "libsochdb_index.*"))
            if candidates:
                os.environ["SOCHDB_LIB_PATH"] = candidates[0]
    
    def monitor_loop(self, iterations: int = 0):
        """Monitor metrics and respond to incidents."""
        print("👀 Monitoring metrics for incidents...\n")
        
        count = 0
        while True:
            count += 1
            # Check for active incidents
            severity = self.db.get(b"incidents/current/severity")
            
            if severity and severity.decode() != "NONE" and self.incident_state == "NONE":
                print("\n" + "🚨" * 30)
                print("INCIDENT DETECTED!")
                print("🚨" * 30 + "\n")
                
                self.handle_incident()
            
            # Status update
            if self.incident_state == "NONE":
                latency = self.db.get(b"metrics/latest/latency_p99")
                error_rate = self.db.get(b"metrics/latest/error_rate")
                if latency and error_rate:
                    print(f"  [OK] Latency: {latency.decode()}ms | Error Rate: {error_rate.decode()}%", end="\r")
            
            if iterations and count >= iterations:
                break

            time.sleep(3)
    
    def handle_incident(self):
        """Handle detected incident."""
        # Get incident details
        latency = self.db.get(b"incidents/current/latency")
        error_rate = self.db.get(b"incidents/current/error_rate")
        trigger_time = self.db.get(b"incidents/current/trigger_time")
        
        latency_val = latency.decode() if latency else "unknown"
        error_rate_val = error_rate.decode() if error_rate else "unknown"
        trigger_time_val = trigger_time.decode() if trigger_time else datetime.now().isoformat()
        
        print(f"📊 Incident Details:")
        print(f"   Latency P99: {latency_val}ms")
        print(f"   Error Rate: {error_rate_val}%")
        print(f"   Triggered: {trigger_time_val}")
        
        # Update state to OPEN
        self._update_incident_state("OPEN", "Incident detected, analyzing...")
        
        # Retrieve relevant runbooks
        print(f"\n🔍 Retrieving relevant runbooks (hybrid search)...")
        
        query = f"latency spike high error rate {latency_val}ms {error_rate_val}%"
        query_embedding = self.embedding_client.embed(query)
        
        ns = self.db.get_or_create_namespace("incident_ops")
        try:
            collection = ns.get_collection("runbooks")
        except Exception:
            collection = ns.create_collection(
                "runbooks",
                dimension=self.embedding_client.dimension,
                enable_hybrid_search=True,
            )
        self._ensure_runbooks_indexed(collection)
        
        # Hybrid search with RRF
        results = collection.hybrid_search(
            vector=query_embedding,
            text_query="latency spike deployment rollback database",
            k=8,
            alpha=0.6,
        )
        runbook_chunks = []
        for i, result in enumerate(results.results, 1):
            meta = result.metadata or {}
            content = meta.get("_content", "")
            source = meta.get("source", "unknown")
            runbook_chunks.append(f"({i}) {source}\n{content}")
        
        print(f"   Retrieved {len(runbook_chunks)} runbook chunks")
        
        # Generate mitigation plan
        print(f"\n💡 Generating mitigation plan...")
        
        system_message = """You are an incident commander. Analyze the metrics and runbook guidance.
Suggest concrete mitigation actions in priority order. Be specific and actionable."""
        
        prompt = f"""Incident Details:
- Latency P99: {latency_val}ms (threshold: 1000ms)
- Error Rate: {error_rate_val}% (threshold: 5%)
- Time: {trigger_time_val}

Relevant Runbooks:
{chr(10).join(runbook_chunks)}

Provide:
1. Most likely root cause
2. Immediate mitigation actions (priority order)
3. Next steps after mitigation
"""
        
        response = self.llm.complete(prompt, system_message=system_message)
        
        print(f"\n{'='*60}")
        print("MITIGATION PLAN")
        print('='*60)
        print(response)
        print('='*60)
        
        # Update state to MITIGATING
        self._update_incident_state("MITIGATING", response[:200])
        
        # Simulate mitigation actions
        print(f"\n⚡ Executing mitigation actions...")
        time.sleep(3)
        
        # Check if resolved
        print(f"\n🔬 Checking metrics...")
        time.sleep(2)
        
        # Simulate resolution
        self._update_incident_state("RESOLVED", "Metrics returned to normal")
        
        # Reset incident
        self.db.put(b"incidents/current/severity", b"NONE")
        
        print(f"\n✅ Incident resolved!\n")
        print(f"{'='*60}\n")
    
    def _update_incident_state(self, state: str, details: str):
        """Update incident state with ACID transaction."""
        timestamp = datetime.now().isoformat()
        
        print(f"\n📝 State transition: {self.incident_state} → {state}")
        
        # Store state transition (in real system, would use SQL transaction)
        self.db.put(b"incidents/current/state", state.encode())
        self.db.put(b"incidents/current/last_update", timestamp.encode())
        self.db.put(
            f"incidents/history/{timestamp}".encode(),
            f"{state}: {details}".encode(),
        )
        
        self.incident_state = state

    def _ensure_runbooks_indexed(self, collection):
        if self._runbooks_indexed:
            return

        runbooks_dir = Path(__file__).parent / "runbooks"
        for runbook_file in sorted(runbooks_dir.glob("*.txt")):
            with open(runbook_file, "r") as f:
                content = f.read()
            chunks = [chunk.strip() for chunk in content.split("\n\n") if chunk.strip()]
            for i, chunk in enumerate(chunks):
                if len(chunk) < 50:
                    continue
                embedding = self.embedding_client.embed(chunk)
                doc_id = f"{runbook_file.stem}_chunk_{i}"
                metadata = {
                    "source": runbook_file.name,
                    "type": "runbook",
                    "chunk_index": i,
                }
                collection.insert(
                    id=doc_id,
                    vector=embedding,
                    metadata=metadata,
                    content=chunk,
                )
        self._runbooks_indexed = True


def main():
    """Run incident commander."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--db-path", default="./ops_db")
    parser.add_argument("--iterations", type=int, default=0)
    args = parser.parse_args()
    
    print("="*60)
    print("PROCESS C: INCIDENT COMMANDER")
    print("="*60)
    print(f"Opening SochDB database: {args.db_path}\n")
    
    try:
        commander = IncidentCommander(args.db_path)
        print("✅ Opened shared SochDB!\n")
        
        commander.monitor_loop(iterations=args.iterations)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Incident commander stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
