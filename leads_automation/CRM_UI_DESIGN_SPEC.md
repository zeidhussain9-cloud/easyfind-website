# EasyFind CRM — UI Design Specification

**Status:** D01–D04 approved; D05 proposed  
**Working branch:** `feature/leads-crm-architecture`  
**Visual workspace:** [Figma — EasyFind CRM — Design System & Lead Inbox](https://www.figma.com/design/PBiMGsVQ0fVpSf39WwNmKb)  
**Visual baseline:** [Approved Canva CRM concept](https://canva.link/qmph6ij1o6lue57)  
**Decision register:** [CRM_DESIGN_DECISIONS.md](./CRM_DESIGN_DECISIONS.md)

## 1. Product structure

Main navigation:
1. Dashboard
2. Leads Inbox
3. Follow-ups
4. Inventory
5. Activity
6. Settings

Selecting a lead opens a logical dedicated Lead Workspace. It is not a physical Google Sheets tab.

Lead Workspace tabs:
1. Overview
2. Conversation
3. Requirements
4. Property Matches
5. AI & Drafts
6. Activity & History

Desktop uses the focused tabbed workspace approved in the D01 visual comparison. Mobile follows Inbox → Lead Workspace → tabbed sections.

## 2. Global controls

Top bar:
- Global Search
- EFPS WhatsApp source dropdown
- Data / refresh status
- Account menu / logout

Page-specific filters are compact dropdowns, not a permanent sidebar.

## 3. Inbox and qualification

### Main Inbox
Shows Qualified Leads.

### Review Queue
Shows Cold/uncertain inquiries and anything requiring qualification review.

### Archive / non-lead classifications
Agent/Partner, Vendor/Supplier, Personal/Family, Spam/Marketing and Internal remain retained in the raw/archive layer and are excluded from the primary qualified-lead inbox unless reclassified.

## 4. Lead row

Compact row hierarchy:
- Customer name — primary
- Phone — secondary/stable identifier
- BHK + primary preferred location
- Budget max when known
- Status
- Priority
- EFPS source badge(s)
- Last interaction
- New activity / Needs Analysis marker

Customer name appears wherever known; phone is the fallback when unknown.

## 5. Inbox behavior

### Sorting
Default: latest customer activity first.

Alternates:
- Priority
- Follow-up due
- Recently created

### Filters
- EFPS source
- Classification / queue
- Lead status
- Priority
- BHK
- Location
- Follow-up state
- New activity / needs analysis

### Search
Searches without AI across:
- Customer name
- Phone
- BHK
- Preferred location
- Tags / notes
- Conversation text

The UI should indicate what field matched when that improves clarity.

### Operational counts
Use:
- Qualified Leads
- Review Queue
- Needs Attention
- Follow-ups Due
- New Activity

Avoid ambiguous raw totals as primary working metrics.

## 6. Duplicate handling

One logical customer is used when identity is confidently the same.

Multiple EFPS WhatsApp source numbers remain attached to that customer.

When identity is uncertain:
- Show Suspected Duplicate
- Offer Merge
- Offer Keep Separate
- Never silently merge

Merges and separations are auditable.

## 7. Reclassification

Reversible actions:
- Promote to Lead
- Send to Review
- Not a Lead
- Reclassify
- Restore / Undo where applicable

Every classification change creates an audit/activity record and preserves the prior state.

## 8. Reliability and observability

Global design rule:

**No silent failures.**

For loading:
- Skeleton UI

For no results:
- Explicit explanation
- Clear Filters or another relevant recovery action

For errors:
- Inline error banner
- Affected system/area
- Safe retry/recovery action

For stale data:
- Visible freshness timestamp/state

For processing:
- User-visible state when a failed or delayed process affects the operator
- Internal structured log for debugging
- Traceable activity/error context

The interface must not present stale or unavailable data as current.

## 9. Data-source map

| UI surface | Primary source | Supporting sources |
|---|---|---|
| Dashboard | Leads | Events, Conversations |
| Leads Inbox | Leads | latest Conversations, Lead Sources |
| Review Queue | Leads / classification | Conversations |
| Lead Overview | Leads | Conversations, Events, Lead Sources |
| Conversation | Conversations | Lead Sources, Webhook Events (future) |
| Requirements | Leads | Requirement History (future), AI Runs (future), message references |
| Property Matches | Inventory (future/verified) | Lead Property Matches (future), Leads |
| AI & Drafts | AI Runs + Reply Drafts (future) | Conversations, Leads, Inventory |
| Activity & History | Events | AI Runs, Reply Drafts, Requirement History, Webhook Events |
| Follow-ups | Leads | Events, Conversations |
| Inventory | Inventory (future/verified) | matching state |
| Activity | Events | Webhook Events, AI Runs, Reply Drafts |
| Settings | configuration | integration/auth metadata |
| WhatsApp Live (future) | Webhook Events | Conversations, Leads |

## 10. Data states shown by the UI

Every displayed value should be treated as one of:
- Verified source data
- Human-edited CRM data
- AI-derived proposal/analysis
- System status
- Illustrative design content

Design mockups use illustrative records only and must not be mistaken for live customers or live properties.


## 9. Lead workspace (D03 approved)

The individual lead workspace is a logical dedicated CRM workspace assembled from linked records; it is not a physical spreadsheet tab.

### Header
Name first when known; phone as stable identifier; direct WhatsApp action; EFPS source badge(s); classification; status; priority; last/new activity state.

### Conversation timeline
The chronological timeline is reconstructed from normalized conversation records. Each message carries its timestamp, direction, sender/source context, message type and body. Those stored timestamps create the date separators/grouping shown by the UI. All messages for that customer are retained and displayed within the lead's conversation context. Source WhatsApp attribution is preserved separately so one customer can span multiple EFPS source numbers.

AI-generated drafts are never written into the observed conversation stream.

### Historical coverage
Show first/latest available dates and a visible incomplete/partial-history state whenever completeness is not proven. Never label a limited extraction as the complete customer history.

### Requirements
Current requirement fields are editable. Unknown/unconfirmed values are explicit. Human edits become authoritative and are recorded in history.

### Provenance
Important values can be identified as Human, AI, Source-message-backed or System, with detail available on demand.

### Follow-up and activity
Follow-up state and the chronological activity/audit stream live in the workspace and are also surfaced in the global Follow-ups/Activity views.

### AI run persistence
Every future AI execution for a lead creates an immutable AI Run record. At minimum, the run records which lead was analyzed, when it ran, which message state/context version was examined, the prior AI-memory version used, structured findings/changes and any draft produced. Later AI calls use the saved state plus the newly available conversation delta and can identify exactly what work has happened since the previous run.

## 11. Lead workspace design (D03 proposal)

The D03 visual-review package proposes the following lead workspace behavior. These are design proposals until D03.1–D03.10 are approved in `CRM_DESIGN_DECISIONS.md`.

### Header
Customer name first (phone fallback), phone/direct WhatsApp, EFPS source badge(s), classification, status, priority and last-activity/new-activity state.

### Conversation
Chronological WhatsApp-style timeline with Incoming/Outgoing separation, time/date separators, source/sender attribution, message-type indicators, jump-to-latest and new-message state. AI drafts must never be rendered as actual conversation messages.

### Historical coverage
Show first and latest available message dates, known gaps/partial-window indicators and an explicit partial-history state when completeness is unproven.

### Requirements
Ordered current-state fields: BHK, preferred locations, budget min/max, furnishing, occupancy/tenant type, move-in date, pet preference, parking, requirement summary and notes. Unknown/unconfirmed values have explicit states.

### Provenance
Lightweight Human / AI / Source-message-backed / System indicators, with expandable detail.

### Editing
Inline edit with Save/Cancel. Human-edited values take precedence. Material changes can request confirmation. Manual edits do not require AI.

### Status, priority and follow-up
Compact dropdowns in the header; follow-up includes date/time, next action, overdue state, count, quick reschedule and note.

### Activity
Chronological audit timeline spanning human edits, classifications, status/priority changes, follow-ups, future AI runs/drafts, future property actions and system events.

### Merge/split
Advanced overflow action. Preview both records before merge, explicitly confirm, audit the result, preserve the original trail, and allow later split/reversal.

## 12. AI design — approved

The AI section is intentionally not finalized in D02. Its detailed design will be decided in Section D04 of the design register.

When finalized, the design must preserve:
- full raw conversation
- evolving customer intelligence
- requirement history
- AI run history
- reply draft history
- no unnecessary repeated AI calls
- human override precedence

## 12. Approved design status

### D01 — Navigation & information architecture
**6/6 approved**

### D02 — Inbox & qualification
**9/9 approved**

### D03 — Lead workspace
**10/10 approved**

### D04 — AI intelligence and reply drafting
Not yet reviewed

### D05 — Inventory
Not yet reviewed

### D06 — Live activity/webhooks
Not yet reviewed

### D07 — Privacy/operator control
Not yet reviewed

### D08 — Visual design system/final handoff
Not yet reviewed

## 13. Design handoff rule

This document is a UI specification, not an implementation specification.

Before implementation:
- complete the design decision register
- validate every proposed field against the live data
- validate the actual inventory schema
- resolve the synchronization/source-of-truth strategy
- convert approved Figma layouts into implementation work

Approval of a design item does not mean the feature exists.


## D04 approved design handoff — 2026-09-26
**D04.1–D04.8 APPROVED (8/8); design only, not implemented.** Supersedes the earlier ten-item D04 placeholder. D05 Inventory Experience remains proposed (0/7).
- [x] D04.1 AI workspace: previous runs, saved intelligence, new messages, latest draft; explicit AI actions only. No AI call on open, search, filter, manual edit or copy.
- [x] D04.2 First analysis: full relevant available conversation across linked EFPS numbers, human-confirmed values, source attribution, incomplete-history warning.
- [x] D04.3 Saved intelligence: versioned intelligence, append-only requirement changes and evidence, immutable AI runs, exact successfully analyzed message IDs and per-source cursor.
- [x] D04.4 Subsequent runs: saved intelligence + new message IDs + recent human edits + relevant older context; explicit full reanalysis; cursor advances only after durable commit.
- [x] D04.5 Requirement review: current/proposed side by side, source evidence, uncertainty, individual Accept/Reject/Edit, human authority and audit.
- [x] D04.6 Draft editor: versioned editable drafts, regenerate, save, approve, copy, discard, verified inventory references. Copy/open is not sent; sent needs observed outgoing message or explicit operator confirmation. No automatic send in v1.
- [x] D04.7 AI run and draft history: every attempt, including failures, analyzed message IDs, model/prompt, previous/resulting intelligence, output/error, draft version/status and usage when known.
- [x] D04.8 Failure/cost/recovery: visible processing, partial, failed, stale, retry states; correlation ID and idempotent retry; unknown provider cost is not zero; failure does not advance cursor; no silent failures.
Approved Figma: https://www.figma.com/design/PBiMGsVQ0fVpSf39WwNmKb?node-id=16-2 ; https://www.figma.com/design/PBiMGsVQ0fVpSf39WwNmKb?node-id=20-2 . Field maps: node-id=16-110 and node-id=20-164 in the same file. Illustrative records are not live data.
Existing repository Leads, Conversations and Events are documented. Proposed Lead Sources, Customer Intelligence, Requirement History, AI Runs, Reply Drafts, Webhook Events, Inventory and Lead Property Matches require schema/live-data audit. Preserve EFPS source per message. Live inventory schema and rows remain unverified.
Deployment boundary: repo zeidhussain9-cloud/easyfind-website, Render leads-ui-dashboard, deployed branch feature/leads-automation, root leads_automation/leads-ui. Design branch feature/leads-crm-architecture. Do not merge CRM into main. Documentation changes do not implement functionality.
D05 preview pending approval: D05.1 global Inventory + per-lead Matches; D05.2 verified match cards; D05.3 mandatory/flexible/unknown criteria; D05.4 manual pin/exclude/override with reason; D05.5 freshness; D05.6 verified share preparation; D05.7 lead property history.
