# EasyFind CRM — Design Decision Register

**Phase:** DESIGN ONLY. No implementation, production changes, live-data connection or AI API work in this phase.
**Owner:** Zeid (single operator)
**Updated:** 2026-09-26
**Working branch:** `feature/leads-crm-architecture`
**Related technical architecture:** [LEAD_CRM_MASTER_PLAN.md](./LEAD_CRM_MASTER_PLAN.md)

## How we work

- One design decision at a time. Ask the owner the next unresolved question; do not infer approval from a proposed default.
- Mark `[x]` only after the owner explicitly approves a decision already discussed, or a decision is already unambiguously approved in prior conversation.
- Record the decision, why it was chosen, and any constraints under the relevant section.
- `[ ]` means unresolved. `[x]` means approved; it does **not** mean built or tested.
- Keep a short dated Decision Log at the end. Update this file in GitHub after each design decision.
- No real customer data in mockups. Existing screenshots can inform layout, but sample screens must be clearly labeled illustrative.
- The approved Canva reference is the visual baseline. New layouts must preserve its restrained CRM character.

## Approved visual flow (2026-09-26)

The owner approved the visual presentation showing **Dashboard → Leads Inbox → dedicated Lead Workspace → Update & Act → Saved History**, including compact mobile inbox and mobile lead tabs. The presentation is a **conceptual mockup**; all illustrated names, counts, customer messages and property cards are examples, not verified live data.

**Visual-flow preview:** generated in the design discussion on 2026-09-26. The approved Canva design remains the primary editable design reference: https://canva.link/qmph6ij1o6lue57. Preserve the flow and layout in the next high-fidelity Canva iteration.

**Lead-workspace tabs approved as navigation concept:** Overview, Conversation, Requirements, Property Matches, AI & Drafts, Activity & History. Detailed contents of these tabs remain separate checklist decisions.

**Customer naming rule:** append and display the customer name as soon as it is known, throughout all relevant screens; retain phone as a fallback and as the underlying contact identifier. Never infer an unverified name from illustrative mockup content.

## Design baseline — already agreed

