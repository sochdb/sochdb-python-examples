# Transactions Example

Demonstrates SochDB transactions with multi-key updates and atomic transfers.

## Running

```bash
./venv/bin/python example.py
```

## Expected Output (2026-01-27)

```
=== SochDB Python SDK - Transactions ===

✅ Database opened successfully

1. Successful Transaction
-------------------------
  Staged 3 account updates
✅ Transaction committed

Verified: account:alice = 1000

2. Atomic Transfer
------------------
Before: Alice = 1000
After:  Alice = 800
✅ Atomic transfer complete

3. Scan within Transaction
--------------------------
  account:alice = 800
  account:bob = 700
  account:charlie = 750
✅ Scanned 3 accounts in transaction

=== Example Complete ===
```
