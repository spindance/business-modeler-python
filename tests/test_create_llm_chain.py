import unittest
from unittest.mock import MagicMock, patch

from business_modeler import CallbackHandler, build_chain, create_llm_chain


class TestCreateLLMChain(unittest.TestCase):
    @patch("business_modeler.LLMChain")
    @patch("business_modeler.CallbackHandler")
    @patch("business_modeler.extract_variable_names")
    @patch("business_modeler.read_prompt_template")
    def test_create_llm_chain(
        self,
        mock_read_prompt_template,
        mock_extract_variable_names,
        mock_callback_handler,
        mock_llm_chain,
    ):
        # Mocking the return values
        mock_read_prompt_template.return_value = "{var1} {var2}"
        mock_extract_variable_names.return_value = ["var1", "var2"]

        # Calling the function
        llm = MagicMock()
        create_llm_chain(llm, "template.txt", "dir", "common.txt")

        # Assertions
        mock_read_prompt_template.assert_called_once_with(
            "template.txt", "dir", "common.txt"
        )
        mock_extract_variable_names.assert_called_once_with("{var1} {var2}")
        mock_llm_chain.assert_called_once()


class TestBuildChain(unittest.TestCase):
    @patch("business_modeler.create_llm_chain")
    @patch("business_modeler.SequentialChain")
    @patch("business_modeler.ChatOpenAI")
    @patch("business_modeler.extract_variable_names")
    @patch("business_modeler.read_prompt_template")
    def test_build_chain(
        self,
        mock_read_prompt_template,
        mock_extract_variable_names,
        mock_chat_openai,
        mock_sequential_chain,
        mock_create_llm_chain,
    ):
        # Sample chains_config
        chains_config = [
            {"template_file": "template1.txt"},
            {"template_file": "template2.txt"},
        ]

        # Calling the function
        api_key = "API_KEY"
        build_chain(api_key, chains_config, "dir", "common.txt")

        # Assertions
        mock_chat_openai.assert_called_once_with(
            openai_api_key=api_key, model="gpt-3.5-turbo-16k", temperature=0.7
        )
        mock_create_llm_chain.assert_called()
        mock_sequential_chain.assert_called_once()


def test_on_chain_start_output():
    # Sample data to be passed to on_chain_start method
    serialized = {"key": "value"}
    inputs = {"input_key": "input_value"}
    tags = ["tag1", "tag2"]
    kwargs = {"tags": tags}

    # Expected output string
    expected_output = f"Running chain '{''.join(tags)}'"

    # Patching the click.secho function
    with patch("business_modeler.click.secho") as mock_secho:
        # Create an instance of CallbackHandler
        callback_handler = CallbackHandler()

        # Call the on_chain_start method
        callback_handler.on_chain_start(serialized, inputs, **kwargs)

        # Assert that the click.secho method is called with the expected output string
        mock_secho.assert_called_once_with(expected_output, fg="cyan")
