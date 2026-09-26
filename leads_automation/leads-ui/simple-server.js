const express = require('express');
const path = require('path');
const crypto = require('crypto');
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

// Single-user access control. Protect the API as well as the dashboard.
app.disable('x-powered-by');
app.set('trust proxy', 1);
const loginAttempts = new Map();
const sessionLifetime = 12 * 60 * 60 * 1000;
const sessionSecret = process.env.DASHBOARD_SESSION_SECRET;
const dashboardPassword = process.env.DASHBOARD_PASSWORD;
if (!dashboardPassword || !sessionSecret || sessionSecret.length < 32) {
  console.error('FATAL: DASHBOARD_PASSWORD and DASHBOARD_SESSION_SECRET must be configured');
  process.exit(1);
}
function sign(value) { return crypto.createHmac('sha256', sessionSecret).update(value).digest('hex'); }
function safeEqual(a,b) { const x=Buffer.from(String(a)); const y=Buffer.from(String(b)); return x.length===y.length && crypto.timingSafeEqual(x,y); }
function isAuthenticated(req) {
  const cookies = Object.fromEntries((req.headers.cookie || '').split(';').map(c=>{const i=c.indexOf('=');return i<0?['','']:[c.slice(0,i).trim(),c.slice(i+1).trim()]}));
  const token = cookies.efps_session || '';
  const match = /^(\\d+)\\.([a-f0-9]{64})$/.exec(token);
  if (!match) return false;
  const issued = Number(match[1]);
  return Number.isSafeInteger(issued) && issued <= Date.now() && Date.now()-issued < sessionLifetime && safeEqual(match[2],sign(match[1]));
}
function requireLogin(req,res,next) {
  res.set('Cache-Control','no-store');
  if(isAuthenticated(req)) return next();
  if(req.path.startsWith('/api/')) return res.status(401).json({error:'Authentication required'});
  return res.redirect('/login');
}
app.get('/login',(req,res)=>{
  res.set('Cache-Control','no-store');
  res.type('html').send(\`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>EasyFind · Sign in</title><style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#f3f6fa;font:16px system-ui;color:#152d48}main{width:min(400px,90vw);padding:32px;background:white;border:1px solid #dbe3ee;border-radius:16px;box-shadow:0 6px 30px #14233710}h1{font-size:24px}label{display:block;margin:24px 0 8px}input,button{box-sizing:border-box;width:100%;font:inherit;padding:14px;border-radius:9px}input{border:1px solid #b8c6d8}button{background:#1764aa;color:white;border:0;margin-top:18px;cursor:pointer}.error{color:#ae3030}</style></head><body><main><h1>EasyFind Leads</h1><p>Private dashboard</p><form method="POST" action="/login"><label for="password">Password</label><input type="password" name="password" id="password" autocomplete="current-password" required><button type="submit">Sign in</button></form></main></body></html>\`);
});
app.post('/login',express.urlencoded({extended:false,limit:'2kb'}),(req,res)=>{
  res.set('Cache-Control','no-store');
  const ip=req.ip || 'unknown';const now=Date.now();const attempt=loginAttempts.get(ip)||{count:0,until:now+15*60*1000};
  if(now>attempt.until){attempt.count=0;attempt.until=now+15*60*1000;}
  if(attempt.count>=8)return res.status(429).send('Too many attempts. Try again in 15 minutes.');
  if(typeof req.body.password!=='string'||!safeEqual(req.body.password,dashboardPassword)){
    attempt.count++;loginAttempts.set(ip,attempt);return res.status(401).send('Incorrect password. <a href="/login">Try again</a>');
  }
  loginAttempts.delete(ip);
  const timestamp=String(now);const token=timestamp+'.'+sign(timestamp);
  res.cookie('efps_session',token,{httpOnly:true,secure:true,sameSite:'strict',maxAge:sessionLifetime,path:'/'});
  res.redirect('/');
});
app.post('/logout',requireLogin,(req,res)=>{res.clearCookie('efps_session',{path:'/',httpOnly:true,secure:true,sameSite:'strict'});res.redirect('/login')});
// All subsequent routes (including /api/leads and /api/sheet-info) are private.
app.use(requireLogin);

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
