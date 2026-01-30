"""Process A: Metrics and events collector.

Simulates collecting metrics and deployment events, writing to shared SochDB via IPC.
"""

import sys
import time
import random
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from sochdb import Database


def collect_metrics(db: Database, iterations: int = 0):
    """Simulate metrics collection and write to shared DB."""
    print("🔄 Process A: Metrics Collector")
    print("  Writing metrics to shared SochDB via IPC...\n")
    
    iteration = 0
    
    while True:
        iteration += 1
        timestamp = datetime.now().isoformat()
        
        # Simulate metrics
        latency_p99 = random.randint(200, 1500) if iteration < 20 else random.randint(800, 3000)
        error_rate = round(random.uniform(0.1, 2.5), 2) if iteration < 20 else round(random.uniform(2.0, 8.0), 2)
        cpu_usage = round(random.uniform(30, 85), 1)
        
        # Write metrics to KV paths
        db.put(f"metrics/latency_p99/{timestamp}".encode(), str(latency_p99).encode())
        db.put(f"metrics/error_rate/{timestamp}".encode(), str(error_rate).encode())
        db.put(f"metrics/cpu_usage/{timestamp}".encode(), str(cpu_usage).encode())
        
        # Write latest metrics for quick access
        db.put(b"metrics/latest/latency_p99", str(latency_p99).encode())
        db.put(b"metrics/latest/error_rate", str(error_rate).encode())
        db.put(b"metrics/latest/cpu_usage", str(cpu_usage).encode())
        db.put(b"metrics/latest/timestamp", timestamp.encode())
        
        print(f"  [{timestamp}] Latency P99: {latency_p99}ms | Error Rate: {error_rate}% | CPU: {cpu_usage}%")
        
        # Simulate deployment event occasionally
        if iteration % 30 == 0:
            deploy_event = f"Deployment v1.{iteration // 30}.0 to production"
            db.put(f"events/deployments/{timestamp}".encode(), deploy_event.encode())
            print(f"  📦 {deploy_event}")
        
        # Simulate incident trigger
        if latency_p99 > 1000 and error_rate > 5.0:
            incident_key = b"incidents/current/severity"
            existing = db.get(incident_key)
            if not existing or existing == b"NONE":
                print(f"\n  🚨 HIGH LATENCY + HIGH ERROR RATE DETECTED!")
                print(f"     Triggering incident response...\n")
                db.put(b"incidents/current/severity", b"HIGH")
                db.put(b"incidents/current/trigger_time", timestamp.encode())
                db.put(b"incidents/current/latency", str(latency_p99).encode())
                db.put(b"incidents/current/error_rate", str(error_rate).encode())

        if iterations and iteration >= iterations:
            break

        time.sleep(5)  # Collect metrics every 5 seconds


def main():
    """Run metrics collector."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--db-path", default="./ops_db")
    parser.add_argument("--iterations", type=int, default=0)
    args = parser.parse_args()
    
    print("="*60)
    print("PROCESS A: METRICS COLLECTOR")
    print("="*60)
    print(f"Opening SochDB database: {args.db_path}\n")
    
    try:
        db = Database.open(args.db_path)
        print("✅ Opened shared SochDB!\n")
        
        # Initialize metrics
        db.put(b"metrics/latest/latency_p99", b"0")
        db.put(b"metrics/latest/error_rate", b"0.0")
        db.put(b"metrics/latest/cpu_usage", b"0.0")
        db.put(b"incidents/current/severity", b"NONE")

        collect_metrics(db, iterations=args.iterations)
        db.close()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Metrics collector stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
