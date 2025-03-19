"""Tests for the CLI module."""

import unittest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from cli.main import app


class TestCLI(unittest.TestCase):
    """Test cases for the CLI module."""

    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch("cli.main.PubMedFetcher")
    @patch("cli.main.PaperFilter")
    @patch("cli.main.PaperExporter")
    def test_main_with_file_output(self, mock_exporter, mock_filter, mock_fetcher):
        """Test the main function with file output."""
        # Mock the fetcher, filter, and exporter
        mock_fetcher_instance = MagicMock()
        mock_filter_instance = MagicMock()
        mock_exporter_instance = MagicMock()

        mock_fetcher.return_value = mock_fetcher_instance
        mock_filter.return_value = mock_filter_instance
        mock_exporter.return_value = mock_exporter_instance

        # Mock the fetch_papers method
        mock_fetcher_instance.fetch_papers.return_value = ["paper1", "paper2"]

        # Mock the filter_papers method
        mock_filter_instance.filter_papers.return_value = ["filtered_paper1"]

        # Run the CLI command
        result = self.runner.invoke(
            app, ["test query", "--file", "output.csv", "--email", "test@example.com"]
        )

        # Verify the result
        self.assertEqual(result.exit_code, 0)
        mock_fetcher.assert_called_once_with(email="test@example.com", debug=False)
        mock_fetcher_instance.fetch_papers.assert_called_once_with("test query", max_results=100)
        mock_filter_instance.filter_papers.assert_called_once_with(["paper1", "paper2"])
        mock_exporter_instance.export_to_csv.assert_called_once_with(["filtered_paper1"], "output.csv")

    @patch("cli.main.PubMedFetcher")
    @patch("cli.main.PaperFilter")
    @patch("cli.main.PaperExporter")
    def test_main_with_console_output(self, mock_exporter, mock_filter, mock_fetcher):
        """Test the main function with console output."""
        # Mock the fetcher, filter, and exporter
        mock_fetcher_instance = MagicMock()
        mock_filter_instance = MagicMock()
        mock_exporter_instance = MagicMock()

        mock_fetcher.return_value = mock_fetcher_instance
        mock_filter.return_value = mock_filter_instance
        mock_exporter.return_value = mock_exporter_instance

        # Mock the fetch_papers method
        mock_fetcher_instance.fetch_papers.return_value = ["paper1", "paper2"]

        # Mock the filter_papers method
        mock_filter_instance.filter_papers.return_value = ["filtered_paper1"]

        # Run the CLI command
        result = self.runner.invoke(
            app, ["test query", "--email", "test@example.com"]
        )

        # Verify the result
        self.assertEqual(result.exit_code, 0)
        mock_fetcher.assert_called_once_with(email="test@example.com", debug=False)
        mock_fetcher_instance.fetch_papers.assert_called_once_with("test query", max_results=100)
        mock_filter_instance.filter_papers.assert_called_once_with(["paper1", "paper2"])
        mock_exporter_instance.print_to_console.assert_called_once_with(["filtered_paper1"])

    @patch("cli.main.PubMedFetcher")
    @patch("cli.main.PaperFilter")
    @patch("cli.main.PaperExporter")
    def test_main_with_debug_flag(self, mock_exporter, mock_filter, mock_fetcher):
        """Test the main function with debug flag."""
        # Mock the fetcher, filter, and exporter
        mock_fetcher_instance = MagicMock()
        mock_filter_instance = MagicMock()
        mock_exporter_instance = MagicMock()

        mock_fetcher.return_value = mock_fetcher_instance
        mock_filter.return_value = mock_filter_instance
        mock_exporter.return_value = mock_exporter_instance

        # Mock the fetch_papers method
        mock_fetcher_instance.fetch_papers.return_value = ["paper1", "paper2"]

        # Mock the filter_papers method
        mock_filter_instance.filter_papers.return_value = ["filtered_paper1"]

        # Run the CLI command with debug flag
        result = self.runner.invoke(
            app, ["test query", "--debug", "--email", "test@example.com"]
        )

        # Verify the result
        self.assertEqual(result.exit_code, 0)
        mock_fetcher.assert_called_once_with(email="test@example.com", debug=True)
        mock_filter.assert_called_once_with(debug=True)
        mock_exporter.assert_called_once_with(debug=True)


if __name__ == "__main__":
    unittest.main()