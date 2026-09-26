# EasyFind Lead CRM — Master Design & Implementation Plan

**Status:** Architecture approved for implementation planning  
**Repository:** `zeidhussain9-cloud/easyfind-website`  
**Working branch:** `feature/leads-crm-architecture`  
**Deployment target:** Render `leads-ui-dashboard`  
**Last reviewed:** 2026-09-26

---

## 1. Product goal

Turn the current WhatsApp extraction + Google Sheets system into a **private, operator-first lead workspace** for EasyFind.

The dashboard should help one person answer four questions immediately:

1. **Who needs attention?**
2. **What exactly does this customer want?**
3. **What happened in the conversation?**
4. **What should I do or say next?**

AI is an assistant inside this workflow. It is not the system of record and it should not be called for tasks that deterministic code can perform.

---

## 2. Verified existing architecture

The repository currently describes and implements this pipeline:

`WhatsApp backups → extraction → classification → SQLite → Google Sheets → dashboard`

### Verified source channels

The repository's `config/internal_phones.json` identifies these three EFPS source numbers:

- `+919148338801`
- `+917975102130`
- `+919902024973`

These are **source WhatsApp numbers**, not customer numbers.

### Verified classification taxonomy

`config/taxonomy.json` defines:

- Qualified Lead
- Cold Inquiry
- Agent/Partner
- Property Listing Sent
- Vendor/Supplier
- Personal/Family
- Spam/Marketing
- Internal

### Verified core data model

The repository's `schema.sql` defines:

#### `leads`
One master record keyed by normalized customer `phone_number`, containing:

- customer name
- lead status
- lead source
- priority
- current requirement
- BHK
- preferred location
- budget min / max
- furnishing preference
- occupancy type
- pet preference
- parking required
- move-in date
- matched properties
- last interaction
- next follow-up
- follow-up count
- tags
- notes
- timestamps

#### `conversations`
Message-level history keyed to the customer phone number:

- message ID
- customer phone
- incoming / outgoing direction
- message body
- message type
- media references
- sender
- timestamp
- reply reference
- processing state
- extracted intent
- extracted entities
- sentiment
- follow-up requirement
- processing timestamps

#### `lead_lifecycle_events`
Audit history containing:

- event ID
- customer phone
- event type
- description
- trigger source
- metadata
- related message ID
- related property ID
- timestamp

---

## 3. Important corrections to current assumptions

### The extraction is not hard-coded to "last 3 days"

The current `extract_whatsapp.py` uses an explicit `--date-from` when supplied. When omitted, its default is approximately **60 days**.

The importer also receives a cutoff date.

Therefore, the fact that the current UI appears to contain conversations ending a few days ago does **not** prove that the extraction pipeline is limited to three days. The actual date supplied to the extraction run must be treated as the source of truth.

### The current database import is not safely idempotent for conversations

`import_to_database_v2.py` uses `INSERT OR IGNORE` for the master lead row, but it inserts conversation rows again without a message-level deduplication key.

This means repeating an extraction/import can create duplicate conversation messages and duplicate data-import lifecycle events.

**Required before live webhook operation:** introduce a stable external message/event ID and an idempotent import key.

### The current Google Sheets sync is destructive

`sync_to_sheet_v2.py` currently calls `clear()` and then rewrites the `Leads`, `Conversations` and `Events` worksheets.

This is incompatible with uncontrolled dashboard edits.

**Required before enabling CRM writes:** replace destructive full rewrites with controlled upsert/sync behavior and explicit field ownership.

---

## 4. Core architectural decision: no physical worksheet per lead

The idea of a dedicated worksheet for every qualified lead is understandable, but it should **not** be the operational data model.

Creating one Google Sheets tab per lead would create:

- hundreds of tabs
- slow navigation
- difficult global filtering
- harder synchronization
- harder webhook processing
- duplicated structures
- more fragile formulas and references

### Better interpretation of the idea

Every qualified lead gets a **dedicated logical workspace in the CRM UI**, assembled from shared structured tables.

A customer can therefore have a complete workspace without creating a physical tab.

