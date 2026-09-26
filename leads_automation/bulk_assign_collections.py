#!/usr/bin/env python3
"""
Bulk assign WhatsApp catalogue products to collections based on BHK type.
"""
import json
import re
import time

# Collection mapping (from Whapi)
COLLECTIONS = {
    '1RK/1BHK': {'id': '4509547129362567', 'name': '🏠1RK & 1BHK'},
    '2BHK': {'id': '4042590602564256', 'name': '🏡 2BHK'},
    '3BHK': {'id': '1815741919601804', 'name': '🏡3BHK'},
    '4+BHK': {'id': '1796030415157419', 'name': '🏘️ 4+ BHK'},
}

def detect_bhk_type(product_name):
    """Detect BHK type from product name."""
    name_lower = product_name.lower()

    # Check for specific patterns (most specific first)
    if re.search(r'5\s*bhk', name_lower):
        return '4+BHK'
    elif re.search(r'4\s*bhk', name_lower):
        return '4+BHK'
    elif re.search(r'3\.5\s*bhk', name_lower):
        return '3BHK'
    elif re.search(r'3\s*bhk', name_lower):
        return '3BHK'
    elif re.search(r'2\.5\s*bhk', name_lower):
        return '2BHK'
    elif re.search(r'2\s*bhk', name_lower):
        return '2BHK'
    elif re.search(r'1\s*bhk', name_lower):
        return '1RK/1BHK'
    elif re.search(r'1\s*rk', name_lower):
        return '1RK/1BHK'
    elif 'studio' in name_lower:
        return '1RK/1BHK'
    else:
        return None

def load_data():
    """Load products and collections from saved JSON files."""
    with open('/Users/zeidzakir/.claude/projects/-Users-zeidzakir-Projects-efps-internal-automatios-leads-automation/0eb13371-1df7-4bc8-8a75-e36c194522a1/tool-results/mcp-whapi-mcp-getProducts-1790354385488.txt', 'r') as f:
        products_data = json.load(f)

    with open('/Users/zeidzakir/.claude/projects/-Users-zeidzakir-Projects-efps-internal-automatios-leads-automation/0eb13371-1df7-4bc8-8a75-e36c194522a1/tool-results/mcp-whapi-mcp-getCollectionsList-1790354433548.txt', 'r') as f:
        collections_data = json.load(f)

    return products_data, collections_data

def find_unassigned_products(products_data, collections_data):
    """Find products that are not in any collection."""
    products = products_data.get('content', {}).get('products', [])
    collections = collections_data.get('content', {}).get('collections', [])

    # Get all product IDs that are in collections
    products_in_collections = set()
    for col in collections:
        for prod in col.get('products', []):
            products_in_collections.add(prod.get('id'))

    # Find unassigned products
    unassigned = []
    for prod in products:
        if prod.get('id') not in products_in_collections:
            unassigned.append(prod)

    return unassigned

def group_by_collection(products):
    """Group products by their target collection based on BHK type."""
    grouped = {
        '1RK/1BHK': [],
        '2BHK': [],
        '3BHK': [],
        '4+BHK': [],
        'UNKNOWN': []
    }

    for prod in products:
        name = prod.get('name', '')
        bhk_type = detect_bhk_type(name)

        if bhk_type:
            grouped[bhk_type].append(prod)
        else:
            grouped['UNKNOWN'].append(prod)

    return grouped

def print_summary(grouped):
    """Print assignment summary."""
    print("\n" + "="*70)
    print("BULK COLLECTION ASSIGNMENT PLAN")
    print("="*70)

    total = 0
    for bhk_type, products in grouped.items():
        if bhk_type == 'UNKNOWN':
            continue
        count = len(products)
        total += count
        if count > 0:
            collection_name = COLLECTIONS[bhk_type]['name']
            print(f"\n{collection_name}:")
            print(f"  → Adding {count} products")
            for i, prod in enumerate(products[:3], 1):
                print(f"     {i}. {prod.get('name', 'Unnamed')[:60]}...")
            if count > 3:
                print(f"     ... and {count - 3} more")

    if grouped['UNKNOWN']:
        print(f"\n⚠️  UNKNOWN BHK TYPE ({len(grouped['UNKNOWN'])} products):")
        for prod in grouped['UNKNOWN']:
            print(f"     - {prod.get('name', 'Unnamed')}")

    print(f"\n{'='*70}")
    print(f"TOTAL: {total} products will be assigned to collections")
    print(f"{'='*70}\n")

    return total

def generate_mcp_commands(grouped):
    """Generate MCP command calls for bulk assignment."""
    print("\n" + "="*70)
    print("MCP COMMANDS TO EXECUTE")
    print("="*70 + "\n")

    commands = []
    for bhk_type, products in grouped.items():
        if bhk_type == 'UNKNOWN' or not products:
            continue

        collection_id = COLLECTIONS[bhk_type]['id']
        collection_name = COLLECTIONS[bhk_type]['name']
        product_ids = [p.get('id') for p in products]

        command = {
            'collection_id': collection_id,
            'collection_name': collection_name,
            'product_ids': product_ids,
            'count': len(product_ids)
        }
        commands.append(command)

        print(f"Collection: {collection_name}")
        print(f"  editCollection(")
        print(f"    CollectionID: '{collection_id}',")
        print(f"    add_products: {product_ids}")
        print(f"  )")
        print(f"  → Will add {len(product_ids)} products\n")

    return commands

def main():
    """Main execution function."""
    print("\n🔍 Loading catalogue data...")
    products_data, collections_data = load_data()

    print("🔍 Finding unassigned products...")
    unassigned = find_unassigned_products(products_data, collections_data)
    print(f"   Found {len(unassigned)} products without collections")

    print("\n🔍 Grouping by BHK type...")
    grouped = group_by_collection(unassigned)

    # Print summary
    total = print_summary(grouped)

    # Generate MCP commands
    commands = generate_mcp_commands(grouped)

    # Save commands to file for execution
    output_file = 'collection_assignments.json'
    with open(output_file, 'w') as f:
        json.dump(commands, f, indent=2)

    print(f"\n✅ Assignment plan saved to: {output_file}")
    print(f"\nNext step: Review the plan above, then run the MCP commands")
    print(f"to apply {total} product assignments.\n")

if __name__ == '__main__':
    main()
