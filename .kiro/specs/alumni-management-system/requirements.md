# Requirements Document

## Introduction

The Alumni Management System is a comprehensive platform designed to manage alumni data through automated LinkedIn profile scraping, structured database storage, cloud-based PDF archival, and an intelligent query interface. The system enables educational institutions to maintain up-to-date alumni records, track career progression, facilitate networking, and generate insights about alumni career paths. The system integrates web scraping, database management, cloud storage, web interfaces, and natural language processing to provide a complete alumni relationship management solution.

## Glossary

- **System**: The Alumni Management System as a whole
- **Alumni Database**: PostgreSQL relational database storing alumni records, job history, education history, and scraping logs
- **PostgreSQL**: Open-source relational database management system used for structured data storage
- **LinkedIn Scraper**: Playwright-based browser automation component that extracts profile data from LinkedIn by simulating human browsing behavior
- **Playwright**: Browser automation library that controls Chromium to navigate and extract data from web pages
- **Account Rotation Pool**: Collection of LinkedIn accounts used to distribute scraping load and avoid rate limits
- **Daily Scraping Limit**: Maximum number of profiles that can be scraped per LinkedIn account per day (configurable, recommended 50-100)
- **B2 Storage**: Backblaze B2 cloud storage service for storing LinkedIn profile PDFs as archival snapshots
- **PDF Snapshot**: Browser-generated PDF file of a LinkedIn profile page for archival purposes (not parsed, only stored)
- **Web Interface**: Streamlit-based frontend application for browsing and managing alumni data
- **Streamlit**: Python web framework for building data-driven web applications
- **NLP Chatbot**: Natural language processing component for querying alumni data conversationally
- **Scraping Job**: Automated workflow that periodically updates alumni data from LinkedIn
- **Scraping Queue**: List of alumni profiles waiting to be scraped, populated by Excel/CSV import or manual triggers
- **Profile Data**: Information extracted from LinkedIn including name, company, job history, and education
- **Job History**: Record of employment positions including company, role, dates, and location
- **Education History**: Record of academic credentials including institution, degree, field, and years
- **Admin Interface**: Web-based interface for manual CRUD operations on alumni records
- **Batch**: Graduation year or cohort identifier for grouping alumni
- **Roll Number**: Unique student identifier within the institution
- **Human Behavior Simulation**: Randomized delays, mouse movements, and navigation patterns to avoid detection as a bot

## Requirements

### Requirement 1

**User Story:** As a system administrator, I want to scrape LinkedIn profiles automatically with rate limiting and multi-account support, so that I can collect comprehensive alumni data without triggering LinkedIn's anti-bot detection or account suspension.

#### Acceptance Criteria

1. WHEN the System initializes the LinkedIn Scraper, THE System SHALL load multiple LinkedIn account credentials from environment variables in the format LINKEDIN_EMAIL_1, LINKEDIN_PASSWORD_1, LINKEDIN_EMAIL_2, LINKEDIN_PASSWORD_2
2. WHEN the System receives a LinkedIn profile URL, THE System SHALL select the next available account from the rotation pool and authenticate with those credentials
3. WHEN an account reaches the configured daily scraping limit, THE System SHALL mark that account as exhausted and rotate to the next available account
4. WHEN all accounts are exhausted for the day, THE System SHALL pause scraping and resume the next day or display a message indicating the daily limit has been reached
5. WHEN authentication succeeds, THE System SHALL navigate to the profile page and extract the alumni name, current company, current designation, and location
6. WHEN the profile page loads, THE System SHALL extract all job history entries including company name, designation, location, start date, end date, and employment type
7. WHEN the profile page loads, THE System SHALL extract all education history entries including institution name, degree, field of study, start year, end year, and grade
8. WHEN contact information is available on the profile, THE System SHALL extract email addresses and phone numbers
9. WHEN scraping completes successfully, THE System SHALL generate a PDF snapshot of the LinkedIn profile
10. WHEN multiple profiles are queued for scraping, THE System SHALL introduce random delays between requests ranging from the configured minimum to maximum delay seconds
11. WHEN the System performs scraping actions, THE System SHALL randomize mouse movements, scroll patterns, and page interaction timing to simulate human behavior
12. WHEN the System navigates between profiles, THE System SHALL occasionally visit other LinkedIn pages like the feed or search to avoid predictable patterns
13. WHEN LinkedIn presents a security checkpoint, THE System SHALL log the error, mark the account as requiring manual verification, and rotate to the next account
14. WHEN a scraping attempt fails, THE System SHALL retry up to the configured maximum retry count before marking the attempt as failed
15. WHEN the System tracks account usage, THE System SHALL store the number of profiles scraped per account per day in the database
16. WHEN the System resets daily limits, THE System SHALL reset all account usage counters at midnight UTC

### Requirement 2

**User Story:** As a system administrator, I want to store alumni data in a structured database, so that I can efficiently query and manage the information.

#### Acceptance Criteria

