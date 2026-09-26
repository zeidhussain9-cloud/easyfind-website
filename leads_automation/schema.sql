-- ============================================================================
-- EASYFIND LEAD MANAGEMENT SYSTEM - DATABASE SCHEMA
-- ============================================================================
-- Created: 2026-09-23
-- Purpose: Track WhatsApp leads from extraction to conversion
-- Tables: leads, conversations, lead_lifecycle_events
-- ============================================================================

-- ============================================================================
-- TABLE 1: LEADS (Master Lead Registry)
-- ============================================================================
-- One row per unique phone number
-- Stores current state, requirements, and tracking metadata
-- ============================================================================

CREATE TABLE IF NOT EXISTS leads (
    -- Primary Identifier
    phone_number TEXT PRIMARY KEY,           -- Normalized: +919876543210 (with country code)

    -- Contact Information
    customer_name TEXT,                      -- "Ravi Kumar" or NULL if unknown

    -- Lead Status & Classification
    lead_status TEXT DEFAULT 'New',          -- 'New', 'Active', 'Matched', 'No Match', 'Lost', 'Converted'
    lead_source TEXT DEFAULT 'WhatsApp',     -- 'WhatsApp', 'Referral', 'Website', 'Walk-in'
    priority TEXT DEFAULT 'Medium',          -- 'High', 'Medium', 'Low'

    -- Property Requirements (AI-Extracted)
    current_requirement TEXT,                -- Free-form: "2 BHK in Baner under 25K with parking"
    bhk_requirement TEXT,                    -- "1 RK", "1 BHK", "2 BHK", "3 BHK", etc.
    preferred_location TEXT,                 -- "Baner", "Hinjewadi", "Wakad" (comma-separated if multiple)
    budget_min INTEGER,                      -- Minimum monthly rent (in INR)
    budget_max INTEGER,                      -- Maximum monthly rent (in INR)
    furnishing_preference TEXT,              -- "Fully Furnished", "Semi Furnished", "Unfurnished"
    occupancy_type TEXT,                     -- "Family", "Bachelor", "Corporate", "Any"
    pet_preference TEXT,                     -- "Yes", "No", "Negotiable"
    parking_required TEXT,                   -- "Yes", "No", "Preferred"
    move_in_date TEXT,                       -- ISO-8601: "2026-10-15" or "Immediate"

    -- Matching & Follow-up
    matched_properties TEXT,                 -- JSON array: ["EF-2609-FFEB", "EF-2609-WVPB"]
    last_interaction_date TEXT,              -- ISO-8601: "2026-09-22T18:30:00"
    next_followup_date TEXT,                 -- ISO-8601: "2026-09-25T10:00:00"
    followup_count INTEGER DEFAULT 0,        -- How many times followed up

    -- Metadata
    tags TEXT,                               -- JSON array: ["urgent", "corporate", "hot_lead"]
    notes TEXT,                              -- Free-form notes (human or AI-generated)
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(lead_status);
CREATE INDEX IF NOT EXISTS idx_leads_priority ON leads(priority);
CREATE INDEX IF NOT EXISTS idx_leads_followup ON leads(next_followup_date);
CREATE INDEX IF NOT EXISTS idx_leads_location ON leads(preferred_location);
CREATE INDEX IF NOT EXISTS idx_leads_created ON leads(created_at);

-- ============================================================================
-- TABLE 2: CONVERSATIONS (Complete Message Log)
-- ============================================================================
-- Every WhatsApp message (incoming/outgoing) with full context
-- Used for AI analysis, conversation reconstruction, and audit trail
-- ============================================================================

CREATE TABLE IF NOT EXISTS conversations (
    -- Primary Key
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Message Ownership
    phone_number TEXT NOT NULL,              -- Links to leads(phone_number)

    -- Message Content
    direction TEXT NOT NULL,                 -- 'Incoming' (from customer) or 'Outgoing' (from you)
    message_body TEXT NOT NULL,              -- Raw message text (UTF-8, preserves emojis)
    message_type TEXT DEFAULT 'text',        -- 'text', 'image', 'audio', 'video', 'document', 'location', 'contact'
    media_urls TEXT,                         -- JSON array: ["https://...", "https://..."]
    media_filenames TEXT,                    -- JSON array: ["IMG_1234.jpg", "document.pdf"]

    -- Message Metadata
    sender_name TEXT,                        -- "Ravi Kumar" or "Zeid" or "You"
    timestamp TEXT NOT NULL,                 -- ISO-8601: "2026-09-22T18:30:00"
    replied_to_id INTEGER,                   -- Foreign key to another message_id (for threaded replies)

    -- AI Processing
    is_processed BOOLEAN DEFAULT 0,          -- 0 = not analyzed yet, 1 = analyzed by LLM
    extracted_intent TEXT,                   -- "Looking for property", "Follow-up inquiry", "Price negotiation"
    extracted_entities TEXT,                 -- JSON: {"bhk": "2 BHK", "location": "Baner", "budget": 25000}
    sentiment TEXT,                          -- 'Positive', 'Neutral', 'Negative', 'Urgent'
    requires_followup BOOLEAN DEFAULT 0,     -- 1 = needs response from you

    -- Timestamps
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    processed_at TEXT,                       -- When AI analyzed this message

    -- Foreign Keys
    FOREIGN KEY (phone_number) REFERENCES leads(phone_number) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_conv_phone ON conversations(phone_number);
CREATE INDEX IF NOT EXISTS idx_conv_timestamp ON conversations(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_conv_direction ON conversations(direction);
CREATE INDEX IF NOT EXISTS idx_conv_unprocessed ON conversations(is_processed) WHERE is_processed = 0;
CREATE INDEX IF NOT EXISTS idx_conv_followup ON conversations(requires_followup) WHERE requires_followup = 1;

-- ============================================================================
-- TABLE 3: LEAD_LIFECYCLE_EVENTS (Audit Trail)
-- ============================================================================
-- Every status change, action taken, or system event
-- Provides complete history of what happened and why
-- ============================================================================

CREATE TABLE IF NOT EXISTS lead_lifecycle_events (
    -- Primary Key
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Event Ownership
    phone_number TEXT NOT NULL,              -- Links to leads(phone_number)

    -- Event Details
    event_type TEXT NOT NULL,                -- 'status_change', 'property_matched', 'followup_scheduled',
                                              -- 'reminder_sent', 'message_sent', 'requirement_updated'
    event_description TEXT NOT NULL,         -- Human-readable: "Status changed from New to Active"

    -- Event Context
    triggered_by TEXT DEFAULT 'AI',          -- 'AI', 'Manual', 'System', 'Scheduled Task', 'User (Zeid)'
    metadata TEXT,                           -- JSON: {"old_status": "New", "new_status": "Active", "reason": "Customer replied"}

    -- Related References
    related_message_id INTEGER,              -- Links to conversations(message_id) if applicable
    related_property_id TEXT,                -- "EF-2609-FFEB" if event relates to a property

    -- Timestamp
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Keys
    FOREIGN KEY (phone_number) REFERENCES leads(phone_number) ON DELETE CASCADE,
    FOREIGN KEY (related_message_id) REFERENCES conversations(message_id) ON DELETE SET NULL
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_events_phone ON lead_lifecycle_events(phone_number);
CREATE INDEX IF NOT EXISTS idx_events_type ON lead_lifecycle_events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON lead_lifecycle_events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_events_triggered_by ON lead_lifecycle_events(triggered_by);

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: Active Leads with Last Conversation
CREATE VIEW IF NOT EXISTS v_active_leads AS
SELECT
    l.*,
    (SELECT message_body FROM conversations
     WHERE phone_number = l.phone_number
     ORDER BY timestamp DESC LIMIT 1) as last_message,
    (SELECT timestamp FROM conversations
     WHERE phone_number = l.phone_number
     ORDER BY timestamp DESC LIMIT 1) as last_message_time,
    (SELECT COUNT(*) FROM conversations
     WHERE phone_number = l.phone_number) as message_count
FROM leads l
WHERE l.lead_status IN ('New', 'Active', 'Matched');

-- View: Leads Requiring Follow-up Today
CREATE VIEW IF NOT EXISTS v_followup_today AS
SELECT
    l.*,
    (SELECT COUNT(*) FROM conversations
     WHERE phone_number = l.phone_number AND direction = 'Outgoing') as outgoing_count
FROM leads l
WHERE DATE(l.next_followup_date) <= DATE('now')
  AND l.lead_status NOT IN ('Lost', 'Converted');

-- View: Recent Lifecycle Events (Last 7 Days)
CREATE VIEW IF NOT EXISTS v_recent_events AS
SELECT
    e.*,
    l.customer_name,
    l.lead_status
FROM lead_lifecycle_events e
JOIN leads l ON e.phone_number = l.phone_number
WHERE DATE(e.timestamp) >= DATE('now', '-7 days')
ORDER BY e.timestamp DESC;

-- ============================================================================
-- TRIGGERS FOR AUTOMATIC TIMESTAMP UPDATES
-- ============================================================================

-- Trigger: Update leads.updated_at on any change
CREATE TRIGGER IF NOT EXISTS trigger_leads_updated_at
AFTER UPDATE ON leads
FOR EACH ROW
BEGIN
    UPDATE leads SET updated_at = CURRENT_TIMESTAMP WHERE phone_number = NEW.phone_number;
END;

-- Trigger: Auto-create lifecycle event on status change
CREATE TRIGGER IF NOT EXISTS trigger_status_change_event
AFTER UPDATE OF lead_status ON leads
FOR EACH ROW
WHEN OLD.lead_status != NEW.lead_status
BEGIN
    INSERT INTO lead_lifecycle_events (phone_number, event_type, event_description, triggered_by, metadata)
    VALUES (
        NEW.phone_number,
        'status_change',
        'Status changed from ' || OLD.lead_status || ' to ' || NEW.lead_status,
        'System',
        json_object('old_status', OLD.lead_status, 'new_status', NEW.lead_status)
    );
END;

-- ============================================================================
-- INITIAL DATA VALIDATION CONSTRAINTS
-- ============================================================================

-- Ensure lead_status has valid values
CREATE TRIGGER IF NOT EXISTS validate_lead_status
BEFORE INSERT ON leads
FOR EACH ROW
WHEN NEW.lead_status NOT IN ('New', 'Active', 'Matched', 'No Match', 'Lost', 'Converted')
BEGIN
    SELECT RAISE(ABORT, 'Invalid lead_status. Must be: New, Active, Matched, No Match, Lost, or Converted');
END;

-- Ensure direction has valid values
CREATE TRIGGER IF NOT EXISTS validate_conversation_direction
BEFORE INSERT ON conversations
FOR EACH ROW
WHEN NEW.direction NOT IN ('Incoming', 'Outgoing')
BEGIN
    SELECT RAISE(ABORT, 'Invalid direction. Must be: Incoming or Outgoing');
END;

-- ============================================================================
-- SCHEMA VERSION TRACKING
-- ============================================================================

CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

INSERT OR IGNORE INTO schema_version (version, description)
VALUES (1, 'Initial schema: leads, conversations, lead_lifecycle_events');

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
