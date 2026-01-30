"""Run analytics copilot demo interactively."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from copilot import AnalyticsCopilot


def main():
    """Run interactive analytics copilot."""
    csv_path = Path(__file__).parent / "sample_data" / "customers.csv"
    
    if not csv_path.exists():
        print(f"❌ Error: {csv_path} not found")
        return
    
    print("="*70)
    print("TOONDB ANALYTICS COPILOT DEMO")
    print("="*70)
    print("\nShowcasing:")
    print("  ✓ CSV ingestion to SQL tables")
    print("  ✓ TOON encoding (40-67% token savings vs JSON)")
    print("  ✓ Vector search for semantic text analysis")
    print("  ✓ Token-budgeted context assembly")
    print("  ✓ SQL + Vectors in one database")
    print("\n" + "="*70 + "\n")
    
    # Initialize copilot and setup database
    copilot = AnalyticsCopilot()
    copilot.setup_database(csv_path)
    
    # Example queries
    queries = [
        "Which customers are most at risk of churn, and why?",
        "What patterns do you see in customers with high support ticket counts?",
        "Which accounts should we prioritize for retention calls?",
        "Identify customers with low engagement but high account value"
    ]
    
    print("Available example queries:")
    for i, q in enumerate(queries, 1):
        print(f"  {i}. {q}")
    print(f"  {len(queries) + 1}. Custom query")
    print(f"  0. Exit")
    
    non_interactive = not sys.stdin.isatty()
    while True:
        print("\n" + "-"*70)
        if non_interactive:
            choice = "1"
        else:
            choice = input(f"\nSelect query (0-{len(queries) + 1}): ")
        
        if choice == "0":
            print("\nExiting demo.")
            break
        
        try:
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(queries):
                query = queries[choice_num - 1]
            elif choice_num == len(queries) + 1:
                query = input("\nEnter your query: ")
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
            
            print(f"\n{'='*70}")
            print("STATISTICS")
            print("="*70)
            print(f"📊 At-risk customers found: {result['at_risk_count']}")
            print(f"📝 Relevant notes retrieved: {result['notes_retrieved']}")
            print(f"\n💾 Token Savings (TOON vs JSON):")
            print(f"   JSON tokens:  {result['json_tokens']}")
            print(f"   TOON tokens:  {result['toon_tokens']}")
            print(f"   Saved:        {result['tokens_saved']} tokens ({result['percent_saved']:.1f}%)")
            print("="*70)

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
