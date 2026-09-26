#!/usr/bin/env python3
"""
Execute bulk collection assignments with rate limit handling.
This script will be called by Claude using MCP tools.
"""
import json
import time

def load_assignments():
    """Load assignment plan."""
    with open('collection_assignments.json', 'r') as f:
        return json.load(f)

def main():
    """Main execution with delay."""
    assignments = load_assignments()

    print(f"\n🚀 Executing {len(assignments)} collection assignments...")
    print(f"⏱️  Adding 3-second delay between API calls to avoid rate limiting\n")

    for i, assignment in enumerate(assignments, 1):
        collection_name = assignment['collection_name']
        collection_id = assignment['collection_id']
        product_ids = assignment['product_ids']
        count = assignment['count']

        print(f"{i}/{len(assignments)}. {collection_name}")
        print(f"   Adding {count} products to collection {collection_id}")
        print(f"   Product IDs: {product_ids[:3]}...")
        print(f"   ⏳ Waiting 3 seconds before next call...")

        # Note: Actual API call will be made via MCP by Claude
        # This script just provides the structure

        if i < len(assignments):
            time.sleep(3)  # 3-second delay between calls

    print(f"\n✅ All assignments queued for execution")
    print(f"\nCommands to execute via MCP:\n")

    for assignment in assignments:
        print(f"mcp__whapi-mcp__editCollection(")
        print(f"  CollectionID='{assignment['collection_id']}',")
        print(f"  add_products={json.dumps(assignment['product_ids'])}")
        print(f")")
        print()

if __name__ == '__main__':
    main()