### The UI becomes the "dedicated worksheet"

When a lead is opened, the workspace shows:

- customer identity
- source WhatsApp number(s)
- current requirements
- requirement history
- full conversation
- AI memory
- AI analysis history
- reply drafts
- inventory matches
- follow-up
- activity history

This gives the exact experience desired without multiplying worksheet tabs.

---

## 5. Qualification model

The raw extraction layer should **never delete non-lead conversations**.

Instead:

`Raw WhatsApp data → classification → qualification → CRM visibility`

All conversations remain available for audit and future reclassification.

Only contacts that qualify for CRM workflows should appear in the primary **Qualified Leads** view.

### Example

A personal/family conversation may remain in raw data but not appear in the operator's qualified-lead inbox.

A known agent may remain searchable but should not look like a rental customer.

A true rental/property inquiry becomes a CRM lead.

### Important identity rule

The customer phone number is the person identity.

The source WhatsApp number is a separate attribute.

A single customer may appear in conversations extracted from multiple EFPS source numbers.

Therefore the future data model must support:

`one customer → many source WhatsApp numbers`

Do **not** overwrite one source number with another when the same customer appears in multiple imports.

---

## 6. Persistent AI memory model

The AI should not repeatedly consume the entire conversation unless explicitly requested.

The system should retain the original conversation and maintain an evolving customer memory.

### A. Conversation history — immutable

Every WhatsApp message remains as an individual record.

This is the ground truth.

### B. Customer intelligence — current working state

A compact structured record representing what is currently understood.

Suggested fields:

- current requirement
- BHK requirement
- preferred locations
- budget range
- furnishing
- occupancy
- pet requirement
- parking
- move-in timing
- urgency
- missing information
- latest intent
- qualification state
- concise conversation summary
- last analyzed message ID / timestamp
- manually overridden fields

### C. Requirement history — append-only

Every meaningful requirement change should be recorded.

For example:

- budget changed from ₹45K to ₹50K
- location added
- pet requirement introduced
- move-in date changed

Each change should include provenance.

Suggested provenance:

- `AI`
- `Human`
- `System`

Where possible, store the source message ID that supports the extracted value.

### D. AI analysis history — immutable

Each AI execution becomes an `AI Run` record containing:

- run ID
- lead ID
- run timestamp
- model
- prompt/context version
- message range or message IDs used
- previous intelligence version
- output JSON
- extracted changes
- confidence / uncertainty
- generated draft ID

This ensures no AI call is "lost".

### E. Reply drafts — immutable versions

Each generated response should be saved separately.

Suggested fields:

- draft ID
- lead ID
- AI run ID
- created at
- draft text
- referenced inventory IDs
- status: `draft / edited / approved / discarded / sent`
- manually edited text
- sent-at (only if the user confirms it was actually sent)

A draft is never treated as an actual WhatsApp message.

---

## 7. AI call strategy

### First AI analysis

When the user explicitly requests:

**Analyze + Draft Reply**

the backend assembles:

1. complete recent conversation context as needed
2. current lead fields
3. prior customer intelligence if present
4. requirement history where relevant
5. source WhatsApp identity
6. relevant previous draft, if useful
7. verified inventory matches, if the user requested property recommendations

The AI returns structured information plus a draft.

### Subsequent AI calls

Default context:

`saved customer intelligence + new/unanalysed messages + selected relevant history`

Not:

`entire conversation every time`

A separate **Re-analyze Full Conversation** action can exist when the user wants a full reset/review.

### Important principle

**Do not call AI when deterministic code can answer the question.**

Opening a lead = no AI  
Searching inventory = no AI  
Filtering leads = no AI  
Changing a status = no AI  
Copying a draft = no AI

Generate analysis/reply = AI

---

## 8. Inventory matching architecture

Inventory matching should be **strictly sheet/data driven**.

AI should not decide whether a property is available.

### Deterministic match engine

Input:

- BHK
- preferred locations
- budget
- furnishing
- occupancy
- pet requirement
- parking
- move-in date
- inventory availability
- listing status

Output:

For each candidate:

