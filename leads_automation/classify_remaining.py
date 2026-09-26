#!/usr/bin/env python3
"""
Classify ONLY remaining unclassified leads
"""

import sys
sys.path.insert(0, '.')

# Import the existing classifier
from classify_with_bedrock import LeadClassifier, DB_PATH, BATCH_SIZE, BATCH_DELAY
import sqlite3
import time

print("\n" + "="*80)
print("CLASSIFYING REMAINING UNCLASSIFIED LEADS")
print("="*80 + "\n")

# Initialize classifier
classifier = LeadClassifier()

# Connect to database
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get ONLY unclassified leads
cursor.execute("""
    SELECT phone_number, extracted_from_phone
    FROM leads
    WHERE classification IS NULL
    ORDER BY last_interaction_date DESC
""")
leads = cursor.fetchall()

print(f"📊 Unclassified leads: {len(leads)}")
print(f"📦 Batch size: {BATCH_SIZE}")
print(f"⏱️  Delay: {BATCH_DELAY}s between batches")
print(f"⏳ Estimated time: ~{(len(leads) / BATCH_SIZE) * BATCH_DELAY / 60:.1f} minutes\n")
print("-"*80 + "\n")

results = []
start_time = time.time()

# Process in batches
for batch_idx in range(0, len(leads), BATCH_SIZE):
    batch = leads[batch_idx:batch_idx + BATCH_SIZE]
    batch_num = (batch_idx // BATCH_SIZE) + 1
    total_batches = (len(leads) + BATCH_SIZE - 1) // BATCH_SIZE

    print(f"Batch {batch_num}/{total_batches} (Leads {batch_idx + 1}-{min(batch_idx + BATCH_SIZE, len(leads))}):")

    for lead in batch:
        phone = lead['phone_number']
        source_phone = lead['extracted_from_phone']

        # Fetch conversations
        cursor.execute("""
            SELECT direction, message_body, message_type, timestamp
            FROM conversations
            WHERE phone_number = ?
            ORDER BY timestamp ASC
        """, (phone,))
        conversations = [dict(row) for row in cursor.fetchall()]

        # Classify
        result = classifier.classify(phone, conversations, source_phone)

        # Format notes
        notes = f"{result['reasoning']} | Confidence: {result['confidence']:.2f} | Intent: {result['intent']}"

        # Update database
        cursor.execute("""
            UPDATE leads
            SET classification = ?,
                notes = ?,
                bhk_requirement = ?,
                preferred_location = ?,
                budget_max = ?,
                furnishing_preference = ?,
                occupancy_type = ?,
                move_in_date = ?
            WHERE phone_number = ?
        """, (
            result['classification'],
            notes,
            result['extracted_entities'].get('bhk_requirement'),
            result['extracted_entities'].get('preferred_location'),
            result['extracted_entities'].get('budget_max'),
            result['extracted_entities'].get('furnishing'),
            result['extracted_entities'].get('occupancy_type'),
            result['extracted_entities'].get('urgency'),
            phone
        ))

        results.append(result)

    # Commit batch
    conn.commit()
    print(f"  ✓ Batch complete ({len(batch)} leads classified)")

    # Delay between batches
    if batch_idx + BATCH_SIZE < len(leads):
        print(f"  ⏳ Waiting {BATCH_DELAY}s...\n")
        time.sleep(BATCH_DELAY)

conn.close()

# Summary
elapsed = time.time() - start_time
print("\n" + "="*80)
print(f"✅ COMPLETE: {len(results)} leads classified in {elapsed/60:.1f} minutes")
print("="*80 + "\n")

# Distribution
categories = {}
for r in results:
    cat = r['classification']
    categories[cat] = categories.get(cat, 0) + 1

for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
    pct = (count / len(results)) * 100
    print(f"  {cat}: {count} ({pct:.1f}%)")
