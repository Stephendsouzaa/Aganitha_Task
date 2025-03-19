"""Module for filtering papers based on author affiliations."""

from typing import Dict, List, Any, Set, Tuple
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Keywords that indicate a company affiliation
COMPANY_KEYWORDS = [
    r"\b(?:inc|llc|ltd|corp|corporation|company|co\.|pharmaceuticals|pharma|biotech|therapeutics|biosciences)\b",
    r"\b(?:gmbh|ag|sa|bv|nv|plc|pty|pte)\b",
    r"\b(?:laboratories|labs)\b"
]

# Keywords that indicate an academic affiliation
ACADEMIC_KEYWORDS = [
    r"\b(?:university|college|institute|school|academy|faculty)\b",
    r"\b(?:hospital|clinic|medical center|health center)\b",
    r"\b(?:department|division|school)\b",
    r"\b(?:national|federal|government|ministry)\b"
]


class PaperFilter:
    """Class to filter papers based on author affiliations."""

    def __init__(self, debug: bool = False):
        """Initialize the paper filter.

        Args:
            debug: Whether to enable debug logging
        """
        # Set logging level based on debug flag
        if debug:
            logger.setLevel(logging.DEBUG)
        
        # Compile regex patterns for better performance
        self.company_pattern = re.compile('|'.join(COMPANY_KEYWORDS), re.IGNORECASE)
        self.academic_pattern = re.compile('|'.join(ACADEMIC_KEYWORDS), re.IGNORECASE)
        
        logger.debug("PaperFilter initialized")

    def filter_papers(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter papers to include only those with company affiliations.

        Args:
            papers: List of paper dictionaries from PubMedFetcher

        Returns:
            List of filtered paper dictionaries with additional fields for non-academic authors,
            company affiliations, and corresponding author email
        """
        filtered_papers = []
        
        for paper in papers:
            # Process affiliations and authors
            non_academic_authors, company_affiliations = self._process_affiliations(paper)
            
            # Only include papers with at least one company affiliation
            if company_affiliations:
                # Add the filtered information to the paper
                paper["non_academic_authors"] = non_academic_authors
                paper["company_affiliations"] = company_affiliations
                
                # Add to filtered papers
                filtered_papers.append(paper)
        
        logger.debug("Filtered %d papers with company affiliations", len(filtered_papers))
        return filtered_papers

    def _process_affiliations(self, paper: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Process author affiliations to identify non-academic authors and company affiliations.

        Args:
            paper: Paper dictionary from PubMedFetcher

        Returns:
            Tuple of (non-academic author names, company affiliation names)
        """
        non_academic_authors: List[str] = []
        company_affiliations: Set[str] = set()
        
        # Process each author and their affiliations
        for author in paper.get("authors", []):
            author_name = author.get("name", "")
            author_affiliations = author.get("affiliations", [])
            
            # Check each affiliation for this author
            for affiliation in author_affiliations:
                # Check if this is a company affiliation
                if self._is_company_affiliation(affiliation):
                    # Add author to non-academic authors if not already added
                    if author_name and author_name not in non_academic_authors:
                        non_academic_authors.append(author_name)
                    
                    # Extract company name from affiliation
                    company_name = self._extract_company_name(affiliation)
                    if company_name:
                        company_affiliations.add(company_name)
        
        return non_academic_authors, list(company_affiliations)

    def _is_company_affiliation(self, affiliation: str) -> bool:
        """Check if an affiliation is from a company (non-academic).

        Args:
            affiliation: Affiliation string

        Returns:
            True if the affiliation is from a company, False otherwise
        """
        # Check for company keywords
        if self.company_pattern.search(affiliation):
            # If it has company keywords but also academic keywords, need to determine which is stronger
            if self.academic_pattern.search(affiliation):
                # This is a heuristic - if there are more company matches than academic matches,
                # consider it a company
                company_matches = len(self.company_pattern.findall(affiliation))
                academic_matches = len(self.academic_pattern.findall(affiliation))
                return company_matches > academic_matches
            return True
        return False

    def _extract_company_name(self, affiliation: str) -> str:
        """Extract company name from affiliation string.

        Args:
            affiliation: Affiliation string

        Returns:
            Extracted company name or original affiliation if extraction fails
        """
        try:
            # This is a simple heuristic - in practice, a more sophisticated NLP approach would be better
            # Look for company patterns and extract the surrounding text
            match = self.company_pattern.search(affiliation)
            if match:
                # Get the start position of the match
                start_pos = max(0, match.start() - 30)  # Look up to 30 chars before the match
                end_pos = min(len(affiliation), match.end() + 30)  # Look up to 30 chars after the match
                
                # Extract the substring
                company_text = affiliation[start_pos:end_pos].strip()
                
                # Clean up the text - remove common prefixes like "Department of"
                company_text = re.sub(r'^.*?\b(?:at|from|with|of)\s+', '', company_text)
                
                return company_text
            
            return affiliation
        except Exception as e:
            logger.warning("Error extracting company name: %s", str(e))
            return affiliation