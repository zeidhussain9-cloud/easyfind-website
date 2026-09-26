#!/usr/bin/env python3
"""
Import classifications from Gemini CSV output into SQLite database.
"""

import sqlite3
import csv
import sys

DB_PATH = "/Users/zeidzakir/Projects/efps-internal-automatios/leads_automation/leads.db"

def import_classifications(csv_file):
    """Import classifications from CSV into database."""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Read CSV
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f, delimiter='|')
        classifications = list(reader)

    print(f"Importing {len(classifications)} classifications...")

    updated = 0
    errors = []

    for row in classifications:
        phone = row['phone_number'].strip()
        classification = row['classification'].strip()
        confidence = row['confidence'].strip()
        notes = row['notes'].strip()

        # Combine classification with confidence in notes
        full_classification = f"{classification} ({confidence})"

        try:
            cursor.execute("""
                UPDATE leads
                SET classification = ?,
                    notes = CASE
                        WHEN notes IS NULL OR notes = '' THEN ?
                        ELSE notes || ' | Classification: ' || ?
                    END
                WHERE phone_number = ?
            """, (full_classification, notes, notes, phone))

            if cursor.rowcount > 0:
                updated += 1
            else:
                errors.append(f"Phone not found: {phone}")

        except Exception as e:
            errors.append(f"Error updating {phone}: {e}")

    conn.commit()
    conn.close()

    print(f"✓ Updated {updated} leads")

    if errors:
        print(f"\n⚠ {len(errors)} errors:")
        for err in errors[:10]:
            print(f"  - {err}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")

    return updated, len(errors)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python import_classifications.py <csv_file>")
        sys.exit(1)

    updated, errors = import_classifications(sys.argv[1])

    if errors > 0:
        sys.exit(1)
