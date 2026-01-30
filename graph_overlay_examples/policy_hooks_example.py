"""
SochDB Policy Hooks (App-Level) Example
=======================================

The current Python SDK does not expose built-in policy hooks,
so this example demonstrates equivalent guardrails at the
application layer.
"""

from sochdb import Database


def validate_user(value: dict) -> bool:
    return "email" in value and "name" in value


def redact_pii(value: dict) -> dict:
    redacted = dict(value)
    if "email" in redacted:
        redacted["email"] = "***@***"
    return redacted


def main():
    print("=== SochDB Policy Hooks (App-Level) Example ===\n")

    db = Database.open("./policy_example_db")
    print("✓ Database opened")

    user_key = b"users/1001"
    user_value = {"name": "Alice", "email": "alice@example.com"}

    # Before-write validation
    if not validate_user(user_value):
        print("✗ Validation failed: missing required fields")
    else:
        db.put(user_key, str(user_value).encode())
        print("✓ User stored")

    # After-read redaction
    raw = db.get(user_key)
    if raw:
        stored = eval(raw.decode())  # demo-only parsing
        redacted = redact_pii(stored)
        print(f"✓ Redacted view: {redacted}")

    # Before-delete guard
    allow_delete = False
    if not allow_delete:
        print("✓ Delete blocked by policy")
    else:
        db.delete(user_key)

    db.close()
    print("\n=== Policy Hooks Example Complete ===")


if __name__ == "__main__":
    main()