1. WHEN the System initializes, THE System SHALL create database tables for alumni, job history, education history, and scraping logs if they do not exist
2. WHEN scraped profile data is received, THE System SHALL insert or update the alumni record with personal information, contact details, and current position
3. WHEN job history data is received for an alumni, THE System SHALL store each employment record with company, designation, dates, location, and employment type
4. WHEN education history data is received for an alumni, THE System SHALL store each education record with institution, degree, field of study, and years
5. WHEN an alumni record is updated, THE System SHALL preserve the creation timestamp and update the modification timestamp
6. WHEN a scraping operation completes, THE System SHALL log the operation status, duration, errors, and PDF storage status in the scraping logs table
7. WHEN querying alumni data, THE System SHALL support filtering by batch, company, location, and text search across name and company fields
8. WHEN an alumni record is deleted, THE System SHALL cascade delete all associated job history and education history records

### Requirement 3

**User Story:** As a system administrator, I want to store LinkedIn profile PDFs in cloud storage for archival purposes, so that I can preserve profile snapshots cost-effectively without needing to parse them.

#### Acceptance Criteria

1. WHEN a LinkedIn profile is successfully scraped, THE System SHALL generate a PDF snapshot of the profile page using the browser's print-to-PDF functionality
2. WHEN a LinkedIn profile PDF is generated, THE System SHALL upload the PDF to the configured Backblaze B2 bucket using the B2 SDK
3. WHEN uploading to B2, THE System SHALL name the file using the pattern "linkedin_profiles/{roll_number}_{timestamp}.pdf"
4. WHEN the upload succeeds, THE System SHALL store the B2 file URL in the alumni record for future reference
5. WHEN the upload fails, THE System SHALL log the error and mark the PDF storage status as failed in the scraping log without failing the entire scraping operation
6. WHEN B2 credentials are invalid or the bucket does not exist, THE System SHALL raise a configuration error with a descriptive message
7. WHEN the administrator views an alumni record, THE System SHALL provide a download link to the stored PDF if available

### Requirement 4

**User Story:** As an alumni relations officer, I want to browse and filter alumni records through a web interface, so that I can quickly find specific alumni or groups.

#### Acceptance Criteria

1. WHEN the Web Interface loads, THE System SHALL display a dashboard showing total alumni count, number of batches, number of companies, and number of locations
2. WHEN the user navigates to the browse page, THE System SHALL display alumni records in a paginated table with configurable page size
3. WHEN the user applies filters for batch, company, or location, THE System SHALL return only alumni matching all selected filter criteria
4. WHEN the user enters a search query, THE System SHALL return alumni whose name or current company contains the search text
5. WHEN the user views the alumni table, THE System SHALL display columns for name, batch, roll number, current company, current designation, location, previous companies, and contact information
6. WHEN the user selects an alumni record, THE System SHALL display detailed information including full job history with all previous companies and roles
7. WHEN the user requests an export, THE System SHALL generate an Excel file containing all displayed alumni records with all visible columns
8. WHEN the user views alumni details, THE System SHALL display job history sorted by date with current position indicated

### Requirement 5

**User Story:** As an alumni relations officer, I want to query alumni data using natural language, so that I can find information without learning complex query syntax.

#### Acceptance Criteria

1. WHEN the user submits a natural language query to the NLP Chatbot, THE System SHALL parse the query to identify intent and entities
2. WHEN the query asks about alumni at a specific company, THE System SHALL return all alumni whose current company matches the specified company name
3. WHEN the query asks about alumni from a specific batch, THE System SHALL return all alumni whose batch matches the specified year
4. WHEN the query asks about alumni with a specific job title, THE System SHALL return all alumni whose current designation contains the specified title
5. WHEN the query asks for a count, THE System SHALL return the numerical count of matching alumni
6. WHEN the query asks about alumni in a location, THE System SHALL return all alumni whose location matches the specified location
7. WHEN the NLP Chatbot returns results, THE System SHALL display the response text and a formatted table of matching alumni records
8. WHEN the query cannot be understood, THE System SHALL provide a helpful error message with example queries

### Requirement 6

**User Story:** As a system administrator, I want to bulk import alumni data from Excel or CSV files and automatically trigger scraping, so that I can efficiently onboard large batches of alumni without manual entry.

#### Acceptance Criteria

1. WHEN the administrator uploads an Excel or CSV file with alumni data, THE System SHALL parse the file and detect column names flexibly matching variations like "Roll No.", "roll_number", "LinkedIn ID", "linkedin_url"
2. WHEN the uploaded file contains required columns for roll number and LinkedIn ID, THE System SHALL create or update alumni records for each row
3. WHEN the uploaded file contains LinkedIn usernames without full URLs, THE System SHALL automatically convert them to full LinkedIn profile URLs
4. WHEN the System creates alumni records from the uploaded file, THE System SHALL automatically queue each profile for LinkedIn scraping
5. WHEN the System processes the uploaded file, THE System SHALL skip duplicate entries based on roll number and log skipped records
6. WHEN the uploaded file is missing required columns, THE System SHALL display an error message indicating which columns are required
7. WHEN the administrator clicks the "Start Scraping" button after import, THE System SHALL begin processing the scraping queue with the configured delays and account rotation
8. WHEN scraping is in progress, THE System SHALL display real-time progress showing profiles completed, current account in use, and estimated time remaining
9. WHEN scraping completes for imported profiles, THE System SHALL update the alumni records with scraped data including current company, job history, and education history
10. WHEN the administrator uploads a file, THE System SHALL display a summary showing how many profiles will be imported and how many are new versus updates

