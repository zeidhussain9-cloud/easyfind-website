#!/usr/bin/env python3
"""
Sync leads.db to Google Sheets - V2
NEW FORMAT:
- Date format: DD-Month-YYYY HH:MM:SS (IST)
- Added: extracted_from_phone column
"""

import sqlite3
import os
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

LEADS_DB = os.path.join(os.path.dirname(__file__), "leads.db")
SHEET_ID = "1GfM9lPQSukVpxCEVUlUDxFj_WYg0xQj8Inn7FA4sLVI"
KEY_PATH = "/Users/zeidzakir/Projects/efps-internal-automatios/gcpnew-key.json"

# Month name mapping
MONTH_NAMES = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}

def format_date_for_display(iso_date_str):
    """Convert ISO-8601 to DD-Month-YYYY HH:MM:SS (IST)"""
    if not iso_date_str:
        return ""
    try:
        dt = datetime.strptime(iso_date_str, "%Y-%m-%d %H:%M:%S")
        return f"{dt.day:02d}-{MONTH_NAMES[dt.month]}-{dt.year} {dt.strftime('%H:%M:%S')} (IST)"
    except:
        return iso_date_str

def get_sheet():
    """Authorize and open Google Sheet"""
    creds = Credentials.from_service_account_file(
        KEY_PATH,
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ],
    )
    gc = gspread.authorize(creds)
    return gc.open_by_key(SHEET_ID)

