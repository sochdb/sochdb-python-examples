"""
Namespace Example - SochDB Python SDK
"""

from sochdb import Database

def main():
    print("=== SochDB Python SDK - Namespaces ===\n")

    db = Database.open("./data/namespace_db")
    print("✅ Database opened\n")

    try:
        # Create and use namespaces
        print("1. Create Namespaces")
        print("--------------------")
        
        # Namespaces must be created before use
        ns1 = db.get_or_create_namespace("tenant_acme")
        ns2 = db.get_or_create_namespace("tenant_globex")
        
        ns1.put(b"company", b"Acme Corporation")
        ns1.put(b"users", b"150")
        
        ns2.put(b"company", b"Globex Corporation")
        ns2.put(b"users", b"500")
        
        print("✅ Stored data in 2 namespaces\n")

        # Data isolation
        print("2. Data Isolation")
        print("-----------------")
        
        acme = ns1.get(b"company")
        globex = ns2.get(b"company")
        
        print(f"Acme:   {acme.decode()}")
        print(f"Globex: {globex.decode()}")
        print("✅ Data properly isolated\n")

        print("=== Example Complete ===")
    finally:
        db.close()

if __name__ == "__main__":
    main()