### Requirement 11

**User Story:** As a system administrator, I want to manually add, edit, and delete individual alumni records, so that I can correct errors and handle special cases.

#### Acceptance Criteria

1. WHEN the administrator submits the add alumni form with name and roll number, THE System SHALL create a new alumni record with the provided information
2. WHEN the administrator attempts to add an alumni with a duplicate roll number, THE System SHALL reject the operation and display an error message
3. WHEN the administrator loads an alumni record by ID, THE System SHALL populate the edit form with all current field values
4. WHEN the administrator submits the edit form, THE System SHALL update the alumni record with the new values and update the modification timestamp
5. WHEN the administrator requests to delete an alumni by ID, THE System SHALL remove the alumni record and all associated job history and education history records

### Requirement 7

**User Story:** As a system administrator, I want to automate periodic scraping of alumni profiles, so that the database stays current without manual intervention.

#### Acceptance Criteria

1. WHEN the Scraping Job is triggered, THE System SHALL query the Alumni Database for profiles that have not been updated within the configured threshold days
2. WHEN the Scraping Job processes profiles, THE System SHALL scrape each profile using the LinkedIn Scraper with configured delays
3. WHEN the Scraping Job completes a profile scrape, THE System SHALL update the alumni record with new data and set the last scraped timestamp
4. WHEN the Scraping Job encounters an error for a profile, THE System SHALL log the error and continue processing remaining profiles
5. WHEN the Scraping Job is configured to run via GitHub Actions, THE System SHALL execute on the first day of January and July each year
6. WHEN the Scraping Job is triggered manually, THE System SHALL accept optional parameters for batch filter, maximum profile count, and force update flag
7. WHEN the force update flag is set, THE System SHALL scrape all profiles regardless of last scrape timestamp
8. WHEN the Scraping Job is triggered from an Excel/CSV import, THE System SHALL process only the newly imported profiles in the queue

### Requirement 8

**User Story:** As a system administrator, I want all sensitive credentials stored securely in environment variables, so that credentials are not exposed in code or version control.

#### Acceptance Criteria

1. WHEN the System initializes database connections, THE System SHALL read database host, port, name, username, and password from environment variables
2. WHEN the LinkedIn Scraper initializes, THE System SHALL read multiple LinkedIn account credentials from numbered environment variables (LINKEDIN_EMAIL_1, LINKEDIN_PASSWORD_1, LINKEDIN_EMAIL_2, LINKEDIN_PASSWORD_2, etc.)
3. WHEN the System loads LinkedIn accounts, THE System SHALL continue reading numbered credentials until it encounters a missing number in the sequence
4. WHEN the System uploads to B2 Storage, THE System SHALL read B2 application key ID, application key, and bucket name from environment variables
5. WHEN the System reads rate limit configuration, THE System SHALL read SCRAPER_DAILY_LIMIT_PER_ACCOUNT from environment variables with a default value of 80
6. WHEN a required environment variable is missing, THE System SHALL raise a configuration error with the name of the missing variable
7. WHEN the System runs in GitHub Actions, THE System SHALL read credentials from GitHub repository secrets
8. WHEN the System provides example configuration, THE System SHALL use placeholder values and never include actual credentials

### Requirement 9

**User Story:** As a developer, I want the system to handle errors gracefully, so that failures in one component do not crash the entire system.

#### Acceptance Criteria

1. WHEN the Alumni Database connection fails, THE System SHALL display an error message in the Web Interface and operate in demo mode
2. WHEN a LinkedIn scraping attempt fails after all retries, THE System SHALL log the failure and continue processing other profiles
3. WHEN B2 Storage upload fails, THE System SHALL log the error and mark the PDF storage status as failed without failing the entire scraping operation
4. WHEN the NLP Chatbot encounters a database error, THE System SHALL return an error message to the user without exposing internal details
5. WHEN the Web Interface encounters an exception, THE System SHALL display a user-friendly error message and log the full stack trace
6. WHEN LinkedIn presents a security checkpoint during scraping, THE System SHALL log the checkpoint event and skip the profile without retrying

### Requirement 10

**User Story:** As an alumni relations officer, I want to see previous companies for each alumni, so that I can understand their complete career progression.

#### Acceptance Criteria

1. WHEN the System displays the alumni browse table, THE System SHALL include a column showing all previous companies separated by semicolons
2. WHEN the user views alumni details, THE System SHALL display a complete job history table with company, role, location, duration, and employment type
3. WHEN the System displays job history, THE System SHALL indicate which position is the current position
4. WHEN the System displays job history, THE System SHALL sort positions by start date with most recent first
5. WHEN the System displays alumni details, THE System SHALL show summary statistics including total companies worked at and total positions held
