# Changelog

All notable changes to the EasyFind Lead Management System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Real-time WhatsApp integration via webhooks
- Mobile application (React Native)
- Advanced analytics and predictive lead scoring
- Automated follow-up reminders and email notifications
- CRM integration (Salesforce, HubSpot)
- Role-based access control (RBAC)
- Multi-language support

## [1.0.0] - 2026-09-26

### Added - Initial Release

#### Core Features
- **WhatsApp Data Extraction**
  - Support for Android backups (crypt14, crypt15, plain DB)
  - Support for iOS backups (iTunes/Finder)
  - Date range filtering
  - Media file extraction
  - Contact name preservation

- **AI-Powered Lead Classification**
  - Dual AI provider support (AWS Bedrock Claude / Google Gemini)
  - Rule-based classification (Tier 1)
  - AI-based classification (Tier 2)
  - Intent extraction
  - Sentiment analysis
  - Entity extraction (BHK, location, budget, etc.)
  - 8-category taxonomy:
    - Qualified Lead
    - Cold Inquiry
    - Agent/Partner
    - Property Listing Sent
    - Vendor/Supplier
    - Personal/Family
    - Spam/Marketing
    - Internal

- **Database Management**
  - SQLite database with 3 tables:
    - `leads` - Master lead registry
    - `conversations` - Complete message log
    - `lead_lifecycle_events` - Audit trail
  - 3 views for common queries:
    - `v_active_leads` - Active leads with last conversation
    - `v_followup_today` - Leads requiring follow-up
    - `v_recent_events` - Recent lifecycle events
  - 15 performance indexes
  - 4 automated triggers for timestamps and status changes

- **Google Sheets Integration**
  - Real-time sync to Google Sheets
  - Service account authentication
  - Three-tab structure (Leads, Conversations, Events)
  - Batch updates for performance (1000 rows)
  - Bi-directional data flow support

- **Web Dashboard (React)**
  - Material-UI based interface
  - Lead list view with filtering
  - Individual lead details
  - Conversation viewer
  - Statistics and charts (Recharts)
  - Responsive design
  - Real-time data updates

#### Configuration
- Configuration-driven classification rules
- JSON-based keyword patterns:
  - `taxonomy.json` - Category definitions
  - `rental_keywords.json` - Rental detection patterns
  - `bangalore_locations.json` - Location mapping
  - `intent_keywords.json` - Intent detection
  - `personal_contacts.json` - Known personal contacts
  - `internal_phones.json` - Internal team numbers
  - `known_agents.json` - Partner agents
  - `promotional_keywords.json` - Spam detection

#### Documentation
- Comprehensive README with quick start guide
- Deployment guide for Render.com
- API documentation with all endpoints
- Development guide with coding standards
- Architecture documentation
- Environment variable templates
- Code examples in Python and JavaScript

#### Scripts
- `extract_whatsapp.py` - WhatsApp backup extraction wrapper
- `classify_with_bedrock.py` - AI classification with AWS Bedrock
- `classify_leads.py` - Rule-based classification
- `classify_leads_dual_model.py` - AI classification with Gemini
- `import_to_database_v2.py` - Import classified data to SQLite
- `sync_to_sheet_v2.py` - Sync database to Google Sheets
- `bulk_assign_collections.py` - Bulk lead operations
- `create_google_sheet.py` - Create new Google Sheet with tabs

#### Infrastructure
- Render.com deployment configuration
- Express.js backend server
- Google Sheets API integration
- AWS Bedrock integration
- Environment-based configuration
- Production-ready error handling

### Security
- Service account authentication for Google Sheets
- Environment variable management
- Credentials excluded from version control
- HTTPS enforcement (via Render)
- Input validation and sanitization

### Performance
- Batch processing for Google Sheets (1000 rows)
- Database indexing for fast queries
- Efficient AI classification with retry logic
- Optimized React rendering
- Connection pooling for database

---

## Version History Summary

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2026-09-26 | Initial release with complete feature set |

---

## Migration Guide

### From Development to v1.0.0

This is the initial release. No migration needed.

**Setup Steps:**
1. Install dependencies: `pip install -r requirements.txt`
2. Configure environment: Copy `.env.example` to `.env`
3. Initialize database: `sqlite3 leads.db < schema.sql`
4. Set up Google Sheets: Follow `DEPLOYMENT.md`
5. Run extraction: `python extract_whatsapp.py`
6. Classify leads: `python classify_with_bedrock.py`
7. Import to database: `python import_to_database_v2.py`
8. Sync to sheets: `python sync_to_sheet_v2.py`
9. Start dashboard: `cd leads-ui && npm start`

---

## Breaking Changes

### v1.0.0
- Initial release - no breaking changes

---

## Dependencies

### v1.0.0

**Python:**
- gspread >= 6.0.0
- boto3 >= 1.34.0
- whatsapp-chat-exporter >= 0.9.0
- pycryptodome >= 3.19.0
- See `requirements.txt` for complete list

**Node.js:**
- react: 18.2.0
- express: 4.18.2
- @mui/material: 5.14.18
- axios: 1.6.2
- See `leads-ui/package.json` for complete list

---

## Known Issues

### v1.0.0

1. **SQLite Concurrency**
   - **Issue**: SQLite has limited concurrent write support
   - **Impact**: May cause "database locked" errors under heavy load
   - **Workaround**: Use `PRAGMA busy_timeout` or migrate to PostgreSQL
   - **Status**: Acceptable for current scale (< 1000 leads)

2. **Google Sheets Rate Limits**
   - **Issue**: 500 requests per 100 seconds per project
   - **Impact**: Sync may fail for very large datasets
   - **Workaround**: Batch operations implemented (1000 rows)
   - **Status**: Mitigated with batching

3. **Render Free Tier Sleep**
   - **Issue**: Free tier services sleep after 15 minutes of inactivity
   - **Impact**: First request after sleep takes 30-60 seconds
   - **Workaround**: Upgrade to paid plan or use keep-alive pings
   - **Status**: Known limitation

4. **WhatsApp Backup Encryption**
   - **Issue**: Some Android 13+ backups use new encryption
   - **Impact**: May fail to extract certain backups
   - **Workaround**: Use older backup or unencrypted export
   - **Status**: Dependency limitation

---

## Contributors

- **Zeid Hussain** - Initial development and architecture
- **EasyFind Team** - Testing and feedback

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Support

For issues and questions:
- 📧 Email: support@easyfindprops.com
- 🐛 Issues: [GitHub Issues](https://github.com/zeidhussain9-cloud/easyfind-website/issues)
- 📖 Documentation: See README.md and other docs/

---

## Acknowledgments

- WhatsApp-Chat-Exporter team for backup extraction tool
- AWS Bedrock team for Claude AI access
- Google for Gemini AI and Sheets API
- Material-UI team for beautiful React components
- Render.com for hosting platform

---

**Last Updated:** September 26, 2026  
**Maintained By:** EasyFind Development Team
