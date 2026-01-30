"""Interactive demo runner for support agent."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent import SupportAgent


def main():
    """Run interactive support agent demo."""
    print("="*60)
    print("TOONDB SUPPORT AGENT DEMO")
    print("="*60)
    print("\nShowcasing:")
    print("  ✓ SQL queries for order data")
    print("  ✓ KV lookups for user preferences")
    print("  ✓ Vector RAG with hybrid search (vector + keyword)")
    print("  ✓ TOON encoding (40-67% token savings)")
    print("  ✓ ACID transactions for multi-table updates")
    print("\n" + "="*60 + "\n")
    
    agent = SupportAgent()
    
    # Example scenarios
    scenarios = [
        {
            "user_id": 123,
            "query": "My order #1004 is late. I'm traveling tomorrow. Can you reroute or replace it?"
        },
        {
            "user_id": 123,
            "query": "What's the status of my recent orders?"
        },
        {
            "user_id": 456,
            "query": "I need to change the delivery address for order #1003"
        }
    ]
    
    print("Available scenarios:")
    for i, scenario in enumerate(scenarios, 1):
        print(f"  {i}. User {scenario['user_id']}: {scenario['query']}")
    
    print(f"  {len(scenarios) + 1}. Custom query")
    print(f"  0. Exit")
    
    non_interactive = not sys.stdin.isatty()
    while True:
        print("\n" + "-"*60)
        if not non_interactive:
            choice = input("\nSelect scenario (0-{}): ".format(len(scenarios) + 1))
        else:
            choice = "1"
        
        if choice == "0":
            print("\nExiting demo.")
            break
        
        try:
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(scenarios):
                scenario = scenarios[choice_num - 1]
                user_id = scenario["user_id"]
                query = scenario["query"]
            elif choice_num == len(scenarios) + 1:
                user_id = int(input("Enter user ID: "))
                query = input("Enter query: ")
            else:
                print("Invalid choice. Try again.")
                continue
            
            # Run agent
            result = agent.handle_query(user_id, query)
            
            # Display result
            print("\n" + "="*60)
            print("AGENT RESPONSE")
            print("="*60)
            print(result["response"])
            
            if result["actions_taken"]:
                print("\n📋 Actions taken:")
                for action in result["actions_taken"]:
                    print(f"  - {action}")
            
            print(f"\n📊 Debug info:")
            print(f"  - Orders found: {result['orders_count']}")
            print(f"  - Policies retrieved: {result['policies_retrieved']}")
            print(f"  - TOON preview: {result['toon_preview'][:100]}...")

            if non_interactive:
                break
            
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
