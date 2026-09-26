const express = require('express');
const path = require('path');
const { GoogleAuth } = require('google-auth-library');
const { google } = require('googleapis');

const app = express();
const PORT = process.env.PORT || 5000;

app.use(express.json());

// Initialize Google Sheets
let sheets;
let auth;

async function initializeGoogleSheets() {
  try {
    const credentials = JSON.parse(process.env.GOOGLE_APPLICATION_CREDENTIALS_JSON || '{}');
    
    auth = new GoogleAuth({
      credentials,
      scopes: ['https://www.googleapis.com/auth/spreadsheets'],
    });

    const authClient = await auth.getClient();
    sheets = google.sheets({ version: 'v4', auth: authClient });
    
    console.log('✅ Google Sheets initialized successfully');
  } catch (error) {
    console.error('❌ Failed to initialize Google Sheets:', error.message);
  }
}

// Discover the actual worksheet title instead of assuming the default "Sheet1".
// Prefer the Leads tab used by the lead-management sync; fall back to the
// first visible worksheet for spreadsheets with a different naming scheme.
async function resolveLeadsRange(spreadsheetId) {
  const metadata = await sheets.spreadsheets.get({
    spreadsheetId,
    fields: 'sheets(properties(title,hidden))',
  });
  const tabs = (metadata.data.sheets || []).map(s => s.properties).filter(p => !p.hidden);
  const tab = tabs.find(p => p.title.toLowerCase() === 'leads') || tabs[0];
  if (!tab) throw new Error('No visible worksheets found in the configured spreadsheet');
  const escapedTitle = tab.title.replace(/'/g, "''");
  return "'" + escapedTitle + "'!A:Z";
}

// Serve the lead-management interface at the service homepage.
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'dashboard.html'));
});

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', service: 'leads-ui-dashboard' });
});

// Get all leads from Google Sheet
app.get('/api/leads', async (req, res) => {
  try {
    if (!sheets) {
      return res.status(503).json({ error: 'Google Sheets not initialized. Check GOOGLE_APPLICATION_CREDENTIALS_JSON.' });
    }

    const sheetId = process.env.SHEET_ID;
    if (!sheetId) {
      return res.status(400).json({ error: 'SHEET_ID environment variable not set' });
    }

    const response = await sheets.spreadsheets.values.get({
      spreadsheetId: sheetId,
      range: await resolveLeadsRange(sheetId),
    });

    const rows = response.data.values || [];
    const headers = rows[0] || [];
    const data = rows.slice(1).map(row => {
      const obj = {};
      headers.forEach((header, index) => {
        obj[header] = row[index] || '';
      });
      return obj;
    });

    res.json({
      success: true,
      count: data.length,
      data: data
    });
  } catch (error) {
    console.error('Error fetching leads:', error);
    res.status(500).json({ 
      error: 'Failed to fetch leads',
      message: error.message 
    });
  }
});

// Get sheet info
app.get('/api/sheet-info', async (req, res) => {
  try {
    if (!sheets) {
      return res.status(503).json({ error: 'Google Sheets not initialized' });
    }

    const sheetId = process.env.SHEET_ID;
    if (!sheetId) {
      return res.status(400).json({ error: 'SHEET_ID not set' });
    }

    const response = await sheets.spreadsheets.get({
      spreadsheetId: sheetId,
    });

    res.json({
      success: true,
      title: response.data.properties.title,
      sheets: response.data.sheets.map(s => s.properties.title)
    });
  } catch (error) {
    console.error('Error fetching sheet info:', error);
    res.status(500).json({ 
      error: 'Failed to fetch sheet info',
      message: error.message 
    });
  }
});

// Start server
app.listen(PORT, async () => {
  console.log(`🚀 Server running on port ${PORT}`);
  await initializeGoogleSheets();
});
