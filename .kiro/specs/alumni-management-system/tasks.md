# Implementation Plan

- [x] 1. Set up enhanced database schema with queue and account tracking
  - Add scraping_queue table for managing scraping tasks
  - Add account_usage table for rate limiting tracking
  - Create indexes for performance optimization
  - Implement database migration scripts
  - _Requirements: 2.1, 1.15_

- [x] 1.1 Write property test for database initialization
  - **Property 10: Database initialization is idempotent**
  - **Validates: Requirements 2.1**

- [x] 2. Implement account rotation and rate limiting system
  - Create LinkedInAccount data class
  - Implement AccountRotationManager class with account pool management
  - Add daily limit tracking and enforcement
  - Implement account exhaustion detection and rotation logic
  - Add account flagging for security checkpoints
  - Create daily reset functionality (midnight UTC)
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.15, 1.16_

- [x] 2.1 Write property test for account loading from environment
  - **Property 1: Account loading from environment variables**
  - **Validates: Requirements 1.1**

- [x] 2.2 Write property test for account selection
  - **Property 2: Account selection from available pool**
  - **Validates: Requirements 1.2**

- [x] 2.3 Write property test for account exhaustion
  - **Property 3: Account exhaustion triggers rotation**
  - **Validates: Requirements 1.3**

- [x] 2.4 Write property test for account usage tracking
  - **Property 8: Account usage tracking is accurate**
  - **Validates: Requirements 1.15**

- [x] 2.5 Write property test for daily reset
  - **Property 9: Daily reset clears all counters**
  - **Validates: Requirements 1.16**

- [x] 3. Implement human behavior simulation for scraping
  - Create HumanBehaviorSimulator class
  - Implement random delay with configurable bounds
  - Add random scroll patterns
  - Add random mouse movement simulation
  - Implement occasional visits to other LinkedIn pages (feed, search)
  - Add action sequence randomization
  - _Requirements: 1.10, 1.11, 1.12_

- [x] 3.1 Write property test for delay bounds
  - **Property 4: Delay bounds are respected**
  - **Validates: Requirements 1.10**

- [x] 3.2 Write property test for action randomization
  - **Property 5: Scraping actions are randomized**
  - **Validates: Requirements 1.11**

- [x] 4. Enhance LinkedIn scraper with multi-account support
  - Update LinkedInScraper to accept account parameter
  - Integrate AccountRotationManager into scraper
  - Add retry logic with configurable max retries
  - Implement security checkpoint detection
  - Add account rotation on checkpoint detection
  - Update scraping logs to include account_email
  - _Requirements: 1.2, 1.13, 1.14_

- [x] 4.1 Write property test for checkpoint rotation
  - **Property 6: Checkpoint detection triggers account rotation**
  - **Validates: Requirements 1.13**

- [x] 4.2 Write property test for retry limit
  - **Property 7: Retry limit is enforced**
  - **Validates: Requirements 1.14**

- [x] 5. Implement scraping queue management
  - Create ScrapingQueue model and CRUD operations
  - Implement add_to_scraping_queue function
  - Implement get_next_from_queue with priority support
  - Add queue status tracking (pending, in_progress, completed, failed)
  - Implement mark_queue_item_complete and mark_queue_item_failed
  - Add queue statistics functions (pending count, completed count, failed count)
  - _Requirements: 6.4, 7.1, 7.8_

- [x] 6. Enhance bulk import with automatic queue population
  - Update import_from_csv/excel to add profiles to scraping queue
  - Implement flexible column name detection (variations like "Roll No.", "roll_number")
  - Add LinkedIn username to URL conversion
  - Implement duplicate detection and skipping based on roll number
  - Add import summary generation (new vs updates)
  - Create validation for required columns
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.10_

- [x] 6.1 Write property test for column name detection
  - **Property 37: Column name detection is flexible**
  - **Validates: Requirements 6.1**

- [x] 6.2 Write property test for import record count
  - **Property 38: Import creates correct number of records**
  - **Validates: Requirements 6.2**

- [x] 6.3 Write property test for LinkedIn URL conversion
  - **Property 39: LinkedIn username conversion is consistent**
  - **Validates: Requirements 6.3**

