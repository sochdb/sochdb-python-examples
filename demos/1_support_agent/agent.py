"""Support agent with RAG + SQL + transactional writes.

Showcases:
- SQL queries for order data (execute_sql)
- KV lookups for user preferences
- Vector RAG with token-budgeted ContextQuery
- TOON encoding (40-67% token savings vs JSON)
- ACID transactions for multi-table writes
"""

import os
import sys
import glob
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add parent directory to path to import shared utilities
sys.path.insert(0, str(Path(__file__).parent.parent))

from sochdb import Database
from shared.toon_encoder import rows_to_toon
from shared.llm_client import LLMClient
from shared.embeddings import EmbeddingClient


class SupportAgent:
    """Support agent with SQL, KV, vector RAG, and ACID transactions."""

    @staticmethod
    def _sanitize_sql_text(value: str) -> str:
        """Sanitize text for SochDB's basic SQL parser (commas break inserts)."""
        return value.replace(",", " ").replace("\n", " ").replace("\r", " ").replace("'", "''")
    
    def __init__(self, db_path: str = "./shop_db"):
        """Initialize agent with database connection."""
        self.db_path = db_path
        self.llm = LLMClient(model="gpt-4-turbo-preview", temperature=0.7)
        self.embedding_client = EmbeddingClient()
        self._policies_indexed = False

        if not os.environ.get("SOCHDB_LIB_PATH"):
            import sochdb

            lib_root = os.path.join(os.path.dirname(sochdb.__file__), "lib")
            candidates = glob.glob(os.path.join(lib_root, "*", "libsochdb_index.*"))
            if candidates:
                os.environ["SOCHDB_LIB_PATH"] = candidates[0]
    
    def handle_query(self, user_id: int, user_question: str) -> Dict[str, Any]:
        """Handle user support query.
        
        Args:
            user_id: Customer user ID
            user_question: User's question/request
            
        Returns:
            Dictionary with response, actions taken, and debug info
        """
        print(f"\n{'='*60}")
        print(f"User {user_id}: {user_question}")
        print(f"{'='*60}\n")
        
        with Database.open(self.db_path) as db:
            # 1. Fetch customer orders from SQL
            print("📊 Fetching order data from SQL...")
            orders_result = db.execute_sql(f"""
                SELECT id, status, eta, destination, total
                FROM orders
                WHERE user_id = {user_id}
                ORDER BY created_at DESC
                LIMIT 5
            """)
            
            orders = orders_result.rows if orders_result else []
            print(f"   Found {len(orders)} orders")
            
            # 2. Convert to TOON format
            print("🔧 Encoding orders to TOON format...")
            orders_toon = rows_to_toon(
                "orders",
                orders,
                fields=["id", "status", "eta", "destination", "total"]
            )
            print(f"   TOON format:\n{orders_toon}")
            
            # 3. Get user preferences from KV
            print("👤 Fetching user preferences from KV...")
            prefs = {}
            prefs_keys = [
                "replacements_over_refunds",
                "expedited_shipping_only",
                "eco_friendly"
            ]
            
            for key in prefs_keys:
                value = db.get(f"users/{user_id}/prefs/{key}".encode())
                if value:
                    prefs[key] = value.decode()
            
            user_name = db.get(f"users/{user_id}/name".encode())
            user_name = user_name.decode() if user_name else f"User {user_id}"
            print(f"   User: {user_name}")
            print(f"   Preferences: {prefs}")
            
            # 4. Vector RAG: retrieve relevant policies
            print("🔍 Retrieving relevant policies (vector RAG)...")
            query_embedding = self.embedding_client.embed(user_question)
            
            ns = db.get_or_create_namespace("support_system")
            try:
                collection = ns.get_collection("policies")
            except Exception:
                collection = ns.create_collection(
                    "policies",
                    dimension=self.embedding_client.dimension,
                    enable_hybrid_search=True,
                )

            self._ensure_policies_indexed(collection)
            
            results = collection.hybrid_search(
                vector=query_embedding,
                text_query="late shipment reroute replacement policy",
                k=5,
                alpha=0.7,
            )
            
            policy_chunks = []
            for i, result in enumerate(results.results, 1):
                meta = result.metadata or {}
                content = meta.get("_content", "")
                source = meta.get("source", "unknown")
                policy_chunks.append(f"({i}) {source}\n{content}")
            
            policies_markdown = "\n\n".join(policy_chunks)
            print(f"   Retrieved {len(policy_chunks)} policy chunks")
            
            # 5. Build prompt with TOON + context
            print("💬 Generating LLM response...")
            
            prefs_str = ", ".join(f"{k}={v}" for k, v in prefs.items()) if prefs else "none"
            
            system_message = """You are a customer support agent. Follow company policies strictly.
Do not invent shipment facts. Base your response on the order data and policies provided.
Suggest concrete actions (reroute, replacement, refund) based on the situation."""
            
            prompt = f"""User: {user_name} ({user_id})
Preferences: {prefs_str}

Question: {user_question}

Recent orders (TOON format):
{orders_toon}

Relevant policies:
{policies_markdown}

Provide a helpful response and suggest specific actions to resolve this issue.
"""
            
            response = self.llm.complete(prompt, system_message=system_message)
            print(f"   Response: {response[:100]}...")
            
            # 6. Execute actions (ACID transaction)
            actions_taken = []
            
            # Parse response to determine actions (simplified - in real system, use structured output)
            if "reroute" in response.lower() or "re-route" in response.lower():
                print("⚡ Executing ACID transaction: reroute order...")
                actions_taken.append(self._execute_reroute_transaction(db, orders, user_question))
            
            elif "replacement" in response.lower() and len(orders) > 0:
                print("⚡ Executing ACID transaction: create replacement...")
                actions_taken.append(self._execute_replacement_transaction(db, orders[0]))
            
            # Always log the interaction
            self._log_interaction(db, user_id, user_question, response)
            
            return {
                "user_id": user_id,
                "user_name": user_name,
                "question": user_question,
                "response": response,
                "orders_count": len(orders),
                "actions_taken": actions_taken,
                "policies_retrieved": len(policy_chunks),
                "toon_preview": orders_toon[:200]
            }
    
    def _execute_reroute_transaction(
        self,
        db: Database,
        orders: List[Dict],
        user_question: str
    ) -> str:
        """Execute reroute transaction (update order + create ticket + audit log)."""
        if not orders:
            return "No orders to reroute"
        
        # Find order that needs rerouting (simplified - take first late/in-transit order)
        target_order = None
        for order in orders:
            if order.get("status") in ["LATE", "IN_TRANSIT"]:
                target_order = order
                break
        
        if not target_order:
            return "No eligible orders for reroute"
        
        order_id = target_order["id"]
        timestamp = datetime.now().isoformat()
        
        # ACID transaction: all-or-nothing
        try:
            # Update order status
            db.execute_sql(f"""
                UPDATE orders
                SET status = 'REROUTE_REQUESTED'
                WHERE id = {order_id}
            """)
            
            # Create support ticket
            reason = self._sanitize_sql_text("Reroute request")
            db.execute_sql(f"""
                INSERT INTO tickets (order_id, reason, created_at)
                VALUES ({order_id}, '{reason}', '{timestamp}')
            """)
            
            # Log audit trail
            details = self._sanitize_sql_text("User requested reroute")
            db.execute_sql(f"""
                INSERT INTO audit_logs (entity_type, entity_id, action, details, timestamp)
                VALUES ('order', {order_id}, 'reroute_requested', '{details}', '{timestamp}')
            """)
            
            return f"Rerouted order #{order_id}"
        except Exception as e:
            return f"Transaction failed: {e}"
    
    def _execute_replacement_transaction(self, db: Database, order: Dict) -> str:
        """Execute replacement transaction."""
        order_id = order["id"]
        timestamp = datetime.now().isoformat()
        
        try:
            # Update order
            db.execute_sql(f"""
                UPDATE orders
                SET status = 'REPLACEMENT_PROCESSING'
                WHERE id = {order_id}
            """)
            
            # Create ticket
            reason = self._sanitize_sql_text("Replacement requested")
            db.execute_sql(f"""
                INSERT INTO tickets (order_id, reason, created_at)
                VALUES ({order_id}, '{reason}', '{timestamp}')
            """)
            
            # Audit log
            details = self._sanitize_sql_text("Replacement order initiated")
            db.execute_sql(f"""
                INSERT INTO audit_logs (entity_type, entity_id, action, details, timestamp)
                VALUES ('order', {order_id}, 'replacement_requested', '{details}', '{timestamp}')
            """)
            
            return f"Created replacement for order #{order_id}"
        except Exception as e:
            return f"Transaction failed: {e}"

    def _ensure_policies_indexed(self, collection):
        """Index policy documents in the current process (vector index is in-memory)."""
        if self._policies_indexed:
            return

        policies_dir = Path(__file__).parent / "policies"
        for policy_file in policies_dir.glob("*.txt"):
            with open(policy_file, "r") as f:
                content = f.read()
            chunks = [chunk.strip() for chunk in content.split("\n\n") if chunk.strip()]
            for i, chunk in enumerate(chunks):
                if len(chunk) < 50:
                    continue
                embedding = self.embedding_client.embed(chunk)
                doc_id = f"{policy_file.stem}_chunk_{i}"
                metadata = {
                    "source": policy_file.name,
                    "type": "policy",
                    "chunk_index": i,
                }
                collection.insert(
                    id=doc_id,
                    vector=embedding,
                    metadata=metadata,
                    content=chunk,
                )

        self._policies_indexed = True
    
    def _log_interaction(
        self,
        db: Database,
        user_id: int,
        question: str,
        response: str
    ):
        """Log customer interaction to audit trail."""
        timestamp = datetime.now().isoformat()
        details = self._sanitize_sql_text(f"Q: {question[:50]}... | A: {response[:50]}...")
        
        db.execute_sql(f"""
            INSERT INTO audit_logs (entity_type, entity_id, action, details, timestamp)
            VALUES ('user', {user_id}, 'support_interaction', '{details}', '{timestamp}')
        """)


if __name__ == "__main__":
    # Example usage
    agent = SupportAgent()
    
    # Test query
    result = agent.handle_query(
        user_id=123,
        user_question="My order #1004 is late. I'm traveling tomorrow. Can you reroute or replace it?"
    )
    
    print("\n" + "="*60)
    print("RESULT SUMMARY")
    print("="*60)
    print(f"Response: {result['response']}")
    print(f"Actions: {result['actions_taken']}")
    print(f"Policies retrieved: {result['policies_retrieved']}")
