"""
Query executor for NLP chatbot.

This module provides the QueryExecutor class that executes database queries
based on parsed intent and entities, and formats results as natural language responses.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from ..database.crud import get_all_alumni, search_alumni
from ..database.models import Alumni
from .query_parser import ParsedQuery


@dataclass
class ChatbotResponse:
    """
    Chatbot response containing formatted text and alumni data.
    
    Attributes:
        response: Natural language response text
        alumni: List of alumni dictionaries
        count: Number of alumni in results
        intent: Original query intent
        entities: Extracted entities from query
    """
    response: str
    alumni: List[Dict]
    count: int
    intent: str = ""
    entities: Dict[str, str] = None
    
    def __post_init__(self):
        if self.entities is None:
            self.entities = {}


class QueryExecutor:
    """
    Execute database queries based on parsed intent and format responses.
    
    This class takes a ParsedQuery object and executes the appropriate
    database query, then formats the results as a natural language response
    with a table of alumni data.
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize the query executor.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
    
    def execute(self, parsed_query: ParsedQuery) -> ChatbotResponse:
        """
        Execute a parsed query and return formatted response.
        
        Args:
            parsed_query: ParsedQuery object with intent and entities
            
        Returns:
            ChatbotResponse with results and formatted text
        """
        intent = parsed_query.intent
        entities = parsed_query.entities
        
        # Handle different intents
        if intent == "help":
            return self._handle_help()
        elif intent == "count":
            return self._handle_count(entities)
        elif intent == "find_by_company":
            return self._handle_company_query(entities)
        elif intent == "find_by_batch":
            return self._handle_batch_query(entities)
        elif intent == "find_by_title":
            return self._handle_title_query(entities)
        elif intent == "find_by_location":
            return self._handle_location_query(entities)
        elif intent == "unknown":
            return self._handle_unknown(parsed_query.raw_query)
        else:
            return self._handle_unknown(parsed_query.raw_query)
    
    def _handle_help(self) -> ChatbotResponse:
        """
        Handle help queries.
        
        Returns:
            ChatbotResponse with help text
        """
        help_text = """I can help you find alumni information. Here are some things you can ask:

**By Company:**
- "Who works at Google?"
- "Find alumni at Microsoft"
- "Show me people from Amazon"

**By Job Title:**
- "Who is a Software Engineer?"
- "Find all Data Scientists"
- "Show Product Managers"

**By Batch:**
- "Alumni from batch 2020"
- "Show 2019 graduates"

**By Location:**
- "Alumni in Bangalore"
- "Who is in New York?"

**Count Queries:**
- "How many alumni do we have?"
- "Count of alumni at Google"
- "How many alumni from batch 2020?"

**Combined Queries:**
- "Software engineers at Google from batch 2020"
- "Data scientists in Bangalore"

Just type your question and I'll do my best to help!"""
        
        return ChatbotResponse(
            response=help_text,
            alumni=[],
            count=0,
            intent="help",
            entities={}
        )
    
    def _handle_count(self, entities: Dict[str, str]) -> ChatbotResponse:
        """
        Handle count queries.
        
        Args:
            entities: Extracted entities (may include filters)
            
        Returns:
            ChatbotResponse with count
        """
        try:
            # Build filter criteria
            filters = self._build_filters(entities)
            
            # Query database
            results = get_all_alumni(self.db, limit=100000, **filters)
            count = len(results)
            
            # Format response
            response = f"We have {count} alumni"
            
            if filters:
                filter_parts = []
                if "company" in filters:
                    filter_parts.append(f"at {entities.get('company', 'that company')}")
                if "batch" in filters:
                    filter_parts.append(f"from batch {entities.get('batch')}")
                if "designation" in filters:
                    filter_parts.append(f"with title '{entities.get('title')}'")
                if "location" in filters:
                    filter_parts.append(f"in {entities.get('location')}")
                
                if filter_parts:
                    response += " " + " and ".join(filter_parts)
            
            response += " in the database."
            
            return ChatbotResponse(
                response=response,
                alumni=[],
                count=count,
                intent="count",
                entities=entities
            )
        
        except Exception as e:
            return ChatbotResponse(
                response=f"Sorry, I encountered an error while counting: {str(e)}",
                alumni=[],
                count=0,
                intent="count",
                entities=entities
            )
    
    def _handle_company_query(self, entities: Dict[str, str]) -> ChatbotResponse:
        """
        Handle company-focused queries.
        
        Args:
            entities: Extracted entities (must include 'company')
            
        Returns:
            ChatbotResponse with matching alumni
        """
        company = entities.get("company")
        
        if not company:
            return ChatbotResponse(
                response="I couldn't identify which company you're asking about. Please try again with a company name.",
                alumni=[],
                count=0,
                intent="find_by_company",
                entities=entities
            )
        
        try:
            # Build filters
            filters = self._build_filters(entities)
            
            # Query database
            results = get_all_alumni(self.db, limit=1000, **filters)
            
            # Format response
            if not results:
                response = f"I couldn't find any alumni at {company}"
                if "batch" in entities:
                    response += f" from batch {entities['batch']}"
                if "title" in entities:
                    response += f" with title '{entities['title']}'"
                response += ". Try a different search or check the spelling."
            else:
                count = len(results)
                response = f"I found {count} alumni at {company}"
                if "batch" in entities:
                    response += f" from batch {entities['batch']}"
                if "title" in entities:
                    response += f" with title '{entities['title']}'"
                response += "."
            
            return ChatbotResponse(
                response=response,
                alumni=[self._alumni_to_dict(a) for a in results],
                count=len(results),
                intent="find_by_company",
                entities=entities
            )
        
        except Exception as e:
            return ChatbotResponse(
                response=f"Sorry, I encountered an error while searching: {str(e)}",
                alumni=[],
                count=0,
                intent="find_by_company",
                entities=entities
            )
    
    def _handle_batch_query(self, entities: Dict[str, str]) -> ChatbotResponse:
        """
        Handle batch-focused queries.
        
        Args:
            entities: Extracted entities (must include 'batch')
            
        Returns:
            ChatbotResponse with matching alumni
        """
        batch = entities.get("batch")
        
        if not batch:
            return ChatbotResponse(
                response="I couldn't identify which batch you're asking about. Please specify a year.",
                alumni=[],
                count=0,
                intent="find_by_batch",
                entities=entities
            )
        
        try:
            # Build filters
            filters = self._build_filters(entities)
            
            # Query database
            results = get_all_alumni(self.db, limit=1000, **filters)
            
            # Format response
            if not results:
                response = f"I couldn't find any alumni from batch {batch}"
                if "company" in entities:
                    response += f" at {entities['company']}"
                if "title" in entities:
                    response += f" with title '{entities['title']}'"
                response += ". Try a different search."
            else:
                count = len(results)
                response = f"I found {count} alumni from batch {batch}"
                if "company" in entities:
                    response += f" at {entities['company']}"
                if "title" in entities:
                    response += f" with title '{entities['title']}'"
                response += "."
            
            return ChatbotResponse(
                response=response,
                alumni=[self._alumni_to_dict(a) for a in results],
                count=len(results),
                intent="find_by_batch",
                entities=entities
            )
        
        except Exception as e:
            return ChatbotResponse(
                response=f"Sorry, I encountered an error while searching: {str(e)}",
                alumni=[],
                count=0,
                intent="find_by_batch",
                entities=entities
            )
    
    def _handle_title_query(self, entities: Dict[str, str]) -> ChatbotResponse:
        """
        Handle title-focused queries.
        
        Args:
            entities: Extracted entities (must include 'title')
            
        Returns:
            ChatbotResponse with matching alumni
        """
        title = entities.get("title")
        
        if not title:
            return ChatbotResponse(
                response="I couldn't identify which job title you're asking about. Please try again.",
                alumni=[],
                count=0,
                intent="find_by_title",
                entities=entities
            )
        
        try:
            # Build filters
            filters = self._build_filters(entities)
            
            # Query database
            results = get_all_alumni(self.db, limit=1000, **filters)
            
            # Format response
            if not results:
                response = f"I couldn't find any alumni with title '{title}'"
                if "company" in entities:
                    response += f" at {entities['company']}"
                if "batch" in entities:
                    response += f" from batch {entities['batch']}"
                response += ". Try a different search."
            else:
                count = len(results)
                response = f"I found {count} alumni with title '{title}'"
                if "company" in entities:
                    response += f" at {entities['company']}"
                if "batch" in entities:
                    response += f" from batch {entities['batch']}"
                response += "."
            
            return ChatbotResponse(
                response=response,
                alumni=[self._alumni_to_dict(a) for a in results],
                count=len(results),
                intent="find_by_title",
                entities=entities
            )
        
        except Exception as e:
            return ChatbotResponse(
                response=f"Sorry, I encountered an error while searching: {str(e)}",
                alumni=[],
                count=0,
                intent="find_by_title",
                entities=entities
            )
    
    def _handle_location_query(self, entities: Dict[str, str]) -> ChatbotResponse:
        """
        Handle location-focused queries.
        
        Args:
            entities: Extracted entities (must include 'location')
            
        Returns:
            ChatbotResponse with matching alumni
        """
        location = entities.get("location")
        
        if not location:
            return ChatbotResponse(
                response="I couldn't identify which location you're asking about. Please try again.",
                alumni=[],
                count=0,
                intent="find_by_location",
                entities=entities
            )
        
        try:
            # Build filters
            filters = self._build_filters(entities)
            
            # Query database
            results = get_all_alumni(self.db, limit=1000, **filters)
            
            # Format response
            if not results:
                response = f"I couldn't find any alumni in {location}"
                if "company" in entities:
                    response += f" at {entities['company']}"
                if "batch" in entities:
                    response += f" from batch {entities['batch']}"
                response += ". Try a different search."
            else:
                count = len(results)
                response = f"I found {count} alumni in {location}"
                if "company" in entities:
                    response += f" at {entities['company']}"
                if "batch" in entities:
                    response += f" from batch {entities['batch']}"
                response += "."
            
            return ChatbotResponse(
                response=response,
                alumni=[self._alumni_to_dict(a) for a in results],
                count=len(results),
                intent="find_by_location",
                entities=entities
            )
        
        except Exception as e:
            return ChatbotResponse(
                response=f"Sorry, I encountered an error while searching: {str(e)}",
                alumni=[],
                count=0,
                intent="find_by_location",
                entities=entities
            )
    
    def _handle_unknown(self, raw_query: str) -> ChatbotResponse:
        """
        Handle unrecognized queries.
        
        Args:
            raw_query: Original query text
            
        Returns:
            ChatbotResponse with helpful error message
        """
        response = """I'm not sure I understood your query. Here are some examples of what you can ask:

- "Who works at Google?"
- "Find alumni from batch 2020"
- "Show me software engineers"
- "Alumni in Bangalore"
- "How many alumni do we have?"

Type 'help' for more examples."""
        
        return ChatbotResponse(
            response=response,
            alumni=[],
            count=0,
            intent="unknown",
            entities={}
        )
    
    def _build_filters(self, entities: Dict[str, str]) -> Dict[str, str]:
        """
        Build database filter criteria from entities.
        
        Args:
            entities: Extracted entities
            
        Returns:
            Dictionary of filter criteria for database query
        """
        filters = {}
        
        if "company" in entities:
            filters["company"] = entities["company"]
        
        if "batch" in entities:
            filters["batch"] = entities["batch"]
        
        if "title" in entities:
            filters["designation"] = entities["title"]
        
        if "location" in entities:
            filters["location"] = entities["location"]
        
        return filters
    
    def _alumni_to_dict(self, alumni: Alumni) -> Dict:
        """
        Convert Alumni model to dictionary for response.
        
        Args:
            alumni: Alumni model instance
            
        Returns:
            Dictionary with alumni data
        """
        return {
            "id": alumni.id,
            "name": alumni.name,
            "batch": alumni.batch,
            "roll_number": alumni.roll_number,
            "current_company": alumni.current_company,
            "current_designation": alumni.current_designation,
            "location": alumni.location,
            "personal_email": alumni.personal_email,
            "linkedin_url": alumni.linkedin_url,
        }
