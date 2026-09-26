#!/usr/bin/env python3
"""Add Lead Management tabs to existing Google Sheet"""
import gspread
from google.oauth2.service_account import Credentials
import os

SHEET_ID = "1GfM9lPQSukVpxCEVUlUDxFj_WYg0xQj8Inn7FA4sLVI"

key_path = os.path.abspath('../gcpnew-key.json')
scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
credentials = Credentials.from_service_account_file(key_path, scopes=scopes)
gc = gspread.authorize(credentials)

print(f"Opening spreadsheet: {SHEET_ID}")
spreadsheet = gc.open_by_key(SHEET_ID)
print(f"✅ Opened: {spreadsheet.title}")
print(f"🔗 URL: https://docs.google.com/spreadsheets/d/{SHEET_ID}")

# Get existing sheets
existing_sheets = [ws.title for ws in spreadsheet.worksheets()]
print(f"\nExisting sheets: {existing_sheets}")

# Create or get "Leads" tab
if "Leads" in existing_sheets:
    print("✅ 'Leads' tab already exists")
    leads_sheet = spreadsheet.worksheet("Leads")
else:
    leads_sheet = spreadsheet.add_worksheet(title="Leads", rows=1000, cols=23)
    print("✅ Created 'Leads' tab")

# Set headers for Leads
leads_headers = [
    "Phone Number", "Customer Name", "Lead Status", "Lead Source", "Priority",
    "Current Requirement", "BHK Requirement", "Preferred Location", "Budget Min", "Budget Max",
    "Furnishing Preference", "Occupancy Type", "Pet Preference", "Parking Required", "Move-in Date",
    "Matched Properties", "Last Interaction Date", "Next Followup Date", "Followup Count",
    "Tags", "Notes", "Created At", "Updated At"
]
leads_sheet.update('A1:W1', [leads_headers])
leads_sheet.format('A1:W1', {
    'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.8},
    'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
    'horizontalAlignment': 'CENTER'
})
leads_sheet.freeze(rows=1)
print("✅ Set up 'Leads' tab headers")

# Create or get "Conversations" tab
if "Conversations" in existing_sheets:
    print("✅ 'Conversations' tab already exists")
    conv_sheet = spreadsheet.worksheet("Conversations")
else:
    conv_sheet = spreadsheet.add_worksheet(title="Conversations", rows=1000, cols=17)
    print("✅ Created 'Conversations' tab")

# Set headers for Conversations
conv_headers = [
    "Message ID", "Phone Number", "Direction", "Message Body", "Message Type",
    "Media URLs", "Media Filenames", "Sender Name", "Timestamp", "Replied To ID",
    "Is Processed", "Extracted Intent", "Extracted Entities", "Sentiment",
    "Requires Followup", "Created At", "Processed At"
]
conv_sheet.update('A1:Q1', [conv_headers])
conv_sheet.format('A1:Q1', {
    'backgroundColor': {'red': 0.3, 'green': 0.7, 'blue': 0.4},
    'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
    'horizontalAlignment': 'CENTER'
})
conv_sheet.freeze(rows=1)
print("✅ Set up 'Conversations' tab headers")

# Create or get "Events" tab
if "Events" in existing_sheets:
    print("✅ 'Events' tab already exists")
    events_sheet = spreadsheet.worksheet("Events")
else:
    events_sheet = spreadsheet.add_worksheet(title="Events", rows=1000, cols=9)
    print("✅ Created 'Events' tab")

# Set headers for Events
events_headers = [
    "Event ID", "Phone Number", "Event Type", "Event Description", "Triggered By",
    "Metadata", "Related Message ID", "Related Property ID", "Timestamp"
]
events_sheet.update('A1:I1', [events_headers])
events_sheet.format('A1:I1', {
    'backgroundColor': {'red': 0.9, 'green': 0.6, 'blue': 0.2},
    'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
    'horizontalAlignment': 'CENTER'
})
events_sheet.freeze(rows=1)
print("✅ Set up 'Events' tab headers")

# Save config
with open("google_sheet_config.txt", 'w') as f:
    f.write(f"SPREADSHEET_ID={SHEET_ID}\n")
    f.write(f"URL=https://docs.google.com/spreadsheets/d/{SHEET_ID}\n")

print(f"\n{'='*80}")
print("GOOGLE SHEET SETUP COMPLETE")
print(f"{'='*80}")
print(f"📊 Spreadsheet: {spreadsheet.title}")
print(f"🆔 ID: {SHEET_ID}")
print(f"🔗 URL: https://docs.google.com/spreadsheets/d/{SHEET_ID}")
print(f"\n📑 Tabs:")
print(f"   1. Leads (23 columns)")
print(f"   2. Conversations (17 columns)")
print(f"   3. Events (9 columns)")
print(f"{'='*80}")
