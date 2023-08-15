#!/usr/bin/env python
import click
from dotenv import load_dotenv
from langchain.callbacks import get_openai_callback

from engine import Engine
from reporting import generate_report, generate_reports, report_results
from utils import (
    check_api_key,
    load_chain_file,
    load_configuration,
    measure_time,
    read_seed,
)

PROMPTS_DIR = "prompts"
PROMPT_TEMPLATES_DIR = "templates"
CONFIG_FILE = "config.yaml"
EXAMPLE_INPUT_FILE = "input_example.md"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MODEL_NAME = "gpt-3.5-turbo-16k"
# TODO: set defaults for colors


def callback_handler(serialized, inputs, **kwargs):
    click.secho(f"Running chain '{''.join(kwargs['tags'])}'", fg="cyan")


@click.command()
@click.option("--seed-file", required=True, help="Path to the seed file.")
@click.option("--chain-file", required=True, help="The name of the chain to run.")
@click.option(
    "--config-file", default="config.yaml", help="Path to the configuration file."
)
@click.option(
    "--markdown", is_flag=True, default=False, help="Save output as markdown."
)
@click.option("--pdf", is_flag=True, default=False, help="Save output as markdown.")
@click.option("--verbose", is_flag=True, default=False, help="Enable verbose output.")
@click.option("--temperature", default=None, type=float, help="Set the temperature.")
@click.option("--model-name", default=None, type=str, help="Set the model name.")
def main(**kwargs):
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

        # todo: print the
        seed = read_seed(kwargs["seed_file"], EXAMPLE_INPUT_FILE, PROMPT_TEMPLATES_DIR)

        prompt_list, report_files, errors = load_chain_file(kwargs["chain_file"])
        if errors:
            print(errors)
            exit(1)

        configuration = load_configuration(kwargs["config_file"], kwargs)

        engine = Engine(
            api_key,
            prompt_list,
            callback_handler,
            kwargs["verbose"],
            configuration["model_name"],
            configuration["temperature"],
        )

        click.secho(f"Using seed file: {kwargs['seed_file']}", fg="green")
        click.secho(
            f"Using model '{configuration['model_name']}' with tempature {configuration['temperature']}",
            fg="green",
        )

        with measure_time() as duration, get_openai_callback() as cb:
            output = engine.run(seed)

            markdown_file_names, pdf_file_names = generate_reports(
                report_files, kwargs["markdown"], **output
            )

            # Reporting on result.
            results = report_results(
                kwargs["markdown"], markdown_file_names, pdf_file_names, cb, duration()
            )
            if results["markdown_file"]:
                click.secho(
                    f"Markdown file(s) created: {', '.join(results['markdown_file'])}",
                    fg="green",
                )
            click.secho(
                f"PDF file(s) created: {', '.join(results['pdf_file'])}", fg="green"
            )
            click.secho(f"Total tokens: {results['total_tokens']}", fg="yellow")
            click.secho(f"Total cost: ${results['total_cost']:.3f}", fg="yellow")
            click.secho(f"Runtime: {results['runtime']:.2f} seconds", fg="yellow")

    except (ValueError, FileNotFoundError) as e:
        click.secho(f"Error: {e}", fg="red")
        exit(1)


if __name__ == "__main__":
    load_dotenv()
    main()
