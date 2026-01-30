"""Analytics copilot with spreadsheet data, SQL queries, and vector search.

Showcases:
- CSV ingestion to SQL tables
- TOON encoding for query results (40-67% token savings)
- Vector search for semantic analysis
- Token-budgeted context assembly
"""

import sys
import csv
import os
import glob
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from sochdb import Database
import sochdb
from shared.toon_encoder import rows_to_toon
from shared.llm_client import LLMClient
from shared.embeddings import EmbeddingClient


class AnalyticsCopilot:
    """Analytics copilot with SQL, TOON, and vector search."""
    
    def __init__(self, db_path: str = "./analytics_db"):
        """Initialize copilot."""
        self.db_path = db_path
        self.llm = LLMClient(model="gpt-4-turbo-preview")
        self.embedding_client = EmbeddingClient()
        self._cached_rows: List[Dict[str, Any]] = []
        self._notes_indexed = False

        if not os.environ.get("SOCHDB_LIB_PATH"):
            lib_root = os.path.join(os.path.dirname(sochdb.__file__), "lib")
            candidates = glob.glob(os.path.join(lib_root, "*", "libsochdb_index.*"))
            if candidates:
                os.environ["SOCHDB_LIB_PATH"] = candidates[0]

    @staticmethod
    def _sanitize_sql_text(value: str) -> str:
        return value.replace(",", " ").replace("\n", " ").replace("\r", " ").replace("'", "''")

    def _sql_value(self, value: Optional[str], is_text: bool = False) -> str:
        if value is None or value == "":
            return "NULL"
        if is_text:
            return f"'{self._sanitize_sql_text(value)}'"
        return str(value)
    
    def setup_database(self, csv_path: str):
        """Load CSV data into SQL table and index notes."""
        print(f"📥 Loading data from {csv_path}...")
        
        with Database.open(self.db_path) as db:
            # Create customers table
            db.execute_sql("""
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    account_value REAL NOT NULL,
                    contract_end TEXT NOT NULL,
                    monthly_active_days INTEGER,
                    support_tickets_30d INTEGER,
                    last_login_days_ago INTEGER,
                    feature_usage_score REAL,
                    notes TEXT
                )
            """)
            
            # Load CSV data
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            self._cached_rows = rows
            
            for row in rows:
                db.execute_sql(f"DELETE FROM customers WHERE id = {row['id']}")
                columns = (
                    "id, name, email, account_value, contract_end, "
                    "monthly_active_days, support_tickets_30d, last_login_days_ago, "
                    "feature_usage_score, notes"
                )
                values = ", ".join([
                    self._sql_value(row["id"]),
                    self._sql_value(row["name"], is_text=True),
                    self._sql_value(row["email"], is_text=True),
                    self._sql_value(row["account_value"]),
                    self._sql_value(row["contract_end"], is_text=True),
                    self._sql_value(row["monthly_active_days"]),
                    self._sql_value(row["support_tickets_30d"]),
                    self._sql_value(row["last_login_days_ago"]),
                    self._sql_value(row["feature_usage_score"]),
                    self._sql_value(row["notes"], is_text=True),
                ])
                insert_sql = f"INSERT INTO customers ({columns}) VALUES ({values})"
                db.execute_sql(insert_sql)
            
            print(f"  ✓ Loaded {len(rows)} customers into SQL table")
            
            # Index customer notes into vector collection
            print(f"🔍 Indexing customer notes for semantic search...")
            
            ns = db.get_or_create_namespace("analytics")
            dimension = self.embedding_client.dimension
            try:
                collection = ns.create_collection(
                    "customer_notes",
                    dimension=dimension,
                    enable_hybrid_search=True,
                )
            except Exception:
                collection = ns.get_collection("customer_notes")
            
            for row in rows:
                if row['notes'].strip():
                    embedding = self.embedding_client.embed(row['notes'])
                    collection.insert(
                        id=f"customer_{row['id']}",
                        vector=embedding,
                        metadata={
                            "customer_id": row['id'],
                            "customer_name": row['name'],
                        },
                        content=row["notes"],
                    )
            
            print(f"  ✓ Indexed {len(rows)} customer notes")
            self._notes_indexed = False
        
        print(f"✅ Database setup complete!\n")
    
    def analyze_churn_risk(self, query: str) -> Dict[str, Any]:
        """Analyze churn risk using SQL, TOON, and vector search.
        
        Args:
            query: User's analytical question
            
        Returns:
            Analysis results with response and debug info
        """
        print(f"{'='*70}")
        print(f"QUERY: {query}")
        print(f"{'='*70}\n")
        
        with Database.open(self.db_path) as db:
            # 1. SQL: Find at-risk customers
            print("📊 Querying at-risk customers (SQL)...")
            
            sql_query = """
                SELECT id, name, account_value, contract_end,
                       monthly_active_days, support_tickets_30d,
                       last_login_days_ago, feature_usage_score
                FROM customers
            """
            
            result = db.execute_sql(sql_query)
            all_customers = result.rows if result else []

            def is_at_risk(row):
                return (
                    row.get("monthly_active_days", 0) < 15
                    or row.get("support_tickets_30d", 0) > 5
                    or row.get("last_login_days_ago", 0) > 7
                    or row.get("feature_usage_score", 100) < 50
                )

            at_risk_customers = [row for row in all_customers if is_at_risk(row)]
            at_risk_customers.sort(
                key=lambda r: (r.get("feature_usage_score", 100), -r.get("support_tickets_30d", 0))
            )
            at_risk_customers = at_risk_customers[:10]
            
            print(f"  Found {len(at_risk_customers)} at-risk customers")
            
            # 2. TOON: Encode results compactly
            print("🔧 Encoding to TOON format...")
            
            fields = [
                "id", "name", "account_value", "contract_end",
                "monthly_active_days", "support_tickets_30d",
                "last_login_days_ago", "feature_usage_score"
            ]
            
            customers_toon = rows_to_toon(
                "at_risk_customers",
                at_risk_customers,
                fields=fields
            )
            
            # Count tokens saved
            import json
            import tiktoken
            
            json_version = json.dumps(at_risk_customers)
            enc = tiktoken.encoding_for_model("gpt-4")
            json_tokens = len(enc.encode(json_version))
            toon_tokens = len(enc.encode(customers_toon))
            if not at_risk_customers:
                tokens_saved = 0
                percent_saved = 0.0
            else:
                tokens_saved = json_tokens - toon_tokens
                percent_saved = (tokens_saved / json_tokens * 100) if json_tokens > 0 else 0
            
            print(f"  TOON tokens: {toon_tokens} | JSON tokens: {json_tokens}")
            print(f"  Saved: {tokens_saved} tokens ({percent_saved:.1f}%)")
            
            # 3. Vector search: Find relevant customer notes
            print("🔍 Searching customer notes (vector semantic search)...")
            
            query_embedding = self.embedding_client.embed(query)
            
            ns = db.get_or_create_namespace("analytics")
            collection = ns.get_collection("customer_notes")
            self._ensure_notes_indexed(collection)
            
            results = collection.hybrid_search(
                vector=query_embedding,
                text_query="churn risk support tickets low engagement",
                k=6,
                alpha=0.8,
            )
            
            notes_chunks = []
            for i, result in enumerate(results.results, 1):
                meta = result.metadata or {}
                content = meta.get("_content", "")
                customer = meta.get("customer_name", "unknown")
                notes_chunks.append(f"({i}) {customer}\n{content}")
            
            print(f"  Retrieved {len(notes_chunks)} relevant notes")
            
            # 4. Generate analysis
            print("💡 Generating churn risk analysis...")
            
            system_message = """You are a customer success data analyst.
Analyze customer data to identify churn risks and provide actionable recommendations.
Base your analysis on the SQL data and customer notes provided."""
            
            prompt = f"""Question: {query}

At-Risk Customers (TOON format):
{customers_toon}

Customer Notes (semantic search results):
{chr(10).join(notes_chunks)}

Provide:
1. Summary of top churn risks (list top 3-5 customers with reasons)
2. Common patterns across at-risk customers
3. Recommended interventions (priority order)
"""
            
            response = self.llm.complete(prompt, system_message=system_message)
            
            return {
                "query": query,
                "at_risk_count": len(at_risk_customers),
                "toon_tokens": toon_tokens,
                "json_tokens": json_tokens,
                "tokens_saved": tokens_saved,
                "percent_saved": percent_saved,
                "notes_retrieved": len(notes_chunks),
                "response": response,
                "customers_toon": customers_toon
            }

    def _ensure_notes_indexed(self, collection):
        if self._notes_indexed:
            return

        rows = self._cached_rows
        if not rows:
            return

        for row in rows:
            if row["notes"].strip():
                embedding = self.embedding_client.embed(row["notes"])
                collection.insert(
                    id=f"customer_{row['id']}",
                    vector=embedding,
                    metadata={
                        "customer_id": row["id"],
                        "customer_name": row["name"],
                    },
                    content=row["notes"],
                )
        self._notes_indexed = True


