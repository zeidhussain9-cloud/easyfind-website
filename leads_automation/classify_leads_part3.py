import json
import csv

def classify_lead(lead):
    messages = lead.get('messages', [])
    conversation_text = " ".join([msg.get('message_body', '') for msg in messages]).lower()

    is_rental_inquiry = any(keyword in conversation_text for keyword in ['bhk', 'rent', 'budget', 'furnished', 'bachelor', 'family', 'yemlur', 'hsr', 'marathahalli', 'whitefield'])
    agent_sent_listing = any("here are some options" in msg.get('message_body', '').lower() or "property details" in msg.get('message_body', '').lower() or "catalogue" in msg.get('message_body', '').lower() for msg in messages if msg.get('direction') == 'Outgoing')

    if 'broker' in conversation_text or 'agent' in conversation_text:
        return 'Real Estate Broker/Agent', 'medium', 'Mentions of broker or agent.'

    if is_rental_inquiry:
        notes = "Contains rental keywords like "
        found_keywords = []
        for keyword in ['bhk', 'rent', 'budget', 'furnished', 'bachelor', 'family', 'yemlur', 'hsr', 'marathahalli', 'whitefield']:
            if keyword in conversation_text:
                found_keywords.append(keyword)
        notes += ", ".join(found_keywords)
        return 'Rental Inquiry', 'high', notes

    if agent_sent_listing:
        return 'Property Listing Sent', 'high', 'Agent sent property listings.'

    if any(keyword in conversation_text for keyword in ['friend', 'plan', 'weekend']):
        return 'Personal Contact (non-business)', 'medium', 'Keywords suggest personal conversation.'

    if any(keyword in conversation_text for keyword in ['bank', 'otp', 'transaction', 'delivery']):
        return 'Service Notification', 'high', 'Keywords suggest service notifications.'

    if messages and len([msg for msg in messages if msg.get('message_type') in ['image', 'video', 'audio']]) / len(messages) > 0.9:
        return 'Media-Only Contact', 'high', 'Over 90% of messages are media.'

    if 'group' in conversation_text:
        return 'Group Artifact', 'low', 'Conversation appears to be from a group chat.'
        
    if 'business' in conversation_text and not is_rental_inquiry:
        return 'General Business Inquiry', 'medium', 'General business discussion, not real estate.'

    return 'Other - Unclear', 'low', 'Could not determine a clear category.'


def main():
    try:
        with open('part3_conversations.json', 'r') as f:
            leads = json.load(f)
    except FileNotFoundError:
        print("Error: part3_conversations.json not found.")
        return
    except json.JSONDecodeError:
        print("Error: Could not decode JSON from part3_conversations.json.")
        return

    with open('part3_classifications.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter='|')
        writer.writerow(['phone_number', 'classification', 'confidence', 'notes'])

        for lead in leads:
            phone_number = lead.get('phone_number')
            if not phone_number:
                continue
            
            classification, confidence, notes = classify_lead(lead)
            writer.writerow([phone_number, classification, confidence, notes])

if __name__ == "__main__":
    main()
