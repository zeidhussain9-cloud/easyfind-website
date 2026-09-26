# 📡 API Documentation

Complete API reference for the EasyFind Lead Management System backend.

## 📋 Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Base URL](#base-url)
- [REST API Endpoints](#rest-api-endpoints)
- [Data Models](#data-models)
- [Google Sheets API Integration](#google-sheets-api-integration)
- [Python Scripts API](#python-scripts-api)
- [Error Handling](#error-handling)
- [Rate Limits](#rate-limits)
- [Examples](#examples)

## 🎯 Overview

The API consists of two layers:

1. **Express REST API** - Node.js backend serving the React dashboard
2. **Python Scripts** - Backend processing scripts for data extraction, classification, and sync

### API Architecture

```
┌─────────────────┐
│  React Frontend │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│  Express Server │ ← server.js (Port 5000/10000)
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  Google Sheets API      │ ← gspreadService.js
│  (via Service Account)  │
└─────────────────────────┘

┌─────────────────┐
│ Python Scripts  │ ← Classification, Extraction, Sync
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  SQLite (local) │ ← leads.db
└─────────────────┘
```

## 🔐 Authentication

### Express API

Currently uses **Google Service Account** authentication for Sheets API.

**Authentication Flow:**
1. Service account JSON key stored as environment variable
2. Backend authenticates with Google Sheets API
3. Frontend calls backend API (no auth required for frontend)

**Future:** Implement user authentication with JWT tokens.

### Python Scripts

**Google Sheets:**
- Service account authentication via `GOOGLE_APPLICATION_CREDENTIALS`

**AWS Bedrock (optional):**
- AWS credentials via environment variables or `~/.aws/credentials`

**Google Gemini (optional):**
- API key via `GOOGLE_API_KEY` environment variable

## 🌐 Base URL

### Local Development
```
http://localhost:5000
```

### Production (Render)
```
https://your-service.onrender.com
```

## 🛣️ REST API Endpoints

### 1. Get All Leads

Retrieve all leads from Google Sheets.

**Endpoint:**
```
GET /api/leads
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status` | string | No | Filter by lead status |
| `priority` | string | No | Filter by priority (High/Medium/Low) |
| `limit` | integer | No | Max results (default: 100) |
| `offset` | integer | No | Pagination offset |

**Response:**
```json
{
  "data": [
    {
      "phone_number": "+919876543210",
      "customer_name": "Ravi Kumar",
      "lead_status": "Active",
      "lead_source": "WhatsApp",
      "priority": "High",
      "current_requirement": "2 BHK in Baner under 25K",
      "bhk_requirement": "2 BHK",
      "preferred_location": "Baner",
      "budget_min": 20000,
      "budget_max": 25000,
      "furnishing_preference": "Fully Furnished",
      "occupancy_type": "Family",
      "pet_preference": "No",
      "parking_required": "Yes",
      "move_in_date": "2026-10-15",
      "matched_properties": ["EF-2609-FFEB", "EF-2609-WVPB"],
      "last_interaction_date": "2026-09-22T18:30:00",
      "next_followup_date": "2026-09-25T10:00:00",
      "followup_count": 3,
      "tags": ["urgent", "hot_lead"],
      "notes": "Customer very interested in Baner properties",
      "created_at": "2026-09-01T10:00:00",
      "updated_at": "2026-09-22T18:30:00"
    }
  ],
  "total": 150,
  "page": 1,
  "limit": 100
}
```

**Status Codes:**
- `200` - Success
- `500` - Server error (Google Sheets API failure)

---

### 2. Get Lead by Phone Number

Retrieve a specific lead's details.

**Endpoint:**
```
GET /api/leads/:phoneNumber
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `phoneNumber` | string | Yes | Phone number (URL encoded) |

**Example:**
```
GET /api/leads/%2B919876543210
```

**Response:**
```json
{
  "phone_number": "+919876543210",
  "customer_name": "Ravi Kumar",
  "lead_status": "Active",
  "priority": "High",
  "current_requirement": "2 BHK in Baner under 25K",
  "bhk_requirement": "2 BHK",
  "preferred_location": "Baner",
  "budget_min": 20000,
  "budget_max": 25000,
  "last_interaction_date": "2026-09-22T18:30:00",
  "next_followup_date": "2026-09-25T10:00:00",
  "created_at": "2026-09-01T10:00:00",
  "updated_at": "2026-09-22T18:30:00"
}
```

**Status Codes:**
- `200` - Success
- `404` - Lead not found
- `500` - Server error

---

### 3. Get Conversations

Retrieve all conversations for a specific phone number.

**Endpoint:**
```
GET /api/conversations/:phoneNumber
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `phoneNumber` | string | Yes | Phone number (URL encoded) |

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | integer | No | Max messages to return (default: 50) |
| `offset` | integer | No | Pagination offset |
| `direction` | string | No | Filter by direction (Incoming/Outgoing) |

**Example:**
```
GET /api/conversations/%2B919876543210?limit=20&direction=Incoming
```

**Response:**
```json
{
  "phone_number": "+919876543210",
  "conversations": [
    {
      "message_id": 1234,
      "direction": "Incoming",
      "message_body": "Hi, I'm looking for a 2 BHK in Baner",
      "message_type": "text",
      "sender_name": "Ravi Kumar",
      "timestamp": "2026-09-22T18:30:00",
      "is_processed": true,
      "extracted_intent": "Looking for property",
      "extracted_entities": {
        "bhk": "2 BHK",
        "location": "Baner"
      },
      "sentiment": "Positive",
      "requires_followup": false
    },
    {
      "message_id": 1235,
      "direction": "Outgoing",
      "message_body": "Sure! I have some great options in Baner. What's your budget?",
      "message_type": "text",
      "sender_name": "You",
      "timestamp": "2026-09-22T18:35:00",
      "is_processed": true
    }
  ],
  "total": 45,
  "page": 1,
  "limit": 20
}
```

**Status Codes:**
- `200` - Success
- `404` - No conversations found
- `500` - Server error

---

### 4. Update Lead Status

Update the status of a lead.

**Endpoint:**
```
POST /api/leads/:phoneNumber/status
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `phoneNumber` | string | Yes | Phone number (URL encoded) |

**Request Body:**
```json
{
  "status": "Converted",
  "notes": "Customer signed the lease agreement"
}
```

**Response:**
```json
{
  "success": true,
  "phone_number": "+919876543210",
  "old_status": "Active",
  "new_status": "Converted",
  "updated_at": "2026-09-26T14:30:00"
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid status value
- `404` - Lead not found
- `500` - Server error

**Valid Status Values:**
- `New`
- `Active`
- `Matched`
- `No Match`
- `Lost`
- `Converted`

---

### 5. Update Lead Priority

Update the priority of a lead.

**Endpoint:**
```
POST /api/leads/:phoneNumber/priority
```

**Request Body:**
```json
{
  "priority": "High"
}
```

**Valid Priority Values:**
- `High`
- `Medium`
- `Low`

**Response:**
```json
{
  "success": true,
  "phone_number": "+919876543210",
  "priority": "High"
}
```

---

### 6. Get Lead Statistics

Get aggregated statistics for all leads.

**Endpoint:**
```
GET /api/stats
```

**Response:**
```json
{
  "total_leads": 150,
  "by_status": {
    "New": 30,
    "Active": 60,
    "Matched": 25,
    "No Match": 15,
    "Lost": 10,
    "Converted": 10
  },
  "by_priority": {
    "High": 45,
    "Medium": 75,
    "Low": 30
  },
  "followup_today": 12,
  "active_conversations": 85,
  "conversion_rate": 0.067
}
```

---

### 7. Health Check

Check if the API server is running.

**Endpoint:**
```
GET /health
```

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2026-09-26T14:30:00Z",
  "uptime": 86400,
  "memory": {
    "rss": 50331648,
    "heapTotal": 20971520,
    "heapUsed": 15728640
  },
  "google_sheets_connected": true
}
```

---

## 📊 Data Models

### Lead Model

```typescript
interface Lead {
  // Primary Identifier
  phone_number: string;              // E.164 format: +919876543210
  
  // Contact Information
  customer_name: string | null;
  
  // Lead Status & Classification
  lead_status: 'New' | 'Active' | 'Matched' | 'No Match' | 'Lost' | 'Converted';
  lead_source: 'WhatsApp' | 'Referral' | 'Website' | 'Walk-in';
  priority: 'High' | 'Medium' | 'Low';
  
  // Property Requirements
  current_requirement: string | null;
  bhk_requirement: string | null;     // "1 RK", "1 BHK", "2 BHK", etc.
  preferred_location: string | null;  // Comma-separated if multiple
  budget_min: number | null;          // Monthly rent in INR
  budget_max: number | null;
  furnishing_preference: 'Fully Furnished' | 'Semi Furnished' | 'Unfurnished' | null;
  occupancy_type: 'Family' | 'Bachelor' | 'Corporate' | 'Any' | null;
  pet_preference: 'Yes' | 'No' | 'Negotiable' | null;
  parking_required: 'Yes' | 'No' | 'Preferred' | null;
  move_in_date: string | null;        // ISO-8601 or "Immediate"
  
  // Matching & Follow-up
  matched_properties: string[];       // Array of property IDs
  last_interaction_date: string | null;
  next_followup_date: string | null;
  followup_count: number;
  
  // Metadata
  tags: string[];                     // JSON array
  notes: string | null;
  created_at: string;
  updated_at: string;
}
```

### Conversation Model

```typescript
interface Conversation {
  // Primary Key
  message_id: number;
  
  // Message Ownership
  phone_number: string;
  
  // Message Content
  direction: 'Incoming' | 'Outgoing';
  message_body: string;
  message_type: 'text' | 'image' | 'audio' | 'video' | 'document' | 'location' | 'contact';
  media_urls: string[] | null;
  media_filenames: string[] | null;
  
  // Message Metadata
  sender_name: string | null;
  timestamp: string;                   // ISO-8601
  replied_to_id: number | null;
  
  // AI Processing
  is_processed: boolean;
  extracted_intent: string | null;
  extracted_entities: Record<string, any> | null;
  sentiment: 'Positive' | 'Neutral' | 'Negative' | 'Urgent' | null;
  requires_followup: boolean;
  
  // Timestamps
  created_at: string;
  processed_at: string | null;
}
```

### Lead Lifecycle Event Model

```typescript
interface LeadLifecycleEvent {
  event_id: number;
  phone_number: string;
  event_type: 'Status Change' | 'Follow-up' | 'Property Matched' | 'Note Added';
  old_value: string | null;
  new_value: string | null;
  event_description: string;
  created_by: string | null;
  created_at: string;
}
```

---

## 🔗 Google Sheets API Integration

### Sheet Structure

**Sheet ID:** `1GfM9lPQSukVpxCEVUlUDxFj_WYg0xQj8Inn7FA4sLVI`

**Tabs:**
1. **Leads** - Column A to W (23 columns)
2. **Conversations** - Column A to Q (17 columns)
3. **Events** - Column A to I (9 columns)

### gspreadService Methods

```javascript
// Initialize connection
gspreadService.init()

// Get all leads
gspreadService.getLeadsData()
// Returns: Array<Lead>

// Get conversations for phone number
gspreadService.getConversations(phoneNumber: string)
// Returns: Array<Conversation>

// Update lead status
gspreadService.updateLeadStatus(phoneNumber: string, status: string)
// Returns: boolean

// Batch update
gspreadService.batchUpdate(updates: Array<Update>)
// Returns: boolean
```

---

## 🐍 Python Scripts API

### 1. WhatsApp Extraction

**Script:** `extract_whatsapp.py`

```bash
python extract_whatsapp.py \
  --phone-number "+919876543210" \
  --backup-dir whatsapp_backups/backup1 \
  --backup-type android-crypt15 \
  --key-file whatsapp_backups/backup1/key \
  --date-from 2026-07-23
```

**Output:** `extracted_data/[phone]_export.json`

### 2. Lead Classification

**Script:** `classify_with_bedrock.py`

```bash
python classify_with_bedrock.py \
  --input extracted_data/conversations.json \
  --output classified_leads.json \
  --model anthropic.claude-3-sonnet-20240229-v1:0
```

**Output:** Classified JSON with intent, entities, sentiment

### 3. Database Import

**Script:** `import_to_database_v2.py`

```bash
python import_to_database_v2.py \
  --input classified_leads.json \
  --database leads.db
```

**Output:** Data imported to SQLite

### 4. Google Sheets Sync

**Script:** `sync_to_sheet_v2.py`

```bash
python sync_to_sheet_v2.py \
  --database leads.db \
  --sheet-id 1GfM9lPQSukVpxCEVUlUDxFj_WYg0xQj8Inn7FA4sLVI
```

**Output:** Data synced to Google Sheets

---

## ⚠️ Error Handling

### Error Response Format

```json
{
  "error": "Error message description",
  "code": "ERROR_CODE",
  "details": {
    "field": "Additional context"
  },
  "timestamp": "2026-09-26T14:30:00Z"
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_PHONE_NUMBER` | 400 | Phone number format invalid |
| `LEAD_NOT_FOUND` | 404 | Lead doesn't exist |
| `INVALID_STATUS` | 400 | Invalid status value |
| `SHEETS_API_ERROR` | 500 | Google Sheets API failure |
| `AUTHENTICATION_FAILED` | 401 | Service account auth failed |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `SERVER_ERROR` | 500 | Internal server error |

---

## 🚦 Rate Limits

### Google Sheets API Limits

- **Read requests:** 100 per 100 seconds per user
- **Write requests:** 100 per 100 seconds per user
- **Total requests:** 500 per 100 seconds per project

### Best Practices

1. **Batch Operations:** Use batch update instead of individual updates
2. **Caching:** Cache frequently accessed data
3. **Pagination:** Use limit/offset for large datasets
4. **Retry Logic:** Implement exponential backoff for failed requests

---

## 📝 Examples

### Example 1: Fetch and Display Leads

```javascript
// Frontend React component
import axios from 'axios';

const fetchLeads = async () => {
  try {
    const response = await axios.get('/api/leads', {
      params: {
        status: 'Active',
        priority: 'High',
        limit: 50
      }
    });
    
    console.log('Leads:', response.data.data);
    setLeads(response.data.data);
  } catch (error) {
    console.error('Error fetching leads:', error);
  }
};
```

### Example 2: Update Lead Status

```javascript
const updateStatus = async (phoneNumber, newStatus) => {
  try {
    const response = await axios.post(
      `/api/leads/${encodeURIComponent(phoneNumber)}/status`,
      { status: newStatus }
    );
    
    if (response.data.success) {
      console.log('Status updated successfully');
    }
  } catch (error) {
    console.error('Error updating status:', error);
  }
};
```

### Example 3: View Conversations

```javascript
const viewConversations = async (phoneNumber) => {
  try {
    const response = await axios.get(
      `/api/conversations/${encodeURIComponent(phoneNumber)}`,
      { params: { limit: 100 } }
    );
    
    const messages = response.data.conversations;
    console.log('Total messages:', messages.length);
    
    messages.forEach(msg => {
      console.log(`[${msg.timestamp}] ${msg.sender_name}: ${msg.message_body}`);
    });
  } catch (error) {
    console.error('Error fetching conversations:', error);
  }
};
```

### Example 4: Python - Sync to Sheets

```python
import gspread
from google.oauth2.service_account import Credentials
import sqlite3

# Authenticate
creds = Credentials.from_service_account_file(
    'service-account-key.json',
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)
gc = gspread.authorize(creds)

# Open sheet
sheet = gc.open_by_key('1GfM9lPQSukVpxCEVUlUDxFj_WYg0xQj8Inn7FA4sLVI')
worksheet = sheet.worksheet('Leads')

# Get data from database
conn = sqlite3.connect('leads.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM leads WHERE lead_status = "Active"')
rows = cursor.fetchall()

# Update sheet
worksheet.clear()
worksheet.append_rows(rows, value_input_option='RAW')

print(f'Synced {len(rows)} leads to Google Sheets')
```

---

## 🔄 Webhooks (Future)

### Planned Webhook Events

- `lead.created` - New lead added
- `lead.updated` - Lead information changed
- `lead.status_changed` - Lead status updated
- `conversation.received` - New message received
- `followup.due` - Follow-up reminder due

---

## 📚 Additional Resources

- [Google Sheets API Documentation](https://developers.google.com/sheets/api)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [gspread Library Documentation](https://docs.gspread.org/)
- [Express.js Documentation](https://expressjs.com/)

---

**Need help?** Contact support@easyfindprops.com or open an issue on GitHub.
