const { GoogleAuth } = require('google-auth-library');
const { GoogleSpreadsheet } = require('google-spreadsheet');

class GspreadService {
  constructor() {
    this.sheetId = process.env.SHEET_ID;
    this.doc = null;
  }

  async init() {
    try {
      const auth = new GoogleAuth({
        keyFile: process.env.GOOGLE_APPLICATION_CREDENTIALS,
        scopes: ['https://www.googleapis.com/auth/spreadsheets'],
      });

      this.doc = new GoogleSpreadsheet(this.sheetId, auth);
      await this.doc.loadInfo();
      console.log('Successfully connected to Google Sheet');
    } catch (error) {
      console.error('Error initializing Google Sheets:', error);
      throw error;
    }
  }

  async getLeadsData() {
    try {
      const leadsSheet = this.doc.sheetsByTitle['Leads'];
      const rows = await leadsSheet.getRows();
      return rows.map(row => row.toObject());
    } catch (error) {
      console.error('Error fetching leads data:', error);
      throw error;
    }
  }

  async getConversations(phoneNumber) {
    try {
      const convSheet = this.doc.sheetsByTitle['Conversations'];
      const rows = await convSheet.getRows();
      return rows
        .filter(row => row.get('Phone Number') === phoneNumber)
        .map(row => row.toObject());
    } catch (error) {
      console.error('Error fetching conversations:', error);
      throw error;
    }
  }

  async updateLeadStatus(phoneNumber, newStatus) {
    try {
      const leadsSheet = this.doc.sheetsByTitle['Leads'];
      const rows = await leadsSheet.getRows();
      const leadRow = rows.find(row => row.get('Phone Number') === phoneNumber);

      if (leadRow) {
        leadRow.set('Lead Status', newStatus);
        await leadRow.save();
        return true;
      }
      return false;
    } catch (error) {
      console.error('Error updating lead status:', error);
      throw error;
    }
  }

  async getExtractionData() {
    try {
      const logSheet = this.doc.sheetsByTitle['Extraction Log'];
      const rows = await logSheet.getRows();
      return rows.map(row => row.toObject());
    } catch (error) {
      console.error('Error fetching extraction data:', error);
      throw error;
    }
  }
}

const gspreadService = new GspreadService();
module.exports = { gspreadService };