- [x] **D00.1 — Visual direction:** restrained, clean, compact CRM; navy header, white surfaces, muted blue-gray typography, green WhatsApp action, minimal decoration; responsive/mobile-first.
- [x] **D00.2 — Canva reference:** [Approved CRM design — open in Canva](https://canva.link/qmph6ij1o6lue57). Preserve this reference throughout design and handoff.
- [x] **D00.3 — Product scope:** private, single-user EasyFind leads CRM covering three EFPS WhatsApp source numbers.
- [x] **D00.4 — Dedicated lead workspace:** one logical workspace per qualifying customer; do not create a physical Google Sheets tab per lead.
- [x] **D00.5 — Core workspace capabilities:** complete available conversation history, evolving customer requirements, editable fields, AI analysis/draft history, inventory matching and activity history.
- [x] **D00.6 — Human control:** the operator can edit requirements, status and notes; explicit manual overrides take precedence over AI proposals.
- [x] **D00.7 — AI interaction:** on-demand analysis and response drafts; opening a lead, searching or filtering does not itself invoke AI.
- [x] **D00.8 — Inventory matching:** deterministic matching against verified inventory; AI may word a response using only verified property records.
- [x] **D00.9 — Event concept:** preserve raw webhook events and append normalized messages; do not silently delete non-lead conversations from the raw archive.
- [x] **D00.10 — Reply safety:** draft first; user reviews/edits before copying/opening WhatsApp. No automatic sending in the initial design.
- [x] **D00.11 — Design sequence:** finalize UX/UI decisions first, then inspect live data, reconcile fields, connect data, and implement.

## Complete design checklist

### 1. Navigation and information architecture

- [x] **D01.1 — Primary navigation:** approved after visual flow review: **Dashboard, Leads Inbox, Follow-ups, Inventory, Activity, Settings**. Clicking a lead opens its dedicated workspace (not a top-level menu item), with **Overview, Conversation, Requirements, Property Matches, AI & Drafts, Activity & History** tabs. Customer name is shown wherever available; otherwise show the phone number. The approved visual flow also shows the mobile inbox and tabbed mobile workspace.
- [x] **D01.2 — Default landing screen:** **Main Dashboard** opens after login, with business/lead overview and navigation to the Inbox and other sections. Approved together with the visual flow.
- [x] **D01.3 — Desktop structure:** approved **Tabbed Lead Workspace (Option A)** as the primary lead-detail experience. The selected lead opens a focused workspace with a lead header and tabs, while the Inbox remains the separate place for browsing/switching leads. A compact Overview can surface key details, latest conversation, AI draft and matching properties without forcing all detailed panels to remain permanently visible.
- [x] **D01.4 — Mobile structure:** approved the visual flow **Inbox → Lead Workspace → tabbed sections**, with compact fixed actions such as WhatsApp and Generate AI Reply. Avoid an endless single-page scroll for lead detail.
- [x] **D01.5 — Persistent controls:** approved **top-bar control layout** shown in the visual comparison: global search, WhatsApp source dropdown, data/refresh status and account menu stay in the top bar. Page-specific filters use dropdown controls in the page content rather than a permanently visible filter sidebar. This preserves the clean, spacious CRM layout.
- [x] **D01.6 — Loading, empty and error states:** approved with strict **NO SILENT FAILURE**. Use skeleton loading, explicit useful empty states, inline errors with Retry, and visible freshness/stale indicators. Every meaningful failure, retry, stale-data condition and processing exception must be logged and mapped to a user-visible state when it affects the operator. No silent drop or misleading stale/current presentation.

### 2. Inbox and lead qualification

- [x] **D02.1 — Inbox eligibility:** the primary working Inbox shows **Qualified Leads**. **Cold Inquiry / uncertain conversations go to a separate Review Queue** so everything potentially relevant remains reviewable. Other categories (Agent/Partner, Vendor/Supplier, Personal/Family, Spam/Marketing, Internal) remain outside the main lead inbox but are retained in the raw/archive layer and can be reclassified or reviewed when appropriate. **Property Listing Sent** is handled outside the primary qualified-lead inbox unless later reclassified.
- [x] **D02.2 — Customer identity:** show and progressively populate the customer's name wherever available (dashboard recent activity, inbox row, lead header, conversation where appropriate, follow-ups, inventory matches/sharing and activity); fall back to phone when the name is unknown. Preserve source-number attribution when the same customer appears across multiple EFPS numbers. Exact name-verification/edit controls remain for D03.1/D03.6.
- [x] **D02.3 — Lead-row content:** compact Inbox row shows customer name (primary); phone, BHK + primary location; budget max when known; status; priority; source badge(s); last interaction; and a clear new-activity / needs-review marker.
- [x] **D02.4 — Sorting:** default is **latest customer activity first**; alternate sorts are priority, follow-up due, and recently created.
- [x] **D02.5 — Filters:** compact dropdown filters for EFPS source, classification/queue, lead status, priority, BHK, location, follow-up state, and new activity / needs analysis; include Clear Filters.
- [x] **D02.6 — Search:** deterministic search across customer name, phone, BHK, preferred location, tags/notes and conversation text; indicate the matching field; never invoke AI for search.
- [x] **D02.7 — Counts:** use operational counts: Qualified Leads, Review Queue, Needs Attention, Follow-ups Due, and New Activity. Avoid ambiguous raw totals as primary working metrics.
- [x] **D02.8 — Duplicates:** confidently identical customers become one logical customer with multiple EFPS source badges/conversations; uncertain identity becomes Suspected Duplicate; user chooses Merge or Keep Separate; never silently merge.
- [x] **D02.9 — Reclassification:** reversible actions: Promote to Lead, Send to Review, Not a Lead, Reclassify, and Restore/Undo where applicable; every change creates an audit/activity event and preserves classification history.

### 3. Individual lead workspace

- [ ] **D03.1 — Lead header:** visual flow approved in principle: display available customer name (otherwise phone), click-to-WhatsApp, source-number badges, classification, status and last activity. Exact header field hierarchy remains to be finalized.
- [ ] **D03.2 — Conversation view:** incoming/outgoing bubbles, dates, source number, media placeholders and jump to latest.
- [ ] **D03.3 — Historical coverage:** display first/last available message dates and clearly identify gaps; never imply the archive is complete if it is not.
- [ ] **D03.4 — Requirements panel:** approve visible fields and ordering (BHK, location, budget, furnishing, move-in, tenant type, pets, parking, notes).
- [ ] **D03.5 — Provenance:** display AI-extracted, user-edited and message-supported values without clutter.
- [ ] **D03.6 — Manual editing:** decide inline editing, save/cancel behavior, required fields and change confirmation.
- [ ] **D03.7 — Status and priority:** approve workflow statuses, priority labels and edit controls.
- [ ] **D03.8 — Follow-up:** next action, due date, overdue indicator and activity notes.
- [ ] **D03.9 — Activity timeline:** show edits, analysis, drafts, property matches/shares and conversation events.
- [ ] **D03.10 — Lead merge/split:** visual workflow for mistaken identity or duplicates.

### 4. AI intelligence and reply drafting

- [ ] **D04.1 — AI entry points:** exact buttons and placements (Analyze New Messages, Generate Reply, Full Re-analysis).
- [ ] **D04.2 — First analysis experience:** review the initial AI summary, extracted requirements, missing questions and proposed reply.
- [ ] **D04.3 — Incremental analysis:** show new messages since last analysis and what changed.
- [ ] **D04.4 — AI memory display:** approve summary, confirmed requirements, open questions and history layout.
- [ ] **D04.5 — Requirement proposals:** accept/reject/edit AI suggestions; never silently overwrite human values.
- [ ] **D04.6 — Draft editor:** generated text, manual edits, regenerate, copy and open WhatsApp.
- [ ] **D04.7 — Draft history:** version list, timestamps, previous text, model/run linkage and draft status.
- [ ] **D04.8 — Sent-state truth:** define how to distinguish copied/opened from confirmed sent and from observed outgoing WhatsApp messages.
- [ ] **D04.9 — Cost transparency:** show whether a button triggers an AI call; avoid hidden calls.
- [ ] **D04.10 — AI failure states:** handle insufficient context, low confidence, API error and stale inventory.

### 5. Inventory experience

- [ ] **D05.1 — Inventory entry:** global Inventory screen and contextual Matches panel within each lead.
- [ ] **D05.2 — Match card:** listing ID, verified locality, BHK, rent, furnishing, availability, match explanation and missing information.
- [ ] **D05.3 — Match strictness:** mandatory criteria, flexible criteria and explicit Unknown states.
- [ ] **D05.4 — Manual matching:** let the operator search, pin, exclude or override a suggestion with a recorded reason.
- [ ] **D05.5 — Inventory freshness:** last verified/updated indicator and treatment of unavailable properties.
- [ ] **D05.6 — Share workflow:** choose properties, prepare a verified listing summary and optionally incorporate them into a reply draft.
- [ ] **D05.7 — Share history:** track suggested/shared/rejected/visited properties per lead without claiming a WhatsApp send unless verified.

### 6. Live activity and webhook visibility

- [ ] **D06.1 — New-message behavior:** badges, updated ordering and per-lead Needs Analysis state.
- [ ] **D06.2 — Three-number source UI:** clearly distinguish the customer number from the EFPS number on which the conversation occurred.
- [ ] **D06.3 — Webhook event monitor:** decide whether raw event history belongs in an advanced admin/activity view rather than the main inbox.
- [ ] **D06.4 — Processing states:** show received, deduplicated, processed, failed and retry/replay states.
- [ ] **D06.5 — Media and message edits:** define treatment of attachments, unsupported content, deletions and delivery/read receipts where provided.
- [ ] **D06.6 — Provider limitations:** design unavailable states for events/history the chosen WhatsApp integration cannot actually supply.

### 7. Privacy, safety and operator control

- [ ] **D07.1 — Authentication UX:** private login, session expiry, logout and password-reset/recovery design.
- [ ] **D07.2 — Sensitive content:** masking/reveal, privacy on mobile and safe display of personal chats outside the qualified inbox.
- [ ] **D07.3 — Confirmation patterns:** changes requiring confirmation, reversible operations and destructive-action warnings.
- [ ] **D07.4 — Audit visibility:** what is shown for manual edits, AI runs, exports and event processing.
- [ ] **D07.5 — Data export/retention UX:** export lead/history, retention and deletion request controls.
- [ ] **D07.6 — Failure recovery:** Sheets write conflicts, offline/disconnected state, webhook backlog and stale data banners.

### 8. Visual design system and final handoff

- [ ] **D08.1 — Typography, spacing and colors:** formalize tokens from the approved Canva concept.
- [ ] **D08.2 — Components:** lead row, status badge, source badge, requirement field, conversation bubble, draft card, inventory card, timeline event.
- [ ] **D08.3 — Desktop screens:** approve annotated high-fidelity Inbox, Lead Workspace, Inventory and Activity views.
- [ ] **D08.4 — Mobile screens:** approve corresponding narrow-screen flows and fixed primary actions.
- [ ] **D08.5 — Realistic but synthetic sample states:** qualified lead, cold inquiry, no matches, multiple matches, AI draft and follow-up overdue.
- [ ] **D08.6 — Accessibility:** readable text sizes, contrast, touch targets, keyboard navigation and color-independent statuses.
- [ ] **D08.7 — Design walkthrough:** the initial **Dashboard → Inbox → individual tabbed Lead Workspace → Update & Act → Saved History** navigation flow has been visually approved. A later complete operational walkthrough from a new incoming WhatsApp message through qualification, matching and reply is still required.
- [ ] **D08.8 — Final design freeze:** owner approves the full UI specification and all unresolved design questions are documented.
- [ ] **D08.9 — Data-audit handoff:** list actual live fields/tabs/rows that must be verified before implementation; no fabricated data.

## Design-phase exit criteria

- [ ] Every D01–D08 item has a decision or explicitly documented deferred status.
- [ ] Canva design reference and updated screen mockups are linked here.
- [ ] The approved navigation, desktop and mobile flows are documented.
- [ ] Every UI field is tagged **verified existing / proposed new / awaiting live-data audit**.
- [ ] No AI output is presented as an observed customer fact without attribution.
- [ ] Owner approves the design before any production UI, database, sync or webhook changes.

## Non-silent failure requirement

**Design-wide requirement approved 2026-09-26:** every meaningful failure state must be observable. The system should provide structured internal logging plus a corresponding user-facing state whenever the failure affects data freshness, an action, processing status or expected behavior. Error states should identify the affected area and provide a safe recovery action (for example Retry) without exposing secrets or raw provider payloads. Silent fallback is not permitted when it could mislead the operator about current data or completed actions.

**2026-09-26:** Figma is now the preferred design workspace for future CRM design exploration, high-fidelity screens, component work and visual iteration. Canva remains the **approved visual reference** for the original restrained CRM direction; Figma is the working design environment going forward.

## Dataset-to-screen design map (design-level)

This map defines what each UI area is intended to read from or write to. It distinguishes existing verified repositories/sheets from proposed future records. Final column names and live-row availability will be validated during the later live-data audit.

| UI area | Primary data source | Supporting data | What the user sees |
|---|---|---|---|
| **Main Dashboard** | `Leads` | `Events`, `Conversations` | Lead counts, status/priority distribution, recent activity, source-number activity, follow-up workload, latest changes. |
| **Leads Inbox** | `Leads` | latest `Conversations`, source mapping | Qualified-lead rows, name/phone, BHK, location, budget, status, priority, source, last interaction, new-activity marker. |
| **Lead → Overview** | `Leads` | latest `Conversations`, `Events`, future `Lead Sources` | Customer identity, source WhatsApp number(s), status, priority, current requirements, latest conversation, next action, key matches/draft preview. |
| **Lead → Conversation** | `Conversations` | source mapping, future `Webhook Events` | Full available message timeline, incoming/outgoing messages, timestamps, message types/media indicators, source attribution and history boundaries. |
| **Lead → Requirements** | current `Leads` requirement fields | future `Requirement History`, message references, future `AI Runs` | Current requirement values, AI/manual provenance, proposed changes, missing information, requirement-change timeline. |
| **Lead → Property Matches** | future/verified `Inventory` | future `Lead Property Matches`, current lead requirements | Deterministic property matches, exact inventory facts, match/fail/unknown criteria, shortlist/share history. |
| **Lead → AI & Drafts** | future `AI Runs`, future `Reply Drafts` | `Conversations`, current requirements, inventory matches | Latest AI analysis, what changed, saved drafts, draft versions, referenced properties and regenerate/copy actions. |
| **Lead → Activity & History** | `Events` | `Conversations`, future `AI Runs`, `Reply Drafts`, `Webhook Events` | Human edits, follow-ups, requirement changes, analyses, drafts, property actions and system events in chronological order. |
| **Follow-ups** | `Leads` (`Next Followup Date`, status, priority) | `Events`, latest `Conversations` | Due/overdue leads, next action, latest customer context and one-click opening of the lead workspace. |
| **Inventory** | future `Inventory` | future matching indexes/status data | Searchable available inventory, listing status/freshness and structured property details. |
| **Activity** | `Events` | future `Webhook Events`, `AI Runs`, `Reply Drafts` | System/operator activity stream, filters by event type/source/lead and processing state. |
| **Settings** | configured source-number/config records | authentication/integration metadata | EFPS source numbers, integration state, account/session controls and system preferences. |
| **WhatsApp Live** (future live-ingestion view) | future `Webhook Events` | `Conversations`, `Leads` | Incoming event stream, source number, customer number, message/event type, processing state, retry/error state. |

### Data-flow principles

- **Leads** is the current customer-level working state.
- **Conversations** is the raw normalized message history and should remain append-only.
- **Events** is the business/lifecycle activity history.
- **Inventory** is the property source of truth once connected and verified.
- **AI Runs / Reply Drafts / Requirement History / Webhook Events / Lead Sources / Lead Property Matches** are proposed persistent records for the next architecture phases; they are not claimed to exist in the current live workbook yet.
- The user should experience this as **one lead workspace**, even though the data is linked across multiple records/tables.
- The physical Google Sheets layout is an implementation concern; the UI should not mirror spreadsheet tabs one-to-one.

## Persistence rules confirmed with D03

Every AI run is recorded as an immutable history entry for the lead, including when it ran, what message state/context was analyzed, the previous AI-memory version, structured findings/changes, confidence/uncertainty and the generated draft reference. A later AI call can therefore identify what was previously analyzed and what new work appeared afterward.

The conversation timeline is reconstructed from stored message timestamps, direction, sender/source context, message type and body. The full available conversation remains linked to the lead. Source-number provenance remains separate for customers appearing across multiple EFPS numbers.

## Decision log

| Date | Decision | Rationale |
|---|---|---|
| 2026-09-26 | Preserve approved restrained CRM Canva reference | User explicitly approved the visual direction. |
| 2026-09-26 | Design before live-data connection and implementation | User wants to settle the experience and track decisions first. |
| 2026-09-26 | One logical workspace per qualified customer | Preserves full history without hundreds of physical spreadsheet tabs. |
| 2026-09-26 | Human-edited fields take priority over AI suggestions | Operator remains in control of customer records. |
| 2026-09-26 | On-demand AI, deterministic inventory matching | Avoid unnecessary API calls and fabricated property details. |
| 2026-09-26 | **D01.1 approved after visual review**: Dashboard, Inbox, Follow-ups, Inventory, Activity, Settings; lead opens a dedicated tabbed workspace | Owner explicitly approved the shown desktop/mobile navigation flow. |
| 2026-09-26 | **D01.2 approved**: main Dashboard is the landing screen | Owner requested the Dashboard in the visual flow and approved it. |
| 2026-09-26 | **D02.2 approved**: show customer names as soon as available, with phone fallback | Owner explicitly requested progressive name display throughout the CRM. |
| 2026-09-26 | **D01.6 approved**: no-silent-failure loading/error/stale-data design | User explicitly requires all failures to be logged and properly surfaced for easy debugging and trustworthy operation. |
| 2026-09-26 | **D01.3 approved**: use Tabbed Lead Workspace (Option A) as the primary desktop lead-detail pattern | Owner approved the visual comparison and the focused, structured layout. |
| 2026-09-26 | **D01.4 approved**: use tabbed lead navigation on mobile | Owner approved the mobile representation in the visual comparison. |
| 2026-09-26 | **D01.5 approved**: top-bar persistent controls with dropdown source/filter controls | Owner approved the dropdown UI version; page-specific filters remain compact dropdowns instead of a permanent sidebar. |
| 2026-09-26 | **Figma approved as the ongoing design workspace** | Owner explicitly requested Figma for design help going forward. |

## D02 review package — pending owner approval

The following D02.3–D02.9 decisions are being presented together for one visual approval pass. Until the owner explicitly approves the package, they remain unchecked.

### D02.3 — Lead-row content
Proposed compact row:
- Customer name (primary)
- Phone (secondary, masked/truncated where appropriate)
- Requirement snapshot: BHK + primary preferred location
- Budget max when known
- Status + priority badges
- Source WhatsApp badge(s)
- Last interaction
- New-activity / needs-review marker

### D02.4 — Sorting
Proposed default: **Latest customer activity first**.
Secondary sort options: Priority, Follow-up due, Recently created.
A manual "pinned" state can remain above normal sorting if later approved.

### D02.5 — Filters
Proposed compact dropdown/filter controls:
- EFPS source number
- Classification / queue
- Lead status
- Priority
- BHK
- Location
- Follow-up state
- New activity / needs analysis

Filters combine with search and are removable with one Clear Filters action.

### D02.6 — Search
Proposed global Inbox search across:
- customer name
- phone number
- BHK / preferred location
- tags / notes
- conversation text

Search should indicate which field produced the match and should not require AI.

### D02.7 — Counts
Proposed dashboard/inbox counters:
- **Qualified Leads**
- **Review Queue**
- **Needs Attention**
- **Follow-ups Due**
- **New Activity**
Counts are descriptive and operational, not ambiguous "total leads" numbers.

### D02.8 — Duplicate customer handling
Proposed behavior:
- One logical customer record when identity is confidently the same.
- Multiple EFPS source badges and conversations linked underneath.
- Suspected duplicate state when identity is uncertain.
- Manual "Merge" / "Keep Separate" action with audit event.
- Never silently merge based only on a matching phone fragment or name.

### D02.9 — Reclassification
Proposed reversible controls:
- **Promote to Lead**
- **Send to Review**
- **Not a Lead**
- **Reclassify**
- **Restore / Undo** where applicable

Every reclassification creates an activity/audit event and preserves the original classification history.

### Package approval rule
Approve all D02.3–D02.9 together as proposed, or specify only the item(s) to change. Approval means **design approved**, not implementation complete.

## Next question

**D01.6 — Loading, empty and error states.** Decide what the user sees when a page is loading, has no records, has stale data, or a source (Google Sheets, webhook stream, AI or inventory) is temporarily unavailable.
