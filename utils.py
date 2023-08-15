import contextlib
import os
import re
import time

import yaml


def load_chain_config(config_file):
    """
    Load and return configuration from a YAML file.

    Parameters:
    - config_file (str): The path to the configuration YAML file.

    Returns:
    - dict: Configuration data loaded from the file.
    """
    try:
        with open(config_file, "r") as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"Error loading configuration file: {e}")
        return {}


def extract_variable_names(template):
    """
    Extract and return variable names from a template string.

    Parameters:
    - template (str): The template string containing variables enclosed in curly braces {}.

    Returns:
    - list: A list of variable names extracted from the template string.
    """
    return re.findall(r"{(.*?)}", template)


def check_api_key():
    """
    Checks if the OPENAI_API_KEY environment variable is set.

    Returns:
    - str: The API key if it is set.

    Raises:
    - ValueError: If the OPENAI_API_KEY environment variable is not set.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY environment variable is not set. Please set it by running: export OPENAI_API_KEY=your_api_key"
        )
    return api_key


@contextlib.contextmanager
def measure_time():
    """
    Context manager for measuring the execution time of a code block.

    Yields:
    - function: A function that when called, returns the elapsed time in seconds.
    """
    start_time = time.time()
    yield lambda: time.time() - start_time


def read_template(template_name, prompt_templates_dir):
    """
    Read and return content from a template file.

    Parameters:
    - template_name (str): Name of the template file.

    Returns:
    - str: Content of the template file.
    """
    path = os.path.join(prompt_templates_dir, template_name)
    with open(path, "r") as f:
        return f.read()


def read_seed(seed_file, example_input_file, prompt_templates_dir):
    """
    Reads the content of a seed file or provides an example input if no file is provided.

    Parameters:
    - seed_file (str or None): The name of the seed file or None if there's no seed file.

    Returns:
    - str: The contents of the seed file or the example input content.

    Raises:
    - ValueError: If the provided seed file doesn't exist.
    - FileNotFoundError: If seed file is not found.
    """
    if seed_file is None:
        # Assuming `read_template` is a function that reads the EXAMPLE_INPUT_FILE
        return read_template(example_input_file, prompt_templates_dir)
    elif not os.path.exists(seed_file):
        raise FileNotFoundError(f"Seed file '{seed_file}' not found.")
    else:
        with open(seed_file, "r") as f:
            return f.read()


# TODO: Move this to report.py


# def report_results(markdown, markdown_file_name, pdf_file_name, cb, duration):
#     """
#     Packages the results of the report generation into a dictionary.

#     Parameters:
#     - markdown (bool): If True, indicates markdown file was created.
#     - markdown_file_name (str): The name of the markdown file.
#     - pdf_file_name (str): The name of the PDF file.
#     - cb (CallbackHandler): The callback handler used during report generation.
#     - duration (float): The total runtime in seconds.

#     Returns:
#     - dict: A dictionary containing the results.
#     """
#     return {
#         "markdown_file": markdown_file_name if markdown else None,
#         "pdf_file": pdf_file_name,
#         "total_tokens": cb.total_tokens,
#         "total_cost": cb.total_cost,
#         "runtime": duration,
#     }
