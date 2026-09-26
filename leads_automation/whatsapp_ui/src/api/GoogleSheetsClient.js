import { google } from 'googleapis';

const sheets = google.sheets('v4');

const SPREADSHEET_ID = 'your-spreadsheet-id';
const RANGE = 'Sheet1!A:D';

const auth = new google.auth.GoogleAuth({
  keyFile: 'path/to/your/service-account-key.json',
  scopes: ['https://www.googleapis.com/auth/spreadsheets'],
});

const getLeads = async () => {
  const client = await auth.getClient();
  const response = await sheets.spreadsheets.values.get({
    spreadsheetId: SPREADSHEET_ID,
    range: RANGE,
    auth: client,
  });
  const rows = response.data.values;
  return rows.map(row => ({
    id: row[0],
    phoneNumber: row[1],
    message: row[2],
    status: row[3],
  }));
};

const getLead = async (id) => {
  const leads = await getLeads();
  return leads.find(lead => lead.id === id);
};

const updateLeadStatus = async (id, status) => {
  const client = await auth.getClient();
  const leads = await getLeads();
  const rowIndex = leads.findIndex(lead => lead.id === id) + 1;
  await sheets.spreadsheets.values.update({
    spreadsheetId: SPREADSHEET_ID,
    range: `Sheet1!D${rowIndex}`,
    valueInputOption: 'RAW',
    resource: {
      values: [[status]],
    },
    auth: client,
  });
};

export { getLeads, getLead, updateLeadStatus };