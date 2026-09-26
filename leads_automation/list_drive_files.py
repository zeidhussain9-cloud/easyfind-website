#!/usr/bin/env python3
"""List all files in service account Google Drive"""
import gspread
from google.oauth2.service_account import Credentials
import os

key_path = os.path.abspath('../gcpnew-key.json')
scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
credentials = Credentials.from_service_account_file(key_path, scopes=scopes)
gc = gspread.authorize(credentials)

print("Fetching all files from service account Drive...\n")
files = gc.list_spreadsheet_files()

print(f"{'='*100}")
print(f"TOTAL FILES: {len(files)}")
print(f"{'='*100}\n")

# Sort by creation date (newest first)
files_sorted = sorted(files, key=lambda x: x.get('createdTime', ''), reverse=True)

for i, file in enumerate(files_sorted, 1):
    print(f"{i}. {file['name']}")
    print(f"   ID: {file['id']}")
    print(f"   Created: {file.get('createdTime', 'Unknown')}")
    print(f"   Modified: {file.get('modifiedTime', 'Unknown')}")
    print(f"   URL: https://docs.google.com/spreadsheets/d/{file['id']}")
    print()
