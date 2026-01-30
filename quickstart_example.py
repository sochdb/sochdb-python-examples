#!/usr/bin/env python3
"""
Quick Start Example for SochDB Comprehensive Test Harness

This demonstrates how to use the harness components programmatically.
"""

from comprehensive_harness import (
    SyntheticGenerator,
    MetricsRecorder,
    ScenarioRunner,
    ScorecardAggregator,
)
from sochdb import Database
from datetime import datetime
import json
import os
import glob
import sochdb


def _ensure_sochdb_lib_path():
    if os.environ.get("SOCHDB_LIB_PATH"):
        return
    lib_root = os.path.join(os.path.dirname(sochdb.__file__), "lib")
    candidates = glob.glob(os.path.join(lib_root, "*", "libsochdb_index.*"))
    if candidates:
        os.environ["SOCHDB_LIB_PATH"] = candidates[0]

def main():
    print("SochDB Test Harness - Quick Start Example\n")
    print("=" * 70)

    _ensure_sochdb_lib_path()
    
    # 1. Setup
    print("\n1. Initializing components...")
    generator = SyntheticGenerator(seed=42, scale="small")
    recorder = MetricsRecorder()
    db = Database.open("./quickstart_db")
    
    print(f"   - Topics: {generator.num_topics}")
    print(f"   - Embedding dimension: {generator.embedding_dim}")
    print(f"   - Tenants: {generator.params['tenants']}")
    
    # 2. Generate synthetic data
    print("\n2. Generating synthetic test data...")
    tenants = generator.generate_tenants()
    print(f"   - Created {len(tenants)} tenants: {tenants}")
    
    # Example: Generate documents for one tenant
    docs = generator.generate_collection_docs(tenants[0], "support", num_docs=10)
    print(f"   - Generated {len(docs)} documents")
    print(f"   - Sample doc ID: {docs[0]['id']}")
    print(f"   - Sample topic: {docs[0]['topic_id']}")
    
    # 3. Run one scenario
    print("\n3. Running a test scenario...")
    runner = ScenarioRunner(db, generator, recorder, mode="embedded")
    
    # Run just scenario 1
    metrics = recorder.get_or_create("01_multi_tenant_support")
    try:
        runner.scenario_01_multi_tenant(metrics)
        status = "✅ PASSED" if metrics.passed else "❌ FAILED"
        print(f"   - Status: {status}")
        print(f"   - Leakage rate: {metrics.leakage_rate:.4f}")
        print(f"   - NDCG@10: {metrics.ndcg_at_10:.3f}")
    except Exception as e:
        print(f"   - Error: {e}")
    
    # 4. Generate scorecard
    print("\n4. Generating scorecard...")
    run_meta = {
        "seed": 42,
        "scale": "small",
        "mode": "embedded",
        "sdk_version": "0.3.3",
        "started_at": datetime.now().isoformat(),
        "duration_s": 0.0,
    }
    
    aggregator = ScorecardAggregator(recorder, run_meta)
    scorecard = aggregator.generate_scorecard()
    
    print(f"   - Overall score: {scorecard['overall']['score_0_100']:.1f}/100")
    print(f"   - Passed: {scorecard['overall']['passed_scenarios']}/{scorecard['overall']['total_scenarios']}")
    
    # 5. Save results
    output_file = "quickstart_scorecard.json"
    with open(output_file, "w") as f:
        json.dump(scorecard, f, indent=2)
    
    print(f"\n5. Results saved to: {output_file}")
    
    # 6. Cleanup
    db.close()
    import shutil
    shutil.rmtree("./quickstart_db")
    
    print("\n" + "=" * 70)
    print("✅ Quick start complete!\n")
    print("Next steps:")
    print("  - Run full harness: python3 comprehensive_harness.py")
    print("  - Try different scales: --scale medium")
    print("  - Read docs: cat HARNESS_README.md")


if __name__ == "__main__":
    main()
