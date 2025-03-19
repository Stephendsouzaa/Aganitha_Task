"""Tests for the export module."""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import io

from papers_fetcher.export import PaperExporter


class TestPaperExporter(unittest.TestCase):
    """Test cases for the PaperExporter class."""

    def setUp(self):
        """Set up test fixtures."""
        self.exporter = PaperExporter(debug=True)

    def test_prepare_data_for_export(self):
        """Test the _prepare_data_for_export method."""
        # Create test papers
        papers = [
            {
                "pmid": "12345",
                "title": "Test Paper 1",
                "publication_date": "2023 Jan",
                "non_academic_authors": ["Author A", "Author B"],
                "company_affiliations": ["Acme Pharmaceuticals Inc.", "BioTech Labs Ltd."],
                "corresponding_email": "author@example.com"
            },
            {
                "pmid": "67890",
                "title": "Test Paper 2",
                "publication_date": "2023 Feb",
                "non_academic_authors": ["Author C"],
                "company_affiliations": ["Test Pharma Ltd."],
                "corresponding_email": "author2@example.com"
            }
        ]

        # Prepare data for export
        result = self.exporter._prepare_data_for_export(papers)

        # Verify the result
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["PubmedID"], "12345")
        self.assertEqual(result[1]["PubmedID"], "67890")
        self.assertEqual(result[0]["Non-academic Author(s)"], "Author A; Author B")
        self.assertEqual(result[1]["Non-academic Author(s)"], "Author C")
        self.assertEqual(result[0]["Company Affiliation(s)"], "Acme Pharmaceuticals Inc.; BioTech Labs Ltd.")
        self.assertEqual(result[1]["Company Affiliation(s)"], "Test Pharma Ltd.")

    @patch("papers_fetcher.export.pd.DataFrame")
    def test_export_to_csv_file(self, mock_dataframe):
        """Test exporting papers to a CSV file."""
        # Create test papers
        papers = [
            {
                "pmid": "12345",
                "title": "Test Paper 1",
                "publication_date": "2023 Jan",
                "non_academic_authors": ["Author A"],
                "company_affiliations": ["Acme Pharmaceuticals Inc."],
                "corresponding_email": "author@example.com"
            }
        ]

        # Mock DataFrame and to_csv
        mock_df_instance = MagicMock()
        mock_dataframe.return_value = mock_df_instance

        # Call the method
        self.exporter.export_to_csv(papers, "test_output.csv")

        # Verify the result
        mock_dataframe.assert_called_once()
        mock_df_instance.to_csv.assert_called_once()

    @patch("papers_fetcher.export.pd.DataFrame")
    def test_export_to_csv_string(self, mock_dataframe):
        """Test exporting papers to a CSV string."""
        # Create test papers
        papers = [
            {
                "pmid": "12345",
                "title": "Test Paper 1",
                "publication_date": "2023 Jan",
                "non_academic_authors": ["Author A"],
                "company_affiliations": ["Acme Pharmaceuticals Inc."],
                "corresponding_email": "author@example.com"
            }
        ]

        # Mock DataFrame and to_csv
        mock_df_instance = MagicMock()
        mock_dataframe.return_value = mock_df_instance
        mock_df_instance.to_csv.side_effect = lambda buffer, **kwargs: buffer.write("test,csv,data")

        # Call the method
        result = self.exporter.export_to_csv(papers)

        # Verify the result
        self.assertIsNotNone(result)
        mock_dataframe.assert_called_once()
        mock_df_instance.to_csv.assert_called_once()

    def test_export_empty_papers(self):
        """Test exporting empty papers list."""
        # Call the method with empty papers
        result_string = self.exporter.export_to_csv([])
        result_file = self.exporter.export_to_csv([], "test_output.csv")

        # Verify the result
        self.assertEqual(result_string, "")
        self.assertIsNone(result_file)


if __name__ == "__main__":
    unittest.main()