# 🏗️ System Architecture

Comprehensive architectural documentation for the EasyFind Lead Management System.

## 📋 Table of Contents

- [System Overview](#system-overview)
- [Architecture Layers](#architecture-layers)
- [Data Flow](#data-flow)
- [Component Diagrams](#component-diagrams)
- [Technology Stack](#technology-stack)
- [Database Design](#database-design)
- [API Architecture](#api-architecture)
- [Security Architecture](#security-architecture)
- [Scalability Considerations](#scalability-considerations)
- [Integration Points](#integration-points)

## 🎯 System Overview

The EasyFind Lead Management System is a **multi-tier application** designed for real estate lead tracking and management using AI-powered classification.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         PRESENTATION LAYER                       │
│                    (React Dashboard + Material-UI)               │
└───────────────────────────────┬─────────────────────────────────┘
                                │ HTTP/REST
┌───────────────────────────────▼─────────────────────────────────┐
│                      APPLICATION LAYER                           │
│                   (Express.js API Server)                        │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    ▼                       ▼
┌────────────────────────────┐  ┌─────────────────────────────┐
│   DATA LAYER (Sheets)      │  │   PROCESSING LAYER          │
│   Google Sheets API        │  │   Python Scripts            │
│   (Cloud Storage)          │  │   - Extraction              │
└────────────────────────────┘  │   - Classification (AI)     │
                                │   - Database Import         │
                                │   - Sync                    │
                                └─────────────┬───────────────┘
                                              │
                                              ▼
                                ┌──────────────────────────┐
                                │  DATA PERSISTENCE        │
                                │  SQLite (Local)          │
                                └──────────────────────────┘
```

## 🏛️ Architecture Layers

### 1. Presentation Layer

**Technology:** React 18.2, Material-UI 5.14

**Components:**
- Dashboard (main view)
- LeadsList (table/cards view)
- LeadDetails (individual lead view)
- ConversationView (message history)
- Statistics (charts and metrics)

**Responsibilities:**
- User interface rendering
- User interaction handling
- State management
- API calls to backend
- Real-time data updates

### 2. Application Layer

**Technology:** Node.js 18+, Express.js 4.18

**Components:**
- HTTP server (Express)
- REST API endpoints
- Google Sheets service layer
- Request validation
- Error handling middleware
- CORS configuration

**Responsibilities:**
- Handle HTTP requests
- Route to appropriate handlers
- Authenticate with Google Sheets
- Transform data for frontend
- Error handling and logging

### 3. Data Layer

**Technology:** Google Sheets API, SQLite 3

**Components:**
- Google Sheets (cloud storage)
- SQLite database (local storage)
- gspread library (Python)
- google-auth (authentication)

**Responsibilities:**
- Persist lead data
- Persist conversation history
- Provide query interface
- Handle concurrent access
- Data backup and recovery

### 4. Processing Layer

**Technology:** Python 3.12+, AWS Bedrock, Google Gemini

**Components:**
- WhatsApp extraction (`extract_whatsapp.py`)
- AI classification (`classify_with_bedrock.py`)
- Database import (`import_to_database_v2.py`)
- Sheets sync (`sync_to_sheet_v2.py`)
- Bulk operations (`bulk_assign_collections.py`)

**Responsibilities:**
- Extract WhatsApp data
- Classify leads with AI
- Import to database
- Sync to Google Sheets
- Data transformations

## 🔄 Data Flow

### End-to-End Flow

```
┌──────────────────┐
│ WhatsApp Backup  │
│ (msgstore.db)    │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────┐
│ Step 1: Extraction           │
│ extract_whatsapp.py          │
│ Output: JSON files           │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ Step 2: AI Classification    │
│ classify_with_bedrock.py     │
│ AWS Bedrock (Claude)         │
│ Output: Classified JSON      │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ Step 3: Database Import      │
│ import_to_database_v2.py     │
│ Output: leads.db (SQLite)    │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ Step 4: Sheets Sync          │
│ sync_to_sheet_v2.py          │
│ Output: Google Sheets        │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ Step 5: Dashboard Display    │
│ React UI reads from Sheets   │
│ via Express API              │
└──────────────────────────────┘
```

### Real-time Data Flow

```
User Action (Dashboard)
       │
       ▼
React Component
       │
       ▼
Axios HTTP Request
       │
       ▼
Express API Endpoint
       │
       ▼
Google Sheets Service
       │
       ▼
Google Sheets API
       │
       ▼
Google Sheets (Cloud)
       │
       ▼
Response Data
       │
       ▼
Express Response
       │
       ▼
React State Update
       │
       ▼
UI Re-render
```

## 📊 Component Diagrams

### Lead Classification Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    Classification Pipeline                       │
└─────────────────────────────────────────────────────────────────┘

Input: Conversation Object
    │
    ▼
┌────────────────────┐
│  Phone Number      │ ──────────┐
│  Validation        │           │
└─────────┬──────────┘           │
          │                      │
          ▼                      │
┌────────────────────┐           │
│  Rule-Based        │           │
│  Classification    │           │
│  (Tier 1)          │           │
└─────────┬──────────┘           │
          │                      │
    ┌─────┴─────┐                │
    │ Matched?  │                │
    └─────┬─────┘                │
          │                      │
     NO   │   YES                │
    ┌─────┴────┐                 │
    │          ▼                 │
    │    Return Result           │
    │                            │
    ▼                            │
┌────────────────────┐           │
│  AI Classification │           │
│  (Tier 2)          │           │
│  - Bedrock Claude  │           │
│  - Gemini          │           │
└─────────┬──────────┘           │
          │                      │
          ▼                      │
┌────────────────────┐           │
│  Extract Entities  │           │
│  - Intent          │           │
│  - Requirements    │           │
│  - Sentiment       │           │
└─────────┬──────────┘           │
          │                      │
          ▼                      │
┌────────────────────┐           │
│  Confidence Score  │           │
│  Calculation       │           │
└─────────┬──────────┘           │
          │                      │
          ▼                      │
    Return Full Result ◄─────────┘
```

### Google Sheets Integration

```
┌─────────────────────────────────────────────────────────────────┐
│                  Google Sheets Integration                       │
└─────────────────────────────────────────────────────────────────┘

┌────────────────────┐
│ Service Account    │
│ JSON Key           │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ OAuth 2.0          │
│ Authentication     │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ gspread Library    │
│ (Python)           │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Google Sheets API  │
│ v4                 │
└─────────┬──────────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
┌────────┐  ┌────────┐
│ Read   │  │ Write  │
│ Data   │  │ Data   │
└────────┘  └────────┘
```

## 💻 Technology Stack

### Frontend

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Framework | React | 18.2 | UI library |
| Component Library | Material-UI | 5.14 | UI components |
| State Management | React Hooks | Built-in | Local state |
| HTTP Client | Axios | 1.6 | API calls |
| Routing | React Router | 6.20 | Navigation |
| Charts | Recharts | 2.10 | Visualizations |

### Backend

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Runtime | Node.js | 18+ | JavaScript runtime |
| Framework | Express | 4.18 | Web server |
| Google Sheets | gspread (Python) | 6.1 | Sheets integration |
| Auth | google-auth-library | 9.4 | OAuth 2.0 |

### Data Processing

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Language | Python | 3.12+ | Processing scripts |
| Database | SQLite | 3 | Local storage |
| AI (Option 1) | AWS Bedrock | Latest | Claude AI |
| AI (Option 2) | Google Gemini | Latest | Gemini AI |
| WhatsApp | whatsapp-chat-exporter | 0.9+ | Extraction |

### Infrastructure

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Hosting | Render.com | Web deployment |
| Database | Google Sheets | Cloud storage |
| Version Control | Git/GitHub | Code repository |
| CI/CD | Render Auto-Deploy | Continuous deployment |

## 🗄️ Database Design

### SQLite Schema

**Tables:**

1. **leads** (Master Lead Registry)
```sql
CREATE TABLE leads (
    phone_number TEXT PRIMARY KEY,
    customer_name TEXT,
    lead_status TEXT DEFAULT 'New',
    lead_source TEXT DEFAULT 'WhatsApp',
    priority TEXT DEFAULT 'Medium',
    current_requirement TEXT,
    bhk_requirement TEXT,
    preferred_location TEXT,
    budget_min INTEGER,
    budget_max INTEGER,
    furnishing_preference TEXT,
    occupancy_type TEXT,
    pet_preference TEXT,
    parking_required TEXT,
    move_in_date TEXT,
    matched_properties TEXT,  -- JSON array
    last_interaction_date TEXT,
    next_followup_date TEXT,
    followup_count INTEGER DEFAULT 0,
    tags TEXT,  -- JSON array
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

2. **conversations** (Message Log)
```sql
CREATE TABLE conversations (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone_number TEXT NOT NULL,
    direction TEXT NOT NULL,  -- 'Incoming' or 'Outgoing'
    message_body TEXT NOT NULL,
    message_type TEXT DEFAULT 'text',
    media_urls TEXT,  -- JSON array
    media_filenames TEXT,  -- JSON array
    sender_name TEXT,
    timestamp TEXT NOT NULL,
    replied_to_id INTEGER,
    is_processed BOOLEAN DEFAULT 0,
    extracted_intent TEXT,
    extracted_entities TEXT,  -- JSON object
    sentiment TEXT,
    requires_followup BOOLEAN DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    processed_at TEXT,
    FOREIGN KEY (phone_number) REFERENCES leads(phone_number)
);
```

3. **lead_lifecycle_events** (Audit Trail)
```sql
CREATE TABLE lead_lifecycle_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone_number TEXT NOT NULL,
    event_type TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    event_description TEXT,
    created_by TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (phone_number) REFERENCES leads(phone_number)
);
```

**Indexes:**
- `idx_leads_status` on `leads(lead_status)`
- `idx_leads_priority` on `leads(priority)`
- `idx_leads_followup` on `leads(next_followup_date)`
- `idx_leads_location` on `leads(preferred_location)`
- `idx_conversations_phone` on `conversations(phone_number)`
- `idx_conversations_timestamp` on `conversations(timestamp)`
- `idx_events_phone` on `lead_lifecycle_events(phone_number)`

### Google Sheets Schema

**Tab 1: Leads** (23 columns)
- Same structure as `leads` table
- Real-time sync from SQLite
- Edited fields sync back to SQLite

**Tab 2: Conversations** (17 columns)
- Same structure as `conversations` table
- Append-only log
- Used for conversation history view

**Tab 3: Events** (9 columns)
- Same structure as `lead_lifecycle_events` table
- Audit trail for changes

## 🔌 API Architecture

### REST API Design

**Principles:**
- RESTful endpoints
- JSON request/response
- HTTP status codes
- Error handling middleware
- CORS support

**Endpoint Structure:**
```
/api/leads              - GET (list), POST (create)
/api/leads/:phone       - GET (retrieve), PUT (update), DELETE (remove)
/api/conversations/:phone - GET (list messages)
/api/stats              - GET (aggregated statistics)
/health                 - GET (health check)
```

**Response Format:**
```json
{
  "data": { },
  "meta": {
    "total": 150,
    "page": 1,
    "limit": 50
  },
  "timestamp": "2026-09-26T14:30:00Z"
}
```

**Error Format:**
```json
{
  "error": "Error description",
  "code": "ERROR_CODE",
  "details": { },
  "timestamp": "2026-09-26T14:30:00Z"
}
```

## 🔒 Security Architecture

### Authentication

**Google Sheets:**
- Service account authentication
- OAuth 2.0
- JSON Web Tokens (JWT)
- Scoped permissions

**Future: User Authentication**
- JWT tokens
- Session management
- Role-based access control (RBAC)

### Data Security

**At Rest:**
- SQLite database encryption (optional)
- Encrypted service account keys
- Environment variables for secrets

**In Transit:**
- HTTPS only (enforced by Render)
- TLS 1.2+
- Secure headers (CORS, CSP)

**Access Control:**
- Service account with minimal permissions
- Sheet-level sharing controls
- API key rotation

### Best Practices

1. **Never commit credentials** - Use `.env` files
2. **Rotate API keys** - Quarterly rotation
3. **Principle of least privilege** - Minimal permissions
4. **Audit logging** - Track all changes
5. **Input validation** - Sanitize user input
6. **Rate limiting** - Prevent abuse

## 📈 Scalability Considerations

### Current Architecture (Free Tier)

**Limits:**
- Google Sheets API: 500 requests/100 seconds
- Render Free: 750 hours/month
- SQLite: Single file, limited concurrency

**Suitable for:**
- Up to 1,000 leads
- Up to 10,000 conversations
- Small team (< 5 users)
- Low traffic (< 1,000 requests/day)

### Scaling Strategy

**Phase 1: Optimize Current Stack**
1. Implement caching (Redis)
2. Batch Google Sheets operations
3. Add database indexes
4. Optimize queries

**Phase 2: Horizontal Scaling**
1. Load balancer (multiple Render instances)
2. Read replicas for database
3. CDN for static assets
4. Background job queue

**Phase 3: Migrate to Scalable Architecture**
1. Replace SQLite with PostgreSQL/MySQL
2. Migrate to AWS/GCP infrastructure
3. Implement microservices
4. Add message queue (RabbitMQ/SQS)
5. Implement caching layer (Redis/Memcached)

## 🔗 Integration Points

### External Services

| Service | Purpose | Protocol |
|---------|---------|----------|
| Google Sheets API | Data storage | REST/HTTP |
| AWS Bedrock | AI classification | REST/HTTP |
| Google Gemini | AI classification | REST/HTTP |
| WhatsApp | Data source | File extraction |
| Render.com | Hosting | Web deployment |

### Integration Patterns

**Google Sheets:**
- Pull pattern (read on demand)
- Push pattern (write on change)
- Batch updates (bulk operations)

**AI Services:**
- Request-response pattern
- Retry with exponential backoff
- Circuit breaker for failures

**WhatsApp:**
- File-based extraction
- Scheduled processing
- Manual trigger

## 🏗️ Future Architecture

### Planned Enhancements

1. **Real-time Sync**
   - WebSocket connections
   - Live updates
   - Collaborative editing

2. **Advanced Analytics**
   - Machine learning models
   - Predictive lead scoring
   - Trend analysis

3. **Mobile App**
   - React Native
   - Native iOS/Android
   - Offline support

4. **Workflow Automation**
   - Automated follow-ups
   - Email notifications
   - SMS integration

5. **CRM Integration**
   - Salesforce connector
   - HubSpot integration
   - Zapier webhooks

---

**Document Version:** 1.0  
**Last Updated:** September 26, 2026  
**Maintained By:** EasyFind Development Team
