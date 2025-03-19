"""Module for fetching papers from PubMed API."""

import logging
from typing import Dict, List, Any, Optional
import time

from Bio import Entrez
from Bio import Medline

# Configure logging
logger = logging.getLogger(__name__)


class PubMedFetcher:
    """Class to fetch papers from PubMed API."""

    def __init__(self, email: str, debug: bool = False) -> None:
        """Initialize the PubMed fetcher.

        Args:
            email: Email address to use for NCBI API (required by PubMed)
            debug: Whether to enable debug logging
        """
        # Set email for NCBI API
        Entrez.email = email
        
        # Set logging level based on debug flag
        if debug:
            logger.setLevel(logging.DEBUG)
        
        logger.debug(f"PubMedFetcher initialized with email: {email}")

    def fetch_papers(self, query: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """Fetch papers from PubMed based on the query.

        Args:
            query: PubMed search query
            max_results: Maximum number of results to fetch

        Returns:
            List of paper dictionaries with metadata

        Raises:
            Exception: If there is an error fetching papers from PubMed
        """
        logger.debug(f"Fetching papers with query: {query} (max: {max_results})")
        papers = []

        try:
            # Search PubMed
            logger.debug("Searching PubMed")
            search_handle = Entrez.esearch(
                db="pubmed",
                term=query,
                retmax=max_results,
                sort="relevance"
            )
            search_results = Entrez.read(search_handle)
            search_handle.close()

            # Get the list of IDs
            id_list = search_results["IdList"]
            logger.debug("Found %d papers matching the query", len(id_list))

            if not id_list:
                logger.info("No papers found matching the query")
                return []

            # Fetch details for each paper
            logger.debug("Fetching details for %d papers", len(id_list))
            fetch_handle = Entrez.efetch(
                db="pubmed",
                id=id_list,
                rettype="medline",
                retmode="text"
            )
            records = Medline.parse(fetch_handle)
            
            # Process each record
            for record in records:
                paper = self._process_record(record)
                if paper:
                    papers.append(paper)
                    
            fetch_handle.close()

        except Exception as e:
            logger.error("Error fetching papers from PubMed: %s", str(e))
            raise

        logger.info("Fetched %d papers from PubMed", len(papers))
        return papers

    def _process_record(self, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a PubMed record into a standardized paper dictionary.

        Args:
            record: PubMed record from Medline parser

        Returns:
            Processed paper dictionary or None if processing fails
        """
        try:
            # Extract basic information
            paper = {
                "pmid": record.get("PMID", ""),
                "title": record.get("TI", ""),
                "publication_date": self._format_date(record),
                "authors": self._extract_authors(record),
                "corresponding_email": self._extract_email(record)
            }
            
            return paper
            
        except Exception as e:
            logger.warning("Error processing record: %s", str(e))
            return None

    def _extract_authors(self, record: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract author information from a PubMed record.

        Args:
            record: PubMed record from Medline parser

        Returns:
            List of author dictionaries with name and affiliations
        """
        authors = []
        
        # Get author list
        author_list = record.get("AU", [])
        
        # Get affiliations
        affiliations = record.get("AD", "")
        
        # Handle both string and list types for affiliations
        if isinstance(affiliations, list):
            # If it's already a list, use it directly
            affiliation_list = [aff.strip() for aff in affiliations if aff.strip()]
        else:
            # If it's a string, split by semicolon
            affiliation_list = [aff.strip() for aff in affiliations.split(";") if aff.strip()]
        
        # Process each author
        for i, author_name in enumerate(author_list):
            # Try to match author with affiliation
            # This is a simplistic approach - in reality, PubMed data structure is more complex
            # and would require more sophisticated parsing
            author_affiliations = []
            
            # Look for affiliations that mention this author
            for affiliation in affiliation_list:
                # Check if author's last name is mentioned in the affiliation
                last_name = author_name.split(",")[0] if "," in author_name else author_name
                if last_name.lower() in affiliation.lower():
                    author_affiliations.append(affiliation)
            
            # If no specific affiliations found, use all affiliations
            # This is a fallback and not ideal
            if not author_affiliations and affiliation_list:
                author_affiliations = affiliation_list
            
            authors.append({
                "name": author_name,
                "affiliations": author_affiliations
            })
        
        return authors

    def _extract_email(self, record: Dict[str, Any]) -> str:
        """Extract corresponding author email from a PubMed record.

        Args:
            record: PubMed record from Medline parser

        Returns:
            Corresponding author email or empty string if not found
        """
        # Try to find email in the affiliations field
        affiliations = record.get("AD", "")
        
        # Simple regex-free approach to find email
        email = ""
        
        # Handle both string and list types for affiliations
        if isinstance(affiliations, list):
            # If it's a list, join all elements with spaces
            affiliations_text = " ".join(affiliations)
        else:
            # If it's a string, use it directly
            affiliations_text = affiliations
            
        if "@" in affiliations_text:
            # Split by spaces and find part containing @
            parts = affiliations_text.split()
            for part in parts:
                if "@" in part:
                    # Clean up the email (remove punctuation at the end)
                    email = part.strip(".,;()[]{}\"'")
                    break
        
        return email

    def _format_date(self, record: Dict[str, Any]) -> str:
        """Format the publication date from a PubMed record.

        Args:
            record: PubMed record from Medline parser

        Returns:
            Formatted publication date string
        """
        # Try different date fields in order of preference
        for date_field in ["DP", "DEP", "DA", "PHST"]:
            if date_field in record:
                date_str = record[date_field]
                
                # Handle different date formats
                if date_field == "DP":  # Standard date field
                    # Usually in format "YYYY Mon DD" or "YYYY Mon-Mon"
                    return date_str
                
                # For other date fields, just return as is
                return date_str
        
        # If no date found
        return ""