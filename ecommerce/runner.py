import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
import random

from .memory import SochDBMemory
from .config import get_sochdb_config

async def ingest_products_data(memory: SochDBMemory):
    print("📦 Ingesting products...")
    # Assume we are running from sochdb-examples root
    json_file_path = Path("donotuse/data/manybirds_products.json")
    
    if not json_file_path.exists():
        print(f"⚠️  Product file not found at {json_file_path}, using sample products.")
        products = [
            {
                "title": "SuperLight Wool Runners",
                "product_type": "Shoes",
                "vendor": "Manybirds",
                "body_html": "Lightweight wool runners with breathable comfort.",
                "variants": [{"title": "Size 10", "price": 120}, {"title": "Size 11", "price": 120}],
            },
            {
                "title": "Trail Wool Mizzles",
                "product_type": "Shoes",
                "vendor": "Manybirds",
                "body_html": "Water-resistant wool shoes for trail and city.",
                "variants": [{"title": "Size 9", "price": 140}, {"title": "Size 10", "price": 140}],
            },
        ]
    else:
        with open(json_file_path) as file:
            data = json.load(file)
            products = data.get('products', [])

    print(f"Found {len(products)} products.")
    
    for i, product in enumerate(products):
        # Create a nice text representation for embedding
        content = f"Product: {product['title']}\n"
        content += f"Type: {product['product_type']}\n"
        content += f"Vendor: {product['vendor']}\n"
        content += f"Description: {product.get('body_html', '')}\n"
        
        # Add variants info
        variants = product.get('variants', [])
        if variants:
            prices = [v['price'] for v in variants]
            content += f"Price Range: ${min(prices)} - ${max(prices)}\n"
            content += f"Sizes: {', '.join([v['title'] for v in variants])}\n"
            
        memory.add_episode(
            content=content,
            source="product_catalog",
            timestamp=datetime.now(timezone.utc).timestamp()
        )
        if (i+1) % 5 == 0:
            print(f"  Processed {i+1} products...")
            
    print("✅ Ingestion complete.")

async def simulate_conversation(memory: SochDBMemory):
    print("\n💬 Simulating conversation...")
    
    # Store conversation history
    conversation = [
        ("User", "I'm looking for some comfortable wool shoes."),
        ("Assistant", "We have great wool options. Are you looking for men's or women's?"),
        ("User", "Men's, specifically something grey."),
        ("Assistant", "I'd recommend the SuperLight Wool Runners in Dark Grey."),
        ("User", "That sounds good. Do you have size 10?"), 
        ("Assistant", "Yes, we have size 10 available for $120.")
    ]
    
    for role, text in conversation:
        print(f"{role}: {text}")
        memory.add_episode(
            content=f"{role}: {text}",
            source="conversation_history"
        )
        
    print("✅ Conversation stored.")

async def demonstrate_search(memory: SochDBMemory):
    print("\n🔍 Demonstrating TOON Search...")
    
    queries = [
        "wool shoes grey",
        "size 10 availability",
        "comfortable sneakers"
    ]
    
    for q in queries:
        print(f"\nQuery: '{q}'")
        result = memory.search(q, top_k=3)
        print(f"--- TOON Context ---\n{result}\n--------------------")

async def main():
    print("=== SochDB eCommerce Example ===")
    config = get_sochdb_config()
    print(f"Database: {config.db_path}")
    
    memory = SochDBMemory()
    
    try:
        # 1. Ingest Data
        await ingest_products_data(memory)
        
        # 2. Simulate Chat
        await simulate_conversation(memory)
        
        # 3. Search
        await demonstrate_search(memory)
        
    finally:
        memory.close()

if __name__ == "__main__":
    asyncio.run(main())
