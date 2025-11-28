"""
Scraping job coordinator for the Alumni Management System.

This module coordinates the LinkedIn scraping process:
1. Retrieves alumni records that need updating
2. Scrapes LinkedIn profiles
3. Stores scraped data in the database
4. Uploads PDFs to B2 storage
5. Logs all operations
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from ..database.connection import get_db_context
from ..database.crud import (
    create_education_history,
    create_job_history,
    create_scraping_log,
    get_all_alumni,
    get_alumni_by_id,
    get_next_from_queue,
    mark_queue_item_complete,
    mark_queue_item_failed,
    mark_queue_item_in_progress,
    update_alumni,
)
from ..database.models import Alumni
from ..storage.b2_client import get_storage_client
from ..utils.error_handling import (
    get_logger,
    handle_scraping_error,
    handle_storage_error,
    get_account_exhaustion_message,
    ErrorCategory,
    ErrorSeverity,
    log_error,
)
from .account_rotation import AccountRotationManager
from .linkedin_scraper import LinkedInScraper

logger = get_logger(__name__)


async def run_scraping_job(
    batch: Optional[str] = None,
    force_update: bool = False,
    max_profiles: int = 100,
    update_threshold_days: int = 180,
) -> dict:
    """
    Run the scraping job for alumni profiles.
    
    Args:
        batch: Filter by specific batch (optional).
        force_update: If True, update all profiles regardless of last scrape time.
        max_profiles: Maximum number of profiles to scrape in this run.
        update_threshold_days: Only update profiles not scraped within this many days.
    
    Returns:
        Dictionary with job statistics.
    """
    stats = {
        "total_processed": 0,
        "successful": 0,
        "failed": 0,
        "skipped": 0,
        "pdfs_uploaded": 0,
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": None,
        "errors": [],
    }

    try:
        with get_db_context() as db:
            # Get alumni records to process
            alumni_list = get_all_alumni(db, limit=max_profiles, batch=batch)

            # Filter by last scraped date if not forcing update
            threshold_date = datetime.utcnow() - timedelta(days=update_threshold_days)
            
            if not force_update:
                alumni_to_process = [
                    a for a in alumni_list
                    if not a.last_scraped_at or a.last_scraped_at < threshold_date
                ]
            else:
                alumni_to_process = alumni_list

            if not alumni_to_process:
                stats["skipped"] = len(alumni_list)
                stats["completed_at"] = datetime.utcnow().isoformat()
                return stats

            # Initialize scraper
            async with LinkedInScraper() as scraper:
                for alumni in alumni_to_process:
                    stats["total_processed"] += 1
                    
                    if not alumni.linkedin_url and not alumni.linkedin_id:
                        stats["skipped"] += 1
                        continue

                    linkedin_url = alumni.linkedin_url or f"https://www.linkedin.com/in/{alumni.linkedin_id}"
                    start_time = datetime.utcnow()

                    try:
                        # Scrape profile
                        profile_data = await scraper.scrape_profile(linkedin_url)
                        
                        # Get account email from scraper
                        account_email = scraper.get_current_account_email()

                        if profile_data:
                            # Update alumni record
                            await _update_alumni_from_profile(db, alumni, profile_data)

                            # Download and store PDF
                            pdf_stored = await _store_profile_pdf(
                                scraper, alumni, linkedin_url, db
                            )
                            if pdf_stored:
                                stats["pdfs_uploaded"] += 1

                            stats["successful"] += 1

                            # Log success
                            duration = (datetime.utcnow() - start_time).seconds
                            create_scraping_log(
                                db,
                                alumni_id=alumni.id,
                                linkedin_url=linkedin_url,
                                account_email=account_email,
                                status="success",
                                pdf_stored=pdf_stored,
                                duration_seconds=duration,
                            )
                        else:
                            stats["failed"] += 1
                            create_scraping_log(
                                db,
                                alumni_id=alumni.id,
                                linkedin_url=linkedin_url,
                                account_email=account_email,
                                status="failed",
                                error_message="Failed to scrape profile data",
                                duration_seconds=(datetime.utcnow() - start_time).seconds,
                            )

                    except Exception as e:
                        stats["failed"] += 1
                        stats["errors"].append(f"Alumni {alumni.id}: {str(e)}")
                        # Try to get account email, but it might not be available if login failed
                        account_email = scraper.get_current_account_email() if scraper else None
                        create_scraping_log(
                            db,
                            alumni_id=alumni.id,
                            linkedin_url=linkedin_url,
                            account_email=account_email,
                            status="failed",
                            error_message=str(e),
                            duration_seconds=(datetime.utcnow() - start_time).seconds,
                        )

    except Exception as e:
        stats["errors"].append(f"Job error: {str(e)}")

    stats["completed_at"] = datetime.utcnow().isoformat()
    return stats


async def _update_alumni_from_profile(
    db,
    alumni: Alumni,
    profile_data: dict,
) -> None:
    """
    Update alumni record with scraped profile data.
    
    Args:
        db: Database session.
        alumni: Alumni record to update.
        profile_data: Scraped profile data dictionary.
    """
    # Update basic info
    update_data = {
        "last_scraped_at": datetime.utcnow(),
    }

    if "name" in profile_data:
        update_data["name"] = profile_data["name"]
    if "current_company" in profile_data:
        update_data["current_company"] = profile_data["current_company"]
    if "current_designation" in profile_data:
        update_data["current_designation"] = profile_data["current_designation"]
    if "location" in profile_data:
        update_data["location"] = profile_data["location"]
    if "email" in profile_data:
        update_data["corporate_email"] = profile_data["email"]

    update_alumni(db, alumni.id, **update_data)

    # Update job history
    if "job_history" in profile_data and profile_data["job_history"]:
        # Clear existing job history (optional, might want to merge instead)
        for job in alumni.job_history:
            db.delete(job)
        db.flush()

        # Add new job history
        for job_data in profile_data["job_history"]:
            create_job_history(
                db,
                alumni_id=alumni.id,
                company_name=job_data.get("company_name", "Unknown"),
                designation=job_data.get("designation"),
                location=job_data.get("location"),
                start_date=job_data.get("start_date"),
                end_date=job_data.get("end_date"),
                is_current=job_data.get("is_current", False),
            )

    # Update education history
    if "education_history" in profile_data and profile_data["education_history"]:
        # Clear existing education history
        for edu in alumni.education_history:
            db.delete(edu)
        db.flush()

        # Add new education history
        for edu_data in profile_data["education_history"]:
            create_education_history(
                db,
                alumni_id=alumni.id,
                institution_name=edu_data.get("institution_name", "Unknown"),
                degree=edu_data.get("degree"),
                field_of_study=edu_data.get("field_of_study"),
                start_year=edu_data.get("start_year"),
                end_year=edu_data.get("end_year"),
            )


async def _store_profile_pdf(
    scraper: LinkedInScraper,
    alumni: Alumni,
    linkedin_url: str,
    db,
) -> bool:
    """
    Download and store LinkedIn profile PDF.
    
    Ensures upload failures don't prevent database saves.
    
    Args:
        scraper: LinkedIn scraper instance.
        alumni: Alumni record.
        linkedin_url: LinkedIn profile URL.
        db: Database session.
    
    Returns:
        True if PDF was stored successfully, False otherwise.
    """
    try:
        pdf_bytes = await scraper.download_profile_pdf(linkedin_url)
        if not pdf_bytes:
            logger.warning(f"No PDF bytes returned for alumni {alumni.id}")
            return False

        storage_client = get_storage_client()
        result = storage_client.upload_pdf_bytes(
            pdf_bytes,
            alumni.roll_number,
        )

        # Update alumni record with PDF URL using existing session
        update_alumni(db, alumni.id, linkedin_pdf_url=result["download_url"])

        logger.info(f"Successfully stored PDF for alumni {alumni.id}")
        return True

    except Exception as e:
        # Log error but don't fail the scraping operation
        logger.error(f"Error storing PDF for alumni {alumni.id}: {e}")
        return False


def run_scraping_job_sync(
    batch: Optional[str] = None,
    force_update: bool = False,
    max_profiles: int = 100,
) -> dict:
    """
    Synchronous wrapper for the scraping job.
    
    Args:
        batch: Filter by specific batch (optional).
        force_update: If True, update all profiles regardless of last scrape time.
        max_profiles: Maximum number of profiles to scrape.
    
    Returns:
        Dictionary with job statistics.
    """
    return asyncio.run(run_scraping_job(batch, force_update, max_profiles))



class ScrapingJobOrchestrator:
    """
    Orchestrates scraping jobs with queue-based processing and account rotation.
    
    Features:
    - Queue-based processing of alumni profiles
    - Multi-account rotation with rate limiting
    - Error handling and logging for each profile
    - Graceful handling of account exhaustion
    - Support for batch filtering and force update flag
    - Updates last_scraped_at timestamp after successful scrape
    - Ensures errors in one profile don't stop batch processing
    """
    
    def __init__(
        self,
        db: Session,
        account_manager: Optional[AccountRotationManager] = None,
        update_threshold_days: int = 180
    ):
        """
        Initialize the scraping job orchestrator.
        
        Args:
            db: Database session.
            account_manager: AccountRotationManager instance. If None, creates new one.
            update_threshold_days: Only update profiles not scraped within this many days.
        """
        self.db = db
        self.account_manager = account_manager or AccountRotationManager()
        self.update_threshold_days = update_threshold_days
        self.stats = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "skipped": 0,
            "pdfs_uploaded": 0,
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": None,
            "errors": [],
        }
    
    async def run_queue_based_scraping(
        self,
        max_profiles: Optional[int] = None,
        force_update: bool = False
    ) -> dict:
        """
        Run scraping job processing profiles from the queue.
        
        Args:
            max_profiles: Maximum number of profiles to process. If None, processes all.
            force_update: If True, scrape regardless of last_scraped_at timestamp.
        
        Returns:
            Dictionary with job statistics.
        """
        logger.info("Starting queue-based scraping job")
        
        processed_count = 0
        
        while True:
            # Check if we've reached max profiles
            if max_profiles and processed_count >= max_profiles:
                logger.info(f"Reached max profiles limit: {max_profiles}")
                break
            
            # Get next item from queue
            queue_item = get_next_from_queue(self.db)
            if not queue_item:
                logger.info("Queue is empty, stopping")
                break
            
            # Get alumni record
            alumni = get_alumni_by_id(self.db, queue_item.alumni_id)
            if not alumni:
                logger.warning(f"Alumni {queue_item.alumni_id} not found, marking as failed")
                mark_queue_item_failed(self.db, queue_item.id)
                self.stats["failed"] += 1
                continue
            
            # Check if profile needs updating (unless force_update is True)
            if not force_update and alumni.last_scraped_at:
                threshold_date = datetime.utcnow() - timedelta(days=self.update_threshold_days)
                if alumni.last_scraped_at >= threshold_date:
                    logger.info(f"Alumni {alumni.id} was recently scraped, skipping")
                    mark_queue_item_complete(self.db, queue_item.id)
                    self.stats["skipped"] += 1
                    processed_count += 1
                    continue
            
            # Mark as in progress
            mark_queue_item_in_progress(self.db, queue_item.id)
            
            # Process the profile
            success = await self._process_profile(alumni, queue_item.id)
            
            if success:
                mark_queue_item_complete(self.db, queue_item.id)
                self.stats["successful"] += 1
            else:
                mark_queue_item_failed(self.db, queue_item.id)
                self.stats["failed"] += 1
            
            self.stats["total_processed"] += 1
            processed_count += 1
        
        self.stats["completed_at"] = datetime.utcnow().isoformat()
        logger.info(f"Scraping job completed: {self.stats}")
        return self.stats
    
    async def run_threshold_based_scraping(
        self,
        batch: Optional[str] = None,
        max_profiles: Optional[int] = None,
        force_update: bool = False
    ) -> dict:
        """
        Run scraping job for profiles that haven't been updated recently.
        
        Args:
            batch: Filter by specific batch (optional).
            max_profiles: Maximum number of profiles to process.
            force_update: If True, scrape all profiles regardless of last_scraped_at.
        
        Returns:
            Dictionary with job statistics.
        """
        logger.info(f"Starting threshold-based scraping job (threshold: {self.update_threshold_days} days)")
        
        # Get alumni records to process
        alumni_list = get_all_alumni(self.db, limit=max_profiles or 1000, batch=batch)
        
        # Filter by last scraped date if not forcing update
        if not force_update:
            threshold_date = datetime.utcnow() - timedelta(days=self.update_threshold_days)
            alumni_to_process = [
                a for a in alumni_list
                if not a.last_scraped_at or a.last_scraped_at < threshold_date
            ]
        else:
            alumni_to_process = alumni_list
        
        logger.info(f"Found {len(alumni_to_process)} profiles to process")
        
        if not alumni_to_process:
            self.stats["skipped"] = len(alumni_list)
            self.stats["completed_at"] = datetime.utcnow().isoformat()
            return self.stats
        
        # Process each profile
        for alumni in alumni_to_process:
            success = await self._process_profile(alumni)
            
            if success:
                self.stats["successful"] += 1
            else:
                self.stats["failed"] += 1
            
            self.stats["total_processed"] += 1
        
        self.stats["completed_at"] = datetime.utcnow().isoformat()
        logger.info(f"Scraping job completed: {self.stats}")
        return self.stats
    
    async def _process_profile(
        self,
        alumni: Alumni,
        queue_id: Optional[int] = None
    ) -> bool:
        """
        Process a single alumni profile with account rotation and error handling.
        
        Args:
            alumni: Alumni record to process.
            queue_id: Optional queue item ID for logging.
        
        Returns:
            True if successful, False otherwise.
        """
        if not alumni.linkedin_url and not alumni.linkedin_id:
            logger.warning(f"Alumni {alumni.id} has no LinkedIn URL or ID, skipping")
            self.stats["skipped"] += 1
            return False
        
        linkedin_url = alumni.linkedin_url or f"https://www.linkedin.com/in/{alumni.linkedin_id}"
        start_time = datetime.utcnow()
        
        # Try scraping with account rotation
        max_account_attempts = len(self.account_manager.accounts)
        attempt = 0
        
        while attempt < max_account_attempts:
            # Get next available account
            account = self.account_manager.get_next_account()
            
            if not account:
                logger.error("All accounts exhausted, stopping")
                self._log_scraping_failure(
                    alumni,
                    linkedin_url,
                    "All accounts exhausted",
                    start_time,
                    None
                )
                return False
            
            logger.info(f"Processing alumni {alumni.id} with account {account.email}")
            
            try:
                # Create scraper with specific account
                async with LinkedInScraper(account=account) as scraper:
                    # Login
                    login_success = await scraper.login(account)
                    if not login_success:
                        logger.error(f"Login failed for account {account.email}")
                        attempt += 1
                        continue
                    
                    # Scrape profile
                    profile_data = await scraper.scrape_profile(linkedin_url)
                    
                    if profile_data:
                        # Update alumni record
                        await self._update_alumni_from_profile(alumni, profile_data)
                        
                        # Increment account usage
                        self.account_manager.increment_usage(account.email)
                        
                        # Try to download and store PDF (don't fail if this fails)
                        pdf_stored = await self._store_profile_pdf_safe(
                            scraper,
                            alumni,
                            linkedin_url
                        )
                        if pdf_stored:
                            self.stats["pdfs_uploaded"] += 1
                        
                        # Log success
                        duration = (datetime.utcnow() - start_time).seconds
                        create_scraping_log(
                            self.db,
                            alumni_id=alumni.id,
                            linkedin_url=linkedin_url,
                            account_email=account.email,
                            status="success",
                            pdf_stored=pdf_stored,
                            duration_seconds=duration,
                        )
                        
                        logger.info(f"Successfully scraped alumni {alumni.id}")
                        return True
                    else:
                        logger.warning(f"No profile data returned for alumni {alumni.id}")
                        self._log_scraping_failure(
                            alumni,
                            linkedin_url,
                            "No profile data returned",
                            start_time,
                            account.email
                        )
                        return False
            
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Error scraping alumni {alumni.id}: {error_msg}")
                
                # Check if it's a security checkpoint
                if "checkpoint" in error_msg.lower() or "challenge" in error_msg.lower():
                    logger.warning(f"Security checkpoint detected for account {account.email}, flagging")
                    self.account_manager.mark_account_flagged(account.email)
                    attempt += 1
                    continue
                else:
                    # Other error - log and fail
                    self._log_scraping_failure(
                        alumni,
                        linkedin_url,
                        error_msg,
                        start_time,
                        account.email
                    )
                    self.stats["errors"].append(f"Alumni {alumni.id}: {error_msg}")
                    return False
        
        # All account attempts exhausted
        logger.error(f"Failed to scrape alumni {alumni.id} after {max_account_attempts} account attempts")
        return False
    
    async def _update_alumni_from_profile(
        self,
        alumni: Alumni,
        profile_data: dict
    ) -> None:
        """
        Update alumni record with scraped profile data.
        
        Args:
            alumni: Alumni record to update.
            profile_data: Scraped profile data dictionary.
        """
        # Update basic info
        update_data = {
            "last_scraped_at": datetime.utcnow(),
        }
        
        if "name" in profile_data:
            update_data["name"] = profile_data["name"]
        if "current_company" in profile_data:
            update_data["current_company"] = profile_data["current_company"]
        if "current_designation" in profile_data:
            update_data["current_designation"] = profile_data["current_designation"]
        if "location" in profile_data:
            update_data["location"] = profile_data["location"]
        if "email" in profile_data:
            update_data["corporate_email"] = profile_data["email"]
        
        update_alumni(self.db, alumni.id, **update_data)
        
        # Update job history
        if "job_history" in profile_data and profile_data["job_history"]:
            # Clear existing job history
            for job in alumni.job_history:
                self.db.delete(job)
            self.db.flush()
            
            # Add new job history
            for job_data in profile_data["job_history"]:
                create_job_history(
                    self.db,
                    alumni_id=alumni.id,
                    company_name=job_data.get("company_name", "Unknown"),
                    designation=job_data.get("designation"),
                    location=job_data.get("location"),
                    start_date=job_data.get("start_date"),
                    end_date=job_data.get("end_date"),
                    is_current=job_data.get("is_current", False),
                )
        
        # Update education history
        if "education_history" in profile_data and profile_data["education_history"]:
            # Clear existing education history
            for edu in alumni.education_history:
                self.db.delete(edu)
            self.db.flush()
            
            # Add new education history
            for edu_data in profile_data["education_history"]:
                create_education_history(
                    self.db,
                    alumni_id=alumni.id,
                    institution_name=edu_data.get("institution_name", "Unknown"),
                    degree=edu_data.get("degree"),
                    field_of_study=edu_data.get("field_of_study"),
                    start_year=edu_data.get("start_year"),
                    end_year=edu_data.get("end_year"),
                )
    
    async def _store_profile_pdf_safe(
        self,
        scraper: LinkedInScraper,
        alumni: Alumni,
        linkedin_url: str
    ) -> bool:
        """
        Download and store LinkedIn profile PDF with error handling.
        
        Ensures that PDF storage failures don't fail the entire scraping operation.
        
        Args:
            scraper: LinkedIn scraper instance.
            alumni: Alumni record.
            linkedin_url: LinkedIn profile URL.
        
        Returns:
            True if PDF was stored successfully, False otherwise.
        """
        try:
            pdf_bytes = await scraper.download_profile_pdf(linkedin_url)
            if not pdf_bytes:
                logger.warning(f"No PDF bytes returned for alumni {alumni.id}")
                return False
            
            storage_client = get_storage_client()
            result = storage_client.upload_pdf_bytes(
                pdf_bytes,
                alumni.roll_number,
            )
            
            # Update alumni record with PDF URL
            update_alumni(self.db, alumni.id, linkedin_pdf_url=result["download_url"])
            
            logger.info(f"Successfully stored PDF for alumni {alumni.id}")
            return True
        
        except Exception as e:
            # Log error but don't fail the scraping operation
            logger.error(f"Error storing PDF for alumni {alumni.id}: {e}")
            self.stats["errors"].append(f"PDF storage failed for alumni {alumni.id}: {str(e)}")
            return False
    
    def _log_scraping_failure(
        self,
        alumni: Alumni,
        linkedin_url: str,
        error_message: str,
        start_time: datetime,
        account_email: Optional[str]
    ) -> None:
        """
        Log a scraping failure to the database.
        
        Args:
            alumni: Alumni record.
            linkedin_url: LinkedIn profile URL.
            error_message: Error message.
            start_time: Start time of scraping attempt.
            account_email: Email of account used (if any).
        """
        duration = (datetime.utcnow() - start_time).seconds
        create_scraping_log(
            self.db,
            alumni_id=alumni.id,
            linkedin_url=linkedin_url,
            account_email=account_email,
            status="failed",
            error_message=error_message,
            pdf_stored=False,
            duration_seconds=duration,
        )


def run_orchestrated_scraping_job(
    batch: Optional[str] = None,
    force_update: bool = False,
    max_profiles: Optional[int] = None,
    update_threshold_days: int = 180,
    use_queue: bool = False
) -> dict:
    """
    Run an orchestrated scraping job with account rotation.
    
    Args:
        batch: Filter by specific batch (optional).
        force_update: If True, update all profiles regardless of last scrape time.
        max_profiles: Maximum number of profiles to scrape.
        update_threshold_days: Only update profiles not scraped within this many days.
        use_queue: If True, process from queue. Otherwise use threshold-based.
    
    Returns:
        Dictionary with job statistics.
    """
    async def _run():
        with get_db_context() as db:
            orchestrator = ScrapingJobOrchestrator(
                db=db,
                update_threshold_days=update_threshold_days
            )
            
            if use_queue:
                return await orchestrator.run_queue_based_scraping(
                    max_profiles=max_profiles,
                    force_update=force_update
                )
            else:
                return await orchestrator.run_threshold_based_scraping(
                    batch=batch,
                    max_profiles=max_profiles,
                    force_update=force_update
                )
    
    return asyncio.run(_run())
