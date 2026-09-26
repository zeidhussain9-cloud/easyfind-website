#!/usr/bin/env python3
"""
Create Google Sheet Dashboard for Easyfind Lead Management System
Creates a new spreadsheet with 3 tabs: Leads, Conversations, Events
"""

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os

def create_lead_management_sheet():
    """Create the lead management Google Sheet with 3 tabs"""

    print("Initializing Google Sheets client...")

    # Load service account credentials
    key_path = os.path.join(os.path.dirname(__file__), '..', 'gcpnew-key.json')
    key_path = os.path.abspath(key_path)

    if not os.path.exists(key_path):
        raise FileNotFoundError(f"Service account key not found: {key_path}")

    print(f"Using credentials: {key_path}")

    # Set up credentials
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    credentials = Credentials.from_service_account_file(key_path, scopes=scopes)
    gc = gspread.authorize(credentials)

    # Create new spreadsheet
    spreadsheet_name = f"Easyfind Lead Management - {datetime.now().strftime('%Y-%m-%d')}"
    print(f"\nCreating spreadsheet: {spreadsheet_name}")

    spreadsheet = gc.create(spreadsheet_name)
    spreadsheet_id = spreadsheet.id

    print(f"✅ Spreadsheet created: {spreadsheet_id}")
    print(f"🔗 URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")

    # Get the default sheet (Sheet1) and rename it to "Leads"
    default_sheet = spreadsheet.get_worksheet(0)
    default_sheet.update_title("Leads")
    print("✅ Renamed default sheet to 'Leads'")

    # Add "Conversations" and "Events" sheets
    spreadsheet.add_worksheet(title="Conversations", rows=1000, cols=20)
    print("✅ Added 'Conversations' sheet")

    spreadsheet.add_worksheet(title="Events", rows=1000, cols=15)
    print("✅ Added 'Events' sheet")

    # ========================================================================
    # TAB 1: LEADS - Headers
    # ========================================================================
    leads_headers = [
        "Phone Number",
        "Customer Name",
        "Lead Status",
        "Lead Source",
        "Priority",
        "Current Requirement",
        "BHK Requirement",
        "Preferred Location",
        "Budget Min",
        "Budget Max",
        "Furnishing Preference",
        "Occupancy Type",
        "Pet Preference",
        "Parking Required",
        "Move-in Date",
        "Matched Properties",
        "Last Interaction Date",
        "Next Followup Date",
        "Followup Count",
        "Tags",
        "Notes",
        "Created At",
        "Updated At"
    ]

    leads_sheet = spreadsheet.worksheet("Leads")
    leads_sheet.update('A1:W1', [leads_headers])

    # Format header row
    leads_sheet.format('A1:W1', {
        'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.8},
        'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
        'horizontalAlignment': 'CENTER'
    })

    # Freeze header row
    leads_sheet.freeze(rows=1)

    # Set column widths for better readability
    leads_sheet.set_basic_filter()

    print("✅ Set up 'Leads' tab with headers")

    # ========================================================================
    # TAB 2: CONVERSATIONS - Headers
    # ========================================================================
    conversations_headers = [
        "Message ID",
        "Phone Number",
        "Direction",
        "Message Body",
        "Message Type",
        "Media URLs",
        "Media Filenames",
        "Sender Name",
        "Timestamp",
        "Replied To ID",
        "Is Processed",
        "Extracted Intent",
        "Extracted Entities",
        "Sentiment",
        "Requires Followup",
        "Created At",
        "Processed At"
    ]

    conversations_sheet = spreadsheet.worksheet("Conversations")
    conversations_sheet.update('A1:Q1', [conversations_headers])

    # Format header row
    conversations_sheet.format('A1:Q1', {
        'backgroundColor': {'red': 0.3, 'green': 0.7, 'blue': 0.4},
        'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
        'horizontalAlignment': 'CENTER'
    })

    # Freeze header row
    conversations_sheet.freeze(rows=1)
    conversations_sheet.set_basic_filter()

    print("✅ Set up 'Conversations' tab with headers")

    # ========================================================================
    # TAB 3: EVENTS - Headers
    # ========================================================================
    events_headers = [
        "Event ID",
        "Phone Number",
        "Event Type",
        "Event Description",
        "Triggered By",
        "Metadata",
        "Related Message ID",
        "Related Property ID",
        "Timestamp"
    ]

    events_sheet = spreadsheet.worksheet("Events")
    events_sheet.update('A1:I1', [events_headers])

    # Format header row
    events_sheet.format('A1:I1', {
        'backgroundColor': {'red': 0.9, 'green': 0.6, 'blue': 0.2},
        'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
        'horizontalAlignment': 'CENTER'
    })

    # Freeze header row
    events_sheet.freeze(rows=1)
    events_sheet.set_basic_filter()

    print("✅ Set up 'Events' tab with headers")

    # ========================================================================
    # Share with your email (make it editable)
    # ========================================================================
    print("\n📧 Sharing spreadsheet...")

    # Get service account email from credentials
    service_account_email = credentials.service_account_email
    print(f"   Service account: {service_account_email}")

    # Make it accessible to anyone with the link
    spreadsheet.share('', perm_type='anyone', role='writer')
    print("✅ Spreadsheet is now accessible to anyone with the link (edit access)")

    # ========================================================================
    # Save spreadsheet ID to config file
    # ========================================================================
    config_file = "google_sheet_config.txt"
    with open(config_file, 'w') as f:
        f.write(f"SPREADSHEET_ID={spreadsheet_id}\n")
        f.write(f"URL=https://docs.google.com/spreadsheets/d/{spreadsheet_id}\n")
        f.write(f"CREATED_AT={datetime.now().isoformat()}\n")

    print(f"\n✅ Configuration saved to: {config_file}")

    # ========================================================================
    # Summary
    # ========================================================================
    print("\n" + "="*80)
    print("GOOGLE SHEET DASHBOARD CREATED SUCCESSFULLY")
    print("="*80)
    print(f"📊 Spreadsheet Name: {spreadsheet_name}")
    print(f"🆔 Spreadsheet ID: {spreadsheet_id}")
    print(f"🔗 URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
    print()
    print("📑 Tabs Created:")
    print("   1. Leads           - 23 columns (master lead registry)")
    print("   2. Conversations   - 17 columns (message log)")
    print("   3. Events          - 9 columns (lifecycle events)")
    print()
    print("✅ All tabs have headers, formatting, and filters applied")
    print("✅ Anyone with the link can edit")
    print("="*80)

    return spreadsheet_id

if __name__ == "__main__":
    import sys
    try:
        spreadsheet_id = create_lead_management_sheet()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
