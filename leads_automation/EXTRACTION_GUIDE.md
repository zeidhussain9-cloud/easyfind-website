# WhatsApp Data Extraction Guide

## Overview
Extract 2 months of WhatsApp conversation history for 3 phone numbers using WhatsApp-Chat-Exporter.

## Prerequisites

✅ **Software Installed:**
- Python 3.12
- whatsapp-chat-exporter
- pycryptodome (for encrypted backups)

## What You Need

### For Android Backups:
1. **WhatsApp Backup File** - One of these:
   - `msgstore.db` (unencrypted)
   - `msgstore.db.crypt14` (encrypted)
   - `msgstore.db.crypt15` (end-to-end encrypted)

2. **Decryption Key** (if backup is encrypted):
   - `key` file (for crypt12/crypt14)
   - `encrypted_backup.key` (for crypt15)
   - OR 64-character hex key (for crypt15)

3. **Contact Database** (optional but recommended):
   - `wa.db`

4. **Media Folder** (optional):
   - `WhatsApp/Media/` directory

### For iOS Backups:
1. **iTunes/Finder Backup Location**:
   - Mac: `~/Library/Application Support/MobileSync/Backup/[device-id]`
   - Windows: `C:\Users\[Username]\AppData\Roaming\Apple Computer\MobileSync\Backup\[device-id]`

2. **Backup Password** (if encrypted)

## File Structure

Place your backup files in subdirectories:

```
leads_automation/
├── whatsapp_backups/
│   ├── number1/          # First number (lowest history)
│   │   ├── msgstore.db.crypt15
│   │   ├── encrypted_backup.key
│   │   ├── wa.db
│   │   └── WhatsApp/
│   ├── number2/
│   │   └── ...
│   └── number3/
│       └── ...
├── extracted_data/       # Output JSON files go here
│   ├── number1_export.json
│   ├── number2_export.json
│   └── number3_export.json
└── extract_whatsapp.py   # Extraction script
```

## Extraction Commands

### Android - Unencrypted Database
```bash
wtsexporter -a \
  -d whatsapp_backups/number1/msgstore.db \
  -w whatsapp_backups/number1/wa.db \
  -m whatsapp_backups/number1/WhatsApp \
  -o extracted_data/number1 \
  -j number1_export.json \
  --date 2026-07-23 \
  --no-html
```

### Android - Crypt14 (Encrypted)
```bash
wtsexporter -a \
  -b whatsapp_backups/number1/msgstore.db.crypt14 \
  -k whatsapp_backups/number1/key \
  -w whatsapp_backups/number1/wa.db \
  -m whatsapp_backups/number1/WhatsApp \
  -o extracted_data/number1 \
  -j number1_export.json \
  --date 2026-07-23 \
  --no-html
```

### Android - Crypt15 (End-to-End Encrypted) with Key File
```bash
wtsexporter -a \
  -b whatsapp_backups/number1/msgstore.db.crypt15 \
  -k whatsapp_backups/number1/encrypted_backup.key \
  -w whatsapp_backups/number1/wa.db \
  -m whatsapp_backups/number1/WhatsApp \
  -o extracted_data/number1 \
  -j number1_export.json \
  --date 2026-07-23 \
  --no-html
```

### Android - Crypt15 with 64-Char Hex Key
```bash
wtsexporter -a \
  -b whatsapp_backups/number1/msgstore.db.crypt15 \
  -k YOUR_64_CHAR_HEX_KEY_HERE \
  -w whatsapp_backups/number1/wa.db \
  -m whatsapp_backups/number1/WhatsApp \
  -o extracted_data/number1 \
  -j number1_export.json \
  --date 2026-07-23 \
  --no-html
```

### iOS - Unencrypted Backup
```bash
wtsexporter -i \
  -b "~/Library/Application Support/MobileSync/Backup/[device-id]" \
  -o extracted_data/number1 \
  -j number1_export.json \
  --date 2026-07-23 \
  --no-html
```

## Automated Extraction Script

Use the provided `extract_whatsapp.py` script:

```bash
python3 extract_whatsapp.py \
  --phone-number "+919876543210" \
  --backup-dir whatsapp_backups/number1 \
  --backup-type android-crypt15 \
  --key-file whatsapp_backups/number1/encrypted_backup.key \
  --output extracted_data/number1_export.json \
  --date-from 2026-07-23
```

## Output Format

The extraction produces a JSON file with this structure:

```json
{
  "metadata": {
    "phone_number": "+919876543210",
    "extraction_date": "2026-09-23T12:00:00",
    "total_conversations": 150,
    "date_range": {
      "start": "2026-07-23",
      "end": "2026-09-23"
    }
  },
  "chats": [
    {
      "chat_id": "+919998887771",
      "name": "Ravi Kumar",
      "messages": [
        {
          "message_id": 1,
          "timestamp": "2026-09-20T14:35:22",
          "sender": "+919998887771",
          "direction": "incoming",
          "message_type": "text",
          "body": "Hi, looking for 2 BHK in Baner under 25K",
          "media": [],
          "replied_to": null
        }
      ]
    }
  ]
}
```

## Next Steps

After extraction:
1. ✅ JSON files saved to `extracted_data/`
2. ⏳ Run `import_to_database.py` to load into SQLite
3. ⏳ Run `sync_to_sheets.py` to push to Google Sheets
4. ⏳ Set up NanoClaw for ongoing tracking

## Troubleshooting

**Error: "Could not decrypt backup"**
- Verify key file is correct
- For Crypt15, ensure you have the 64-char hex key or correct key file

**Error: "Database is locked"**
- Close WhatsApp on the device
- Make a fresh backup copy

**Error: "No messages found"**
- Check date filter (`--date` parameter)
- Verify backup file is not corrupted

**Error: "Contact names missing"**
- Include `wa.db` file with `-w` flag
- Use `--enrich-from-vcards` if wa.db is empty

## Status

- ✅ WhatsApp-Chat-Exporter installed
- ✅ Database schema created (3 tables)
- ⏳ Google Sheet creation - Pending (storage quota issue)
- ⏳ Backup files placement - Pending
- ⏳ Extraction run - Pending

## Commands Reference

Extract only (no HTML):
```bash
wtsexporter [options] --no-html -j output.json
```

Extract with date filter (last 2 months):
```bash
wtsexporter [options] --date 2026-07-23
```

Extract specific chats only:
```bash
wtsexporter [options] --include "+919876543210" "+919876543211"
```

Extract all except specific chats:
```bash
wtsexporter [options] --exclude "+919999999999"
```
