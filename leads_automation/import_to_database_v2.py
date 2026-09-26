#!/usr/bin/env python3
"""
Import decrypted WhatsApp messages into leads database - V2
FIXES:
- Adds extracted_from_phone column tracking
- Filters out leads with <2 messages (group artifacts)
- Formats dates as "DD-Month-YYYY HH:MM:SS (IST)"
- Enforces IST timezone consistently
"""

import sqlite3
import os
import sys
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

LEADS_DB = os.path.join(os.path.dirname(__file__), "leads.db")

# Month name mapping for display format
MONTH_NAMES = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}

def format_date_display(dt):
    """Format datetime as DD-Month-YYYY HH:MM:SS (IST)"""
    return f"{dt.day:02d}-{MONTH_NAMES[dt.month]}-{dt.year} {dt.strftime('%H:%M:%S')} (IST)"

def format_date_storage(timestamp_ms):
    """Convert timestamp to IST datetime object"""
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=IST)

def import_whatsapp_data(msgstore_path, phone_number, cutoff_date="2026-07-23"):
    """Import WhatsApp data from decrypted msgstore.db into leads.db"""

    if not os.path.exists(msgstore_path):
        print(f"❌ File not found: {msgstore_path}")
        return False

    print(f"{'='*80}")
    print(f"IMPORTING WHATSAPP DATA - V2 (WITH FILTERS)")
    print(f"{'='*80}")
    print(f"Source: {msgstore_path}")
    print(f"Target: {LEADS_DB}")
    print(f"Phone:  {phone_number}")
    print(f"Cutoff: {cutoff_date}")
    print(f"Filters:")
    print(f"  • Minimum 2 messages per lead")
    print(f"  • Individual chats only (no groups)")
    print(f"  • IST timezone enforcement")
    print(f"{'='*80}\n")

    # Connect to both databases
    wa_conn = sqlite3.connect(msgstore_path)
    wa_conn.row_factory = sqlite3.Row
    wa_cur = wa_conn.cursor()

    leads_conn = sqlite3.connect(LEADS_DB)
    leads_cur = leads_conn.cursor()

    # Get cutoff timestamp in milliseconds
    cutoff_dt = datetime.strptime(cutoff_date, "%Y-%m-%d")
    cutoff_ms = int(cutoff_dt.timestamp() * 1000)

    # Step 1: Get all individual chats (non-group) since cutoff
    # Support both legacy s.whatsapp.net JIDs and newer LID-based JIDs
    print("Step 1: Extracting individual chats...")

    has_lid = False
    try:
        wa_cur.execute("SELECT count(*) FROM jid_map")
        has_lid = wa_cur.fetchone()[0] > 0
    except:
        pass

    if has_lid:
        wa_cur.execute("""
            SELECT
                COALESCE(j_phone.user, j.user) as phone_number,
                COALESCE(j_phone.raw_string, j.raw_string) as raw_string,
                c._id as chat_row_id,
                count(m._id) as msg_count,
                SUM(CASE WHEN m.from_me = 0 THEN 1 ELSE 0 END) as incoming,
                SUM(CASE WHEN m.from_me = 1 THEN 1 ELSE 0 END) as outgoing,
                MIN(m.timestamp) as first_msg_ts,
                MAX(m.timestamp) as last_msg_ts
            FROM message m
            JOIN chat c ON m.chat_row_id = c._id
            JOIN jid j ON c.jid_row_id = j._id
            LEFT JOIN jid_map jm ON j._id = jm.lid_row_id
            LEFT JOIN jid j_phone ON jm.jid_row_id = j_phone._id
            WHERE m.timestamp >= ?
            AND (j.server = 's.whatsapp.net' OR j.server = 'lid')
            GROUP BY COALESCE(j_phone.user, j.user)
            HAVING count(m._id) >= 2
            ORDER BY MAX(m.timestamp) DESC
        """, (cutoff_ms,))
    else:
        wa_cur.execute("""
            SELECT
                j.user as phone_number,
                j.raw_string,
                c._id as chat_row_id,
                count(m._id) as msg_count,
                SUM(CASE WHEN m.from_me = 0 THEN 1 ELSE 0 END) as incoming,
                SUM(CASE WHEN m.from_me = 1 THEN 1 ELSE 0 END) as outgoing,
                MIN(m.timestamp) as first_msg_ts,
                MAX(m.timestamp) as last_msg_ts
            FROM message m
            JOIN chat c ON m.chat_row_id = c._id
            JOIN jid j ON c.jid_row_id = j._id
            WHERE m.timestamp >= ?
            AND j.server = 's.whatsapp.net'
            GROUP BY j.user
            HAVING count(m._id) >= 2
            ORDER BY MAX(m.timestamp) DESC
        """, (cutoff_ms,))

    chats = wa_cur.fetchall()
    print(f"   Found {len(chats)} individual chats (minimum 2 messages)\n")

    # Step 2: Import each chat
    total_messages = 0
    total_leads = 0
    skipped_single_message = 0

    for chat in chats:
        phone = chat['phone_number']

        # Skip if this is a group artifact (shouldn't happen with HAVING clause, but double-check)
        if chat['msg_count'] < 2:
            skipped_single_message += 1
            continue

        # Normalize phone number (add + prefix)
        if not phone.startswith('+'):
            normalized_phone = f"+{phone}"
        else:
            normalized_phone = phone

        first_dt = format_date_storage(chat['first_msg_ts'])
        last_dt = format_date_storage(chat['last_msg_ts'])

        first_msg_time = format_date_display(first_dt)
        last_msg_time = format_date_display(last_dt)

        # For internal storage (ISO-8601 for sorting)
        first_msg_iso = first_dt.strftime('%Y-%m-%d %H:%M:%S')
        last_msg_iso = last_dt.strftime('%Y-%m-%d %H:%M:%S')

        # Try to get contact name
        contact_name = None

        # Check wa_contacts table if it exists
        try:
            wa_cur.execute("""
                SELECT wa_name, display_name, given_name FROM wa_contacts
                WHERE jid = ? OR jid = ?
                LIMIT 1
            """, (chat['raw_string'], f"{phone}@s.whatsapp.net"))
            contact_row = wa_cur.fetchone()
            if contact_row:
                contact_name = contact_row['display_name'] or contact_row['wa_name'] or contact_row['given_name']
        except:
            pass

        # Insert lead with extracted_from_phone
        leads_cur.execute("""
            INSERT OR IGNORE INTO leads (
                phone_number, customer_name, lead_status, lead_source, priority,
                last_interaction_date, extracted_from_phone, created_at, updated_at
            ) VALUES (?, ?, 'New', 'WhatsApp', 'Medium', ?, ?, ?, ?)
        """, (
            normalized_phone,
            contact_name,
            last_msg_iso,
            phone_number,  # Track source phone
            first_msg_iso,
            last_msg_iso
        ))

        if leads_cur.rowcount > 0:
            total_leads += 1

        # Step 3: Import all messages for this chat
        wa_cur.execute("""
            SELECT
                m._id,
                m.from_me,
                m.text_data,
                m.message_type,
                m.timestamp,
                m.status
            FROM message m
            WHERE m.chat_row_id = ?
            AND m.timestamp >= ?
            ORDER BY m.timestamp ASC
        """, (chat['chat_row_id'], cutoff_ms))

        messages = wa_cur.fetchall()
        chat_msg_count = 0

        for msg in messages:
            if not msg['text_data'] and msg['message_type'] in (0, None):
                continue  # Skip system/empty messages

            msg_dt = format_date_storage(msg['timestamp'])
            msg_time_iso = msg_dt.strftime('%Y-%m-%d %H:%M:%S')

            direction = 'Outgoing' if msg['from_me'] else 'Incoming'

            # Map message types
            type_map = {
                0: 'text', 1: 'image', 2: 'audio', 3: 'video',
                4: 'contact', 5: 'location', 8: 'document',
                9: 'text', 13: 'gif', 15: 'sticker', 16: 'location'
            }
            msg_type = type_map.get(msg['message_type'], 'text')

            body = msg['text_data'] or f"[{msg_type}]"

            leads_cur.execute("""
                INSERT INTO conversations (
                    phone_number, direction, message_body, message_type,
                    sender_name, timestamp, is_processed, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, 0, ?)
            """, (
                normalized_phone,
                direction,
                body,
                msg_type,
                contact_name if not msg['from_me'] else 'You',
                msg_time_iso,
                msg_time_iso
            ))

            chat_msg_count += 1

        total_messages += chat_msg_count

        # Create lifecycle event
        leads_cur.execute("""
            INSERT INTO lead_lifecycle_events (
                phone_number, event_type, event_description, triggered_by, timestamp
            ) VALUES (?, 'data_import', ?, 'System', ?)
        """, (
            normalized_phone,
            f"Imported {chat_msg_count} messages from WhatsApp backup ({phone_number})",
            datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')
        ))

        status_char = "✅"
        print(f"   {status_char} +{phone}: {chat_msg_count} messages ({chat['incoming']} in / {chat['outgoing']} out)")

    # Commit
    leads_conn.commit()

    # Summary
    print(f"\n{'='*80}")
    print(f"IMPORT COMPLETE")
    print(f"{'='*80}")
    print(f"✅ Leads created: {total_leads}")
    print(f"✅ Messages imported: {total_messages}")
    print(f"✅ Lifecycle events: {total_leads}")
    if skipped_single_message > 0:
        print(f"⏭️  Skipped (1 message only): {skipped_single_message}")
    print(f"{'='*80}")

    # Verify
    leads_cur.execute("SELECT count(*) FROM leads")
    print(f"\nDatabase totals:")
    print(f"   Leads table: {leads_cur.fetchone()[0]} rows")
    leads_cur.execute("SELECT count(*) FROM conversations")
    print(f"   Conversations table: {leads_cur.fetchone()[0]} rows")
    leads_cur.execute("SELECT count(*) FROM lead_lifecycle_events")
    print(f"   Events table: {leads_cur.fetchone()[0]} rows")

    wa_conn.close()
    leads_conn.close()

    return True


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Import WhatsApp data into leads database (V2)")
    parser.add_argument("--msgstore", required=True, help="Path to decrypted msgstore.db")
    parser.add_argument("--phone", required=True, help="Source phone number")
    parser.add_argument("--cutoff", default="2026-07-23", help="Cutoff date (YYYY-MM-DD)")
    args = parser.parse_args()

    success = import_whatsapp_data(args.msgstore, args.phone, args.cutoff)
    sys.exit(0 if success else 1)
