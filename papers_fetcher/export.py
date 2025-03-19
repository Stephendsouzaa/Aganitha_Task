"""Module for exporting papers to CSV format."""

import csv
import io
import logging
import sys
from typing import Dict, List, Any, Optional, TextIO

import pandas as pd

# Configure logging
logger = logging.getLogger(__name__)


class PaperExporter:
    """Class to export papers to CSV format."""

    def __init__(self, debug: bool = False) -> None:
        """Initialize the paper exporter.

        Args:
            debug: Whether to print debug information.
        """
        self.debug = debug
        if debug:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

    def _prepare_data_for_export(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare paper data for export to CSV.

        Args:
            papers: List of papers to prepare for export.

        Returns:
            List of dictionaries with flattened structure for CSV export.
        """
        export_data = []

        for paper in papers:
            # Join multiple authors and company affiliations with semicolons
            non_academic_authors = "; ".join(paper.get("non_academic_authors", []))
            company_affiliations = "; ".join(paper.get("company_affiliations", []))

            # Create a flattened dictionary for CSV export
            export_row = {
                "PubmedID": paper.get("pmid", ""),
                "Title": paper.get("title", ""),
                "Publication Date": paper.get("publication_date", ""),
                "Non-academic Author(s)": non_academic_authors,
                "Company Affiliation(s)": company_affiliations,
                "Corresponding Author Email": paper.get("corresponding_email", "") or "Not Available"
            }

            export_data.append(export_row)

        return export_data

    def export_to_csv(self, papers: List[Dict[str, Any]], output_file: Optional[str] = None) -> Optional[str]:
        """Export papers to CSV format.

        Args:
            papers: List of papers to export.
            output_file: Path to the output file. If None, returns the CSV as a string.

        Returns:
            CSV string if output_file is None, otherwise None.

        Raises:
            IOError: If there is an error writing to the output file.
        """
        if not papers:
            logger.warning("No papers to export")
            return "" if output_file is None else None

        # Prepare data for export
        export_data = self._prepare_data_for_export(papers)
        logger.debug(f"Prepared {len(export_data)} papers for export")

        try:
            # Create a DataFrame for easier CSV handling
            df = pd.DataFrame(export_data)

            if output_file:
                # Write to file
                df.to_csv(output_file, index=False, quoting=csv.QUOTE_NONNUMERIC)
                logger.info(f"Exported {len(export_data)} papers to {output_file}")
                return None
            else:
                # Return as string
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False, quoting=csv.QUOTE_NONNUMERIC)
                csv_string = csv_buffer.getvalue()
                logger.debug(f"Generated CSV string with {len(export_data)} papers")
                return csv_string

        except Exception as e:
            logger.error(f"Error exporting papers to CSV: {e}")
            raise

    def print_to_console(self, papers: List[Dict[str, Any]]) -> None:
        """Print papers to console in a readable format.

        Args:
            papers: List of papers to print.
        """
        if not papers:
            print("No papers found matching the criteria.")
            return

        print(f"\nFound {len(papers)} papers with pharmaceutical/biotech company affiliations:\n")

        for i, paper in enumerate(papers, 1):
            print(f"Paper {i}:")
            print(f"  PubMed ID: {paper.get('pmid', 'N/A')}")
            print(f"  Title: {paper.get('title', 'N/A')}")
            print(f"  Publication Date: {paper.get('publication_date', 'N/A')}")
            print(f"  Non-academic Authors: {', '.join(paper.get('non_academic_authors', ['N/A']))}")
            print(f"  Company Affiliations: {', '.join(paper.get('company_affiliations', ['N/A']))}")
            print(f"  Corresponding Email: {paper.get('corresponding_email', 'N/A')}")
            print()