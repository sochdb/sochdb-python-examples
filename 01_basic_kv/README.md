# Basic Key-Value Operations

Demonstrates fundamental SochDB operations for storing and retrieving data.

## Features

- Opening an embedded database
- PUT: Storing key-value pairs
- GET: Retrieving values by key
- SCAN: Iterating over keys with prefix
- DELETE: Removing keys
- Stats: Database statistics

## Running

```bash
./venv/bin/python example.py
```

## Expected Output

Sample output (2026-01-27):
```
=== SochDB Python SDK - Basic Key-Value Operations ===

✅ Database opened successfully

1. PUT Operations
-----------------
Stored: user:1001
✅ Stored multiple key-value pairs

2. GET Operations
-----------------
Retrieved: user:1001 = {"name": "Alice", "email": "alice@example.com"}
Key not found: user:9999 (expected)

3. SCAN Operations
------------------
Scanning keys with prefix "user:"
  user:1001 = {"name": "Alice", "email": "alice@example.com"}
  user:1002 = {"name": "Bob", "email": "bob@example.com"}
  user:1003 = {"name": "Charlie", "email": "charlie@example.com"}
✅ Scanned 3 keys

4. DELETE Operations
--------------------
Deleted: user:1001
✅ Key successfully deleted

5. Database Statistics
----------------------
Keys count: -1
Bytes written: 0 bytes
Transactions committed: 0

=== Example Complete ===
```

Note: `keys_count` currently reports `-1` in the SDK stats output.
