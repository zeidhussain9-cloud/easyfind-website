import json
import csv
import re

def classify_lead(lead):
    messages = lead.get('messages', [])
    conversation_text = " ".join([msg.get('message_body', '') for msg in messages]).lower()
    
    # Pre-compile regex for faster matching
    rental_keywords = re.compile(r'\b(rent|bhk|budget|looking for|furnished|bachelor|family|2bhk|3bhk|1bhk)\b')
    location_keywords = re.compile(r'\b(whitefield|hsr|marathahalli|yemalur|bellandur|sarjapur|kadubeesanahalli|ambalipura|harlur)\b')
    listing_keywords = re.compile(r'\b(catalogue|options|properties|listing)\b')
    broker_keywords = re.compile(r'\b(broker|agent|commission|client|site visit)\b')
    service_keywords = re.compile(r'\b(otp|bank|hfc|maruti|suzuki|delivery|transaction|card)\b')

    incoming_messages = [msg.get('message_body', '').lower() for msg in messages if msg.get('direction') == 'Incoming']
    outgoing_messages = [msg.get('message_body', '').lower() for msg in messages if msg.get('direction') == 'Outgoing']
    
    incoming_text = " ".join(incoming_messages)
    outgoing_text = " ".join(outgoing_messages)

    # 1. Rental Inquiry
    if rental_keywords.search(incoming_text) or location_keywords.search(incoming_text):
        notes = "Customer enquired about rental properties"
        if rental_keywords.search(incoming_text):
            m = rental_keywords.search(incoming_text)
            notes += f", mentioned '{m.group(1)}'"
        if location_keywords.search(incoming_text):
            m = location_keywords.search(incoming_text)
            notes += f" in '{m.group(1)}'"
        return "Rental Inquiry", "high", notes

    # 2. Property Listing Sent
    if listing_keywords.search(outgoing_text) or "here are some options" in outgoing_text:
        return "Property Listing Sent", "high", "Agent sent property listings to the customer."

    if "https://maps.app.goo.gl" in outgoing_text:
        return "Property Listing Sent", "high", "Agent sent a property with a google maps link."

    # 3. Real Estate Broker/Agent
    if broker_keywords.search(conversation_text):
        # Check if it's not a customer asking about brokerage
        if "brokerage" not in incoming_text:
            return "Real Estate Broker/Agent", "medium", "Conversation includes terms like broker/agent/commission."

    # 4. Personal Contact (non-business)
    # This is harder to detect with keywords. We can look for informal language.
    if any(greet in incoming_text for greet in ["bhai", "bro", "dude"]):
         if not (rental_keywords.search(conversation_text) or location_keywords.search(conversation_text)):
            return "Personal Contact (non-business)", "medium", "Informal language used, and no direct rental inquiry."

    # 5. Service Notification
    if service_keywords.search(conversation_text) or "service overdue" in conversation_text:
        return "Service Notification", "high", "Contains keywords related to service notifications."

    # 7. Media-Only Contact
    media_count = sum(1 for msg in messages if msg.get('message_type') != 'text')
    text_count = len(messages) - media_count
    if media_count > 0 and text_count / (media_count + text_count) < 0.1: # less than 10% text
        return "Media-Only Contact", "high", "Conversation is more than 90% media."
        
    # If after all checks, it seems like a rental inquiry from context
    if "looking for" in incoming_text:
         return "Rental Inquiry", "medium", "Customer looking for property."

    # Fallback and other categories
    if len(messages) < 3:
        if "hi" in incoming_text and len(incoming_messages) == 1:
            return "Other - Unclear", "low", "Only a greeting was exchanged."

    return "Other - Unclear", "low", "Could not determine the category with high confidence."


def main():
    try:
        with open('part1_conversations.json', 'r') as f:
            leads = json.load(f)
    except FileNotFoundError:
        print("Error: part1_conversations.json not found.")
        return
    except json.JSONDecodeError:
        print("Error: Could not decode JSON from part1_conversations.json.")
        return

    with open('part1_classifications.csv', 'w', newline='') as f:
        writer = csv.writer(f, delimiter='|')
        writer.writerow(['phone_number', 'classification', 'confidence', 'notes'])

        for lead in leads:
            phone_number = lead.get('phone_number')
            classification, confidence, notes = classify_lead(lead)
            writer.writerow([phone_number, classification, confidence, notes])

if __name__ == '__main__':
    main()
