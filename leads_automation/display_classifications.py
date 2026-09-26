#!/usr/bin/env python3
"""
Display classified leads with message content, sender, and source phone
"""

import sqlite3

DB_PATH = "/Users/zeidzakir/Projects/efps-internal-automatios/leads_automation/leads.db"

def get_classification_category(classification):
    """Extract category from classification string"""
    if not classification:
        return None
    return classification.split(' (')[0]

def display_classifications():
    """Display all classifications with messages"""

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get unique classifications
    cursor.execute("""
        SELECT DISTINCT
            CASE WHEN classification LIKE '%high%' THEN SUBSTR(classification, 1, INSTR(classification, ' (') - 1)
                 WHEN classification LIKE '%medium%' THEN SUBSTR(classification, 1, INSTR(classification, ' (') - 1)
                 WHEN classification LIKE '%low%' THEN SUBSTR(classification, 1, INSTR(classification, ' (') - 1)
                 ELSE classification END as category
        FROM leads
        WHERE classification IS NOT NULL
        ORDER BY category
    """)

    categories = [row['category'] for row in cursor.fetchall()]

    for category in categories:
        print(f"\n{'='*100}")
        print(f"CATEGORY: {category}")
        print(f"{'='*100}\n")

        # Get all leads in this category
        cursor.execute("""
            SELECT phone_number, extracted_from_phone, classification
            FROM leads
            WHERE classification LIKE ?
            ORDER BY last_interaction_date DESC
        """, (f"{category}%",))

        leads = cursor.fetchall()
        print(f"Total leads in this category: {len(leads)}\n")

        for lead in leads:
            phone = lead['phone_number']
            source_phone = lead['extracted_from_phone']
            classification = lead['classification']

            # Get messages
            cursor.execute("""
                SELECT direction, message_body, timestamp, sender_name
                FROM conversations
                WHERE phone_number = ?
                ORDER BY timestamp ASC
            """, (phone,))

            messages = cursor.fetchall()

            print(f"\n{'─'*100}")
            print(f"Customer Phone: {phone}")
            print(f"Source Phone: {source_phone}")
            print(f"Classification: {classification}")
            print(f"Total Messages: {len(messages)}")
            print(f"{'─'*100}")

            for msg in messages:
                direction = "📨 IN" if msg['direction'] == 'Incoming' else "📤 OUT"
                sender = msg['sender_name'] or 'Unknown'
                body = msg['message_body'][:100].strip() if msg['message_body'] else "[No text]"
                timestamp = msg['timestamp']

                print(f"{direction} | {timestamp} | {sender}: {body}")

            print()

    conn.close()

if __name__ == '__main__':
    display_classifications()
