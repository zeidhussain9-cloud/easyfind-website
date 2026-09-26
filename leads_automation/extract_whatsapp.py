#!/usr/bin/env python3
"""
WhatsApp Data Extraction Script
Automated wrapper around wtsexporter for easier usage
"""

import subprocess
import argparse
import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

def run_extraction(
    phone_number,
    backup_dir,
    backup_type,
    key_file=None,
    hex_key=None,
    output_file=None,
    date_from=None,
    include_media=True
):
    """
    Run WhatsApp data extraction

    Args:
        phone_number: Phone number being extracted (for metadata)
        backup_dir: Directory containing backup files
        backup_type: Type of backup ('android-plain', 'android-crypt14', 'android-crypt15', 'ios')
        key_file: Path to decryption key file
        hex_key: 64-char hex key for crypt15
        output_file: Output JSON file path
        date_from: Start date for filtering (YYYY-MM-DD)
        include_media: Whether to include media folder
    """

    backup_dir = Path(backup_dir)
    if not backup_dir.exists():
        print(f"❌ Backup directory not found: {backup_dir}")
        return False

    # Prepare output file
    if output_file is None:
        output_file = f"extracted_data/{phone_number.replace('+', '')}_export.json"

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Build wtsexporter command
    cmd = ["wtsexporter"]

    # Platform-specific flags
    if backup_type.startswith("android"):
        cmd.append("-a")

        # Find backup file
        if backup_type == "android-plain":
            db_file = backup_dir / "msgstore.db"
            if not db_file.exists():
                print(f"❌ Database file not found: {db_file}")
                return False
            cmd.extend(["-d", str(db_file)])

        elif backup_type in ["android-crypt14", "android-crypt15"]:
            # Find encrypted backup
            backup_file = None
            for ext in [".crypt15", ".crypt14"]:
                candidate = backup_dir / f"msgstore.db{ext}"
                if candidate.exists():
                    backup_file = candidate
                    break

            if not backup_file:
                print(f"❌ Encrypted backup file not found in: {backup_dir}")
                return False

            cmd.extend(["-b", str(backup_file)])

            # Handle decryption key
            if hex_key:
                cmd.extend(["-k", hex_key])
            elif key_file:
                key_path = Path(key_file)
                if not key_path.exists():
                    print(f"❌ Key file not found: {key_path}")
                    return False
                cmd.extend(["-k", str(key_path)])
            else:
                print("❌ Encrypted backup requires either --key-file or --hex-key")
                return False

        # Add contact database if available
        wa_db = backup_dir / "wa.db"
        if wa_db.exists():
            cmd.extend(["-w", str(wa_db)])
            print(f"✅ Using contact database: {wa_db}")
        else:
            print(f"⚠️  Contact database not found (wa.db). Names may be missing.")

        # Add media folder if requested and available
        if include_media:
            media_dir = backup_dir / "WhatsApp"
            if media_dir.exists():
                cmd.extend(["-m", str(media_dir)])
                print(f"✅ Including media from: {media_dir}")
            else:
                print(f"⚠️  Media folder not found. Skipping media.")

    elif backup_type == "ios":
        cmd.append("-i")
        cmd.extend(["-b", str(backup_dir)])

    # Output options
    cmd.extend(["-o", str(output_path.parent)])
    cmd.extend(["-j", output_path.name])
    cmd.append("--no-html")  # JSON only, no HTML

    # Date filtering (last 2 months from date_from)
    if date_from:
        cmd.extend(["--date", date_from])
        print(f"✅ Filtering messages from: {date_from}")

    # Don't filter empty chats (we want all chats even if no messages in date range)
    cmd.append("--dont-filter-empty")

    # Pretty print JSON for readability
    cmd.append("--pretty-print-json")

    # Print command being run
    print(f"\n{'='*80}")
    print(f"EXTRACTING WHATSAPP DATA")
    print(f"{'='*80}")
    print(f"Phone Number: {phone_number}")
    print(f"Backup Type: {backup_type}")
    print(f"Backup Dir: {backup_dir}")
    print(f"Output File: {output_path}")
    print(f"\nCommand:")
    print(" ".join(cmd))
    print(f"{'='*80}\n")

    # Run extraction
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)

        if result.returncode == 0:
            print(f"\n✅ Extraction completed successfully!")
            print(f"📄 Output saved to: {output_path}")

            # Add metadata to JSON
            if output_path.exists():
                with open(output_path, 'r') as f:
                    data = json.load(f)

                # Add extraction metadata
                data['extraction_metadata'] = {
                    'phone_number': phone_number,
                    'extraction_date': datetime.now().isoformat(),
                    'backup_type': backup_type,
                    'date_filter_from': date_from,
                    'total_chats': len(data.get('chats', [])),
                    'total_messages': sum(len(chat.get('messages', [])) for chat in data.get('chats', []))
                }

                # Save updated JSON
                with open(output_path, 'w') as f:
                    json.dump(data, f, indent=2)

                print(f"\n📊 Statistics:")
                print(f"   Total Chats: {data['extraction_metadata']['total_chats']}")
                print(f"   Total Messages: {data['extraction_metadata']['total_messages']}")

            return True

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Extraction failed!")
        print(f"Error: {e}")
        if e.stdout:
            print(f"\nStdout:\n{e.stdout}")
        if e.stderr:
            print(f"\nStderr:\n{e.stderr}")
        return False

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Extract WhatsApp conversation history",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:

  # Android - Unencrypted
  python3 extract_whatsapp.py \\
    --phone-number "+919876543210" \\
    --backup-dir whatsapp_backups/number1 \\
    --backup-type android-plain \\
    --date-from 2026-07-23

  # Android - Crypt15 with key file
  python3 extract_whatsapp.py \\
    --phone-number "+919876543210" \\
    --backup-dir whatsapp_backups/number1 \\
    --backup-type android-crypt15 \\
    --key-file whatsapp_backups/number1/encrypted_backup.key \\
    --date-from 2026-07-23

  # Android - Crypt15 with hex key
  python3 extract_whatsapp.py \\
    --phone-number "+919876543210" \\
    --backup-dir whatsapp_backups/number1 \\
    --backup-type android-crypt15 \\
    --hex-key "133735053b5204b08e5c3823423399aa30ff061435ab89bc4e6713969cda1337" \\
    --date-from 2026-07-23

  # iOS
  python3 extract_whatsapp.py \\
    --phone-number "+919876543210" \\
    --backup-dir "~/Library/Application Support/MobileSync/Backup/device-id" \\
    --backup-type ios \\
    --date-from 2026-07-23
        """
    )

    parser.add_argument(
        "--phone-number",
        required=True,
        help="Phone number being extracted (with country code, e.g., +919876543210)"
    )

    parser.add_argument(
        "--backup-dir",
        required=True,
        help="Directory containing WhatsApp backup files"
    )

    parser.add_argument(
        "--backup-type",
        required=True,
        choices=["android-plain", "android-crypt14", "android-crypt15", "ios"],
        help="Type of WhatsApp backup"
    )

    parser.add_argument(
        "--key-file",
        help="Path to decryption key file (for encrypted Android backups)"
    )

    parser.add_argument(
        "--hex-key",
        help="64-character hex decryption key (for crypt15 backups)"
    )

    parser.add_argument(
        "--output",
        help="Output JSON file path (default: extracted_data/{phone}_export.json)"
    )

    parser.add_argument(
        "--date-from",
        help="Start date for extraction (YYYY-MM-DD, default: 2 months ago)"
    )

    parser.add_argument(
        "--no-media",
        action="store_true",
        help="Skip media extraction"
    )

    args = parser.parse_args()

    # Calculate default date_from (2 months ago)
    if not args.date_from:
        two_months_ago = datetime.now() - timedelta(days=60)
        args.date_from = two_months_ago.strftime("%Y-%m-%d")
        print(f"ℹ️  Using default date filter: {args.date_from} (2 months ago)")

    # Run extraction
    success = run_extraction(
        phone_number=args.phone_number,
        backup_dir=args.backup_dir,
        backup_type=args.backup_type,
        key_file=args.key_file,
        hex_key=args.hex_key,
        output_file=args.output,
        date_from=args.date_from,
        include_media=not args.no_media
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
