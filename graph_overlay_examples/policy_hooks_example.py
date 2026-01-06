"""
ToonDB Policy Hooks Example
===========================

Demonstrates the Policy & Safety Hooks feature for agent operations,
providing trigger-based guardrails with decorators.

Features shown:
- @before_write hook for validation
- @after_read hook for audit logging
- @before_delete hook for access control
- Rate limiting with token buckets
- Pattern matching for key paths
"""

import toondb
from toondb.policy import (
    PolicyEngine, PolicyAction, PolicyContext,
    before_write, after_read, before_delete, after_commit,
    RateLimiter
)

def main():
    # Open database and create policy engine
    db = toondb.open("./policy_example_db")
    engine = PolicyEngine(db)
    
    print("=== ToonDB Policy Hooks Example ===\n")
    
    # -------------------------------------------------------
    # 1. Register policies using decorators
    # -------------------------------------------------------
    print("1. Registering policy hooks...")
    
    # Validation hook: ensure user data has required fields
    @before_write(engine, pattern="users/*")
    def validate_user_data(ctx: PolicyContext) -> PolicyAction:
        """Validate that user records have required fields."""
        data = ctx.value
        if isinstance(data, dict):
            if "email" not in data:
                print(f"   [POLICY] DENIED: Missing email for user")
                return PolicyAction.DENY
            if "name" not in data and ctx.operation == "insert":
                print(f"   [POLICY] DENIED: Missing name for new user")
                return PolicyAction.DENY
        print(f"   [POLICY] ALLOWED: Valid user data")
        return PolicyAction.ALLOW
    
    # PII redaction hook: mask sensitive data on read
    @after_read(engine, pattern="users/*/email")
    def redact_email(ctx: PolicyContext) -> PolicyAction:
        """Redact email addresses for audit compliance."""
        original = ctx.value
        if original and "@" in str(original):
            parts = str(original).split("@")
            redacted = parts[0][:2] + "***@" + parts[1]
            ctx.set_modified_value(redacted)
            print(f"   [POLICY] MODIFIED: Redacted email to {redacted}")
            return PolicyAction.MODIFY
        return PolicyAction.ALLOW
    
    # Access control hook: prevent deletion of admin users
    @before_delete(engine, pattern="users/*")
    def protect_admin_users(ctx: PolicyContext) -> PolicyAction:
        """Prevent deletion of admin users."""
        key = ctx.key
        if "admin" in key:
            print(f"   [POLICY] DENIED: Cannot delete admin user")
            return PolicyAction.DENY
        print(f"   [POLICY] ALLOWED: User deletion permitted")
        return PolicyAction.ALLOW
    
    # Audit logging hook: log all commits
    @after_commit(engine)
    def audit_commit(ctx: PolicyContext) -> PolicyAction:
        """Log all transaction commits for audit trail."""
        print(f"   [AUDIT] Committed transaction at timestamp {ctx.timestamp}")
        return PolicyAction.AUDIT
    
    print("   Registered 4 policy hooks")
    
    # -------------------------------------------------------
    # 2. Test validation hook
    # -------------------------------------------------------
    print("\n2. Testing validation hook...")
    
    # This should succeed (has required fields)
    try:
        engine.put("users/alice", {"name": "Alice", "email": "alice@example.com"})
        print("   ✓ Created user 'alice' successfully")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    # This should fail (missing email)
    try:
        engine.put("users/bob", {"name": "Bob"})  # Missing email
        print("   ✓ Created user 'bob' successfully")
    except Exception as e:
        print(f"   ✗ Blocked by policy: {e}")
    
    # -------------------------------------------------------
    # 3. Test read redaction hook
    # -------------------------------------------------------
    print("\n3. Testing read redaction hook...")
    
    # Store a user with email
    engine.put("users/charlie", {"name": "Charlie", "email": "charlie@secret.com"})
    
    # Reading should return redacted email
    user = engine.get("users/charlie")
    print(f"   Read user: {user}")
    
    # -------------------------------------------------------
    # 4. Test delete protection hook
    # -------------------------------------------------------
    print("\n4. Testing delete protection hook...")
    
    # Create an admin user
    engine.put("users/admin_root", {"name": "Root Admin", "email": "root@admin.com"})
    
    # Try to delete admin (should be blocked)
    try:
        engine.delete("users/admin_root")
        print("   ✓ Deleted admin user")
    except Exception as e:
        print(f"   ✗ Blocked by policy: {e}")
    
    # Delete regular user (should succeed)
    try:
        engine.delete("users/alice")
        print("   ✓ Deleted regular user 'alice'")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    # -------------------------------------------------------
    # 5. Rate limiting
    # -------------------------------------------------------
    print("\n5. Testing rate limiting...")
    
    # Create a rate limiter: 5 requests per 10 seconds
    limiter = RateLimiter(engine, max_tokens=5, refill_interval_s=10.0)
    
    # Simulate API calls
    for i in range(7):
        allowed, remaining = limiter.check("agent_1")
        status = "✓ Allowed" if allowed else "✗ Rate limited"
        print(f"   Request {i+1}: {status} (remaining: {remaining})")
    
    # -------------------------------------------------------
    # 6. Pattern matching examples
    # -------------------------------------------------------
    print("\n6. Pattern matching examples...")
    
    # Register a policy for specific patterns
    @before_write(engine, pattern="sessions/*/messages/*")
    def limit_message_size(ctx: PolicyContext) -> PolicyAction:
        """Limit message size to prevent abuse."""
        if len(str(ctx.value)) > 10000:
            return PolicyAction.DENY
        return PolicyAction.ALLOW
    
    patterns = [
        "users/*",
        "users/*/email",
        "sessions/*/messages/*",
        "config/**"
    ]
    for p in patterns:
        print(f"   Pattern: {p}")
    
    # Cleanup
    db.close()
    print("\n=== Policy Hooks Example Complete ===")

if __name__ == "__main__":
    main()
