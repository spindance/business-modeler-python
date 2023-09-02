import re

# Adjusting regular expression patterns
description_pattern = re.compile(
    r"description:(?P<description>(?:\s*(?:\r?\n  [^\r\n]+)+|\s*[^\r\n]+))",
    re.DOTALL,
)
output_pattern = re.compile(r"output:\s*(?P<output>[^\r\n]+)")
file_pattern = re.compile(r"file_suffix:\s*(?P<filename>[^\r\n]+)")


def parse_template(text: str) -> tuple:
    """
    Parse a text based on specific patterns to extract metadata and template content.
    Trims whitespace from the front and rear of the description, output, file, and template.
    Includes error handling to provide feedback on potential issues with the input text.

    Parameters:
    - text (str): The input text to be parsed.

    Returns:
    - tuple: A tuple containing a list of prompts, files, and potential errors.
    """

    # Splitting text into sections, considering different newline characters
    sections = re.split(r"\r?\n---\r?\n", text.strip())

    # Parsing logic
    prompts = []
    files = []
    errors = []

    for i in range(0, len(sections) - 1, 2):
        metadata = sections[i].strip()
        template = sections[i + 1].strip()

        data = {}

        # Detecting description, file, or output pattern
        description_match = (
            description_pattern.search(metadata) if description_pattern else None
        )
        file_match = file_pattern.search(metadata)
        output_match = output_pattern.search(metadata)

        if description_match:
            desc = description_match.group().split(":", 1)[-1].strip()
            data["description"] = "\n".join(
                [line.strip() for line in desc.splitlines()]
            ).strip()

        if file_match:
            data["file_suffix"] = file_match.group("filename").strip()
            files.append(data)
        elif output_match:
            data["output"] = output_match.group("output").strip()
            prompts.append(data)
        else:
            errors.append(
                f"Error in section {i//2 + 1}: Either 'file' or 'output' metadata must be present."
            )

        if not template:
            errors.append(f"Error in section {i//2 + 1}: Template content is missing.")

        data["template"] = template

    # Check if at least one item has a 'file' key
    if not files:
        errors.append("Error: At least one section must have 'file' metadata.")

    return prompts, files, errors
