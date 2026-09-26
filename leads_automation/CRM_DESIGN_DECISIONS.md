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
- [ ] **D01.5 — Persistent controls:** decide where global search, source selector, refresh and account/logout appear.
- [ ] **D01.6 — Empty/loading/error states:** define what the user sees when a tab is empty, data is loading or Sheets is unavailable.

### 2. Inbox and lead qualification

- [ ] **D02.1 — Inbox eligibility:** which classification categories appear in the main working inbox; what happens to Cold Inquiry and Property Listing Sent.
- [x] **D02.2 — Customer identity:** show and progressively populate the customer's name wherever available (dashboard recent activity, inbox row, lead header, conversation where appropriate, follow-ups, inventory matches/sharing and activity); fall back to phone when the name is unknown. Preserve source-number attribution when the same customer appears across multiple EFPS numbers. Exact name-verification/edit controls remain for D03.1/D03.6.
- [ ] **D02.3 — Lead-row content:** agree compact row fields (name/number, BHK, location, source, status, last interaction, unread/new-activity marker).
- [ ] **D02.4 — Sorting:** default order and alternate sorts (latest activity, priority, follow-up due).
- [ ] **D02.5 — Filters:** source WhatsApp number, classification, status, priority, location, BHK and activity.
- [ ] **D02.6 — Search:** searchable fields and whether it searches conversation content as well as lead details.
- [ ] **D02.7 — Counts:** label Total Extracted, Qualified Leads, Needs Attention, Matching Results clearly; avoid ambiguous “228 leads.”
- [ ] **D02.8 — Duplicates:** design treatment for one customer present across two or three EFPS numbers.
- [ ] **D02.9 — Reclassification:** design manual Promote to Lead / Not a Lead / Review controls with reversible actions.

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

## Figma design direction

**2026-09-26:** Figma is now the preferred design workspace for future CRM design exploration, high-fidelity screens, component work and visual iteration. Canva remains the **approved visual reference** for the original restrained CRM direction; Figma is the working design environment going forward.

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
| 2026-09-26 | **D01.3 approved**: use Tabbed Lead Workspace (Option A) as the primary desktop lead-detail pattern | Owner approved the visual comparison and the focused, structured layout. |
| 2026-09-26 | **D01.4 approved**: use tabbed lead navigation on mobile | Owner approved the mobile representation in the visual comparison. |
| 2026-09-26 | **Figma approved as the ongoing design workspace** | Owner explicitly requested Figma for design help going forward. |

## Next question

**D01.5 — Persistent controls.** Decide where global search, source selector, refresh/sync status and account/logout should live across Desktop and Mobile. Visualize the options before approval.
