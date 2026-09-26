const express = require('express');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 5000;

// Serve static files from the React app
app.use(express.static(path.join(__dirname, 'build')));

// API routes
app.get('/api/leads', async (req, res) => {
  try {
    const leadsData = await gspreadService.getLeadsData();
    res.json(leadsData);
  } catch (error) {
    console.error('Error fetching leads:', error);
    res.status(500).json({ error: 'Failed to fetch leads' });
  }
});

app.get('/api/conversations/:phoneNumber', async (req, res) => {
  try {
    const conversations = await gspreadService.getConversations(req.params.phoneNumber);
    res.json(conversations);
  } catch (error) {
    console.error('Error fetching conversations:', error);
    res.status(500).json({ error: 'Failed to fetch conversations' });
  }
});

app.post('/api/leads/:phoneNumber/status', async (req, res) => {
  try {
    const { status } = req.body;
    await gspreadService.updateLeadStatus(req.params.phoneNumber, status);
    res.json({ success: true });
  } catch (error) {
    console.error('Error updating lead status:', error);
    res.status(500).json({ error: 'Failed to update lead status' });
  }
});

// Handles any requests that don't match the ones above
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'build', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});

// Initialize gspread service
const { gspreadService } = require('./src/services/gspreadService');
gspreadService.init();