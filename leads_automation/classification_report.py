#!/usr/bin/env python3
"""
Generate comprehensive classification report with messages, senders, and source phones
"""

import sqlite3
import json

DB_PATH = "/Users/zeidzakir/Projects/efps-internal-automatios/leads_automation/leads.db"

def get_category(classification):
    """Extract category from classification string"""
    if not classification:
        return None
    return classification.split(' (')[0]

def generate_report():
    """Generate full report"""

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get unique categories
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

    report = {}

    for category in categories:
        # Get all leads in category
        cursor.execute("""
            SELECT phone_number, extracted_from_phone, classification
            FROM leads
            WHERE classification LIKE ?
            ORDER BY last_interaction_date DESC
        """, (f"{category}%",))

        leads = cursor.fetchall()
        report[category] = []

        for lead in leads:
            phone = lead['phone_number']
            source_phone = lead['extracted_from_phone']
            classification = lead['classification']

            # Get messages
            cursor.execute("""
                SELECT direction, message_body, timestamp, sender_name, message_type
                FROM conversations
                WHERE phone_number = ?
                ORDER BY timestamp ASC
            """, (phone,))

            messages = [dict(row) for row in cursor.fetchall()]

            report[category].append({
                'customer_phone': phone,
                'source_phone': source_phone,
                'classification': classification,
                'message_count': len(messages),
                'messages': messages
            })

    conn.close()

    return report

def display_report(report):
    """Display report in formatted way"""

    # Map source phones to labels
    source_labels = {
        '+919148338801': 'Phone 1',
        '+917975102130': 'Phone 2',
        '+919902024973': 'Phone 3'
    }

    for category in sorted(report.keys()):
        leads = report[category]
        print(f"\n\n{'='*120}")
        print(f"CLASSIFICATION: {category.upper()}")
        print(f"Total Leads: {len(leads)}")
        print(f"{'='*120}\n")

        for i, lead in enumerate(leads, 1):
            print(f"\n{i}. Customer: {lead['customer_phone']} | Source: {source_labels.get(lead['source_phone'], lead['source_phone'])}")
            print(f"   Classification: {lead['classification']}")
            print(f"   Message Count: {lead['message_count']}")
            print(f"   {'-'*110}")

            for msg in lead['messages']:
                direction = "📨 IN " if msg['direction'] == 'Incoming' else "📤 OUT"
                sender = msg['sender_name'] or 'Unknown'
                body = msg['message_body'][:120] if msg['message_body'] else "[Media/Empty]"
                timestamp = msg['timestamp']
                msg_type = msg['message_type']

                print(f"   {direction} | {timestamp} | {sender} [{msg_type}]: {body}")

if __name__ == '__main__':
    print("Generating classification report...")
    report = generate_report()
    display_report(report)
    print("\n\n✅ Report complete!")
