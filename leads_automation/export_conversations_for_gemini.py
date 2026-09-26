#!/usr/bin/env python3
"""
Export conversations for Gemini classification.
Reads phone numbers from file, extracts full conversation history, outputs JSON.
"""

import sqlite3
import json
import sys

DB_PATH = "/Users/zeidzakir/Projects/efps-internal-automatios/leads_automation/leads.db"

def export_conversations(phone_list_file, output_file):
    """Export conversations for given phone numbers to JSON."""

    # Read phone numbers
    with open(phone_list_file, 'r') as f:
        phone_numbers = [line.strip() for line in f if line.strip()]

    print(f"Loading conversations for {len(phone_numbers)} phone numbers...")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    results = []

    for i, phone in enumerate(phone_numbers, 1):
        if i % 50 == 0:
            print(f"Processed {i}/{len(phone_numbers)}...")

        # Get conversation history
        cursor.execute("""
            SELECT direction, message_body, message_type, timestamp, sender_name
            FROM conversations
            WHERE phone_number = ?
            ORDER BY timestamp ASC
        """, (phone,))

        messages = []
        for row in cursor.fetchall():
            messages.append({
                'direction': row['direction'],
                'message_body': row['message_body'],
                'message_type': row['message_type'],
                'timestamp': row['timestamp'],
                'sender_name': row['sender_name']
            })

        # Get lead info
        cursor.execute("""
            SELECT customer_name, last_interaction_date, current_requirement
            FROM leads
            WHERE phone_number = ?
        """, (phone,))

        lead_row = cursor.fetchone()

        results.append({
            'phone_number': phone,
            'customer_name': lead_row['customer_name'] if lead_row else None,
            'last_interaction_date': lead_row['last_interaction_date'] if lead_row else None,
            'current_requirement': lead_row['current_requirement'] if lead_row else None,
            'message_count': len(messages),
            'messages': messages
        })

    conn.close()

    # Write to JSON
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"✓ Exported {len(results)} leads with conversations to {output_file}")
    print(f"Total messages: {sum(r['message_count'] for r in results)}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python export_conversations_for_gemini.py <phone_list_file> <output_json>")
        sys.exit(1)

    export_conversations(sys.argv[1], sys.argv[2])
