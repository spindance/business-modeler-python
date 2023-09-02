#!/usr/bin/env python
import os
from pathlib import Path

import click
from dotenv import load_dotenv

from chainflow.engine import Engine
from chainflow.reporting import generate_reports
from chainflow.utils import (
    check_api_key,
    load_chain_file,
    load_configuration,
    measure_time,
    read_seed,
    report_results,
)

CONFIG_FILE = "config.yaml"
EXAMPLE_INPUT_FILE = "input_example.md"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MODEL_NAME = "gpt-3.5-turbo-16k"

# Semantic color constants
INFO_COLOR = "green"
WARNING_COLOR = "yellow"
ERROR_COLOR = "red"
ACTION_COLOR = "cyan"


def callback_handler(serialized, inputs, **kwargs):
    click.secho(f"Running chain '{''.join(kwargs['tags'])}'", fg=ACTION_COLOR)


@click.command()
@click.option("--seed-file", required=True, help="Path to the seed file.")
@click.option("--chain-file", required=True, help="The name of the chain to run.")
@click.option(
    "--name",
    required=True,
    help="The name of the run. Output files will be prefixed with this name.",
)
@click.option(
    "--markdown", is_flag=True, default=False, help="Save output as markdown."
)
@click.option("--pdf", is_flag=True, default=True, help="Save output as pdf.")
@click.option(
    "--config-file", default="config.yaml", help="Path to the configuration file."
)
@click.option("--verbose", is_flag=True, default=False, help="Enable verbose output.")
@click.option("--temperature", default=None, type=float, help="Set the temperature.")
@click.option("--model-name", default=None, type=str, help="Set the model name.")
def run(**kwargs):
    """Generate markdown and pdf files using generative AI.

    To get started, create a seed file that contains these questions:

        1. What problem are you trying to solve?
        2. What's your idea/solution to solve this problem?
        3. Who has this problem?
        4. Why do you think this is a problem worth solving?

    Then create a business model using this command:

        ./business_modeler.py --seed-file <your-file> --chain-file prompts/business_model_chain.txt
    """
    try:
        api_key = check_api_key()

        seed = read_seed(kwargs["seed_file"])

        prompt_list, report_files, errors = load_chain_file(kwargs["chain_file"])
        if errors:
            click.secho(errors, fg=ERROR_COLOR)
            exit(1)

        configuration = load_configuration(kwargs["config_file"], kwargs)

        engine = Engine(api_key, prompt_list, callback_handler, kwargs, configuration)

        click.secho(f"Using seed file: {kwargs['seed_file']}", fg=INFO_COLOR)
        click.secho(
            f"Using model '{configuration['model_name']}' with tempature {configuration['temperature']}",
            fg=INFO_COLOR,
        )

        file_types = check_filetypes(kwargs)

        with measure_time() as duration:
            output, stats = engine.run(seed)

            filenames = generate_reports(
                kwargs["name"], report_files, file_types, **output
            )
            display_report_results(kwargs["markdown"], filenames, stats, duration())

    except (ValueError, FileNotFoundError) as e:
        click.secho(f"Error: {e}", fg="red")
        exit(1)


def check_filetypes(kwargs):
    file_types = []
    if kwargs["markdown"]:
        file_types.append("md")
    if kwargs["pdf"]:
        file_types.append("pdf")

    if not file_types and not kwargs["verbose"]:
        click.secho(
            "Error: No output file types specified. Use --verbose to see output.",
            fg=ERROR_COLOR,
        )
        exit(1)
    elif not file_types:
        click.secho(
            "Error: No output file types specified. Use --markdown and/or --pdf to specify output file types.",
            fg=WARNING_COLOR,
        )
    return file_types


def display_report_results(markdown_flag, filenames, stats, runtime_duration):
    results = report_results(
        markdown_flag,
        filenames.get("md"),
        filenames.get("pdf"),
        stats,
        runtime_duration,
    )

    if results["markdown_file"]:
        click.secho(
            f"Markdown file(s) created: {', '.join(results['markdown_file'])}",
            fg=INFO_COLOR,
        )
    if results["pdf_file"]:
        click.secho(
            f"PDF file(s) created: {', '.join(results['pdf_file'])}", fg=INFO_COLOR
        )

    click.secho(f"Total tokens: {results['total_tokens']}", fg=INFO_COLOR)
    click.secho(f"Total cost: ${results['total_cost']:.3f}", fg=INFO_COLOR)
    click.secho(f"Runtime: {results['runtime']:.2f} seconds", fg=INFO_COLOR)


def main():
    load_dotenv()
    run()


if __name__ == "__main__":
    main()
