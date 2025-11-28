# Documentation Index

Welcome to the Alumni Management System documentation! This index will help you find the information you need.

## Quick Links

| Document | Purpose | Best For |
|----------|---------|----------|
| [README.md](README.md) | Main documentation and getting started guide | New users, setup, features overview |
| [API_REFERENCE.md](API_REFERENCE.md) | Complete API documentation | Developers, integration, advanced usage |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution guidelines | Contributors, developers |
| [.env.example](.env.example) | Environment configuration template | Setup, configuration |

## Documentation by Topic

### Getting Started

1. **Installation & Setup**
   - See [README.md - Quick Start](README.md#quick-start)
   - See [README.md - Installation](README.md#installation)
   - See [.env.example](.env.example) for configuration

2. **First Steps**
   - [Local Database Setup](README.md#local-database-setup-testing-mode)
   - [Environment Variables](README.md#environment-variables)
   - [Running the Application](README.md#quick-start)

### Features & Usage

3. **Multi-Account Setup**
   - [Multi-Account Setup and Rate Limiting](README.md#multi-account-setup-and-rate-limiting)
   - [Setting Up Multiple LinkedIn Accounts](README.md#setting-up-multiple-linkedin-accounts)
   - [Account Rotation](README.md#how-account-rotation-works)

4. **Bulk Import Workflow**
   - [Bulk Import Workflow](README.md#bulk-import-workflow)
   - [Step-by-step Import Guide](README.md#step-1-prepare-your-data-file)
   - [Import Features](README.md#import-features)

5. **Scraping Control**
   - [Scraping Control Interface](README.md#scraping-control-interface)
   - [Queue Management](README.md#queue-statistics)
   - [Account Usage Monitoring](README.md#account-usage-monitoring)

6. **Web Interface**
   - [Web Interface Overview](README.md#web-interface)
   - [Dashboard](README.md#web-interface)
   - [Browse & Search](README.md#web-interface)
   - [Chatbot Queries](README.md#chatbot-queries)

7. **Automated Scraping**
   - [GitHub Actions Setup](README.md#automated-scraping-with-github-actions)
   - [Setting Up Secrets](README.md#setting-up-github-secrets)
   - [Workflow Features](README.md#workflow-features)

### Development

8. **API Reference**
   - [Database Operations](API_REFERENCE.md#database-operations)
   - [LinkedIn Scraper](API_REFERENCE.md#linkedin-scraper)
   - [Account Rotation](API_REFERENCE.md#account-rotation)
   - [Bulk Import](API_REFERENCE.md#bulk-import)
   - [B2 Storage](API_REFERENCE.md#b2-storage)
   - [NLP Chatbot](API_REFERENCE.md#nlp-chatbot)
   - [Data Models](API_REFERENCE.md#data-models)

9. **Contributing**
   - [Getting Started](CONTRIBUTING.md#getting-started)
   - [Development Setup](CONTRIBUTING.md#development-setup)
   - [Making Changes](CONTRIBUTING.md#making-changes)
   - [Testing](CONTRIBUTING.md#testing)
   - [Coding Standards](CONTRIBUTING.md#coding-standards)

10. **Project Architecture**
    - [Architecture Overview](README.md#project-structure)
    - [Component Design](CONTRIBUTING.md#project-architecture)
    - [Database Schema](README.md#database-schema)

### Troubleshooting

11. **Common Issues**
    - [Troubleshooting Guide](README.md#troubleshooting-guide)
    - [Database Issues](README.md#database-issues)
    - [LinkedIn Scraping Issues](README.md#linkedin-scraping-issues)
    - [Bulk Import Issues](README.md#bulk-import-issues)
    - [B2 Storage Issues](README.md#b2-storage-issues)
    - [Web Interface Issues](README.md#web-interface-issues)

12. **Error Messages**
    - [Common Error Messages](README.md#common-error-messages)
    - [Error Handling](API_REFERENCE.md#error-handling)

## Documentation by User Type

### For System Administrators

**Priority Reading:**
1. [Installation & Setup](README.md#installation)
2. [Environment Variables](README.md#environment-variables)
3. [Multi-Account Setup](README.md#multi-account-setup-and-rate-limiting)
4. [Database Setup](README.md#local-database-setup-testing-mode)
5. [GitHub Actions Setup](README.md#automated-scraping-with-github-actions)
6. [Troubleshooting Guide](README.md#troubleshooting-guide)

### For Alumni Relations Officers

**Priority Reading:**
1. [Web Interface](README.md#web-interface)
2. [Bulk Import Workflow](README.md#bulk-import-workflow)
3. [Scraping Control](README.md#scraping-control-interface)
4. [Chatbot Queries](README.md#chatbot-queries)
5. [Browse & Search](README.md#usage)

### For Developers

**Priority Reading:**
1. [API Reference](API_REFERENCE.md)
2. [Contributing Guide](CONTRIBUTING.md)
3. [Project Architecture](CONTRIBUTING.md#project-architecture)
4. [Development Setup](CONTRIBUTING.md#development-setup)
5. [Testing](CONTRIBUTING.md#testing)
6. [Coding Standards](CONTRIBUTING.md#coding-standards)

### For Contributors

**Priority Reading:**
1. [Contributing Guide](CONTRIBUTING.md)
2. [Development Setup](CONTRIBUTING.md#development-setup)
3. [Making Changes](CONTRIBUTING.md#making-changes)
4. [Pull Request Process](CONTRIBUTING.md#pull-request-process)
5. [Coding Standards](CONTRIBUTING.md#coding-standards)

## Quick Reference

### Environment Variables

See [.env.example](.env.example) for complete list with descriptions.

**Essential Variables:**
- Database: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- LinkedIn: `LINKEDIN_EMAIL_1`, `LINKEDIN_PASSWORD_1` (and additional accounts)
- B2 Storage: `B2_APPLICATION_KEY_ID`, `B2_APPLICATION_KEY`, `B2_BUCKET_NAME`
- Scraper: `SCRAPER_DAILY_LIMIT_PER_ACCOUNT`, `SCRAPER_MIN_DELAY`, `SCRAPER_MAX_DELAY`

### Common Commands

```bash
# Start local database
docker-compose up -d

# Initialize database
python -c "from alumni_system.database.init_db import init_database; init_database()"

# Run web interface
streamlit run alumni_system/frontend/app.py

# Run tests
pytest

# Manual scraping
python -m alumni_system.scraper.run --batch 2020 --max-profiles 50
```

### Support & Help

- **Questions**: Open a discussion on GitHub
- **Bugs**: Create an issue with reproduction steps
- **Features**: Open an issue to discuss before implementing
- **Security**: Email maintainers directly

## Documentation Updates

This documentation is maintained alongside the codebase. When contributing:

1. Update relevant documentation files
2. Keep examples up-to-date
3. Add troubleshooting entries for new issues
4. Update API reference for new functions
5. Add configuration examples for new features

Last Updated: November 2025