def main():
    """Run analytics copilot demo."""
    csv_path = Path(__file__).parent / "sample_data" / "customers.csv"
    
    if not csv_path.exists():
        print(f"❌ Error: {csv_path} not found")
        return
    
    copilot = AnalyticsCopilot()
    
    # Setup database
    copilot.setup_database(csv_path)
    
    # Example queries
    queries = [
        "Which customers are most at risk of churn, and why?",
        "What patterns do you see in customers with high support ticket counts?",
        "Which accounts should we prioritize for retention calls?"
    ]
    
    print("="*70)
    print("ANALYTICS COPILOT DEMO")
    print("="*70)
    print("\nAvailable queries:")
    for i, q in enumerate(queries, 1):
        print(f"  {i}. {q}")
    print(f"  {len(queries) + 1}. Custom query")
    print(f"  0. Exit")
    
    while True:
        print("\n" + "-"*70)
        choice = input(f"\nSelect query (0-{len(queries) + 1}): ")
        
        if choice == "0":
            print("\nExiting demo.")
            break
        
        try:
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(queries):
                query = queries[choice_num - 1]
            elif choice_num == len(queries) + 1:
                query = input("Enter your query: ")
            else:
                print("Invalid choice. Try again.")
                continue
            
            # Run analysis
            result = copilot.analyze_churn_risk(query)
            
            # Display results
            print("\n" + "="*70)
            print("ANALYSIS RESULTS")
            print("="*70)
            print(result["response"])
            
            print(f"\n📊 Statistics:")
            print(f"  At-risk customers: {result['at_risk_count']}")
            print(f"  Notes retrieved: {result['notes_retrieved']}")
            print(f"  TOON vs JSON: {result['toon_tokens']} vs {result['json_tokens']} tokens")
            print(f"  Token savings: {result['tokens_saved']} ({result['percent_saved']:.1f}%)")
            
        except ValueError:
            print("Invalid input. Try again.")
        except KeyboardInterrupt:
            print("\n\nExiting demo.")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
