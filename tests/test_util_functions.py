import contextlib
import os
import tempfile
import time
import unittest
from unittest.mock import MagicMock, mock_open, patch

import pytest
import yaml

import business_modeler
from business_modeler import (
    check_api_key,
    extract_variable_names,
    measure_time,
    read_prompt_template,
    read_seed,
    read_template,
)


class TestReadPromptTemplate(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

        # Create a common prefix file
        with open(os.path.join(self.tmp_dir, "common_prefix.txt"), "w") as file:
            file.write("COMMON_PREFIX ")

        # Create a template file
        with open(os.path.join(self.tmp_dir, "template.txt"), "w") as file:
            file.write("TEMPLATE_CONTENT")

    def test_read_prompt_template_with_common_prefix(self):
        expected_output = "COMMON_PREFIX TEMPLATE_CONTENT"
        result = read_prompt_template("template.txt", self.tmp_dir, "common_prefix.txt")
        self.assertEqual(result, expected_output)

    def test_read_prompt_template_with_empty_common_prefix(self):
        # Empty common prefix file
        with open(os.path.join(self.tmp_dir, "empty_prefix.txt"), "w") as file:
            file.write("")

        expected_output = "TEMPLATE_CONTENT"
        result = read_prompt_template("template.txt", self.tmp_dir, "empty_prefix.txt")
        self.assertEqual(result, expected_output)

    def test_read_prompt_template_with_non_existing_file(self):
        with self.assertRaises(FileNotFoundError):
            read_prompt_template(
                "non_existing_template.txt", self.tmp_dir, "common_prefix.txt"
            )

    def test_read_prompt_template_with_non_existing_common_prefix_file(self):
        with self.assertRaises(FileNotFoundError):
            read_prompt_template(
                "template.txt", self.tmp_dir, "non_existing_prefix.txt"
            )


class TestExtractVariableNames(unittest.TestCase):
    def test_extract_single_variable(self):
        template = "Hello {name}!"
        expected_output = ["name"]
        self.assertEqual(extract_variable_names(template), expected_output)

    def test_extract_multiple_variables(self):
        template = "My name is {name} and I am {age} years old."
        expected_output = ["name", "age"]
        self.assertEqual(extract_variable_names(template), expected_output)

    def test_extract_no_variables(self):
        template = "Hello World!"
        expected_output = []
        self.assertEqual(extract_variable_names(template), expected_output)

    def test_extract_with_special_characters(self):
        template = "This is {special$chars} and {more@special_chars}."
        expected_output = ["special$chars", "more@special_chars"]
        self.assertEqual(extract_variable_names(template), expected_output)

    def test_extract_with_numbers(self):
        template = "These are numbers {123} and {456}."
        expected_output = ["123", "456"]
        self.assertEqual(extract_variable_names(template), expected_output)

    def test_extract_with_empty_braces(self):
        template = "This template contains empty braces {}."
        expected_output = [""]
        self.assertEqual(extract_variable_names(template), expected_output)

    def test_extract_with_nested_braces(self):
        template = "This template contains nested braces {{nested}}."
        expected_output = ["{nested"]
        self.assertEqual(extract_variable_names(template), expected_output)

    def test_extract_with_spaces(self):
        template = "This template contains spaces {var with spaces}."
        expected_output = ["var with spaces"]
        self.assertEqual(extract_variable_names(template), expected_output)


class TestLoadChainConfig(unittest.TestCase):
    def test_load_chain_config_success(self):
        mock_yaml_content = "key: value"
        mock_open_function = mock_open(read_data=mock_yaml_content)

        # Patching the open and yaml.safe_load functions
        with patch("business_modeler.open", mock_open_function, create=True):
            with patch("business_modeler.yaml.safe_load") as mock_yaml:
                mock_yaml.return_value = {"key": "value"}
                config = business_modeler.load_chain_config("config_file.yaml")
                self.assertEqual(config, {"key": "value"})

    def test_load_chain_config_file_not_found(self):
        mock_open_function = mock_open()
        mock_open_function.side_effect = FileNotFoundError()

        # Patching the open function
        with patch("business_modeler.open", mock_open_function, create=True):
            config = business_modeler.load_chain_config("config_file.yaml")
            self.assertEqual(config, {})

    def test_load_chain_config_invalid_yaml(self):
        mock_yaml_content = "invalid_yaml"
        mock_open_function = mock_open(read_data=mock_yaml_content)

        # Patching the open and yaml.safe_load functions
        with patch("business_modeler.open", mock_open_function, create=True):
            with patch("business_modeler.yaml.safe_load") as mock_yaml:
                mock_yaml.side_effect = yaml.YAMLError()
                config = business_modeler.load_chain_config("config_file.yaml")
                self.assertEqual(config, {})


class TestReadTemplate(unittest.TestCase):
    # Mock value for PROMPT_TEMPLATES_DIR
    mock_prompt_templates_dir = "/path/to/templates"

    @patch("business_modeler.PROMPT_TEMPLATES_DIR", mock_prompt_templates_dir)
    def test_read_template_success(self):
        # Mocking content of the file
        mock_file_content = "This is content of the template"
        mock_open_function = mock_open(read_data=mock_file_content)
        mock_template_name = "template.txt"

        # Patching the open function
        with patch("business_modeler.open", mock_open_function, create=True):
            # Call the function
            content = read_template(mock_template_name)

            # Assert that the content read is as expected
            self.assertEqual(content, mock_file_content)

            # Assert that the open function was called with the correct path
            mock_open_function.assert_called_once_with(
                os.path.join(self.mock_prompt_templates_dir, mock_template_name), "r"
            )

    @patch("business_modeler.PROMPT_TEMPLATES_DIR", mock_prompt_templates_dir)
    def test_read_template_file_not_found(self):
        mock_open_function = mock_open()
        mock_open_function.side_effect = FileNotFoundError()

        # Patching the open function
        with patch("business_modeler.open", mock_open_function, create=True):
            # Call the function and assert that it raises FileNotFoundError
            with self.assertRaises(FileNotFoundError):
                read_template("nonexistent_template.txt")


class TestCheckApiKey(unittest.TestCase):
    @patch("os.getenv")
    @patch("click.secho")
    def test_check_api_key_with_env_variable_set(self, mock_secho, mock_getenv):
        # Mocking the behavior to return an API key
        mock_getenv.return_value = "dummy_api_key"

        # Call the function
        api_key = check_api_key()

        # Assertions
        self.assertEqual(api_key, "dummy_api_key")
        mock_secho.assert_not_called()

    @patch("os.getenv")
    @patch("click.secho")
    def test_check_api_key_without_env_variable_set(self, mock_secho, mock_getenv):
        # Mocking the behavior to return None, simulating that the environment variable is not set
        mock_getenv.return_value = None

        # Call the function and expect SystemExit to be raised
        with self.assertRaises(SystemExit):
            check_api_key()

        # Assertions
        self.assertEqual(mock_secho.call_count, 2)


EXAMPLE_INPUT_CONTENT = "This is an example input content."
SEED_FILE_CONTENT = "This is the content of the seed file."


class TestReadSeed(unittest.TestCase):
    @patch("business_modeler.click.secho")
    @patch("business_modeler.read_template")
    def test_read_seed_no_seed_file(self, mock_read_template, mock_click_secho):
        # Mock the read_template function
        mock_read_template.return_value = EXAMPLE_INPUT_CONTENT

        # Calling the function with no seed file should cause an exit.
        # We catch the SystemExit for testing purposes.
        with self.assertRaises(SystemExit) as cm:
            read_seed(None)

        # Check if exit code 0 is used.
        self.assertEqual(cm.exception.code, 0)

        # Check if the function tried to print the example content.
        mock_click_secho.assert_any_call(EXAMPLE_INPUT_CONTENT, fg="white")

    @patch("business_modeler.click.secho")
    @patch("builtins.open", new_callable=mock_open, read_data=SEED_FILE_CONTENT)
    def test_read_seed_with_seed_file(self, mock_file, mock_click_secho):
        # Calling the function with a seed file.
        seed_file = "some_seed_file.txt"
        result = read_seed(seed_file)

        # Check if the function tried to print "Using seed file: ..."
        mock_click_secho.assert_any_call(f"Using seed file: {seed_file}", fg="green")

        # Check if the content read is correct.
        self.assertEqual(result, SEED_FILE_CONTENT)


class TestMeasureTime(unittest.TestCase):
    def test_measure_time(self):
        # Time spent in the code block (seconds)
        sleep_time = 0.5

        # Using the measure_time context manager
        with measure_time() as elapsed:
            # Sleep to simulate code execution time
            time.sleep(sleep_time)

        # Check if the elapsed time is greater than or equal to the time spent in the code block
        # Allowing a small tolerance
        self.assertGreaterEqual(elapsed(), sleep_time)
        self.assertLess(
            elapsed(), sleep_time + 0.1
        )  # Assuming an upper limit tolerance of 0.1 seconds
