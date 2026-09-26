
import json
import csv
import re

def classify_lead(lead):
    messages = lead.get('messages', [])
    full_conversation = " ".join([msg.get('message_body', '') for msg in messages if msg.get('message_body')])

    # Pre-compile regex for efficiency
    rental_keywords = re.compile(r'\b(rent|bhk|budget|rs|inr|k|lakh|furnished|family|bachelor|studio|apartment|flat|house|villa|property|pg)\b', re.IGNORECASE)
    location_keywords = re.compile(r'\b(whitefield|hsr|marathahalli|sarjapur|bellandur|koramangala|indiranagar|jayanagar|btm|electronic city)\b', re.IGNORECASE)
    broker_keywords = re.compile(r'\b(broker|agent|commission|client|site visit|property viewing)\b', re.IGNORECASE)
    service_keywords = re.compile(r'\b(otp|verification code|transaction|delivery|order|bank|account)\b', re.IGNORECASE)
    personal_keywords = re.compile(r'\b(bro|dude|lunch|dinner|movie|party|weekend)\b', re.IGNORECASE)
    listing_sent_keywords = re.compile(r'\b(catalog|options|here are some|properties for you|we have curated)\b', re.IGNORECASE)

    media_count = sum(1 for msg in messages if msg.get('message_type') not in ['text', 'location'])
    text_message_count = len(messages) - media_count

    if not messages:
        return "Other - Unclear", "low", "No messages in conversation."

    # 1. Service Notification
    if service_keywords.search(full_conversation):
        if "bank" in full_conversation.lower() or "otp" in full_conversation.lower():
            return "Service Notification", "high", "Contains bank or OTP messages."

    # 2. Media-Only Contact
    if text_message_count / len(messages) < 0.1 and media_count > 0:
        return "Media-Only Contact", "high", f"High media content ({media_count}/{len(messages)} messages)."

    # 3. Rental Inquiry
    if rental_keywords.search(full_conversation) or location_keywords.search(full_conversation):
        notes = "Contains rental keywords."
        if location_keywords.search(full_conversation):
            notes += f" Location mentioned: {location_keywords.search(full_conversation).group(0)}"
        return "Rental Inquiry", "high", notes

    # 4. Property Listing Sent
    is_listing_sent = any(listing_sent_keywords.search(msg.get('message_body', '')) for msg in messages if msg.get('direction') == 'Outgoing')
    if is_listing_sent:
        return "Property Listing Sent", "high", "Agent sent property listings/catalogue."

    # 5. Real Estate Broker/Agent
    if broker_keywords.search(full_conversation):
        return "Real Estate Broker/Agent", "medium", "Contains broker/agent related keywords."

    # 6. Personal Contact
    if personal_keywords.search(full_conversation):
        return "Personal Contact (non-business)", "medium", "Informal language suggests personal contact."

    # 7. Group Artifact
    if any("group" in msg.get('sender_name', '').lower() for msg in messages if msg.get('sender_name')):
        return "Group Artifact", "high", "Messages appear to be from a group chat."
        
    # 8. General Business Inquiry
    if "business" in full_conversation.lower() and not rental_keywords.search(full_conversation):
        return "General Business Inquiry", "medium", "General business discussion, not real estate specific."

    # 9. Other
    return "Other - Unclear", "low", "Could not determine intent from conversation."


def main():
    try:
        with open('part2_conversations.json', 'r', encoding='utf-8') as f:
            leads = json.load(f)
    except FileNotFoundError:
        print("Error: part2_conversations.json not found.")
        return
    except json.JSONDecodeError:
        print("Error: Could not decode JSON from part2_conversations.json.")
        return

    with open('part2_classifications.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='|')
        writer.writerow(['phone_number', 'classification', 'confidence', 'notes'])

        for lead in leads:
            phone_number = lead.get('phone_number')
            if not phone_number:
                continue

            classification, confidence, notes = classify_lead(lead)
            writer.writerow([phone_number, classification, confidence, notes])

    print("Classification complete. Output saved to part2_classifications.csv")

if __name__ == "__main__":
    main()
