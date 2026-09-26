const express = require('express');
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

// Health check endpoint
app.get('/', (req, res) => {
  res.json({ 
    status: 'ok',
    service: 'leads-ui-dashboard',
    message: 'API is running',
    endpoints: {
      health: '/',
      leads: '/api/leads',
      sheet_info: '/api/sheet-info'
    }
  });
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
      range: 'Sheet1!A:Z',
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