- listing ID
- verified listing fields
- matched conditions
- failed conditions
- unknown conditions
- reason for inclusion/exclusion

### AI's role

Only after verified inventory candidates exist:

- explain why selected properties fit
- produce natural WhatsApp wording
- combine multiple verified listings into a reply

### Inventory rule

The dashboard must never invent:

- rent
- availability
- property features
- location
- furnishing
- pet policy
- listing status

All property information shown to the AI and user must originate from the inventory dataset.

### Pending verification

The current repository does **not** contain a verified inventory schema or live inventory rows.

Inventory integration therefore begins only after the actual inventory source and columns are inspected.

---

## 9. Manual control

AI must propose. The operator can correct.

Every important AI-extracted requirement should be editable directly from the customer workspace.

Example:

**Preferred Location**

AI: `Bellandur, Yemalur`

[Edit]

If the operator changes it to `Bellandur, HSR Layout`, the human value should take precedence.

The stored value should retain its provenance:

`source = Human`

This prevents the next AI analysis from blindly replacing a deliberate manual decision.

---

## 10. Webhook architecture

The future live ingestion pipeline should begin with an append-only webhook event ledger.

### Proposed table: `webhook_events`

Suggested fields:

- `event_id`
- `provider_event_id`
- `received_at`
- `source_whatsapp_number`
- `customer_phone`
- `event_type`
- `message_id`
- `message_timestamp`
- `payload_json`
- `processing_status`
- `processed_at`
- `processing_error`

### Why keep every event?

The webhook ledger becomes the system's raw event history.

If the downstream classifier, matcher or CRM logic fails, the original event still exists and can be replayed.

### Pipeline

`WhatsApp provider`
↓  
`Webhook endpoint`
↓  
`webhook_events` (append-only)
↓  
`deduplication`
↓  
`conversation record`
↓  
`lead identity resolution`
↓  
`qualification / dirty-state update`
↓  
`CRM`

The webhook should **not automatically call AI for every event** in the initial system.

Instead, a new inbound message can mark the lead:

**Needs analysis**

The operator can then run AI intentionally.

An optional future mode can auto-analyze only specific high-value events.

---

## 11. Recommended physical storage model

For the current Google Sheets based phase, use logical tables/tabs like:

### `Leads`

One row per customer.

Contains current CRM state.

### `Lead Sources`

One row per customer/source-number relationship.

Allows the same customer to be associated with multiple EFPS WhatsApp numbers.

### `Conversations`

Append-only message history.

### `Requirement History`

Append-only changes to requirements.

### `AI Runs`

Every AI analysis execution.

### `Reply Drafts`

Every generated/editable draft version.

### `Events`

Existing lifecycle events, retained for business activity.

### `Webhook Events`

Append-only incoming event ledger.

### `Inventory`

Verified listing dataset.

### `Lead Property Matches`

Deterministic matching results linking leads to inventory IDs.

This is the operational equivalent of giving each lead its own complete worksheet.

---

## 12. CRM screen structure

### Desktop

**Column 1 — Lead Inbox**

Compact list showing:

- customer
- phone
- BHK
- location
- source number
- status
- priority
- last interaction

**Column 2 — Customer Workspace**

- identity
- source
- current requirements
- editable requirement fields
- qualification
- classification
- notes
- follow-up

**Column 3 — Conversation + Action**

- conversation timeline
- latest messages
- AI analysis state
- reply draft
- inventory matches
- Copy Reply
- Open WhatsApp

### Mobile

Mobile becomes a sequential workspace:

`Lead Inbox → Lead Profile → Messages → Reply → Inventory → Activity`

No long page containing hundreds of expanded leads.

---

## 13. UI design language

The approved visual direction is a **restrained CRM**, not a marketing dashboard.

### Principles

- white information surfaces
- restrained navy header
- muted blue-gray typography
- green used mainly for WhatsApp action
- compact density
- strong information hierarchy
- minimal decorative elements
- clear status badges
- no unnecessary charts
- mobile-first behavior
- actions close to the information they affect

### Canva reference