- [x] 6.4 Write property test for queue population
  - **Property 40: Import queues all profiles**
  - **Validates: Requirements 6.4**

- [x] 6.5 Write property test for duplicate handling
  - **Property 41: Duplicate roll numbers are skipped**
  - **Validates: Requirements 6.5**

- [x] 6.6 Write property test for import summary
  - **Property 44: Import summary matches actual results**
  - **Validates: Requirements 6.10**

- [x] 7. Create scraping control interface in admin panel
  - Add "Scraping Control" tab to admin panel
  - Display queue statistics (pending, completed, failed)
  - Show account usage progress bars for each account
  - Add "Start Scraping" button
  - Implement real-time progress display during scraping
  - Show current account in use and estimated time remaining
  - Add ability to pause/resume scraping
  - _Requirements: 6.7, 6.8_

- [x] 7.1 Write property test for progress tracking
  - **Property 42: Progress tracking matches completion**
  - **Validates: Requirements 6.8**

- [x] 8. Implement scraping job orchestrator
  - Create ScrapingJobOrchestrator class
  - Implement queue-based processing with account rotation
  - Add error handling and logging for each profile
  - Implement graceful handling of account exhaustion
  - Add support for batch filtering and force update flag
  - Update last_scraped_at timestamp after successful scrape
  - Ensure errors in one profile don't stop batch processing
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.6, 7.7_

- [x] 8.1 Write property test for threshold query
  - **Property 50: Threshold query returns only stale profiles**
  - **Validates: Requirements 7.1**

- [x] 8.2 Write property test for timestamp updates
  - **Property 52: Scraping updates last_scraped_at timestamp**
  - **Validates: Requirements 7.3**

- [x] 8.3 Write property test for error isolation
  - **Property 53: Scraping errors are isolated**
  - **Validates: Requirements 7.4**

- [x] 8.4 Write property test for force update
  - **Property 54: Force update ignores timestamps**
  - **Validates: Requirements 7.7**

- [x] 9. Enhance database CRUD operations with new features
  - Update create_alumni to support upsert based on roll_number
  - Ensure timestamp preservation (created_at) and updates (updated_at)
  - Verify cascade deletion for job_history and education_history
  - Add get_unique_batches, get_unique_companies, get_unique_locations
  - Implement search_alumni with text search across name and company
  - Add filtering support for batch, company, location
  - _Requirements: 2.2, 2.5, 2.7, 2.8_

- [x] 9.1 Write property test for upsert behavior
  - **Property 11: Upsert prevents duplicates**
  - **Validates: Requirements 2.2**

- [x] 9.2 Write property test for timestamp preservation
  - **Property 14: Timestamp update preserves creation time**
  - **Validates: Requirements 2.5**

- [x] 9.3 Write property test for batch filtering
  - **Property 16: Batch filter returns only matching alumni**
  - **Validates: Requirements 2.7**

- [x] 9.4 Write property test for cascade deletion
  - **Property 17: Cascade deletion removes all related records**
  - **Validates: Requirements 2.8**

- [x] 10. Implement job and education history tracking
  - Ensure job_history stores all employment records with dates
  - Add is_current flag to identify current position
  - Implement sorting by start_date (descending)
  - Store education_history with institution, degree, field, years
  - Create get_job_history_by_alumni function
  - Create get_education_history_by_alumni function
  - _Requirements: 2.3, 2.4, 10.2, 10.3, 10.4_

- [x] 10.1 Write property test for job history count
  - **Property 12: Job history count invariant**
  - **Validates: Requirements 2.3**

- [x] 10.2 Write property test for education history count
  - **Property 13: Education history count invariant**
  - **Validates: Requirements 2.4**

- [x] 10.3 Write property test for job history sorting
  - **Property 30: Job history is sorted by date descending**
  - **Validates: Requirements 4.8, 10.4**

- [x] 11. Enhance B2 storage integration with error resilience
  - Update B2Client to handle upload failures gracefully
  - Ensure upload failures don't prevent database saves
  - Implement PDF naming convention: linkedin_profiles/{roll_number}_{timestamp}.pdf
  - Store B2 file URL in alumni.linkedin_pdf_url
  - Add get_download_url function for PDF access
  - Log B2 errors without failing scraping operation
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.7_

