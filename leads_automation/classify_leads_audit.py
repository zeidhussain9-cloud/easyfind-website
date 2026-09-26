#!/usr/bin/env python3
"""
Complete lead classification audit.
Reads all 308 leads + their conversations.
Classifies each lead using Claude Haiku.
Writes classifications to Google Sheet column X.
"""

import sqlite3
import os
import sys
import time
import gspread
from google.oauth2.service_account import Credentials
from anthropic import Anthropic

LEADS_DB = os.path.join(os.path.dirname(__file__), "leads.db")
SHEET_ID = "1GfM9lPQSukVpxCEVUlUDxFj_WYg0xQj8Inn7FA4sLVI"
KEY_PATH = "/Users/zeidzakir/Projects/efps-internal-automatios/gcpnew-key.json"

client = Anthropic()

def get_sheet():
    creds = Credentials.from_service_account_file(
        KEY_PATH,
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ],
    )
    gc = gspread.authorize(creds)
    return gc.open_by_key(SHEET_ID)


def get_db():
    conn = sqlite3.connect(LEADS_DB)
    conn.row_factory = sqlite3.Row
    return conn


def get_lead_conversations(conn, phone_number):
    """Get all conversations for a lead, ordered by timestamp."""
    cur = conn.cursor()
    cur.execute("""
        SELECT direction, message_body, timestamp
        FROM conversations
        WHERE phone_number = ?
        ORDER BY timestamp ASC
    """, (phone_number,))
    return cur.fetchall()


def classify_lead(phone_number, customer_name, conversations):
    """Use Claude Haiku to classify a lead based on their conversations."""

    if not conversations:
        return "Unknown - No Messages"

    # Build conversation text
    conv_text = ""
    for msg in conversations:
        direction = "→ You:" if msg['direction'] == 'Outgoing' else "← Them:"
        conv_text += f"{direction} {msg['message_body'][:100]}\n"

    prompt = f"""Classify this WhatsApp contact based on their conversation history.

CONTACT INFO:
Phone: {phone_number}
Name: {customer_name or 'Unknown'}

CONVERSATION HISTORY:
{conv_text}

Classify this contact into ONE of these categories (or a similar one that fits):
- "Inbound Lead" - asking about rental/property/real estate services
- "Property Owner" - offering their property or inventory
- "Broker/Agent" - another real estate professional or competitor
- "Family/Friend" - personal/non-business relationship
- "Service/Automated" - OTP, bank alerts, delivery notifications
- "Promotional" - marketing/offers/spam
- "Own Number" - appears to be your own number

Respond ONLY with the classification label. No explanation. Just the label. Examples: "Inbound Lead", "Broker/Agent", "Own Number"

If you're unsure, pick the MOST LIKELY based on the message content."""

    response = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=50,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    classification = response.content[0].text.strip()
    return classification


def main():
    print("=" * 80)
    print("COMPLETE LEAD CLASSIFICATION AUDIT")
    print("=" * 80)
    print(f"Database: {LEADS_DB}")
    print(f"Sheet: {SHEET_ID}")
    print(f"Model: Claude Haiku 3.5")
    print("=" * 80)

    conn = get_db()
    sheet = get_sheet()
    ws = sheet.worksheet("Leads")

    # Get all leads
    cur = conn.cursor()
    cur.execute("""
        SELECT phone_number, customer_name
        FROM leads
        ORDER BY updated_at DESC
    """)
    leads = cur.fetchall()

    print(f"\nClassifying {len(leads)} leads...\n")

    classifications = []
    stats = {
        "Inbound Lead": 0,
        "Property Owner": 0,
        "Broker/Agent": 0,
        "Family/Friend": 0,
        "Service/Automated": 0,
        "Promotional": 0,
        "Own Number": 0,
        "Other": 0,
    }

    for i, lead in enumerate(leads, 1):
        phone = lead['phone_number']
        name = lead['customer_name']

        # Get conversations
        conversations = get_lead_conversations(conn, phone)

        # Classify
        classification = classify_lead(phone, name, conversations)
        classifications.append([classification])

        # Count for stats
        base_class = classification.split(" - ")[0]  # Get main classification
        if base_class in stats:
            stats[base_class] += 1
        else:
            stats["Other"] += 1

        # Progress
        if i % 10 == 0:
            print(f"  [{i:3d}/{len(leads)}] Classified — {classification}")

        # Rate limit: ~2s per request to avoid throttling
        if i < len(leads):
            time.sleep(0.5)

    # Write to Sheet
    print(f"\nWriting {len(classifications)} classifications to Sheet...")
    ws.update(range_name='X2:X309', values=classifications)

    print("✅ Classifications written to column X")

    # Print stats
    print(f"\n{'=' * 80}")
    print("CLASSIFICATION SUMMARY")
    print(f"{'=' * 80}")
    for classification, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            pct = (count / len(leads)) * 100
            print(f"{classification:20s}: {count:3d} ({pct:5.1f}%)")

    print(f"{'=' * 80}")
    print(f"TOTAL LEADS CLASSIFIED: {len(leads)}")
    print(f"{'=' * 80}")

    conn.close()


if __name__ == "__main__":
    main()