The approved Canva-generated CRM concept is:

https://canva.link/qmph6ij1o6lue57

The design concept should remain a visual reference, not a source of invented data.

**Data displayed in the real UI must always come from verified fields.**

---

## 14. Real data policy

The dashboard has to distinguish:

### Verified

Directly sourced from:

- Google Sheets
- conversation records
- inventory records
- confirmed human edits

### AI-derived

Generated interpretation, classification, requirement extraction or draft.

### Illustrative

Never present as actual customer/property information.

The UI should visibly label AI-generated content where ambiguity could matter.

---

## 15. Synchronization strategy

The current destructive synchronization model must be replaced.

### Source-of-truth proposal

**Immutable ingestion data**

Conversation messages and webhook events are append-only.

**Operational CRM state**

Current lead requirements, status, priority, notes and follow-up become controlled CRM fields.

**AI memory**

Stored independently from raw conversation data.

**Inventory**

Read from a controlled inventory source.

### Write flow

Dashboard edit:

`UI → API → validation → write CRM field → lifecycle event → sync`

No client-side direct write to Google Sheets.

---

## 16. Phase-by-phase implementation plan

### Phase 0 — Data integrity foundation

- [ ] Add stable IDs / dedupe strategy for imported WhatsApp messages
- [ ] Separate customer identity from source WhatsApp identity
- [ ] Define qualification visibility rules
- [ ] Replace destructive Sheets sync
- [ ] Define CRM field ownership
- [ ] Verify actual live worksheet headers and row counts
- [ ] Verify extra tabs: Extraction Log, Findings, Priority Sharing

### Phase 1 — Read-only CRM workspace

- [x] Private login
- [x] Current lead API
- [x] Source-number visibility
- [x] Direct WhatsApp link
- [ ] Compact lead inbox
- [ ] Customer workspace
- [ ] Conversation timeline
- [ ] Activity timeline
- [ ] Data audit view
- [ ] Mobile navigation model

### Phase 2 — Manual CRM controls

- [ ] Edit status
- [ ] Edit priority
- [ ] Edit requirements
- [ ] Edit notes
- [ ] Edit next follow-up
- [ ] Save changes through backend
- [ ] Record lifecycle events
- [ ] Show human vs AI field provenance

### Phase 3 — Persistent AI memory

- [ ] Customer intelligence store
- [ ] Requirement history
- [ ] AI run history
- [ ] Reply draft history
- [ ] New/unanalysed message tracking
- [ ] Full re-analysis action
- [ ] On-demand AI analysis endpoint

### Phase 4 — Inventory engine

- [ ] Connect actual inventory source
- [ ] Verify inventory fields
- [ ] Normalize inventory data
- [ ] Implement strict rule-based matching
- [ ] Show match / fail / unknown reasons
- [ ] Link matched properties to lead
- [ ] Track shared/rejected properties

### Phase 5 — AI response generation

- [ ] Structured AI output contract
- [ ] Draft generation
- [ ] Draft versioning
- [ ] Human editing
- [ ] Copy reply
- [ ] Inventory-aware replies
- [ ] Missing-requirement detection
- [ ] Context-size / cost controls

### Phase 6 — Live WhatsApp webhooks

- [ ] Choose/verify WhatsApp provider
- [ ] Webhook endpoint
- [ ] Raw event ledger
- [ ] Event deduplication
- [ ] Source-number identification
- [ ] Customer identity resolution
- [ ] Conversation append pipeline
- [ ] Lead dirty-state handling
- [ ] Replay / retry support

### Phase 7 — Operational polish

- [ ] Follow-up queue
- [ ] "Needs attention" view
- [ ] Recently changed leads
- [ ] Search improvements
- [ ] Inventory availability indicators
- [ ] Error/retry monitoring
- [ ] Audit screen
- [ ] Backup/export
- [ ] Security hardening

---

## 17. Initial API contract

The API should evolve around resources rather than around individual screen elements.

### Leads

- `GET /api/leads`
- `GET /api/leads/:phone`
- `PATCH /api/leads/:phone`

### Conversations

