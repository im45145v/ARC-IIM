"""
Query parser for NLP chatbot.

This module provides the QueryParser class that parses natural language queries
to extract intent and entities for alumni database queries.
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class ParsedQuery:
    """
    Parsed query result containing intent and entities.
    
    Attributes:
        intent: Query intent (find_by_company, find_by_batch, find_by_title, 
                find_by_location, count, help, unknown)
        entities: Dictionary of extracted entities (company, batch, title, location)
        raw_query: Original query text
    """
    intent: str
    entities: Dict[str, str]
    raw_query: str = ""


class QueryParser:
    """
    Parse natural language queries to extract intent and entities.
    
    Supports intents:
    - find_by_company: Find alumni by company
    - find_by_batch: Find alumni by graduation batch/year
    - find_by_title: Find alumni by job title/designation
    - find_by_location: Find alumni by location
    - count: Count alumni (with optional filters)
    - help: Request for help
    - unknown: Unrecognized query
    """
    
    # Intent patterns with regex
    INTENT_PATTERNS = {
        "count": [
            r"how\s+many\s+alumni",
            r"count\s+(?:of\s+)?alumni",
            r"total\s+(?:number\s+of\s+)?alumni",
            r"number\s+of\s+alumni",
        ],
        "help": [
            r"^help$",
            r"what\s+can\s+you\s+do",
            r"how\s+(?:do\s+i|to)\s+use",
            r"how\s+does\s+this\s+work",
        ],
    }
    
    # Entity extraction patterns
    COMPANY_PATTERNS = [
        r"(?:who\s+works?\s+|alumni\s+|people\s+|find\s+(?:alumni\s+)?|show\s+(?:alumni\s+)?|list\s+(?:alumni\s+)?)(?:at|for|in|from|working\s+at)\s+([A-Z][A-Za-z0-9\s&.,-]+?)(?:\s+(?:from|in|and|with|who|batch|\?|$))",
        r"(?:at|from)\s+([A-Z][A-Za-z0-9\s&.,-]+?)(?:\s+(?:from|in|and|with|who|batch|\?|$))",
    ]
    
    BATCH_PATTERNS = [
        r"(?:from|in|of)\s+batch\s+(\d{4})",
        r"batch\s+(\d{4})",
        r"(\d{4})\s+(?:batch|graduates?|class)",
        r"class\s+of\s+(\d{4})",
    ]
    
    TITLE_PATTERNS = [
        r"(?:who\s+(?:is|are)\s+|find\s+|show\s+|list\s+|get\s+)?(?:all\s+)?([a-z]+\s+(?:engineer|scientist|manager|analyst|developer|designer|consultant|director|architect|lead|specialist|coordinator|officer|associate|intern))s?",
        r"(?:who\s+(?:is|are)\s+|find\s+|show\s+|list\s+|get\s+)?(?:all\s+)?(engineer|scientist|manager|analyst|developer|designer|consultant|director|architect|lead|specialist|coordinator|officer|associate|intern|founder|ceo|cto|cfo|vp)s?",
    ]
    
    LOCATION_PATTERNS = [
        r"(?:who\s+(?:is|are|lives?)\s+|alumni\s+|people\s+|find\s+(?:alumni\s+)?|show\s+(?:alumni\s+)?)(?:in|at|from|living\s+in)\s+([A-Z][A-Za-z\s,-]+?)(?:\s+(?:and|with|who|from|batch|\?|$))",
        r"(?:in|at|from)\s+([A-Z][A-Za-z\s,-]+?)(?:\s+(?:and|with|who|from|batch|\?|$))",
    ]
    
    # Known companies for better matching (lowercase)
    KNOWN_COMPANIES = {
        "google", "microsoft", "amazon", "meta", "facebook", "apple", "netflix",
        "uber", "airbnb", "linkedin", "twitter", "salesforce", "oracle", "ibm",
        "deloitte", "mckinsey", "bcg", "bain", "goldman sachs", "morgan stanley",
        "jpmorgan", "tcs", "infosys", "wipro", "flipkart", "paytm", "ola",
        "zomato", "swiggy", "accenture", "cognizant", "capgemini", "intel",
        "nvidia", "adobe", "cisco", "vmware", "paypal", "stripe", "shopify",
    }
    
    # Known job titles (lowercase)
    KNOWN_TITLES = {
        "software engineer", "data scientist", "product manager", "business analyst",
        "consultant", "developer", "designer", "manager", "director", "engineer",
        "scientist", "researcher", "associate", "intern", "founder", "ceo", "cto",
        "cfo", "vp", "vice president", "senior engineer", "lead engineer",
        "principal engineer", "staff engineer", "architect", "tech lead",
        "data analyst", "data engineer", "machine learning engineer", "devops engineer",
        "frontend developer", "backend developer", "full stack developer",
        "ui designer", "ux designer", "product designer", "project manager",
    }
    
    # Known locations (lowercase)
    KNOWN_LOCATIONS = {
        "bangalore", "bengaluru", "mumbai", "delhi", "new delhi", "hyderabad",
        "pune", "chennai", "kolkata", "gurgaon", "gurugram", "noida",
        "san francisco", "new york", "london", "singapore", "dubai", "seattle",
        "boston", "austin", "chicago", "los angeles", "toronto", "vancouver",
    }
    
    def __init__(self):
        """Initialize the query parser."""
        pass
    
    def parse(self, text: str) -> ParsedQuery:
        """
        Parse a natural language query to extract intent and entities.
        
        Args:
            text: Natural language query text
            
        Returns:
            ParsedQuery object with intent and entities
        """
        if not text or not text.strip():
            return ParsedQuery(intent="unknown", entities={}, raw_query=text)
        
        query = text.strip()
        query_lower = query.lower()
        
        # Check for help intent
        if self._match_intent(query_lower, "help"):
            return ParsedQuery(intent="help", entities={}, raw_query=query)
        
        # Check for count intent
        if self._match_intent(query_lower, "count"):
            # Count can have filters, so extract entities
            entities = self._extract_all_entities(query, query_lower)
            return ParsedQuery(intent="count", entities=entities, raw_query=query)
        
        # Extract all entities
        entities = self._extract_all_entities(query, query_lower)
        
        # Determine primary intent based on entities and query structure
        intent = self._determine_intent(query_lower, entities)
        
        return ParsedQuery(intent=intent, entities=entities, raw_query=query)
    
    def _match_intent(self, query_lower: str, intent: str) -> bool:
        """
        Check if query matches an intent pattern.
        
        Args:
            query_lower: Lowercase query text
            intent: Intent name to check
            
        Returns:
            True if query matches intent pattern
        """
        patterns = self.INTENT_PATTERNS.get(intent, [])
        for pattern in patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return True
        return False
    
    def _extract_all_entities(self, query: str, query_lower: str) -> Dict[str, str]:
        """
        Extract all entities from the query.
        
        Args:
            query: Original query text (with case)
            query_lower: Lowercase query text
            
        Returns:
            Dictionary of extracted entities
        """
        entities = {}
        
        # Extract batch (year)
        batch = self._extract_batch(query_lower)
        if batch:
            entities["batch"] = batch
        
        # Extract company
        company = self._extract_company(query, query_lower)
        if company:
            entities["company"] = company
        
        # Extract title
        title = self._extract_title(query_lower)
        if title:
            entities["title"] = title
        
        # Extract location (only if not already identified as company)
        location = self._extract_location(query, query_lower)
        if location and location.lower() != entities.get("company", "").lower():
            entities["location"] = location
        
        return entities
    
    def _extract_batch(self, query_lower: str) -> Optional[str]:
        """
        Extract batch/year from query.
        
        Args:
            query_lower: Lowercase query text
            
        Returns:
            Batch year as string, or None
        """
        for pattern in self.BATCH_PATTERNS:
            match = re.search(pattern, query_lower)
            if match:
                year = match.group(1)
                # Validate year is reasonable (1950-2050)
                if 1950 <= int(year) <= 2050:
                    return year
        return None
    
    def _extract_company(self, query: str, query_lower: str) -> Optional[str]:
        """
        Extract company name from query.
        
        Args:
            query: Original query text
            query_lower: Lowercase query text
            
        Returns:
            Company name, or None
        """
        # First check for known companies (case-insensitive) with word boundaries
        # Sort by length descending to match longest first
        sorted_companies = sorted(self.KNOWN_COMPANIES, key=len, reverse=True)
        for company in sorted_companies:
            # Use word boundaries to avoid partial matches
            if re.search(r'\b' + re.escape(company) + r'\b', query_lower):
                return company.title()
        
        # Try pattern matching for company names
        for pattern in self.COMPANY_PATTERNS:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                company = match.group(1).strip()
                # Clean up common trailing words
                company = re.sub(r'\s+(from|in|and|with|who|batch)$', '', company, flags=re.IGNORECASE)
                if len(company) > 1:
                    return company.strip()
        
        return None
    
    def _extract_title(self, query_lower: str) -> Optional[str]:
        """
        Extract job title from query.
        
        Args:
            query_lower: Lowercase query text
            
        Returns:
            Job title, or None
        """
        # First check for known titles (sorted by length descending to match longest first)
        sorted_titles = sorted(self.KNOWN_TITLES, key=len, reverse=True)
        for title in sorted_titles:
            # Match whole words or with 's' suffix
            if re.search(r'\b' + re.escape(title) + r's?\b', query_lower):
                return title
        
        # Try pattern matching
        for pattern in self.TITLE_PATTERNS:
            match = re.search(pattern, query_lower)
            if match:
                title = match.group(1).strip()
                # Clean up
                title = re.sub(r'\s+(at|in|from|and|with|who|batch)$', '', title)
                if len(title) > 2:
                    return title.strip()
        
        return None
    
    def _extract_location(self, query: str, query_lower: str) -> Optional[str]:
        """
        Extract location from query.
        
        Args:
            query: Original query text
            query_lower: Lowercase query text
            
        Returns:
            Location name, or None
        """
        # First check for known locations
        for location in self.KNOWN_LOCATIONS:
            if location in query_lower:
                return location.title()
        
        # Try pattern matching
        for pattern in self.LOCATION_PATTERNS:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                # Clean up
                location = re.sub(r'\s+(and|with|who|from|batch)$', '', location, flags=re.IGNORECASE)
                if len(location) > 1:
                    return location.strip()
        
        return None
    
    def _determine_intent(self, query_lower: str, entities: Dict[str, str]) -> str:
        """
        Determine the primary intent based on query and entities.
        
        Args:
            query_lower: Lowercase query text
            entities: Extracted entities
            
        Returns:
            Intent string
        """
        # If no entities found, it's unknown
        if not entities:
            return "unknown"
        
        # Determine primary intent based on query keywords and entities
        # Priority: company > title > batch > location
        
        # Check for company-focused queries
        if "company" in entities:
            if any(word in query_lower for word in ["works", "working", "at", "from", "company"]):
                return "find_by_company"
        
        # Check for title-focused queries
        if "title" in entities:
            if any(word in query_lower for word in ["who is", "who are", "find", "show", "list"]):
                return "find_by_title"
        
        # Check for batch-focused queries
        if "batch" in entities:
            if any(word in query_lower for word in ["batch", "class", "graduates", "from"]):
                return "find_by_batch"
        
        # Check for location-focused queries
        if "location" in entities:
            if any(word in query_lower for word in ["in", "at", "lives", "living", "location"]):
                return "find_by_location"
        
        # Default: use the first entity type as intent
        if "company" in entities:
            return "find_by_company"
        elif "title" in entities:
            return "find_by_title"
        elif "batch" in entities:
            return "find_by_batch"
        elif "location" in entities:
            return "find_by_location"
        
        return "unknown"
