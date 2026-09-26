#!/usr/bin/env python3
"""
Lead Classification System - AWS Bedrock Claude Opus 5.5
Implements 5-component framework with rule-based + AI classification
"""

import json
import sqlite3
import time
import re
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

# Configuration
DB_PATH = "leads.db"
CONFIG_DIR = "config"
# Use inference profile ID instead of direct model ID
BEDROCK_MODEL = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
BEDROCK_REGION = "us-east-1"
BATCH_SIZE = 10
BATCH_DELAY = 6  # seconds between batches
MAX_RETRIES = 3

class LeadClassifier:
    def __init__(self):
        print("🔧 Initializing Lead Classifier...")

        # Load configuration files
        self.known_agents = self._load_config("known_agents.json")
        self.personal_contacts = self._load_config("personal_contacts.json")
        self.internal_phones = self._load_config("internal_phones.json")
        self.taxonomy = self._load_config("taxonomy.json")
        self.intent_keywords = self._load_config("intent_keywords.json")
        self.rental_keywords = self._load_config("rental_keywords.json")
        self.locations = self._load_config("bangalore_locations.json")
        self.promotional = self._load_config("promotional_keywords.json")

        print(f"  ✓ {len(self.known_agents['agents'])} known agents loaded")
        print(f"  ✓ {len(self.personal_contacts['contacts'])} personal contacts loaded")
        print(f"  ✓ {len(self.internal_phones['phones'])} internal phones loaded")
        print(f"  ✓ {len(self.taxonomy['categories'])} categories loaded")

        # Initialize Bedrock client
        self.bedrock = boto3.client('bedrock-runtime', region_name=BEDROCK_REGION)
        print(f"  ✓ Bedrock client initialized (region: {BEDROCK_REGION})")
        print(f"  ✓ Model: {BEDROCK_MODEL}")

    def _load_config(self, filename):
        """Load JSON configuration file"""
        with open(f"{CONFIG_DIR}/{filename}", 'r') as f:
            return json.load(f)

    def classify(self, phone_number, conversations, source_phone):
        """
        Main classification method - implements all 5 components
        Returns: {classification, confidence, reasoning, intent, extracted_entities}
        """
        # Tier 1: Rule-based classification
        rule_result = self._apply_rules(phone_number, conversations, source_phone)
        if rule_result:
            return rule_result

        # Tier 2: AI-based classification with Claude Opus 5.5
        return self._classify_with_claude(phone_number, conversations)

    def _apply_rules(self, phone_number, conversations, source_phone):
        """Component 2: Rule-based categorization (Tier 1)"""

        # Priority 1: Internal (only if customer phone is ALSO internal)
        if phone_number in self.internal_phones["phones"]:
            return self._build_result(
                "Internal", 1.0,
                self.internal_phones["reasoning"],
                "None"
            )

        # Priority 2: Known Agents
        if phone_number in self.known_agents["agents"]:
            return self._build_result(
                "Agent/Partner", 1.0,
                self.known_agents["reasoning_template"],
                "None"
            )

        # Priority 3: Personal Contacts
        if phone_number in self.personal_contacts["contacts"]:
            contact = self.personal_contacts["contacts"][phone_number]
            return self._build_result(
                "Personal/Family", 1.0,
                contact["reasoning"],
                "None"
            )

        # Priority 4: Promotional Detection
        promo_result = self._detect_promotional(conversations)
        if promo_result:
            return promo_result

        # No rule match - fall back to AI
        return None

    def _detect_promotional(self, conversations):
        """Detect spam/marketing messages"""
        all_text = " ".join([
            msg['message_body'].lower()
            for msg in conversations
            if msg['message_body']
        ])

        # Check promotional patterns
        promo_matches = sum(1 for keyword in self.promotional['promotional_patterns']
                           if keyword.lower() in all_text)

        # Check service notifications
        service_matches = sum(1 for keyword in self.promotional['service_notifications']
                             if keyword.lower() in all_text)

        # Check movie booking
        movie_matches = sum(1 for keyword in self.promotional['movie_booking']
                           if keyword.lower() in all_text)

        # Check food delivery
        food_matches = sum(1 for keyword in self.promotional['food_delivery']
                          if keyword.lower() in all_text)

        # If 3+ promotional matches or clear service pattern
        if promo_matches >= 3 or service_matches >= 2 or movie_matches >= 2 or food_matches >= 2:
            reasoning = "Promotional message"
            if service_matches >= 2:
                reasoning = "Service notification (bank/delivery)"
            elif movie_matches >= 2:
                reasoning = "Movie ticket booking confirmation"
            elif food_matches >= 2:
                reasoning = "Food delivery notification"

            return self._build_result(
                "Spam/Marketing", 0.95,
                reasoning,
                "None"
            )

        return None

    def _classify_with_claude(self, phone_number, conversations):
        """Component 1-5: AI classification with Claude Sonnet via Bedrock"""

        # Build conversation text
        conv_text = []
        for msg in conversations:
            direction = "Customer" if msg['direction'] == 'Incoming' else "Agent"
            body = msg['message_body'] or f"[{msg['message_type']}]"
            timestamp = msg['timestamp']
            conv_text.append(f"{timestamp} | {direction}: {body[:200]}")  # Limit to 200 chars per message

        conversation_str = "\n".join(conv_text[:50])  # Limit to 50 messages

        # Build system prompt
        system_prompt = f"""You are a lead classification expert for EFPS, a real estate brokerage in Bangalore specializing in rentals.

TAXONOMY:
{json.dumps(self.taxonomy, indent=2)}

YOUR TASK:
Analyze the WhatsApp conversation and classify the lead. Return ONLY a valid JSON object with these exact fields:

{{
  "classification": "one of: {', '.join([cat['name'] for cat in self.taxonomy['categories']])}",
  "confidence": 0.0 to 1.0,
  "reasoning": "one sentence explaining why (max 120 chars)",
  "intent": "one of: {', '.join(list(self.intent_keywords['intents'].keys()))}",
  "extracted_entities": {{
    "bhk_requirement": "string or null",
    "preferred_location": "string or null",
    "budget_max": number or null,
    "furnishing": "string or null",
    "occupancy_type": "string or null",
    "urgency": "string or null"
  }}
}}

RULES:
1. Entity Extraction: Look for BHK, locations ({', '.join(self.locations['locations'][:15])}), budget, furnishing
2. Classification: Pick ONE category that best fits
3. Intent: Primary customer intent from conversation
4. Confidence: 0.8-1.0 if clear, 0.5-0.79 if partial, <0.5 if unclear
5. Reasoning: Specific and concise

Return ONLY the JSON, no markdown, no explanation."""

        # Build user message
        user_message = f"""Phone: {phone_number}
Messages: {len(conversations)}

Conversation:
{conversation_str}

Classify this lead and return the JSON."""

        # Call Bedrock with retry logic
        for attempt in range(MAX_RETRIES):
            try:
                response = self.bedrock.converse(
                    modelId=BEDROCK_MODEL,
                    messages=[
                        {
                            "role": "user",
                            "content": [{"text": user_message}]
                        }
                    ],
                    system=[{"text": system_prompt}]
                )

                # Extract response text
                response_text = response['output']['message']['content'][0]['text']

                # Parse JSON (handle markdown code blocks)
                response_text = response_text.strip()
                if response_text.startswith('```'):
                    # Remove markdown code blocks
                    lines = response_text.split('\n')
                    response_text = '\n'.join([l for l in lines if not l.startswith('```')])

                result = json.loads(response_text)

                return self._build_result(
                    result['classification'],
                    result['confidence'],
                    result['reasoning'],
                    result['intent'],
                    result.get('extracted_entities', {})
                )

            except json.JSONDecodeError as e:
                print(f"    ⚠️  JSON parse error: {e}")
                # Try one more time with explicit instruction
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2)
                    continue
                else:
                    return self._build_result(
                        "Cold Inquiry", 0.3,
                        "JSON parse error",
                        "None"
                    )

            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'ThrottlingException':
                    # Exponential backoff
                    wait_time = (2 ** attempt) * 5
                    print(f"    ⚠️  Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"    ❌ Bedrock error: {e}")
                    return self._build_result(
                        "Cold Inquiry", 0.3,
                        f"API error: {error_code}",
                        "None"
                    )

        # Max retries exceeded
        return self._build_result(
            "Cold Inquiry", 0.2,
            "Max retries exceeded",
            "None"
        )

    def _build_result(self, classification, confidence, reasoning, intent, entities=None):
        """Component 5: Format output"""
        return {
            "classification": classification,
            "confidence": float(confidence),
            "reasoning": reasoning,
            "intent": intent,
            "extracted_entities": entities or {}
        }


def reclassify_all_leads():
    """Re-classify all 735 leads using hybrid system"""

    print("\n" + "="*80)
    print("LEAD CLASSIFICATION SYSTEM - AWS BEDROCK CLAUDE OPUS 5.5")
    print("="*80 + "\n")

    # Initialize classifier
    classifier = LeadClassifier()

    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Fetch all leads
    cursor.execute("SELECT phone_number, extracted_from_phone FROM leads ORDER BY last_interaction_date DESC")
    leads = cursor.fetchall()

    print(f"\n📊 Total leads to classify: {len(leads)}")
    print(f"📦 Batch size: {BATCH_SIZE}")
    print(f"⏱️  Batch delay: {BATCH_DELAY}s")
    print(f"🔄 Max retries: {MAX_RETRIES}")
    print(f"⏳ Estimated time: ~{(len(leads) / BATCH_SIZE) * BATCH_DELAY / 60:.1f} minutes")
    print("\n" + "-"*80 + "\n")

    results = []
    rule_based_count = 0
    ai_count = 0
    failed_count = 0

    start_time = time.time()

    # Process in batches
    for batch_idx in range(0, len(leads), BATCH_SIZE):
        batch = leads[batch_idx:batch_idx + BATCH_SIZE]
        batch_num = (batch_idx // BATCH_SIZE) + 1
        total_batches = (len(leads) + BATCH_SIZE - 1) // BATCH_SIZE

        print(f"Batch {batch_num}/{total_batches} (Leads {batch_idx + 1}-{min(batch_idx + BATCH_SIZE, len(leads))}):")

        batch_rule_based = 0
        batch_ai = 0

        for lead in batch:
            phone = lead['phone_number']
            source_phone = lead['extracted_from_phone']

            # Fetch conversations
            cursor.execute("""
                SELECT direction, message_body, message_type, timestamp
                FROM conversations
                WHERE phone_number = ?
                ORDER BY timestamp ASC
            """, (phone,))
            conversations = [dict(row) for row in cursor.fetchall()]

            # Classify
            try:
                result = classifier.classify(phone, conversations, source_phone)

                if result['confidence'] == 1.0:
                    rule_based_count += 1
                    batch_rule_based += 1
                else:
                    ai_count += 1
                    batch_ai += 1

                # Format notes
                notes = f"{result['reasoning']} | Confidence: {result['confidence']:.2f} | Intent: {result['intent']}"

                # Update database
                cursor.execute("""
                    UPDATE leads
                    SET classification = ?,
                        notes = ?,
                        bhk_requirement = ?,
                        preferred_location = ?,
                        budget_max = ?,
                        furnishing_preference = ?,
                        occupancy_type = ?,
                        move_in_date = ?
                    WHERE phone_number = ?
                """, (
                    result['classification'],
                    notes,
                    result['extracted_entities'].get('bhk_requirement'),
                    result['extracted_entities'].get('preferred_location'),
                    result['extracted_entities'].get('budget_max'),
                    result['extracted_entities'].get('furnishing'),
                    result['extracted_entities'].get('occupancy_type'),
                    result['extracted_entities'].get('urgency'),
                    phone
                ))

                results.append(result)

            except Exception as e:
                print(f"    ❌ Error classifying {phone}: {e}")
                failed_count += 1

        # Commit batch
        conn.commit()

        print(f"  ✓ Rule-based: {batch_rule_based} | AI: {batch_ai}")

        # Delay between batches (except for last batch)
        if batch_idx + BATCH_SIZE < len(leads):
            print(f"  ⏳ Waiting {BATCH_DELAY}s before next batch...\n")
            time.sleep(BATCH_DELAY)
        else:
            print()

    conn.close()

    # Summary
    elapsed_time = time.time() - start_time
    print("\n" + "="*80)
    print("✅ CLASSIFICATION COMPLETE")
    print("="*80)
    print(f"\n📊 Summary:")
    print(f"  Total leads: {len(leads)}")
    print(f"  Rule-based: {rule_based_count} ({rule_based_count/len(leads)*100:.1f}%)")
    print(f"  AI-based: {ai_count} ({ai_count/len(leads)*100:.1f}%)")
    print(f"  Failed: {failed_count}")
    print(f"  Time elapsed: {elapsed_time/60:.1f} minutes")

    # Category distribution
    print(f"\n📋 Classification Distribution:")
    categories = {}
    for r in results:
        cat = r['classification']
        categories[cat] = categories.get(cat, 0) + 1

    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        pct = (count / len(results)) * 100
        print(f"  {cat}: {count} ({pct:.1f}%)")

    # Low confidence
    low_confidence = [r for r in results if r['confidence'] < 0.7]
    print(f"\n⚠️  Low confidence (<0.7): {len(low_confidence)} leads ({len(low_confidence)/len(results)*100:.1f}%)")

    return results


if __name__ == '__main__':
    results = reclassify_all_leads()

    print("\n🔄 Syncing to Google Sheet...")
    print("Run: python3 sync_to_sheet_v2.py")
    print("\n✅ Done!")