- `GET /api/leads/:phone/conversations`

### Events

- `GET /api/leads/:phone/events`

### Intelligence

- `GET /api/leads/:phone/intelligence`
- `POST /api/leads/:phone/analyze`

### Drafts

- `GET /api/leads/:phone/drafts`
- `POST /api/leads/:phone/drafts`

### Inventory

- `GET /api/inventory/matches/:phone`

### Webhooks

- `POST /api/webhooks/whatsapp`

The provider-specific webhook payload should be normalized at the boundary so the rest of the CRM does not depend on one WhatsApp provider's schema.

---

## 18. AI output contract

The AI endpoint should return structured JSON, not free-form prose.

Example shape:

```json
{
  "analysis": {
    "classification": "Qualified Lead",
    "intent": "Property Search",
    "confidence": 0.91,
    "summary": "Customer is actively looking for a 2 BHK...",
    "missing_information": ["budget_max", "move_in_date"]
  },
  "requirement_updates": [
    {
      "field": "preferred_location",
      "value": "Bellandur, Yemalur",
      "source_message_id": "msg_123",
      "confidence": 0.94
    }
  ],
  "draft": {
    "text": "..."
  }
}
```

The application validates this response before storing it.

---

## 19. Cost-control rules

AI spend should be deliberate.

### Do not call AI on:

- page load
- scrolling
- search
- filters
- opening conversations
- inventory filtering
- manual status edits

### Call AI on:

- Analyze
- Generate reply
- Regenerate
- Full re-analysis
- optional future automatic analysis mode

### Context strategy

Prefer:

`customer intelligence + delta messages + relevant context`

over:

`entire history every time`

The complete history remains stored regardless.

---

## 20. Security rules

This is a private CRM containing client WhatsApp information.

Required:

- authenticated dashboard
- authenticated API
- secure HTTP-only session cookie
- no credentials in browser code
- AI secrets server-side
- no raw conversation data in application logs
- no automatic outbound WhatsApp send in v1
- explicit user action for reply copying/opening
- audit trail for manual CRM changes

---

## 21. Current implementation state

The live Render service currently provides:

- private password access
- Google Sheets connectivity
- lead data
- three source-number visibility
- direct WhatsApp links
- a temporary dashboard

The repository now contains a separate CRM workspace implementation branch for the next UI iteration.

The **production system has not yet implemented**:

- persistent AI memory
- AI reply generation
- safe CRM write-back
- deterministic inventory matching
- webhook ingestion
- per-lead persistent AI run/draft history

These are deliberate next phases.

---

## 22. Decision summary

### Approved

**A dedicated logical workspace per qualified lead.**

### Not approved

**A physical Google Sheets worksheet/tab per lead.**

### Approved

**Full raw conversation retained.**

### Approved

**Persistent customer intelligence that evolves over time.**

### Approved

**Persistent AI run and reply-draft history.**

### Approved

**Manual requirement overrides.**

### Approved

**Strict sheet-based inventory matching with no AI dependency.**

### Approved

**Append-only webhook event ledger.**

### Approved

**AI only when useful, not on every page load or message event.**

### Core design principle

> **Raw data is preserved.  
> AI creates understanding.  
> Human edits remain authoritative.  
> Inventory matching is deterministic.  
> The CRM UI brings all of it together into one lead workspace.**



## Design decisions and visual reference

The visual baseline is the approved restrained CRM concept in Canva: https://canva.link/qmph6ij1o6lue57

The approved navigation flow is:

**Dashboard → Leads Inbox → Individual Lead Workspace → Update & Act → Saved History**

The owner approved the **Tabbed Lead Workspace** as the primary desktop pattern and the corresponding tabbed mobile workspace. The logical lead workspace contains Overview, Conversation, Requirements, Property Matches, AI & Drafts, and Activity & History.

Customer names should be displayed wherever known, with phone number as fallback. Figma is the preferred working environment for future CRM design iterations, high-fidelity screens, components and visual review; Canva remains the approved original visual reference.

Detailed decision tracking is maintained in `CRM_DESIGN_DECISIONS.md`.
