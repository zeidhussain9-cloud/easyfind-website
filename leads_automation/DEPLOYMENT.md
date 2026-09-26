# 🚀 Deployment Guide

Complete guide for deploying the EasyFind Lead Management System to Render.com and other platforms.

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Render.com Deployment](#rendercom-deployment)
- [Environment Variables](#environment-variables)
- [Database Setup](#database-setup)
- [Google Sheets Setup](#google-sheets-setup)
- [Post-Deployment](#post-deployment)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

This system consists of two deployable components:

1. **leads-ui** - Main React dashboard with Express backend
2. **whatsapp-ui** - WhatsApp conversation viewer (optional)

Both are configured for deployment on Render.com's free tier.

## 📦 Prerequisites

Before deploying, ensure you have:

### Required Accounts
- ✅ **GitHub Account** - Repository must be pushed to GitHub
- ✅ **Render.com Account** - [Sign up here](https://render.com)
- ✅ **Google Cloud Account** - For Sheets API and service account
- ✅ **AWS Account** (for Bedrock) OR **Google Cloud** (for Gemini)

### Required Files
- ✅ Service account JSON key (for Google Sheets)
- ✅ AWS credentials (if using Bedrock)
- ✅ Google Sheet created and shared with service account

### Data Preparation
- ✅ Database populated with leads data
- ✅ Classification completed
- ✅ At least one successful sync to Google Sheets

## 🌐 Render.com Deployment

### Method 1: Using Render Dashboard (Recommended)

#### Step 1: Push to GitHub

```bash
# Ensure you're in the leads_automation directory
cd /path/to/leads_automation

# Add all files (respects .gitignore)
git add .

# Commit changes
git commit -m "Initial commit: Lead management system"

# Push to GitHub
git push origin main
```

#### Step 2: Create Render Service

1. **Login to Render Dashboard**
   - Go to https://dashboard.render.com
   - Sign in with your account

2. **Create New Web Service**
   - Click **"New +"** → **"Web Service"**
   - Connect your GitHub repository
   - Select the repository: `easyfind-website`
   - Root Directory: `leads_automation/leads-ui`

3. **Configure Service**

| Setting | Value |
|---------|-------|
| **Name** | `leads-ui` (or your choice) |
| **Environment** | `Node` |
| **Region** | `Oregon` (or closest to users) |
| **Branch** | `main` |
| **Build Command** | `npm install && npm run build` |
| **Start Command** | `npm start` |
| **Plan** | `Free` |

#### Step 3: Add Environment Variables

In the Render dashboard, under **Environment**, add:

```bash
# Google Sheets Configuration
GOOGLE_APPLICATION_CREDENTIALS=/etc/secrets/service-account-key.json
SHEET_ID=1GfM9lPQSukVpxCEVUlUDxFj_WYg0xQj8Inn7FA4sLVI

# Node Environment
NODE_ENV=production
PORT=10000
```

#### Step 4: Add Secret Files

1. Click **"Environment"** → **"Secret Files"**
2. Add secret file:
   - **Filename**: `service-account-key.json`
   - **Contents**: Paste your Google service account JSON key
   - **Path**: `/etc/secrets/service-account-key.json`

#### Step 5: Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repository
   - Install dependencies
   - Build the application
   - Start the server

3. Monitor deployment logs in real-time
4. Once complete, you'll get a URL: `https://leads-ui-xxxx.onrender.com`

### Method 2: Using render.yaml (Infrastructure as Code)

The repository includes `render.yaml` configuration files. To deploy using this method:

#### Step 1: Update render.yaml

Edit `leads-ui/render.yaml`:

```yaml
services:
  - type: web
    name: leads-ui
    env: node
    region: oregon
    plan: free
    buildCommand: npm install && npm run build
    startCommand: npm start
    envVars:
      - key: GOOGLE_APPLICATION_CREDENTIALS
        sync: false  # Managed as secret file
      - key: SHEET_ID
        value: YOUR_SHEET_ID_HERE
      - key: NODE_ENV
        value: production
```

#### Step 2: Deploy via Render Dashboard

1. In Render Dashboard, click **"New +"** → **"Blueprint"**
2. Connect your GitHub repository
3. Select the repository containing `render.yaml`
4. Render will automatically detect and deploy all services

### Method 3: Using Render API

```bash
# Set your Render API key
export RENDER_API_KEY="rnd_YOUR_API_KEY_HERE"

# Create service via API
curl -X POST https://api.render.com/v1/services \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "web_service",
    "name": "leads-ui",
    "ownerId": "YOUR_OWNER_ID",
    "repo": "https://github.com/zeidhussain9-cloud/easyfind-website",
    "branch": "main",
    "rootDir": "leads_automation/leads-ui",
    "env": "node",
    "buildCommand": "npm install && npm run build",
    "startCommand": "npm start",
    "plan": "free",
    "region": "oregon",
    "envVars": [
      {
        "key": "SHEET_ID",
        "value": "YOUR_SHEET_ID"
      },
      {
        "key": "NODE_ENV",
        "value": "production"
      }
    ]
  }'
```

## 🔐 Environment Variables

### Complete Environment Variables Reference

#### Backend (Python Scripts)

Create `.env` file in `leads_automation/` root:

```bash
# ============================================================================
# GOOGLE SHEETS CONFIGURATION
# ============================================================================
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
SHEET_ID=1GfM9lPQSukVpxCEVUlUDxFj_WYg0xQj8Inn7FA4sLVI

# ============================================================================
# AWS BEDROCK (If using Claude for classification)
# ============================================================================
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# Or use AWS credentials file in ~/.aws/credentials

# ============================================================================
# GOOGLE GEMINI (If using Gemini for classification)
# ============================================================================
GOOGLE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# ============================================================================
# DATABASE
# ============================================================================
DATABASE_PATH=./leads.db

# ============================================================================
# OPTIONAL: LOGGING
# ============================================================================
LOG_LEVEL=INFO
LOG_FILE=./application.log
```

#### Frontend (React Dashboard)

Create `.env` file in `leads_automation/leads-ui/`:

```bash
# ============================================================================
# SERVER CONFIGURATION
# ============================================================================
NODE_ENV=production
PORT=10000

# ============================================================================
# GOOGLE SHEETS
# ============================================================================
GOOGLE_APPLICATION_CREDENTIALS=/etc/secrets/service-account-key.json
SHEET_ID=1GfM9lPQSukVpxCEVUlUDxFj_WYg0xQj8Inn7FA4sLVI

# ============================================================================
# OPTIONAL: API ENDPOINTS
# ============================================================================
API_BASE_URL=http://localhost:5000
REACT_APP_API_URL=/api
```

### Environment Variable Descriptions

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to Google service account JSON key | Yes | `/etc/secrets/key.json` |
| `SHEET_ID` | Google Sheet ID (from URL) | Yes | `1GfM9lPQSukVpxCEVU...` |
| `AWS_REGION` | AWS region for Bedrock | If using Bedrock | `us-east-1` |
| `AWS_ACCESS_KEY_ID` | AWS access key | If using Bedrock | `AKIAXXXXXXXX` |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | If using Bedrock | `xxxxxxxxxx` |
| `GOOGLE_API_KEY` | Gemini API key | If using Gemini | `AIzaSyXXXXXX` |
| `NODE_ENV` | Node environment | No | `production` |
| `PORT` | Server port | No | `10000` |
| `DATABASE_PATH` | SQLite database path | No | `./leads.db` |
| `LOG_LEVEL` | Logging level | No | `INFO` |

## 🗄️ Database Setup

The SQLite database is local and cannot be deployed to Render's ephemeral filesystem. You have two options:

### Option 1: Use Google Sheets as Primary Data Store (Recommended for Render)

The dashboard reads directly from Google Sheets, eliminating the need for a persistent database on Render.

**Advantages:**
- ✅ No database persistence issues
- ✅ Real-time collaboration
- ✅ Easy backup and recovery
- ✅ Team access without VPN

**Setup:**
1. Ensure `sync_to_sheet_v2.py` has run successfully
2. All data is in Google Sheets
3. Dashboard reads from Sheets via API

### Option 2: Use External Database Service

For production with high traffic, consider:

**PostgreSQL on Render:**
```bash
# Create PostgreSQL database on Render
# Update connection string in environment variables
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

**Supabase (PostgreSQL):**
- Free tier available
- Built-in APIs
- Real-time subscriptions

**PlanetScale (MySQL):**
- Serverless MySQL
- Free tier with branching
- Edge network

## 📊 Google Sheets Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project: `easyfind-lead-management`
3. Enable APIs:
   - Google Sheets API
   - Google Drive API

### Step 2: Create Service Account

1. Navigate to **IAM & Admin** → **Service Accounts**
2. Click **"Create Service Account"**
3. Name: `leads-automation-service`
4. Grant role: **Editor** (or custom role with Sheets access)
5. Click **"Done"**

### Step 3: Generate Key

1. Click on the created service account
2. Go to **"Keys"** tab
3. Click **"Add Key"** → **"Create New Key"**
4. Choose **JSON** format
5. Download and save securely (this is your `service-account-key.json`)

### Step 4: Create Google Sheet

1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new sheet: **"Easyfind Lead Management Dashboard"**
3. Create three tabs:
   - **Leads** - Master lead registry
   - **Conversations** - Message log
   - **Events** - Lifecycle events

### Step 5: Share Sheet with Service Account

1. Open your Google Sheet
2. Click **"Share"**
3. Add the service account email (looks like: `leads-automation-service@project-id.iam.gserviceaccount.com`)
4. Grant **Editor** permission
5. Uncheck **"Notify people"**
6. Click **"Share"**

### Step 6: Get Sheet ID

From the Google Sheet URL:
```
https://docs.google.com/spreadsheets/d/1GfM9lPQSukVpxCEVUlUDxFj_WYg0xQj8Inn7FA4sLVI/edit
                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                      This is your SHEET_ID
```

## ✅ Post-Deployment

### Verify Deployment

1. **Check Service Status**
   - Go to Render Dashboard
   - Ensure service shows "Live" status
   - Check deployment logs for errors

2. **Test Application**
   ```bash
   # Test health endpoint
   curl https://your-service.onrender.com/health
   
   # Expected response:
   {"status": "ok", "timestamp": "2026-09-26T10:30:00Z"}
   ```

3. **Test Google Sheets Integration**
   - Open your deployed dashboard
   - Verify leads are loading
   - Check for any API errors in browser console

### Initial Data Sync

After deployment, run an initial sync to populate Google Sheets:

```bash
# From local machine (with database populated)
python sync_to_sheet_v2.py

# Verify in Google Sheets that data appears
```

### Configure Custom Domain (Optional)

1. In Render Dashboard, go to **Settings**
2. Click **"Custom Domain"**
3. Add your domain: `leads.easyfindprops.com`
4. Update DNS records at your domain provider:
   ```
   CNAME  leads  your-service.onrender.com
   ```
5. Render will auto-provision SSL certificate

## 📈 Monitoring & Maintenance

### Render Built-in Monitoring

- **Logs**: Real-time logs in Render Dashboard
- **Metrics**: CPU, Memory, Request metrics
- **Alerts**: Configure email alerts for downtime

### Health Checks

Add to `server.js`:

```javascript
// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    memory: process.memoryUsage()
  });
});
```

### Automatic Deployments

Enable auto-deploy in Render:
1. Go to **Settings** → **Build & Deploy**
2. Enable **"Auto-Deploy"**
3. Choose **"Yes"** for auto-deploy on git push

Now every push to `main` branch triggers a deployment.

### Backup Strategy

**Google Sheets:**
- Automatically backed up by Google
- Version history available (File → Version history)

**Database (if using external DB):**
- Configure automated backups in your database provider
- Export weekly to Google Drive or S3

**Code:**
- Version controlled in GitHub
- Create release tags for stable versions

### Monitoring Checklist

- [ ] Set up uptime monitoring (UptimeRobot, Pingdom)
- [ ] Configure error tracking (Sentry, LogRocket)
- [ ] Enable Render email alerts
- [ ] Set up weekly backup automation
- [ ] Monitor Google Sheets API quota
- [ ] Monitor AWS Bedrock usage and costs

## 🔧 Troubleshooting

### Common Issues

#### Issue 1: Service Won't Start

**Symptoms:**
- Deploy fails with "Application failed to start"
- 502 Bad Gateway error

**Solutions:**
```bash
# Check logs in Render Dashboard
# Look for:
# - Missing dependencies in package.json
# - Port binding issues (must use process.env.PORT)
# - Missing environment variables

# Fix: Update server.js
const PORT = process.env.PORT || 10000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on port ${PORT}`);
});
```

#### Issue 2: Google Sheets Authentication Failed

**Symptoms:**
- "Unable to read from Google Sheets"
- 403 Forbidden errors

**Solutions:**
1. Verify service account email is added to Sheet with Editor permission
2. Check `GOOGLE_APPLICATION_CREDENTIALS` path is correct
3. Verify JSON key is valid (not expired)
4. Ensure Google Sheets API is enabled in Cloud Console

```bash
# Test authentication locally
node -e "
const { google } = require('googleapis');
const sheets = google.sheets('v4');
// Test connection
console.log('Testing Sheets API...');
"
```

#### Issue 3: Build Fails

**Symptoms:**
- NPM install fails
- Build command errors

**Solutions:**
```bash
# Check package.json for correct scripts
{
  "scripts": {
    "build": "react-scripts build",
    "start": "node server.js"
  }
}

# Check Node version compatibility
# Render uses Node 18 by default
# Specify in package.json:
{
  "engines": {
    "node": ">=18.0.0",
    "npm": ">=9.0.0"
  }
}
```

#### Issue 4: CORS Errors

**Symptoms:**
- Frontend can't access API
- "CORS policy blocked" in browser

**Solutions:**
```javascript
// In server.js, add CORS middleware
const cors = require('cors');

app.use(cors({
  origin: process.env.ALLOWED_ORIGINS || '*',
  credentials: true
}));
```

#### Issue 5: Memory Limits Exceeded

**Symptoms:**
- Service crashes randomly
- "Out of memory" errors

**Solutions:**
1. Upgrade to paid plan for more resources
2. Optimize queries to Google Sheets (batch operations)
3. Implement caching (Redis on Render)
4. Limit data fetched per request

```javascript
// Add pagination
app.get('/api/leads', async (req, res) => {
  const page = parseInt(req.query.page) || 1;
  const limit = 100; // Max 100 rows per request
  const offset = (page - 1) * limit;
  
  // Fetch paginated data
});
```

### Getting Help

**Render Support:**
- [Render Docs](https://render.com/docs)
- [Render Community](https://community.render.com)
- Email: support@render.com

**Project Issues:**
- GitHub Issues: [Create an issue](https://github.com/zeidhussain9-cloud/easyfind-website/issues)
- Email: support@easyfindprops.com

## 🔄 Updating Deployment

### Update Code

```bash
# Make changes locally
git add .
git commit -m "Update: Feature description"
git push origin main

# Render auto-deploys (if enabled)
# Or manually trigger in Dashboard
```

### Update Environment Variables

1. Go to Render Dashboard
2. Navigate to your service
3. Click **"Environment"**
4. Update variables
5. Save changes
6. Service will automatically redeploy

### Rollback Deployment

1. Go to **"Events"** tab in Render Dashboard
2. Find the previous successful deployment
3. Click **"Rollback to this version"**
4. Confirm rollback

## 📝 Deployment Checklist

Before going live, verify:

- [ ] All environment variables configured
- [ ] Service account has Sheet access
- [ ] Health check endpoint working
- [ ] Google Sheets sync tested
- [ ] HTTPS enabled (automatic on Render)
- [ ] Custom domain configured (optional)
- [ ] Auto-deploy enabled
- [ ] Error monitoring set up
- [ ] Backup strategy in place
- [ ] Team has access to Render dashboard
- [ ] Documentation updated
- [ ] Tested on production URL

## 🎉 Success!

Your EasyFind Lead Management System is now live! 

**Next Steps:**
- Share the URL with your team
- Set up regular monitoring
- Configure automated reports
- Train users on the dashboard

---

**Need help?** Contact support@easyfindprops.com
