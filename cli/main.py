"""Command-line interface for the papers-fetcher package."""

import sys
import logging
from typing import Optional

import typer

import os
from papers_fetcher.fetch import PubMedFetcher
from papers_fetcher.filter import PaperFilter
from papers_fetcher.export import PaperExporter
from papers_fetcher.file_naming import generate_filename

# Create Typer app
app = typer.Typer(help="Fetch research papers from PubMed with pharmaceutical/biotech company affiliations")

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@app.command()
def main(
    query: str = typer.Argument(..., help="PubMed search query"),
    file: str = typer.Option(
        None, "-f", "--file", help="Output file path for CSV results"
    ),
    debug: bool = typer.Option(
        False, "-d", "--debug", help="Enable debug logging"
    ),
    max_results: int = typer.Option(
        100, "-m", "--max-results", help="Maximum number of results to fetch"
    ),
    email: str = typer.Option(
        ..., "--email", help="Email for NCBI API (required by PubMed)"
    ),
) -> None:
    """Fetch research papers from PubMed with pharmaceutical/biotech company affiliations.

    Args:
        query: PubMed search query
        file: Output file path for CSV results
        debug: Enable debug logging
        max_results: Maximum number of results to fetch
        email: Email for NCBI API (required by PubMed)
    """
    # Set logging level based on debug flag
    if debug:
        logger.setLevel(logging.DEBUG)
        logging.getLogger("papers_fetcher").setLevel(logging.DEBUG)

    try:
        # Check if --help flag is present - if so, let Typer handle it
        # This prevents the code from trying to execute a search with an empty query
        if '--help' in sys.argv or '-h' in sys.argv:
            # Typer will automatically handle the help display
            return
            
        # Set logging level based on debug flag
        if debug:
            logger.setLevel(logging.DEBUG)
            logging.getLogger("papers_fetcher").setLevel(logging.DEBUG)
        
        # Log the values for debugging
        logger.debug(f"Query: {query}")
        logger.debug(f"Max results: {max_results}")
        logger.debug(f"Email: {email}")
        logger.debug(f"File path: {file}")
        logger.debug(f"Debug mode: {debug}")
        
        # Initialize components
        fetcher = PubMedFetcher(email=email, debug=debug)
        filter_tool = PaperFilter(debug=debug)
        exporter = PaperExporter(debug=debug)

        # Fetch papers
        logger.info(f"Searching PubMed for: {query}")
        papers = fetcher.fetch_papers(query, max_results=max_results)
        logger.info(f"Found {len(papers)} papers from PubMed")
        
        # Filter papers
        logger.info("Filtering papers for company affiliations")
        filtered_papers = filter_tool.filter_papers(papers)
        logger.info(f"Found {len(filtered_papers)} papers with company affiliations")
        
        # Export papers
        if filtered_papers:
            if file:
                # Export to file
                try:
                    # Generate dynamic filename based on search query if not explicitly provided
                    output_dir = os.path.dirname(file) if file and os.path.dirname(file) else os.getcwd()
                    output_file = file if file and '.' in os.path.basename(file) else generate_filename(output_dir, query)
                    exporter.export_to_csv(filtered_papers, output_file)
                    logger.info(f"Results exported to {output_file}")
                except Exception as e:
                    logger.error(f"Error exporting to file: {e}")
                    logger.error(f"File path attempted: {output_file}")
                    sys.exit(1)
            else:
                # Print to console
                exporter.print_to_console(filtered_papers)
        else:
            logger.info("No papers found with company affiliations")
            
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    app()