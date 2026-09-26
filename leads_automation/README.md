# 🏠 EasyFind Lead Management System

**AI-Powered WhatsApp Lead Tracking & Classification System for Real Estate**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Environment Variables](#environment-variables)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

The EasyFind Lead Management System is an intelligent lead tracking solution built for real estate businesses. It extracts WhatsApp conversations from backup files, uses AI to classify and analyze leads, stores structured data in SQLite, syncs to Google Sheets for team dashboards, and provides a React-based UI for lead management.

### What It Does

1. **📱 WhatsApp Extraction**: Extracts conversations from Android/iOS WhatsApp backups
2. **🤖 AI Classification**: Uses AWS Bedrock (Claude) or Google Gemini to classify leads into categories:
   - Rental Inquiries (customers looking for properties)
   - Property Listings Sent
   - Real Estate Brokers/Agents
   - Service/Promotional Spam
   - Personal Contacts (non-business)
3. **💾 Data Storage**: Stores leads, conversations, and lifecycle events in SQLite database
4. **📊 Google Sheets Sync**: Real-time sync to Google Sheets for team collaboration
5. **🎨 Web Dashboard**: React-based UI for viewing and managing leads

## ✨ Features

### Core Features

- ✅ **Multi-source WhatsApp Extraction**
  - Android backups (crypt14, crypt15, plain DB)
  - iOS backups (iTunes/Finder)
  - Date range filtering
  - Media file support

- ✅ **AI-Powered Classification**
  - Dual-model support (AWS Bedrock Claude / Google Gemini)
  - Intent extraction
  - Sentiment analysis
  - Requirement parsing (BHK, location, budget, etc.)
  - Automated tagging and prioritization

- ✅ **Structured Database**
  - 3 main tables: `leads`, `conversations`, `lead_lifecycle_events`
  - 3 views: `v_active_leads`, `v_followup_today`, `v_recent_events`
  - Automated triggers for timestamps and status changes
  - 15 performance indexes

- ✅ **Google Sheets Integration**
  - Real-time bi-directional sync
  - Service account authentication
  - Batch updates for performance
  - Three tabs: Leads, Conversations, Events

- ✅ **Web Dashboard**
  - Material-UI based interface
  - Real-time lead statistics
  - Conversation viewer
  - Filter and search capabilities
  - Charts and visualizations (Recharts)

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    WhatsApp Backups (Input)                     │
│            Android (*.crypt15) / iOS (Backup folder)            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              WhatsApp-Chat-Exporter (Python)                    │
│                   extract_whatsapp.py                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼ (JSON export)
┌─────────────────────────────────────────────────────────────────┐
│                  AI Classification Layer                        │
│     classify_leads.py / classify_with_bedrock.py                │
│            AWS Bedrock (Claude) / Gemini                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼ (Classified JSON)
┌─────────────────────────────────────────────────────────────────┐
│                   SQLite Database (leads.db)                    │
│   Tables: leads | conversations | lead_lifecycle_events        │
│          import_to_database_v2.py                               │
└─────────────┬───────────────────────────────────┬───────────────┘
              │                                   │
              ▼                                   ▼
┌──────────────────────────────┐   ┌─────────────────────────────┐
│    Google Sheets Sync        │   │      React Dashboard        │
│   (sync_to_sheet_v2.py)      │   │  (leads-ui / whatsapp_ui)  │
│                              │   │                             │
│  Service Account Auth        │   │  Material-UI + Express      │
│  Batch Updates (1000 rows)   │   │  Google Sheets API         │
└──────────────────────────────┘   └─────────────────────────────┘
```

## 🛠️ Tech Stack

### Backend
- **Python 3.12+**
  - `whatsapp-chat-exporter` - WhatsApp backup extraction
  - `gspread` - Google Sheets API integration
  - `boto3` - AWS Bedrock integration
  - `google-generativeai` - Gemini AI integration
  - `sqlite3` - Database operations

### Frontend
- **Node.js 18+**
- **React 18.2** - UI framework
- **Material-UI (MUI) 5.14** - Component library
- **Recharts 2.10** - Data visualization
- **Axios** - HTTP client
- **Express 4.18** - Backend server

### Infrastructure
- **SQLite** - Local database
- **Google Sheets API** - Cloud spreadsheet
- **AWS Bedrock** - AI classification (Claude)
- **Google Gemini** - Alternative AI classification
- **Render.com** - Deployment platform (optional)

## 📦 Prerequisites

Before you begin, ensure you have:

### Required
- **Python 3.12 or higher** ([Download](https://www.python.org/downloads/))
- **Node.js 18 or higher** ([Download](https://nodejs.org/))
- **WhatsApp backup files** (Android `.crypt15` or iOS backup folder)

### API Keys & Credentials
- **Google Cloud Service Account** with Sheets API enabled
  - Download JSON key file
  - Share target Google Sheet with service account email
- **AWS Account** (for Bedrock) OR **Google Cloud** (for Gemini)
  - AWS: Configure credentials with Bedrock access
  - Google: API key with Generative AI enabled

### Optional
- **Render.com Account** (for web deployment)
- **Git** (for version control)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/zeidhussain9-cloud/easyfind-website.git
cd easyfind-website/leads_automation
```

### 2. Backend Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install WhatsApp exporter
pip install whatsapp-chat-exporter pycryptodome
```

### 3. Frontend Setup

```bash
# Navigate to UI folder
cd leads-ui

# Install Node dependencies
npm install

# Return to root
cd ..
```

### 4. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env
```

Required variables:
```bash
# Google Sheets
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
SHEET_ID=your-google-sheet-id

# AI Provider (choose one)
AWS_REGION=us-east-1  # For Bedrock
GOOGLE_API_KEY=your-gemini-api-key  # For Gemini
```

### 5. Initialize Database

```bash
# Create database schema
sqlite3 leads.db < schema.sql

# Verify tables created
sqlite3 leads.db "SELECT name FROM sqlite_master WHERE type='table';"
```

### 6. Extract WhatsApp Data

```bash
# Place your WhatsApp backup files in whatsapp_backups/
mkdir -p whatsapp_backups/backup1

# Extract conversations
python extract_whatsapp.py \
  --phone-number "+919876543210" \
  --backup-dir whatsapp_backups/backup1 \
  --backup-type android-crypt15 \
  --key-file whatsapp_backups/backup1/encrypted_backup.key \
  --date-from 2026-07-23
```

### 7. Classify Leads with AI

```bash
# Using AWS Bedrock (Claude)
python classify_with_bedrock.py

# OR using Google Gemini
python classify_leads_dual_model.py
```

### 8. Import to Database

```bash
# Import classified data
python import_to_database_v2.py
```

### 9. Sync to Google Sheets

```bash
# One-time full sync
python sync_to_sheet_v2.py
```

### 10. Start Web Dashboard

```bash
cd leads-ui

# Development mode
npm run dev

# Production mode
npm start
```

Open browser to: `http://localhost:3000`

## 📁 Project Structure

```
leads_automation/
├── README.md                      # This file
├── DEPLOYMENT.md                  # Render deployment guide
├── DEVELOPMENT.md                 # Development setup guide
├── ARCHITECTURE.md                # System architecture documentation
├── API_DOCUMENTATION.md           # API endpoints documentation
├── CHANGELOG.md                   # Version history
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git ignore rules
├── .env.example                   # Environment variables template
│
├── schema.sql                     # Database schema definition
├── leads.db                       # SQLite database (git-ignored)
│
├── config/                        # Configuration files
│   ├── taxonomy.json              # Lead classification rules
│   ├── rental_keywords.json       # Rental detection keywords
│   ├── bangalore_locations.json   # Location mapping
│   ├── intent_keywords.json       # Intent detection
│   ├── personal_contacts.json     # Known personal contacts
│   └── internal_phones.json       # Internal team numbers
│
├── extract_whatsapp.py            # WhatsApp extraction wrapper
├── classify_leads.py              # Basic classification (rule-based)
├── classify_with_bedrock.py       # AI classification (AWS Bedrock)
├── classify_leads_dual_model.py   # AI classification (Gemini)
├── import_to_database_v2.py       # Import classified data to SQLite
├── sync_to_sheet_v2.py            # Sync database to Google Sheets
├── bulk_assign_collections.py     # Bulk lead assignment operations
├── create_google_sheet.py         # Create new Google Sheet
│
├── leads-ui/                      # React dashboard
│   ├── src/
│   │   ├── App.js                 # Main React component
│   │   ├── components/            # UI components
│   │   └── services/              # API services
│   ├── server.js                  # Express backend
│   ├── package.json               # Node dependencies
│   └── render.yaml                # Render deployment config
│
├── whatsapp_ui/                   # WhatsApp conversation viewer
│   ├── src/                       # React app
│   ├── package.json               # Dependencies
│   └── render.yaml                # Deployment config
│
├── whatsapp_backups/              # WhatsApp backup files (git-ignored)
└── extracted_data/                # Extracted JSON files (git-ignored)
```

## 📚 Documentation

- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Render deployment guide with environment setup
- **[DEVELOPMENT.md](./DEVELOPMENT.md)** - Local development setup and contribution guidelines
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Detailed system architecture and data flow
- **[API_DOCUMENTATION.md](./API_DOCUMENTATION.md)** - Backend API endpoints and data models
- **[EXTRACTION_GUIDE.md](./EXTRACTION_GUIDE.md)** - WhatsApp extraction detailed guide
- **[STATUS.md](./STATUS.md)** - Current project status and progress

## 🔐 Environment Variables

See [.env.example](./.env.example) for all required environment variables.

### Core Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to Google service account JSON | Yes | `/path/to/key.json` |
| `SHEET_ID` | Google Sheet ID for sync | Yes | `1GfM9lPQSukVpxCEVUl...` |
| `AWS_REGION` | AWS region for Bedrock | If using Bedrock | `us-east-1` |
| `GOOGLE_API_KEY` | Gemini API key | If using Gemini | `AIzaSy...` |
| `NODE_ENV` | Environment mode | No | `production` |

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [DEVELOPMENT.md](./DEVELOPMENT.md) for detailed contribution guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For issues, questions, or suggestions:

- 📧 Email: support@easyfindprops.com
- 🐛 Issues: [GitHub Issues](https://github.com/zeidhussain9-cloud/easyfind-website/issues)
- 📖 Documentation: See `/docs` folder

## 🎯 Roadmap

- [ ] Real-time WhatsApp integration (webhooks)
- [ ] Advanced analytics and reporting
- [ ] Mobile app (React Native)
- [ ] Multi-language support
- [ ] CRM integration (Salesforce, HubSpot)
- [ ] Automated follow-up reminders
- [ ] Email notifications
- [ ] Role-based access control (RBAC)

## 👥 Authors

- **Zeid Hussain** - *Initial work* - [zeidhussain9-cloud](https://github.com/zeidhussain9-cloud)

## 🙏 Acknowledgments

- WhatsApp-Chat-Exporter for backup extraction
- AWS Bedrock team for Claude AI access
- Google for Gemini AI and Sheets API
- Material-UI team for beautiful components
- Render.com for hosting platform

---

**Built with ❤️ for EasyFind Property Solutions**
