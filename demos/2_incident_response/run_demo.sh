#!/bin/bash

# Run all three processes for the incident response demo

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DB_PATH="$SCRIPT_DIR/ops_db"

echo "=========================================="
echo "Multi-Agent Incident Response Demo"
echo "=========================================="
echo ""
echo "This demo showcases:"
echo "  ✓ IPC mode: shared SochDB across processes"
echo "  ✓ Namespace isolation"
echo "  ✓ Hybrid retrieval (vector + keyword with RRF)"
echo "  ✓ ACID state transitions"
echo ""
echo "Starting 3 processes:"
echo "  A. Metrics Collector (writes metrics to shared DB)"
echo "  B. Runbook Indexer (indexes runbooks to vector collection)"
echo "  C. Incident Commander (monitors metrics + retrieves runbooks)"
echo ""
echo "=========================================="
echo ""

echo "Starting processes..."
echo ""

# Run Process B (indexer) once to populate runbooks
echo "Starting Process B (Runbook Indexer)..."
python "$SCRIPT_DIR/process_b_indexer.py" --db-path "$DB_PATH" --once
echo ""

# Run Process A (collector) for a few iterations
echo "Starting Process A (Metrics Collector)..."
python "$SCRIPT_DIR/process_a_collector.py" --db-path "$DB_PATH" --iterations 4

# Run Process C (commander) for a few iterations
echo "Starting Process C (Incident Commander)..."
echo ""
echo "=========================================="
echo ""

python "$SCRIPT_DIR/process_c_commander.py" --db-path "$DB_PATH" --iterations 6

echo ""
echo "All processes stopped."
