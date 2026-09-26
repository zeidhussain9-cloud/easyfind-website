# 💻 Development Guide

Complete guide for setting up local development environment and contributing to the EasyFind Lead Management System.

## 📋 Table of Contents

- [Getting Started](#getting-started)
- [Development Environment Setup](#development-environment-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Code Style Guide](#code-style-guide)
- [Testing](#testing)
- [Debugging](#debugging)
- [Git Workflow](#git-workflow)
- [Contributing Guidelines](#contributing-guidelines)
- [Common Tasks](#common-tasks)
- [Troubleshooting](#troubleshooting)

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.12+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **Git** - [Download](https://git-scm.com/)
- **SQLite3** - Usually pre-installed on macOS/Linux
- **Code Editor** - VS Code recommended

### Recommended VS Code Extensions

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "bradlc.vscode-tailwindcss",
    "dsznajder.es7-react-js-snippets",
    "streetsidesoftware.code-spell-checker"
  ]
}
```

## 🛠️ Development Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/zeidhussain9-cloud/easyfind-website.git
cd easyfind-website/leads_automation
```

### 2. Backend Setup (Python)

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# OR
.venv\Scripts\activate     # Windows

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy pylint
```

### 3. Frontend Setup (React)

```bash
# Navigate to UI directory
cd leads-ui

# Install dependencies
npm install

# Install development dependencies
npm install --save-dev @testing-library/react @testing-library/jest-dom jest

# Return to root
cd ..
```

### 4. Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit with your local settings
nano .env
```

**Local Development `.env`:**
```bash
# Google Sheets (use your own test sheet)
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/service-account-key.json
SHEET_ID=your-test-sheet-id

# AWS Bedrock (optional - for AI classification)
AWS_REGION=us-east-1

# Google Gemini (alternative to Bedrock)
GOOGLE_API_KEY=your-api-key

# Database
DATABASE_PATH=./leads.db

# Logging
LOG_LEVEL=DEBUG
LOG_FILE=./development.log
```

### 5. Database Setup

```bash
# Create database from schema
sqlite3 leads.db < schema.sql

# Verify tables created
sqlite3 leads.db "SELECT name FROM sqlite_master WHERE type='table';"

# Expected output:
# leads
# conversations
# lead_lifecycle_events
```

### 6. Verify Installation

```bash
# Check Python version
python --version  # Should be 3.12+

# Check Node version
node --version    # Should be 18+

# Check installed packages
pip list
npm list --depth=0

# Run health check
python -c "import gspread, sqlite3; print('✅ Python environment OK')"
cd leads-ui && npm run build && echo "✅ Node environment OK"
```

## 📁 Project Structure

```
leads_automation/
│
├── 📄 Python Backend Scripts
│   ├── extract_whatsapp.py           # WhatsApp data extraction
│   ├── classify_leads.py             # Rule-based classification
│   ├── classify_with_bedrock.py      # AI classification (Bedrock)
│   ├── classify_leads_dual_model.py  # AI classification (Gemini)
│   ├── import_to_database_v2.py      # Import to SQLite
│   ├── sync_to_sheet_v2.py           # Sync to Google Sheets
│   └── bulk_assign_collections.py    # Bulk operations
│
├── 📊 Database
│   ├── schema.sql                    # Database schema
│   └── leads.db                      # SQLite database (git-ignored)
│
├── ⚙️ Configuration
│   └── config/
│       ├── taxonomy.json             # Classification rules
│       ├── rental_keywords.json      # Keyword patterns
│       ├── bangalore_locations.json  # Location mapping
│       ├── intent_keywords.json      # Intent detection
│       ├── personal_contacts.json    # Known contacts
│       └── internal_phones.json      # Internal numbers
│
├── 🎨 Frontend (React Dashboard)
│   └── leads-ui/
│       ├── public/                   # Static assets
│       ├── src/
│       │   ├── App.js                # Main component
│       │   ├── components/           # React components
│       │   │   ├── LeadsList.js
│       │   │   ├── LeadDetails.js
│       │   │   ├── ConversationView.js
│       │   │   └── Dashboard.js
│       │   ├── services/             # API services
│       │   │   └── gspreadService.js
│       │   └── styles/               # CSS/styling
│       ├── server.js                 # Express backend
│       ├── package.json              # Dependencies
│       └── render.yaml               # Deployment config
│
├── 📚 Documentation
│   ├── README.md                     # Main documentation
│   ├── DEPLOYMENT.md                 # Deployment guide
│   ├── DEVELOPMENT.md                # This file
│   ├── ARCHITECTURE.md               # System architecture
│   ├── API_DOCUMENTATION.md          # API reference
│   └── CHANGELOG.md                  # Version history
│
└── 🔧 Configuration Files
    ├── .gitignore                    # Git ignore rules
    ├── .env.example                  # Environment template
    ├── requirements.txt              # Python dependencies
    └── schema.sql                    # Database schema
```

## 🔄 Development Workflow

### Daily Workflow

```bash
# 1. Start your day - Update code
git pull origin main

# 2. Activate Python environment
source .venv/bin/activate

# 3. Start backend development server (if needed)
python -m http.server 8000

# 4. Start frontend development server
cd leads-ui
npm run dev

# 5. Open in browser
# Frontend: http://localhost:3000
# Backend: http://localhost:5000
```

### Making Changes

```bash
# 1. Create a feature branch
git checkout -b feature/your-feature-name

# 2. Make your changes
# Edit files...

# 3. Test your changes
pytest                          # Python tests
cd leads-ui && npm test        # React tests

# 4. Format code
black *.py                      # Python formatting
cd leads-ui && npm run format  # JavaScript formatting

# 5. Commit changes
git add .
git commit -m "feat: Add your feature description"

# 6. Push to GitHub
git push origin feature/your-feature-name

# 7. Create Pull Request on GitHub
```

## 🎨 Code Style Guide

### Python Style Guide

Follow [PEP 8](https://pep8.org/) conventions.

**Formatting:**
```bash
# Format with Black (line length: 88)
black *.py

# Check with flake8
flake8 *.py --max-line-length=88

# Type checking with mypy
mypy *.py
```

**Example Python Code:**
```python
"""
Module docstring: Brief description of the module.
"""

import os
import sys
from typing import List, Dict, Optional

import gspread
from google.oauth2.service_account import Credentials


def extract_conversations(
    phone_number: str,
    date_from: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, any]]:
    """
    Extract conversations for a specific phone number.
    
    Args:
        phone_number: E.164 format phone number
        date_from: ISO-8601 date to filter from
        limit: Maximum number of messages to return
        
    Returns:
        List of conversation dictionaries
        
    Raises:
        ValueError: If phone_number format is invalid
        ConnectionError: If database connection fails
    """
    # Implementation...
    pass


class LeadClassifier:
    """Lead classification using AI models."""
    
    def __init__(self, model: str = "bedrock"):
        """Initialize classifier with specified model."""
        self.model = model
        
    def classify(self, conversation: Dict) -> Dict:
        """Classify a conversation."""
        # Implementation...
        pass
```

### JavaScript/React Style Guide

Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript).

**Formatting:**
```bash
# Format with Prettier
npm run format

# Lint with ESLint
npm run lint
```

**Example React Component:**
```javascript
import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';
import { Box, Typography, CircularProgress } from '@mui/material';

/**
 * LeadsList component displays all leads from Google Sheets.
 *
 * @param {Object} props - Component props
 * @param {string} props.filter - Status filter
 * @param {Function} props.onLeadClick - Callback when lead is clicked
 */
const LeadsList = ({ filter, onLeadClick }) => {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchLeads = async () => {
      try {
        setLoading(true);
        const response = await axios.get('/api/leads', {
          params: { status: filter }
        });
        setLeads(response.data.data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchLeads();
  }, [filter]);

  if (loading) return <CircularProgress />;
  if (error) return <Typography color="error">{error}</Typography>;

  return (
    <Box>
      {leads.map(lead => (
        <LeadCard
          key={lead.phone_number}
          lead={lead}
          onClick={() => onLeadClick(lead)}
        />
      ))}
    </Box>
  );
};

LeadsList.propTypes = {
  filter: PropTypes.string,
  onLeadClick: PropTypes.func.isRequired
};

LeadsList.defaultProps = {
  filter: 'Active'
};

export default LeadsList;
```

### Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/).

**Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(api): Add endpoint to update lead priority

Added POST /api/leads/:phoneNumber/priority endpoint
that allows updating lead priority to High/Medium/Low.

Closes #42
```

```bash
fix(sync): Handle null values in Google Sheets sync

Fixed issue where null values in database caused
sync to fail. Now converts null to empty string.

Fixes #38
```

## 🧪 Testing

### Python Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest test_classification.py

# Run specific test
pytest test_classification.py::test_rental_inquiry
```

**Example Test:**
```python
import pytest
from classify_leads import classify_lead

def test_rental_inquiry_classification():
    """Test that rental inquiries are correctly classified."""
    lead = {
        'messages': [
            {'message_body': 'Looking for 2 BHK in Baner', 'direction': 'Incoming'}
        ]
    }
    
    category, priority, notes = classify_lead(lead)
    
    assert category == 'Rental Inquiry'
    assert priority == 'high'
    assert 'Baner' in notes
```

### React Testing

```bash
# Run all tests
cd leads-ui
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch
```

**Example Test:**
```javascript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import LeadsList from './LeadsList';

describe('LeadsList', () => {
  test('renders leads after fetching', async () => {
    render(<LeadsList filter="Active" onLeadClick={jest.fn()} />);
    
    await waitFor(() => {
      expect(screen.getByText('Ravi Kumar')).toBeInTheDocument();
    });
  });

  test('calls onLeadClick when lead is clicked', async () => {
    const handleClick = jest.fn();
    render(<LeadsList filter="Active" onLeadClick={handleClick} />);
    
    const leadCard = await screen.findByText('Ravi Kumar');
    userEvent.click(leadCard);
    
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

## 🐛 Debugging

### Python Debugging

**Using pdb:**
```python
import pdb

def classify_lead(lead):
    pdb.set_trace()  # Debugger stops here
    # Your code...
```

**Using VS Code:**
Add to `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal",
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    }
  ]
}
```

### React Debugging

**Browser DevTools:**
- Open Chrome DevTools (F12)
- Use React Developer Tools extension
- Add `debugger` statement in code

**VS Code:**
```json
{
  "name": "Chrome: Debug React",
  "type": "chrome",
  "request": "launch",
  "url": "http://localhost:3000",
  "webRoot": "${workspaceFolder}/leads-ui/src"
}
```

### Common Debugging Commands

```bash
# Check Python environment
which python
pip list

# Check Node environment
which node
npm list

# Check database
sqlite3 leads.db "SELECT COUNT(*) FROM leads;"

# Check Google Sheets connection
python -c "
from google.oauth2.service_account import Credentials
import gspread

creds = Credentials.from_service_account_file('key.json')
gc = gspread.authorize(creds)
print('✅ Connected to Google Sheets')
"

# Check API server
curl http://localhost:5000/health
```

## 🔀 Git Workflow

### Branch Naming Convention

```
feature/add-search-functionality
fix/sync-null-values
docs/update-api-docs
refactor/optimize-classification
test/add-unit-tests
chore/update-dependencies
```

### Pull Request Process

1. **Create Branch**
   ```bash
   git checkout -b feature/your-feature
   ```

2. **Make Changes and Commit**
   ```bash
   git add .
   git commit -m "feat: Your feature description"
   ```

3. **Keep Branch Updated**
   ```bash
   git fetch origin
   git rebase origin/main
   ```

4. **Push to GitHub**
   ```bash
   git push origin feature/your-feature
   ```

5. **Create Pull Request**
   - Go to GitHub repository
   - Click "New Pull Request"
   - Fill in PR template
   - Request reviewers

6. **Address Review Comments**
   ```bash
   # Make changes
   git add .
   git commit -m "fix: Address review comments"
   git push origin feature/your-feature
   ```

7. **Merge After Approval**
   - Squash and merge (preferred)
   - Delete branch after merge

## 🤝 Contributing Guidelines

### Code Review Checklist

**Before Submitting PR:**
- [ ] Code follows style guide
- [ ] All tests pass
- [ ] Added tests for new features
- [ ] Updated documentation
- [ ] No console.log or debug statements
- [ ] No hardcoded credentials or API keys
- [ ] Commit messages follow convention
- [ ] Branch is up to date with main

**For Reviewers:**
- [ ] Code is readable and maintainable
- [ ] No security vulnerabilities
- [ ] Performance is acceptable
- [ ] Edge cases are handled
- [ ] Error handling is proper
- [ ] Documentation is clear

### Issue Reporting

When reporting bugs, include:

```markdown
**Bug Description:**
Brief description of the issue

**Steps to Reproduce:**
1. Step one
2. Step two
3. Step three

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Environment:**
- OS: macOS 13.0
- Python: 3.12.0
- Node: 18.17.0
- Browser: Chrome 118

**Screenshots:**
(if applicable)

**Additional Context:**
Any other relevant information
```

## 📝 Common Tasks

### Add New API Endpoint

```javascript
// In leads-ui/server.js

app.get('/api/leads/stats', async (req, res) => {
  try {
    const stats = await gspreadService.getLeadStats();
    res.json(stats);
  } catch (error) {
    console.error('Error fetching stats:', error);
    res.status(500).json({ error: 'Failed to fetch stats' });
  }
});
```

### Add New Classification Rule

```python
# In classify_leads.py

def classify_lead(lead):
    messages = lead.get('messages', [])
    conversation_text = " ".join([
        msg.get('message_body', '') for msg in messages
    ]).lower()
    
    # Add your new rule
    if 'your_keyword' in conversation_text:
        return "Your Category", "priority", "Notes"
    
    # Existing rules...
```

### Add Database Migration

```sql
-- migrations/001_add_email_column.sql

ALTER TABLE leads ADD COLUMN email TEXT;

CREATE INDEX idx_leads_email ON leads(email);
```

```bash
# Apply migration
sqlite3 leads.db < migrations/001_add_email_column.sql
```

### Update Google Sheets Schema

```python
# In sync_to_sheet_v2.py

# Add new column to sync
headers = [
    'phone_number', 'customer_name', 'email',  # Added email
    'lead_status', 'priority'
    # ... other columns
]

# Update worksheet
worksheet.update('A1', [headers])
```

## 🔧 Troubleshooting

### Common Issues

**Issue: Import errors in Python**
```bash
# Solution: Ensure virtual environment is activated
source .venv/bin/activate
pip install -r requirements.txt
```

**Issue: npm install fails**
```bash
# Solution: Clear cache and reinstall
cd leads-ui
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

**Issue: Database locked**
```bash
# Solution: Close all connections and restart
sqlite3 leads.db "PRAGMA busy_timeout = 5000;"
```

**Issue: Google Sheets authentication fails**
```bash
# Solution: Verify service account permissions
# 1. Check JSON key is valid
# 2. Verify Sheet is shared with service account email
# 3. Check Google Sheets API is enabled
```

**Issue: Port already in use**
```bash
# Solution: Kill process using port
lsof -ti:5000 | xargs kill -9  # Backend
lsof -ti:3000 | xargs kill -9  # Frontend
```

## 📚 Additional Resources

- [Python Official Docs](https://docs.python.org/3/)
- [React Documentation](https://react.dev/)
- [Express.js Guide](https://expressjs.com/en/guide/routing.html)
- [Material-UI Components](https://mui.com/material-ui/getting-started/)
- [Google Sheets API](https://developers.google.com/sheets/api)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

## 🆘 Getting Help

- **GitHub Issues**: [Report bugs or request features](https://github.com/zeidhussain9-cloud/easyfind-website/issues)
- **Documentation**: Check docs/ folder
- **Email Support**: support@easyfindprops.com

---

**Happy Coding! 🚀**
