#!/usr/bin/env python3
"""
Raw data sync: leads.db → Google Sheet
No processing, no parsing, no normalization. Straight column-for-column dump.
"""

import sqlite3
import os
import time
import gspread
from google.oauth2.service_account import Credentials

LEADS_DB = os.path.join(os.path.dirname(__file__), "leads.db")
SHEET_ID = "1GfM9lPQSukVpxCEVUlUDxFj_WYg0xQj8Inn7FA4sLVI"
KEY_PATH = "/Users/zeidzakir/Projects/efps-internal-automatios/gcpnew-key.json"
BATCH_SIZE = 1000


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


def safe_str(val):
    """Convert value to string for Sheets. None becomes empty string."""
    if val is None:
        return ""
    return str(val)


def sync_leads(sheet, conn):
    """Dump leads table → Leads tab. Raw data, no processing."""
    ws = sheet.worksheet("Leads")
    cur = conn.cursor()
    cur.execute("""
        SELECT phone_number, customer_name, lead_status, lead_source, priority,
               current_requirement, bhk_requirement, preferred_location,
               budget_min, budget_max, furnishing_preference, occupancy_type,
               pet_preference, parking_required, move_in_date,
               matched_properties, last_interaction_date, next_followup_date,
               followup_count, tags, notes, created_at, updated_at
        FROM leads
        ORDER BY updated_at DESC
    """)
    rows = [[safe_str(col) for col in row] for row in cur.fetchall()]

    if not rows:
        print("  No leads to sync")
        return 0

    # Clear existing data (keep header row 1)
    ws.batch_clear(["A2:W"])
    time.sleep(1)

    ws.update(range_name=f"A2:W{len(rows) + 1}", values=rows)
    return len(rows)


def sync_conversations(sheet, conn):
    """Dump conversations table → Conversations tab. Raw data, no processing."""
    ws = sheet.worksheet("Conversations")
    cur = conn.cursor()
    cur.execute("""
        SELECT message_id, phone_number, direction, message_body, message_type,
               media_urls, media_filenames, sender_name, timestamp,
               replied_to_id, is_processed, extracted_intent, extracted_entities,
               sentiment, requires_followup, created_at, processed_at
        FROM conversations
        ORDER BY timestamp DESC
    """)
    all_rows = [[safe_str(col) for col in row] for row in cur.fetchall()]

    if not all_rows:
        print("  No conversations to sync")
        return 0

    # Expand sheet if needed
    needed_rows = len(all_rows) + 1  # +1 for header
    if ws.row_count < needed_rows:
        ws.resize(rows=needed_rows + 100)
        time.sleep(1)

    # Clear existing data
    ws.batch_clear(["A2:Q"])
    time.sleep(1)

    # Write in batches (Sheets API has payload limits)
    total = 0
    for i in range(0, len(all_rows), BATCH_SIZE):
        batch = all_rows[i : i + BATCH_SIZE]
        start_row = i + 2  # row 1 is header
        end_row = start_row + len(batch) - 1
        ws.update(range_name=f"A{start_row}:Q{end_row}", values=batch)
        total += len(batch)
        print(f"  Written {total}/{len(all_rows)} conversations")
        if i + BATCH_SIZE < len(all_rows):
            time.sleep(2)  # rate limit buffer between batches

    return total


def sync_events(sheet, conn):
    """Dump lead_lifecycle_events table → Events tab. Raw data, no processing."""
    ws = sheet.worksheet("Events")
    cur = conn.cursor()
    cur.execute("""
        SELECT event_id, phone_number, event_type, event_description,
               triggered_by, metadata, related_message_id, related_property_id,
               timestamp
        FROM lead_lifecycle_events
        ORDER BY timestamp DESC
    """)
    rows = [[safe_str(col) for col in row] for row in cur.fetchall()]

    if not rows:
        print("  No events to sync")
        return 0

    # Clear existing data
    ws.batch_clear(["A2:I"])
    time.sleep(1)

    ws.update(range_name=f"A2:I{len(rows) + 1}", values=rows)
    return len(rows)


def main():
    print("=" * 60)
    print("SYNC: leads.db → Google Sheet")
    print("=" * 60)
    print(f"Database: {LEADS_DB}")
    print(f"Sheet: {SHEET_ID}")
    print("Mode: RAW DATA DUMP (no processing)")
    print("=" * 60)

    sheet = get_sheet()
    conn = get_db()

    print("\n1. Syncing Leads tab...")
    leads_count = sync_leads(sheet, conn)
    print(f"   ✅ {leads_count} leads written")

    print("\n2. Syncing Conversations tab...")
    conv_count = sync_conversations(sheet, conn)
    print(f"   ✅ {conv_count} conversations written")

    print("\n3. Syncing Events tab...")
    events_count = sync_events(sheet, conn)
    print(f"   ✅ {events_count} events written")

    conn.close()

    print(f"\n{'=' * 60}")
    print("SYNC COMPLETE")
    print(f"{'=' * 60}")
    print(f"Leads:         {leads_count}")
    print(f"Conversations: {conv_count}")
    print(f"Events:        {events_count}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
