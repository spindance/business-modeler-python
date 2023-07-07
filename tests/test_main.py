import unittest
from unittest.mock import ANY, MagicMock, patch

from click.testing import CliRunner

import business_modeler  # replace 'business_modeler' with the actual module name where your function is defined


class TestMainCommand(unittest.TestCase):
    @patch("business_modeler.report_results")
    @patch("business_modeler.generate_report")
    @patch("business_modeler.build_chain")
    @patch("business_modeler.get_openai_callback")
    @patch("business_modeler.measure_time")
    @patch("business_modeler.load_chain_config")
    @patch("business_modeler.read_seed")
    @patch("business_modeler.check_api_key")
    def test_main_command(
        self,
        mock_check_api_key,
        mock_read_seed,
        mock_load_chain_config,
        mock_measure_time,
        mock_get_openai_callback,
        mock_build_chain,
        mock_generate_report,
        mock_report_results,
    ):
        # Mocking the necessary functions
        mock_check_api_key.return_value = "dummy_api_key"
        mock_read_seed.return_value = "seed"
        mock_load_chain_config.return_value = {"chains": "config"}
        mock_measure_time.return_value.__enter__.return_value = lambda: 0.1
        mock_get_openai_callback.return_value.__enter__.return_value = MagicMock()
        mock_build_chain.return_value = lambda x: {"output": "chain output"}
        mock_generate_report.return_value = ("markdown_file_name", "pdf_file_name")

        # Executing the command
        runner = CliRunner()
        result = runner.invoke(business_modeler.main, ["--seed-file", "seed.txt"])

        # Making sure the command executes without errors
        self.assertEqual(result.exit_code, 0)

        # Making sure report_results is called with the correct arguments
        mock_report_results.assert_called_once_with(
            False, "markdown_file_name", "pdf_file_name", ANY, 0.1
        )
