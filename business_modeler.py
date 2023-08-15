#!/usr/bin/env python

import os
from typing import Any, Dict

import click
from dotenv import load_dotenv
from langchain.callbacks import get_openai_callback
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chains import LLMChain, SequentialChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

from parse import parse_template
from reporting import generate_report, report_results
from utils import (
    check_api_key,
    extract_variable_names,
    load_chain_config,
    measure_time,
    read_seed,
)

PROMPTS_DIR = "prompts"
PROMPT_TEMPLATES_DIR = "templates"
COMMON_PREFIX_FILE = "_common.txt"
CONFIG_FILE = "config.yaml"
OUTPUT_TEMPLATE_FILE = "output.txt"
EXAMPLE_INPUT_FILE = "input_example.md"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MODEL_NAME = "gpt-3.5-turbo-16k"
# TODO: set defaults for colors


# def read_prompt_template(template_name, prompt_templates_dir, common_prefix_file):
#     """
#     Read and return content from a prompt template file with a common prefix added to it.

#     Parameters:
#     - template_name (str): Name of the template file.
#     - prompt_templates_dir (str): Directory path containing prompt template files.
#     - common_prefix_file (str): Name of the file containing common prefix content.

#     Returns:
#     - str: Content of the template file with common prefix added.
#     """
#     common_prefix_path = os.path.join(prompt_templates_dir, common_prefix_file)
#     with open(common_prefix_path, "r") as common_file:
#         common_prefix = common_file.read()

#     template_path = os.path.join(prompt_templates_dir, template_name)
#     with open(template_path, "r") as template_file:
#         return common_prefix + template_file.read()


def create_llm_chain(llm, prompt_text, output_key, callback_func):
    monitor = CallbackHandler(callback_func)
    input_keys = extract_variable_names(prompt_text)

    return LLMChain(
        llm=llm,
        prompt=PromptTemplate(input_variables=input_keys, template=prompt_text),
        output_key=output_key,
        callbacks=[monitor],
        tags=[output_key],
    )


def build_chain(
    api_key,
    prompts_list,
    callback_func,
    verbose=False,
    model_name="gpt-3.5-turbo-16k",
    temperature=0.7,
):
    # Initialize ChatOpenAI
    llm = ChatOpenAI(openai_api_key=api_key, model=model_name, temperature=temperature)

    # from pprint import pprint
    # pprint(prompts_list)

    # Chains created using the create_llm_chain function
    chains = [
        create_llm_chain(
            llm,
            prompt["template"],
            prompt["output"],
            callback_func,
        )
        for prompt in prompts_list
    ]

    # Calculate input_variables and output_variables
    input_variables = extract_variable_names(prompts_list[0]["template"])

    output_variables = [prompt["output"] for prompt in prompts_list]

    # Sequential chain
    sequential_chain = SequentialChain(
        chains=chains,
        input_variables=input_variables,
        output_variables=output_variables,
        verbose=verbose,
    )

    return sequential_chain


class CallbackHandler(BaseCallbackHandler):
    """
    Custom callback handler class for monitoring the progress of the chains.

    This class is a subclass of BaseCallbackHandler and is used to output
    progress information when a chain starts executing.

    Attributes:
        None
    """

    def __init__(self, callback_func):
        self.callback_func = callback_func

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> Any:
        """
        Callback function that is executed when a chain starts.

        Parameters:
        - serialized (dict): The serialized chain information.
        - inputs (dict): The inputs passed to the chain.
        - kwargs (dict): Additional keyword arguments containing tags.

        Returns:
        - None
        """
        self.callback_func(serialized, inputs, **kwargs)


def callback_handler(serialized, inputs, **kwargs):
    click.secho(f"Running chain '{''.join(kwargs['tags'])}'", fg="cyan")


@click.command()
@click.option("--seed-file", default=None, help="Path to the seed file.")
@click.option(
    "--markdown", is_flag=True, default=False, help="Save output as markdown."
)
@click.option("--verbose", is_flag=True, default=False, help="Enable verbose output.")
@click.option(
    "--config-file", default="config.yaml", help="Path to the configuration file."
)
@click.option("--chain", default=None, help="The name of the chain to run.")
@click.option("--temperature", default=None, type=float, help="Set the temperature.")
@click.option("--model-name", default=None, type=str, help="Set the model name.")
def main(
    seed_file,
    markdown,
    verbose,
    config_file,
    chain,
    temperature,
    model_name,
):
    """Generate a business model from a hunch file."""
    try:
        # Check API Key
        api_key = check_api_key()

        # Load the configuration from the specified configuration file
        chain_config = load_chain_config(config_file)

        # Read seed file
        seed = read_seed(seed_file, EXAMPLE_INPUT_FILE, PROMPT_TEMPLATES_DIR)

        if chain:
            # Parse the prompts templates
            with open(chain, "r") as f:
                chain = f.read()
            prompt_list, report_files, errors = parse_template(chain)
            # print(prompt_list)
            # print(report_files)
            if errors:
                print(errors)
                exit(1)
        else:
            print("No seed file given.")
            exit(1)

        # Override temperature and model_name if provided
        temperature = temperature or chain_config.get(
            "temperature", DEFAULT_TEMPERATURE
        )
        model_name = model_name or chain_config.get("model_name", DEFAULT_MODEL_NAME)

        click.secho(f"Using seed file: {seed_file}", fg="green")
        click.secho(
            f"Using model '{model_name}' with tempature {temperature}", fg="green"
        )

        with measure_time() as duration, get_openai_callback() as cb:
            # Build and execute chain
            chain = build_chain(
                api_key,
                prompt_list,
                callback_handler,
                verbose=verbose,
                model_name=model_name,
                temperature=temperature,
            )
            output = chain({"seed": seed})

            # Generate report

            markdown_file_name, pdf_file_name = generate_report(
                report_files[0]["file"],
                report_files[0]["template"],
                markdown,
                **output,
            )

            # Reporting on result.
            results = report_results(
                markdown, markdown_file_name, pdf_file_name, cb, duration()
            )
            if results["markdown_file"]:
                click.secho(
                    f"Markdown file created: {results['markdown_file']}", fg="green"
                )
            click.secho(f"PDF file created: {results['pdf_file']}", fg="green")
            click.secho(f"Total tokens: {results['total_tokens']}", fg="yellow")
            click.secho(f"Total cost: ${results['total_cost']:.3f}", fg="yellow")
            click.secho(f"Runtime: {results['runtime']:.2f} seconds", fg="yellow")

    except (ValueError, FileNotFoundError) as e:
        click.secho(f"Error: {e}", fg="red")
        exit(1)


if __name__ == "__main__":
    load_dotenv()
    main()