- [x] 11.1 Write property test for PDF generation
  - **Property 18: Successful scrape generates PDF**
  - **Validates: Requirements 3.1**

- [x] 11.2 Write property test for PDF naming
  - **Property 20: PDF naming convention is consistent**
  - **Validates: Requirements 3.3**

- [x] 11.3 Write property test for URL storage
  - **Property 21: Successful upload stores URL**
  - **Validates: Requirements 3.4**

- [x] 11.4 Write property test for B2 failure resilience
  - **Property 22: B2 upload failure doesn't fail scraping**
  - **Validates: Requirements 3.5**

- [x] 12. Update web interface dashboard with accurate statistics
  - Display total alumni count from database
  - Show number of unique batches
  - Show number of unique companies
  - Show number of unique locations
  - Ensure statistics match actual database counts
  - Add database connection status indicator
  - _Requirements: 4.1_

- [x] 12.1 Write property test for dashboard statistics
  - **Property 24: Dashboard statistics match database counts**
  - **Validates: Requirements 4.1**

- [x] 13. Implement pagination for browse alumni page
  - Add configurable page size selector (25, 50, 100)
  - Implement page number input
  - Calculate total pages correctly: ceil(total_records / page_size)
  - Display current page of records
  - Add navigation controls (previous, next, first, last)
  - _Requirements: 4.2_

- [x] 13.1 Write property test for pagination math
  - **Property 25: Pagination math is correct**
  - **Validates: Requirements 4.2**

- [x] 14. Enhance search and filter functionality
  - Implement multi-filter support (batch AND company AND location)
  - Add text search across name and current_company fields
  - Ensure search results contain search term in name or company
  - Display result count
  - Add filter reset button
  - _Requirements: 4.3, 4.4_

- [x] 14.1 Write property test for multiple filters
  - **Property 26: Multiple filters return intersection**
  - **Validates: Requirements 4.3**

- [x] 14.2 Write property test for search results
  - **Property 27: Search results contain search term**
  - **Validates: Requirements 4.4**

- [x] 15. Add previous companies column to browse table
  - Extract previous companies from job_history (where is_current=false)
  - Format as semicolon-separated list with role info
  - Display in browse alumni table
  - Include in Excel export
  - _Requirements: 4.5, 10.1_

- [x] 16. Enhance alumni details page with complete career history
  - Display full job history table with all fields
  - Show company, role, location, duration, employment type
  - Indicate current position visually (checkmark or badge)
  - Sort by start_date descending (most recent first)
  - Calculate and display summary statistics (total companies, total positions)
  - Show education history table
  - Add PDF download link if available
  - _Requirements: 4.6, 10.2, 10.3, 10.4, 10.5, 3.7_

- [x] 16.1 Write property test for detail view completeness
  - **Property 28: Detail view includes all job history**
  - **Validates: Requirements 4.6**

- [x] 16.2 Write property test for current position indication
  - **Property 58: Job history display indicates current position**
  - **Validates: Requirements 10.3**

- [x] 16.3 Write property test for summary statistics
  - **Property 59: Job history statistics match actual records**
  - **Validates: Requirements 10.5**

- [x] 17. Implement Excel export with all displayed data
  - Generate Excel file from displayed alumni records
  - Include all visible columns (name, batch, company, previous companies, etc.)
  - Ensure exported data matches displayed data exactly
  - Add timestamp to filename
  - Provide download button
  - _Requirements: 4.7_

- [x] 17.1 Write property test for export data integrity
  - **Property 29: Export contains displayed data**
  - **Validates: Requirements 4.7**

- [x] 18. Implement NLP chatbot query parser
  - Create QueryParser class
  - Implement intent detection (find_by_company, find_by_batch, find_by_title, find_by_location, count)
  - Extract entities from natural language (company names, years, titles, locations)
  - Handle combined queries (e.g., "software engineers at Google from batch 2020")
  - Generate SQL queries based on parsed intent and entities
  - _Requirements: 5.1_

- [x] 19. Implement chatbot query execution and response formatting
  - Create QueryExecutor class
  - Execute database queries based on parsed intent
  - Ensure company queries return only matching alumni
  - Ensure batch queries return only matching alumni
  - Ensure title queries return only matching alumni
  - Ensure location queries return only matching alumni
  - Calculate accurate counts for count queries
  - Format results as natural language response + table
  - Handle unrecognized queries with helpful error messages
  - _Requirements: 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8_

