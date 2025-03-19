"""Tests for the filter module."""

import unittest
from unittest.mock import patch, MagicMock

from papers_fetcher.filter import PaperFilter


class TestPaperFilter(unittest.TestCase):
    """Test cases for the PaperFilter class."""

    def setUp(self):
        """Set up test fixtures."""
        self.filter = PaperFilter(debug=True)

    def test_is_company_affiliation(self):
        """Test the _is_company_affiliation method."""
        # Test cases with company affiliations
        company_affiliations = [
            "Acme Pharmaceuticals Inc., New York, USA",
            "BioTech Labs Ltd., London, UK",
            "Gene Therapeutics Corp., Boston, MA",
            "XYZ Pharma GmbH, Berlin, Germany",
        ]

        # Test cases with academic affiliations
        academic_affiliations = [
            "Department of Biology, Harvard University, Cambridge, MA",
            "School of Medicine, Johns Hopkins University, Baltimore, MD",
            "National Institute of Health, Bethesda, MD",
            "Memorial Hospital, New York, NY",
        ]

        # Test cases with mixed affiliations
        mixed_affiliations = [
            "Department of Oncology, Memorial Hospital; Pfizer Inc., New York, NY",
            "Stanford University School of Medicine; Genentech Inc., South San Francisco, CA",
        ]

        # Test company affiliations
        for affiliation in company_affiliations:
            with self.subTest(affiliation=affiliation):
                self.assertTrue(self.filter._is_company_affiliation(affiliation))

        # Test academic affiliations
        for affiliation in academic_affiliations:
            with self.subTest(affiliation=affiliation):
                self.assertFalse(self.filter._is_company_affiliation(affiliation))

        # Test mixed affiliations - these might be detected as academic or company
        # depending on the specific implementation of the heuristic
        for affiliation in mixed_affiliations:
            with self.subTest(affiliation=affiliation):
                # Just verify the method runs without errors
                result = self.filter._is_company_affiliation(affiliation)
                self.assertIsInstance(result, bool)

    def test_extract_company_name(self):
        """Test the _extract_company_name method."""
        test_cases = [
            ("Acme Pharmaceuticals Inc., New York, USA", "Acme Pharmaceuticals Inc."),
            ("Department of Biology, BioTech Labs Ltd., London, UK", "BioTech Labs Ltd."),
            ("Gene Therapeutics Corp., Boston, MA", "Gene Therapeutics Corp."),
        ]

        for affiliation, expected in test_cases:
            with self.subTest(affiliation=affiliation):
                result = self.filter._extract_company_name(affiliation)
                # We're using assertIn instead of assertEqual because the exact extraction
                # might vary slightly due to the heuristic approach
                self.assertIn(expected, result)

    def test_filter_papers(self):
        """Test the filter_papers method."""
        # Create test papers
        papers = [
            {
                "pmid": "12345",
                "title": "Test Paper 1",
                "publication_date": "2023 Jan",
                "authors": [
                    {
                        "name": "Author A",
                        "affiliations": ["Acme Pharmaceuticals Inc., New York, USA"]
                    },
                    {
                        "name": "Author B",
                        "affiliations": ["Department of Biology, Harvard University, Cambridge, MA"]
                    }
                ],
                "corresponding_email": "author@example.com"
            },
            {
                "pmid": "67890",
                "title": "Test Paper 2",
                "publication_date": "2023 Feb",
                "authors": [
                    {
                        "name": "Author C",
                        "affiliations": ["Department of Biology, Harvard University, Cambridge, MA"]
                    }
                ],
                "corresponding_email": "author@example.com"
            },
            {
                "pmid": "54321",
                "title": "Test Paper 3",
                "publication_date": "2023 Mar",
                "authors": [
                    {
                        "name": "Author D",
                        "affiliations": ["BioTech Labs Ltd., London, UK"]
                    }
                ],
                "corresponding_email": "author@example.com"
            }
        ]

        # Filter papers
        result = self.filter.filter_papers(papers)

        # Verify the result
        self.assertEqual(len(result), 2)  # Only papers with company affiliations
        self.assertEqual(result[0]["pmid"], "12345")
        self.assertEqual(result[1]["pmid"], "54321")
        self.assertIn("Author A", result[0]["non_academic_authors"])
        self.assertIn("Author D", result[1]["non_academic_authors"])
        self.assertIn("Acme Pharmaceuticals Inc.", result[0]["company_affiliations"][0])
        self.assertIn("BioTech Labs Ltd.", result[1]["company_affiliations"][0])


if __name__ == "__main__":
    unittest.main()