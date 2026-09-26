# EasyFind CRM — UI Design Specification

**Status:** Design in progress; D01 and D02 approved  
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

## 12. AI design placeholder

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
10 decisions — **visual review in progress**

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
