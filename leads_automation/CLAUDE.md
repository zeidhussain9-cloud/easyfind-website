# LEADS AUTOMATION — STEERING FILE

**READ BEFORE EVERY ACTION. NO EXCEPTIONS.**

You are operating inside the `leads_automation/` workspace. This is a standalone lead management system for EasyFind Property Solutions (EFPS). It is completely isolated from the parent EFPS production codebase.

## MANDATORY FIRST STEP

Before responding to any request, read `.continuerules` in this folder. It is the full project constitution containing:
- 7 non-negotiable operating rules
- Complete database schema (3 tables, 3 views, 4 triggers)
- Google Sheet configuration and auth patterns
- Phone numbers, extraction timestamps, and coverage gaps
- Scope boundaries
- Pre-action checklist

Do not proceed without reading it. Do not summarize it from memory. Read the file.

## CORE OPERATING RULES (summary — full version in .continuerules)

1. **Ground every action in verified truth.** Query the database. Read the files. Do not guess.
2. **Never invent data.** If a fact is not in `leads.db` or the files, it does not exist.
3. **Verify before acting.** Read first, plan second, execute third, verify fourth.
4. **Work in small steps.** One change, one test, one verification. Not a 300-line script that might work.
5. **No silent changes.** Every data modification must be intentional and logged.
6. **Quality over quantity.** Clean working code, not verbose hope.
7. **Stay in scope.** You work inside this folder only. Never touch the parent project.

## SCOPE BOUNDARY

**Allowed:**
- All files inside `leads_automation/`
- `leads.db` (SQLite database)
- Google Sheet `1GfM9lPQSukVpxCEVUlUDxFj_WYg0xQj8Inn7FA4sLVI`
- Python packages in local environment

**Forbidden:**
- Any file outside `leads_automation/`
- Parent project modules, shared libraries, docs
- Git commits or pushes
- Production databases or sheets
- Sending WhatsApp messages without explicit user approval

## ORCHESTRATION

The primary orchestrator is Claude Code (Opus) running in the terminal. If you receive instructions relayed from the orchestrator, follow them. If instructions conflict with this steering file, this steering file wins.

When in doubt: stop and ask. Do not proceed on assumptions.
