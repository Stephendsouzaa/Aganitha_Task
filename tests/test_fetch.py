"""Tests for the fetch module."""

import unittest
from unittest.mock import patch, MagicMock

from papers_fetcher.fetch import PubMedFetcher


class TestPubMedFetcher(unittest.TestCase):
    """Test cases for the PubMedFetcher class."""

    def setUp(self):
        """Set up test fixtures."""
        self.fetcher = PubMedFetcher(email="test@example.com", debug=True)

    @patch("papers_fetcher.fetch.Entrez")
    def test_fetch_papers_empty_results(self, mock_entrez):
        """Test fetching papers with empty results."""
        # Mock the search results
        mock_search_handle = MagicMock()
        mock_entrez.esearch.return_value = mock_search_handle
        mock_entrez.read.return_value = {"IdList": []}

        # Call the method
        result = self.fetcher.fetch_papers("test query")

        # Verify the result
        self.assertEqual(result, [])
        mock_entrez.esearch.assert_called_once()

    @patch("papers_fetcher.fetch.Entrez")
    @patch("papers_fetcher.fetch.Medline")
    def test_fetch_papers_with_results(self, mock_medline, mock_entrez):
        """Test fetching papers with results."""
        # Mock the search results
        mock_search_handle = MagicMock()
        mock_entrez.esearch.return_value = mock_search_handle
        mock_entrez.read.return_value = {"IdList": ["12345", "67890"]}

        # Mock the fetch results
        mock_fetch_handle = MagicMock()
        mock_entrez.efetch.return_value = mock_fetch_handle

        # Mock the Medline parser
        mock_record1 = {
            "PMID": "12345",
            "TI": "Test Paper 1",
            "DP": "2023 Jan",
            "AU": ["Author A", "Author B"],
            "AD": "Department of Testing, Test University; Test Company Inc., City, Country"
        }
        mock_record2 = {
            "PMID": "67890",
            "TI": "Test Paper 2",
            "DP": "2023 Feb",
            "AU": ["Author C"],
            "AD": "Test Pharma Ltd., City, Country"
        }
        mock_medline.parse.return_value = [mock_record1, mock_record2]

        # Call the method
        result = self.fetcher.fetch_papers("test query")

        # Verify the result
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["pmid"], "12345")
        self.assertEqual(result[1]["pmid"], "67890")
        mock_entrez.esearch.assert_called_once()
        mock_entrez.efetch.assert_called_once()

    def test_format_date(self):
        """Test the _format_date method."""
        # Test with various date formats
        test_cases = [
            ({"DP": "2023 Jan"}, "2023 Jan"),
            ({"DP": "2023 Jan-Feb"}, "2023 Jan-Feb"),
            ({"DP": "2023"}, "2023"),
            ({}, ""),
        ]

        for record, expected in test_cases:
            with self.subTest(record=record):
                result = self.fetcher._format_date(record)
                self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()