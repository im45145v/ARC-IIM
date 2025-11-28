"""
CRUD operations for the Alumni Management System.

Provides functions for Creating, Reading, Updating, and Deleting
alumni records and related data.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from .models import Alumni, EducationHistory, JobHistory, ScrapingLog, ScrapingQueue


# =============================================================================
# Alumni CRUD Operations
# =============================================================================


def create_alumni(db: Session, **kwargs) -> Alumni:
    """
    Create a new alumni record or update existing one (upsert based on roll_number).
    
    If an alumni with the same roll_number exists, updates the existing record
    while preserving the created_at timestamp.
    
    Args:
        db: Database session.
        **kwargs: Alumni field values.
    
    Returns:
        Created or updated Alumni object.
    """
    roll_number = kwargs.get('roll_number')
    
    if roll_number:
        # Check if alumni with this roll_number already exists
        existing_alumni = get_alumni_by_roll_number(db, roll_number)
        
        if existing_alumni:
            # Update existing record, preserving created_at
            for key, value in kwargs.items():
                if hasattr(existing_alumni, key) and key != 'created_at':
                    setattr(existing_alumni, key, value)
            
            existing_alumni.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing_alumni)
            return existing_alumni
    
    # Create new record
    alumni = Alumni(**kwargs)
    db.add(alumni)
    db.commit()
    db.refresh(alumni)
    return alumni


def get_alumni_by_id(db: Session, alumni_id: int) -> Optional[Alumni]:
    """
    Get an alumni record by ID.
    
    Args:
        db: Database session.
        alumni_id: Alumni ID.
    
    Returns:
        Alumni object or None if not found.
    """
    return db.query(Alumni).filter(Alumni.id == alumni_id).first()


def get_alumni_by_roll_number(db: Session, roll_number: str) -> Optional[Alumni]:
    """
    Get an alumni record by roll number.
    
    Args:
        db: Database session.
        roll_number: Roll number.
    
    Returns:
        Alumni object or None if not found.
    """
    return db.query(Alumni).filter(Alumni.roll_number == roll_number).first()


def get_alumni_by_linkedin_id(db: Session, linkedin_id: str) -> Optional[Alumni]:
    """
    Get an alumni record by LinkedIn ID.
    
    Args:
        db: Database session.
        linkedin_id: LinkedIn ID/username.
    
    Returns:
        Alumni object or None if not found.
    """
    return db.query(Alumni).filter(Alumni.linkedin_id == linkedin_id).first()


def get_all_alumni(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    batch: Optional[str] = None,
    company: Optional[str] = None,
    designation: Optional[str] = None,
    location: Optional[str] = None,
) -> list[Alumni]:
    """
    Get all alumni records with optional filtering.
    
    Args:
        db: Database session.
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        batch: Filter by batch.
        company: Filter by current company (partial match).
        designation: Filter by current designation (partial match).
        location: Filter by location (partial match).
    
    Returns:
        List of Alumni objects with job_history eagerly loaded.
    """
    from sqlalchemy.orm import joinedload
    
    query = db.query(Alumni).options(joinedload(Alumni.job_history))
    
    if batch:
        query = query.filter(Alumni.batch == batch)
    if company:
        query = query.filter(Alumni.current_company.ilike(f"%{company}%"))
    if designation:
        query = query.filter(Alumni.current_designation.ilike(f"%{designation}%"))
    if location:
        query = query.filter(Alumni.location.ilike(f"%{location}%"))
    
    return query.offset(skip).limit(limit).all()


def get_alumni_count(db: Session) -> int:
    """
    Get total count of alumni records.
    
    Args:
        db: Database session.
    
    Returns:
        Total number of alumni records.
    """
    return db.query(Alumni).count()


def search_alumni(
    db: Session,
    query: str,
    skip: int = 0,
    limit: int = 100,
    batch: Optional[str] = None,
    company: Optional[str] = None,
    designation: Optional[str] = None,
    location: Optional[str] = None,
) -> list[Alumni]:
    """
    Search alumni by name or company with optional filtering.
    
    Args:
        db: Database session.
        query: Search query string (searches in name and current_company).
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        batch: Filter by batch.
        company: Filter by current company (partial match).
        designation: Filter by current designation (partial match).
        location: Filter by location (partial match).
    
    Returns:
        List of matching Alumni objects with job_history eagerly loaded.
    """
    from sqlalchemy.orm import joinedload
    
    search_pattern = f"%{query}%"
    
    # Start with search condition (name OR current_company) and eager load job_history
    query_obj = db.query(Alumni).options(joinedload(Alumni.job_history)).filter(
        or_(
            Alumni.name.ilike(search_pattern),
            Alumni.current_company.ilike(search_pattern),
        )
    )
    
    # Apply additional filters (AND conditions)
    if batch:
        query_obj = query_obj.filter(Alumni.batch == batch)
    if company:
        query_obj = query_obj.filter(Alumni.current_company.ilike(f"%{company}%"))
    if designation:
        query_obj = query_obj.filter(Alumni.current_designation.ilike(f"%{designation}%"))
    if location:
        query_obj = query_obj.filter(Alumni.location.ilike(f"%{location}%"))
    
    return query_obj.offset(skip).limit(limit).all()


def update_alumni(
    db: Session,
    alumni_id: int,
    **kwargs,
) -> Optional[Alumni]:
    """
    Update an alumni record.
    
    Args:
        db: Database session.
        alumni_id: Alumni ID.
        **kwargs: Fields to update.
    
    Returns:
        Updated Alumni object or None if not found.
    """
    alumni = get_alumni_by_id(db, alumni_id)
    if not alumni:
        return None
    
    for key, value in kwargs.items():
        if hasattr(alumni, key):
            setattr(alumni, key, value)
    
    alumni.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(alumni)
    return alumni


def delete_alumni(db: Session, alumni_id: int) -> bool:
    """
    Delete an alumni record.
    
    Args:
        db: Database session.
        alumni_id: Alumni ID.
    
    Returns:
        True if deleted, False if not found.
    """
    alumni = get_alumni_by_id(db, alumni_id)
    if not alumni:
        return False
    
    db.delete(alumni)
    db.commit()
    return True


def get_unique_batches(db: Session) -> list[str]:
    """
    Get all unique batch values.
    
    Args:
        db: Database session.
    
    Returns:
        List of unique batch values.
    """
    result = db.query(Alumni.batch).distinct().all()
    return [r[0] for r in result if r[0]]


def get_unique_companies(db: Session) -> list[str]:
    """
    Get all unique current company values.
    
    Args:
        db: Database session.
    
    Returns:
        List of unique company values.
    """
    result = db.query(Alumni.current_company).distinct().all()
    return [r[0] for r in result if r[0]]


def get_unique_locations(db: Session) -> list[str]:
    """
    Get all unique location values.
    
    Args:
        db: Database session.
    
    Returns:
        List of unique location values.
    """
    result = db.query(Alumni.location).distinct().all()
    return [r[0] for r in result if r[0]]


# =============================================================================
# Job History CRUD Operations
# =============================================================================


def create_job_history(db: Session, alumni_id: int, **kwargs) -> JobHistory:
    """
    Create a new job history record.
    
    Args:
        db: Database session.
        alumni_id: Alumni ID.
        **kwargs: JobHistory field values.
    
    Returns:
        Created JobHistory object.
    """
    job = JobHistory(alumni_id=alumni_id, **kwargs)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_job_history_by_alumni(db: Session, alumni_id: int) -> list[JobHistory]:
    """
    Get all job history records for an alumni.
    
    Args:
        db: Database session.
        alumni_id: Alumni ID.
    
    Returns:
        List of JobHistory objects.
    """
    return (
        db.query(JobHistory)
        .filter(JobHistory.alumni_id == alumni_id)
        .order_by(JobHistory.start_date.desc())
        .all()
    )


def delete_job_history(db: Session, job_id: int) -> bool:
    """
    Delete a job history record.
    
    Args:
        db: Database session.
        job_id: JobHistory ID.
    
    Returns:
        True if deleted, False if not found.
    """
    job = db.query(JobHistory).filter(JobHistory.id == job_id).first()
    if not job:
        return False
    
    db.delete(job)
    db.commit()
    return True


# =============================================================================
# Education History CRUD Operations
# =============================================================================


def create_education_history(db: Session, alumni_id: int, **kwargs) -> EducationHistory:
    """
    Create a new education history record.
    
    Args:
        db: Database session.
        alumni_id: Alumni ID.
        **kwargs: EducationHistory field values.
    
    Returns:
        Created EducationHistory object.
    """
    education = EducationHistory(alumni_id=alumni_id, **kwargs)
    db.add(education)
    db.commit()
    db.refresh(education)
    return education


def get_education_history_by_alumni(db: Session, alumni_id: int) -> list[EducationHistory]:
    """
    Get all education history records for an alumni.
    
    Args:
        db: Database session.
        alumni_id: Alumni ID.
    
    Returns:
        List of EducationHistory objects.
    """
    return (
        db.query(EducationHistory)
        .filter(EducationHistory.alumni_id == alumni_id)
        .order_by(EducationHistory.end_year.desc())
        .all()
    )


def delete_education_history(db: Session, education_id: int) -> bool:
    """
    Delete an education history record.
    
    Args:
        db: Database session.
        education_id: EducationHistory ID.
    
    Returns:
        True if deleted, False if not found.
    """
    education = db.query(EducationHistory).filter(EducationHistory.id == education_id).first()
    if not education:
        return False
    
    db.delete(education)
    db.commit()
    return True


# =============================================================================
# Scraping Log CRUD Operations
# =============================================================================


def create_scraping_log(db: Session, **kwargs) -> ScrapingLog:
    """
    Create a new scraping log record.
    
    Args:
        db: Database session.
        **kwargs: ScrapingLog field values.
    
    Returns:
        Created ScrapingLog object.
    """
    log = ScrapingLog(**kwargs)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_scraping_logs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
) -> list[ScrapingLog]:
    """
    Get scraping logs with optional filtering.
    
    Args:
        db: Database session.
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        status: Filter by status.
    
    Returns:
        List of ScrapingLog objects.
    """
    query = db.query(ScrapingLog)
    
    if status:
        query = query.filter(ScrapingLog.status == status)
    
    return query.order_by(ScrapingLog.created_at.desc()).offset(skip).limit(limit).all()


# =============================================================================
# Scraping Queue CRUD Operations
# =============================================================================


def add_to_scraping_queue(db: Session, alumni_id: int, priority: int = 0) -> ScrapingQueue:
    """
    Add an alumni profile to the scraping queue.
    
    Args:
        db: Database session.
        alumni_id: Alumni ID to queue for scraping.
        priority: Priority level (higher = more urgent). Default is 0.
    
    Returns:
        Created ScrapingQueue object.
    """
    queue_item = ScrapingQueue(
        alumni_id=alumni_id,
        priority=priority,
        status='pending',
        attempts=0
    )
    db.add(queue_item)
    db.commit()
    db.refresh(queue_item)
    return queue_item


def get_next_from_queue(db: Session) -> Optional[ScrapingQueue]:
    """
    Get the next pending item from the scraping queue.
    
    Items are ordered by priority (descending) then by creation time (ascending).
    Only returns items with status='pending'.
    
    Args:
        db: Database session.
    
    Returns:
        Next ScrapingQueue object or None if queue is empty.
    """
    return (
        db.query(ScrapingQueue)
        .filter(ScrapingQueue.status == 'pending')
        .order_by(ScrapingQueue.priority.desc(), ScrapingQueue.created_at.asc())
        .first()
    )


def mark_queue_item_complete(db: Session, queue_id: int) -> bool:
    """
    Mark a queue item as completed.
    
    Args:
        db: Database session.
        queue_id: ScrapingQueue ID.
    
    Returns:
        True if updated, False if not found.
    """
    queue_item = db.query(ScrapingQueue).filter(ScrapingQueue.id == queue_id).first()
    if not queue_item:
        return False
    
    queue_item.status = 'completed'
    queue_item.last_attempt_at = datetime.utcnow()
    db.commit()
    return True


def mark_queue_item_failed(db: Session, queue_id: int) -> bool:
    """
    Mark a queue item as failed.
    
    Args:
        db: Database session.
        queue_id: ScrapingQueue ID.
    
    Returns:
        True if updated, False if not found.
    """
    queue_item = db.query(ScrapingQueue).filter(ScrapingQueue.id == queue_id).first()
    if not queue_item:
        return False
    
    queue_item.status = 'failed'
    queue_item.attempts += 1
    queue_item.last_attempt_at = datetime.utcnow()
    db.commit()
    return True


def mark_queue_item_in_progress(db: Session, queue_id: int) -> bool:
    """
    Mark a queue item as in progress.
    
    Args:
        db: Database session.
        queue_id: ScrapingQueue ID.
    
    Returns:
        True if updated, False if not found.
    """
    queue_item = db.query(ScrapingQueue).filter(ScrapingQueue.id == queue_id).first()
    if not queue_item:
        return False
    
    queue_item.status = 'in_progress'
    queue_item.attempts += 1
    queue_item.last_attempt_at = datetime.utcnow()
    db.commit()
    return True


def get_queue_statistics(db: Session) -> dict:
    """
    Get statistics about the scraping queue.
    
    Args:
        db: Database session.
    
    Returns:
        Dictionary with counts for each status:
        {
            'pending': int,
            'in_progress': int,
            'completed': int,
            'failed': int,
            'total': int
        }
    """
    pending_count = db.query(ScrapingQueue).filter(ScrapingQueue.status == 'pending').count()
    in_progress_count = db.query(ScrapingQueue).filter(ScrapingQueue.status == 'in_progress').count()
    completed_count = db.query(ScrapingQueue).filter(ScrapingQueue.status == 'completed').count()
    failed_count = db.query(ScrapingQueue).filter(ScrapingQueue.status == 'failed').count()
    total_count = db.query(ScrapingQueue).count()
    
    return {
        'pending': pending_count,
        'in_progress': in_progress_count,
        'completed': completed_count,
        'failed': failed_count,
        'total': total_count
    }