def sync_leads():
    """Sync leads table to Google Sheets"""
    print("=" * 80)
    print("SYNCING LEADS TO GOOGLE SHEET")
    print("=" * 80)

    # Connect to database
    conn = sqlite3.connect(LEADS_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all leads
    cursor.execute("""
        SELECT
            phone_number, customer_name, lead_status, lead_source, priority,
            current_requirement, bhk_requirement, preferred_location,
            budget_min, budget_max, furnishing_preference, occupancy_type,
            pet_preference, parking_required, move_in_date, matched_properties,
            last_interaction_date, next_followup_date, followup_count,
            tags, notes, classification, extracted_from_phone, created_at, updated_at
        FROM leads
        ORDER BY last_interaction_date DESC
    """)

    leads = cursor.fetchall()
    print(f"✓ Fetched {len(leads)} leads from database")

    # Format data for Sheet
    header = [
        "Phone Number", "Customer Name", "Lead Status", "Lead Source", "Priority",
        "Current Requirement", "BHK Requirement", "Preferred Location",
        "Budget Min", "Budget Max", "Furnishing Preference", "Occupancy Type",
        "Pet Preference", "Parking Required", "Move-in Date", "Matched Properties",
        "Last Interaction Date", "Next Followup Date", "Followup Count",
        "Tags", "Notes", "Classification", "Extracted From Phone", "Created At", "Updated At"
    ]

    rows = []
    for lead in leads:
        rows.append([
            lead['phone_number'] or "",
            lead['customer_name'] or "",
            lead['lead_status'] or "",
            lead['lead_source'] or "",
            lead['priority'] or "",
            lead['current_requirement'] or "",
            lead['bhk_requirement'] or "",
            lead['preferred_location'] or "",
            lead['budget_min'] or "",
            lead['budget_max'] or "",
            lead['furnishing_preference'] or "",
            lead['occupancy_type'] or "",
            lead['pet_preference'] or "",
            lead['parking_required'] or "",
            lead['move_in_date'] or "",
            lead['matched_properties'] or "",
            format_date_for_display(lead['last_interaction_date']),
            format_date_for_display(lead['next_followup_date']),
            lead['followup_count'] or 0,
            lead['tags'] or "",
            lead['notes'] or "",
            lead['classification'] or "",
            lead['extracted_from_phone'] or "",
            format_date_for_display(lead['created_at']),
            format_date_for_display(lead['updated_at'])
        ])

    # Open Sheet and write
    print("✓ Connecting to Google Sheet...")
    sheet = get_sheet()
    ws = sheet.worksheet("Leads")

    print("✓ Clearing existing data...")
    ws.clear()

    print("✓ Writing header + data...")
    all_data = [header] + rows
    ws.update(range_name='A1', values=all_data)

    print(f"✅ Written {len(rows)} leads to Sheet")

    conn.close()
    print("=" * 80)

def sync_conversations():
    """Sync conversations table to Google Sheets"""
    print("=" * 80)
    print("SYNCING CONVERSATIONS TO GOOGLE SHEET")
    print("=" * 80)

    # Connect to database
    conn = sqlite3.connect(LEADS_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all conversations
    cursor.execute("""
        SELECT
            message_id, phone_number, direction, message_body, message_type,
            media_urls, media_filenames, sender_name, timestamp, replied_to_id,
            is_processed, extracted_intent, extracted_entities, sentiment,
            requires_followup, created_at, processed_at
        FROM conversations
        ORDER BY timestamp DESC
    """)

    conversations = cursor.fetchall()
    print(f"✓ Fetched {len(conversations)} conversations from database")

    # Format data for Sheet
    header = [
        "Message ID", "Phone Number", "Direction", "Message Body", "Message Type",
        "Media URLs", "Media Filenames", "Sender Name", "Timestamp", "Replied To ID",
        "Is Processed", "Extracted Intent", "Extracted Entities", "Sentiment",
        "Requires Followup", "Created At", "Processed At"
    ]

    rows = []
    for conv in conversations:
        rows.append([
            conv['message_id'] or "",
            conv['phone_number'] or "",
            conv['direction'] or "",
            conv['message_body'] or "",
            conv['message_type'] or "",
            conv['media_urls'] or "",
            conv['media_filenames'] or "",
            conv['sender_name'] or "",
            format_date_for_display(conv['timestamp']),
            conv['replied_to_id'] or "",
            conv['is_processed'] or 0,
            conv['extracted_intent'] or "",
            conv['extracted_entities'] or "",
            conv['sentiment'] or "",
            conv['requires_followup'] or 0,
            format_date_for_display(conv['created_at']),
            format_date_for_display(conv['processed_at'])
        ])

    # Open Sheet and write
    print("✓ Connecting to Google Sheet...")
    sheet = get_sheet()
    ws = sheet.worksheet("Conversations")

    print("✓ Clearing existing data...")
    ws.clear()

    print("✓ Writing header + data...")
    all_data = [header] + rows
    ws.update(range_name='A1', values=all_data)

    print(f"✅ Written {len(rows)} conversations to Sheet")

    conn.close()
    print("=" * 80)

def sync_events():
    """Sync lead_lifecycle_events table to Google Sheets"""
    print("=" * 80)
    print("SYNCING EVENTS TO GOOGLE SHEET")
    print("=" * 80)

    # Connect to database
    conn = sqlite3.connect(LEADS_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all events
    cursor.execute("""
        SELECT
            event_id, phone_number, event_type, event_description, triggered_by,
            metadata, related_message_id, related_property_id, timestamp
        FROM lead_lifecycle_events
        ORDER BY timestamp DESC
    """)

    events = cursor.fetchall()
    print(f"✓ Fetched {len(events)} events from database")

    # Format data for Sheet
    header = [
        "Event ID", "Phone Number", "Event Type", "Event Description", "Triggered By",
        "Metadata", "Related Message ID", "Related Property ID", "Timestamp"
    ]

    rows = []
    for event in events:
        rows.append([
            event['event_id'] or "",
            event['phone_number'] or "",
            event['event_type'] or "",
            event['event_description'] or "",
            event['triggered_by'] or "",
            event['metadata'] or "",
            event['related_message_id'] or "",
            event['related_property_id'] or "",
            format_date_for_display(event['timestamp'])
        ])

    # Open Sheet and write
    print("✓ Connecting to Google Sheet...")
    sheet = get_sheet()
    ws = sheet.worksheet("Events")

    print("✓ Clearing existing data...")
    ws.clear()

    print("✓ Writing header + data...")
    all_data = [header] + rows
    ws.update(range_name='A1', values=all_data)

    print(f"✅ Written {len(rows)} events to Sheet")

    conn.close()
    print("=" * 80)

if __name__ == "__main__":
    import sys

    print("\n" + "=" * 80)
    print("GOOGLE SHEETS SYNC - V2")
    print("Date Format: DD-Month-YYYY HH:MM:SS (IST)")
    print("New Column: Extracted From Phone")
    print("=" * 80 + "\n")

    try:
        sync_leads()
        sync_conversations()
        sync_events()

        print("\n" + "=" * 80)
        print("✅ ALL SYNCS COMPLETE")
        print("=" * 80)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
