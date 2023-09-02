from datetime import datetime

from md2pdf.core import md2pdf

# File name: <prefix>_<suffix>_<timestamp>.<extension>


def generate_reports(prefix, report_files, file_extensions, **chain_output_dict):
    """
    Generate reports based on provided files and extensions.

    Parameters:
    - report_files (list): A list of report file data containing file and template.
    - file_extensions (list): A list of file extensions e.g., ["md", "pdf"].
    - chain_output_dict: Arbitrary keyword arguments to format the template.

    Returns:
    - dict: Dictionary containing file names for each requested extension.
    """
    file_names = {ext: [] for ext in file_extensions}

    print(report_files)

    for report_file in report_files:
        combined_md = create_combined_markdown(
            report_file["template"], **chain_output_dict
        )

        for ext in file_extensions:
            if ext == "md":
                filename = save_markdown(
                    combined_md,
                    prefix,
                    report_file["file_suffix"],
                )
                file_names["md"].append(filename)
            elif ext == "pdf":
                filename = save_pdf(
                    combined_md,
                    prefix,
                    report_file["file_suffix"],
                )
                file_names["pdf"].append(filename)

    return file_names


def create_combined_markdown(template, **chain_output_dict):
    """
    Create combined markdown content using a template and provided data.

    Parameters:
    - template (str): Template string.
    - chain_output_dict: Arbitrary keyword arguments to format the template.

    Returns:
    - str: Formatted markdown content.
    """
    return template.format(**chain_output_dict)


def generate_file_name(prefix, suffix, extension, timestamp=True):
    """
    Generate a file name based on provided prefix, suffix, and extension.

    Parameters:
    - prefix (str): Prefix for the file name.
    - suffix (str): Suffix for the file name.
    - extension (str): File extension.
    - timestamp (bool, optional): If True, includes a timestamp in the filename.

    Returns:
    - str: Generated file name.
    """
    time_string = datetime.now().strftime("%Y-%m-%d-%H-%M-%S") if timestamp else ""
    return f"{prefix}_{suffix}_{time_string}.{extension}"


def save_markdown(markdown_content, prefix, suffix):
    """
    Save markdown content to a markdown file.

    Parameters:
    - markdown_content (str): The content to save.
    - prefix (str): Prefix for the generated file name.

    Returns:
    - str: Name of the generated file.
    """
    file_name = generate_file_name(prefix, suffix, "md")
    with open(file_name, "w") as f:
        f.write(markdown_content)
    return file_name


def save_pdf(markdown_content, prefix, suffix):
    """
    Convert markdown content to a PDF and save it.

    Parameters:
    - markdown_content (str): The markdown content to convert.
    - prefix (str): Prefix for the generated file name.

    Returns:
    - str: Name of the generated PDF file.
    """
    file_name = generate_file_name(prefix, suffix, "pdf")
    md2pdf(file_name, md_content=markdown_content)
    return file_name
