"""
Database models for the Alumni Management System.

Schema designed to handle alumni data including:
- Personal information
- Contact details
- Employment history
- Education history
- LinkedIn profile data
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


class Alumni(Base):
    """
    Main alumni table containing personal and contact information.
    
    Based on the provided sample format with fields like:
    S.No, Batch, Roll No., Name, Gender, Contact Info, LinkedIn ID, etc.
    """

    __tablename__ = "alumni"

    id = Column(Integer, primary_key=True, index=True)
    serial_number = Column(Integer, nullable=True)
    batch = Column(String(50), index=True)
    roll_number = Column(String(50), unique=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    gender = Column(String(20))
    
    # Contact information
    whatsapp_number = Column(String(20))
    mobile_number = Column(String(20))
    college_email = Column(String(255))
    personal_email = Column(String(255))
    corporate_email = Column(String(255))
    
    # LinkedIn information
    linkedin_id = Column(String(255), unique=True, index=True)
    linkedin_url = Column(String(500))
    linkedin_pdf_url = Column(String(500))  # B2 storage URL
    
    # Current position
    current_company = Column(String(255), index=True)
    current_designation = Column(String(255), index=True)
    location = Column(String(255))
    
    # Additional information
    por = Column(Text)  # Positions of Responsibility
    internship = Column(Text)
    higher_studies = Column(Text)
    closest_city = Column(String(255))
    notable_alma_mater = Column(Text)
    step_programme = Column(String(255))
    remarks = Column(Text)
    address = Column(Text)
    annual_parental_income = Column(String(100))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_scraped_at = Column(DateTime)
    
    # Relationships
    job_history = relationship(
        "JobHistory", back_populates="alumni", cascade="all, delete-orphan"
    )
    education_history = relationship(
        "EducationHistory", back_populates="alumni", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Alumni(id={self.id}, name='{self.name}', batch='{self.batch}')>"


class JobHistory(Base):
    """
    Employment history table for tracking previous companies.
    
    Handles fields like Previous Company 1, Previous Company 2,3..
    """

    __tablename__ = "job_history"

    id = Column(Integer, primary_key=True, index=True)
    alumni_id = Column(Integer, ForeignKey("alumni.id"), nullable=False, index=True)
    
    company_name = Column(String(255), nullable=False, index=True)
    designation = Column(String(255))
    location = Column(String(255))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    is_current = Column(Boolean, default=False)
    description = Column(Text)
    employment_type = Column(String(50))  # Full-time, Part-time, Internship, etc.
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    alumni = relationship("Alumni", back_populates="job_history")

    def __repr__(self) -> str:
        return f"<JobHistory(alumni_id={self.alumni_id}, company='{self.company_name}')>"


class EducationHistory(Base):
    """
    Education history table for tracking academic background.
    
    Stores information about degrees, institutions, and graduation years.
    """

    __tablename__ = "education_history"

    id = Column(Integer, primary_key=True, index=True)
    alumni_id = Column(Integer, ForeignKey("alumni.id"), nullable=False, index=True)
    
    institution_name = Column(String(255), nullable=False, index=True)
    degree = Column(String(255))
    field_of_study = Column(String(255))
    start_year = Column(Integer)
    end_year = Column(Integer)
    grade = Column(String(50))
    activities = Column(Text)
    description = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    alumni = relationship("Alumni", back_populates="education_history")

    def __repr__(self) -> str:
        return f"<EducationHistory(alumni_id={self.alumni_id}, institution='{self.institution_name}')>"


class ScrapingLog(Base):
    """
    Logging table for tracking scraping operations.
    
    Stores information about scraping runs for auditing and debugging.
    """

    __tablename__ = "scraping_logs"

    id = Column(Integer, primary_key=True, index=True)
    alumni_id = Column(Integer, ForeignKey("alumni.id"), nullable=True)
    linkedin_url = Column(String(500))
    account_email = Column(String(255))  # Track which account was used
    status = Column(String(50))  # success, failed, skipped
    error_message = Column(Text)
    pdf_stored = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    duration_seconds = Column(Integer)

    def __repr__(self) -> str:
        return f"<ScrapingLog(id={self.id}, status='{self.status}')>"


class AccountUsage(Base):
    """
    Account usage tracking table for rate limiting.
    
    Tracks daily usage per LinkedIn account to enforce scraping limits.
    """

    __tablename__ = "account_usage"
    __table_args__ = (
        UniqueConstraint('account_email', 'date', name='uq_account_email_date'),
    )

    id = Column(Integer, primary_key=True, index=True)
    account_email = Column(String(255), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    profiles_scraped = Column(Integer, default=0)
    is_flagged = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<AccountUsage(account_email='{self.account_email}', date='{self.date}', profiles_scraped={self.profiles_scraped})>"


class ScrapingQueue(Base):
    """
    Scraping queue table for managing scraping tasks.
    
    Maintains a queue of alumni profiles to be scraped with priority support.
    """

    __tablename__ = "scraping_queue"

    id = Column(Integer, primary_key=True, index=True)
    alumni_id = Column(Integer, ForeignKey("alumni.id", ondelete="CASCADE"), nullable=False, index=True)
    priority = Column(Integer, default=0, index=True)
    status = Column(String(50), default='pending', index=True)  # pending, in_progress, completed, failed
    attempts = Column(Integer, default=0)
    last_attempt_at = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<ScrapingQueue(id={self.id}, alumni_id={self.alumni_id}, status='{self.status}')>"