- [x] 19.1 Write property test for company queries
  - **Property 31: Company queries return only matching alumni**
  - **Validates: Requirements 5.2**

- [x] 19.2 Write property test for batch queries
  - **Property 32: Batch queries return only matching alumni**
  - **Validates: Requirements 5.3**

- [x] 19.3 Write property test for title queries
  - **Property 33: Title queries return only matching alumni**
  - **Validates: Requirements 5.4**

- [x] 19.4 Write property test for count accuracy
  - **Property 34: Count queries return accurate counts**
  - **Validates: Requirements 5.5**

- [x] 19.5 Write property test for location queries
  - **Property 35: Location queries return only matching alumni**
  - **Validates: Requirements 5.6**

- [x] 19.6 Write property test for response format
  - **Property 36: Chatbot responses include both text and table**
  - **Validates: Requirements 5.7**

- [x] 20. Enhance admin panel CRUD operations
  - Implement add alumni form with validation
  - Reject duplicate roll numbers with error message
  - Implement edit alumni form with data loading
  - Ensure edit form round-trip preserves data
  - Implement delete alumni with cascade deletion
  - Add confirmation dialog for delete operations
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

- [x] 20.1 Write property test for add operation
  - **Property 45: Add form creates exactly one record**
  - **Validates: Requirements 11.1**

- [x] 20.2 Write property test for duplicate rejection
  - **Property 46: Duplicate roll numbers are rejected**
  - **Validates: Requirements 11.2**

- [x] 20.3 Write property test for edit form round-trip
  - **Property 47: Edit form round-trip preserves data**
  - **Validates: Requirements 11.3**

- [x] 20.4 Write property test for edit persistence
  - **Property 48: Edit form updates persist**
  - **Validates: Requirements 11.4**

- [x] 20.5 Write property test for delete cascade
  - **Property 49: Delete removes all related records**
  - **Validates: Requirements 11.5**

- [x] 21. Implement scraping logs and audit trail
  - Ensure every scraping operation creates a log entry
  - Log status (success, failed, skipped), duration, errors
  - Log account_email used for scraping
  - Log PDF storage status
  - Add scraping logs view in admin panel
  - _Requirements: 2.6_

- [x] 21.1 Write property test for scraping logs
  - **Property 15: Scraping operations are logged**
  - **Validates: Requirements 2.6**

- [x] 22. Implement error handling and graceful degradation
  - Add demo mode for database connection failures
  - Ensure B2 failures don't stop scraping
  - Add user-friendly error messages for chatbot errors
  - Add user-friendly error messages for web interface errors
  - Implement error logging with appropriate levels
  - Display "Daily limit reached" message when all accounts exhausted
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 22.1 Write property test for error isolation
  - **Property 56: Scraping failures don't stop batch processing**
  - **Validates: Requirements 9.2**

- [x] 22.2 Write property test for B2 failure resilience
  - **Property 57: B2 failures don't prevent database saves**
  - **Validates: Requirements 9.3**

- [x] 23. Create GitHub Actions workflow for periodic scraping
  - Create .github/workflows/scraper.yml
  - Schedule for January 1st and July 1st at 00:00 UTC
  - Add workflow_dispatch for manual triggering
  - Configure environment variables from GitHub secrets
  - Run scraping job with update threshold of 180 days
  - Add error notifications
  - _Requirements: 7.5_

- [x] 24. Create comprehensive documentation
  - Update README with new features (multi-account, queue, scraping control)
  - Document environment variable configuration
  - Add setup instructions for multiple LinkedIn accounts
  - Document bulk import workflow
  - Add troubleshooting guide
  - Document API/function interfaces
  - _Requirements: 8.6_

- [x] 25. Final checkpoint - Ensure all tests pass
  - Run all unit tests
  - Run all property-based tests (100+ iterations each)
  - Run integration tests
  - Verify all acceptance criteria are met
  - Test bulk import → scraping → export workflow end-to-end
  - Ensure all tests pass, ask the user if questions arise
