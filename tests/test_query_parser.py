"""
Tests for QueryParser class.

Tests the natural language query parsing functionality.
"""

import pytest

from alumni_system.chatbot.query_parser import QueryParser, ParsedQuery


class TestQueryParser:
    """Test suite for QueryParser."""
    
    def test_parse_company_query(self):
        """Test parsing company-focused queries."""
        parser = QueryParser()
        
        queries = [
            "Who works at Google?",
            "Find alumni at Microsoft",
            "Show me people from Amazon",
        ]
        
        for query in queries:
            result = parser.parse(query)
            assert result.intent == "find_by_company"
            assert "company" in result.entities
    
    def test_parse_batch_query(self):
        """Test parsing batch-focused queries."""
        parser = QueryParser()
        
        queries = [
            "Find alumni from batch 2020",
            "Show batch 2019",
            "2021 graduates",
        ]
        
        for query in queries:
            result = parser.parse(query)
            assert result.intent == "find_by_batch"
            assert "batch" in result.entities
    
    def test_parse_title_query(self):
        """Test parsing title-focused queries."""
        parser = QueryParser()
        
        queries = [
            "Show me software engineers",
            "Find data scientists",
            "Who are the product managers?",
        ]
        
        for query in queries:
            result = parser.parse(query)
            assert result.intent == "find_by_title"
            assert "title" in result.entities
    
    def test_parse_location_query(self):
        """Test parsing location-focused queries."""
        parser = QueryParser()
        
        queries = [
            "Alumni in Bangalore",
            "Who is in New York?",
            "Find people from San Francisco",
        ]
        
        for query in queries:
            result = parser.parse(query)
            assert result.intent == "find_by_location"
            assert "location" in result.entities
    
    def test_parse_count_query(self):
        """Test parsing count queries."""
        parser = QueryParser()
        
        queries = [
            "How many alumni do we have?",
            "Count of alumni",
            "Total number of alumni",
        ]
        
        for query in queries:
            result = parser.parse(query)
            assert result.intent == "count"
    
    def test_parse_help_query(self):
        """Test parsing help queries."""
        parser = QueryParser()
        
        queries = [
            "help",
            "What can you do?",
            "How do I use this?",
        ]
        
        for query in queries:
            result = parser.parse(query)
            assert result.intent == "help"
    
    def test_parse_combined_query(self):
        """Test parsing combined queries with multiple entities."""
        parser = QueryParser()
        
        result = parser.parse("Software engineers at Google from batch 2020")
        
        assert result.intent == "find_by_company"
        assert "company" in result.entities
        assert "title" in result.entities
        assert "batch" in result.entities
        assert result.entities["company"] == "Google"
        assert result.entities["batch"] == "2020"
    
    def test_parse_empty_query(self):
        """Test parsing empty or invalid queries."""
        parser = QueryParser()
        
        result = parser.parse("")
        assert result.intent == "unknown"
        
        result = parser.parse("   ")
        assert result.intent == "unknown"
    
    def test_extract_known_companies(self):
        """Test extraction of known companies."""
        parser = QueryParser()
        
        result = parser.parse("Who works at google?")
        assert result.entities.get("company") == "Google"
        
        result = parser.parse("Find alumni at Microsoft")
        assert result.entities.get("company") == "Microsoft"
    
    def test_extract_batch_year(self):
        """Test extraction of batch years."""
        parser = QueryParser()
        
        result = parser.parse("Alumni from batch 2020")
        assert result.entities.get("batch") == "2020"
        
        result = parser.parse("Class of 2019")
        assert result.entities.get("batch") == "2019"
    
    def test_extract_job_titles(self):
        """Test extraction of job titles."""
        parser = QueryParser()
        
        result = parser.parse("Find data scientists")
        assert result.entities.get("title") == "data scientist"
        
        result = parser.parse("Show software engineers")
        assert result.entities.get("title") == "software engineer"
        
        result = parser.parse("Product managers at Google")
        assert result.entities.get("title") == "product manager"
    
    def test_count_with_filters(self):
        """Test count queries with filters."""
        parser = QueryParser()
        
        result = parser.parse("How many alumni at Google?")
        assert result.intent == "count"
        assert "company" in result.entities
        
        result = parser.parse("Count of alumni from batch 2020")
        assert result.intent == "count"
        assert "batch" in result.entities
