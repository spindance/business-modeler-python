from datetime import datetime

from md2pdf.core import md2pdf


def generate_reports(report_files, markdown_flag, **chain_output_dict):
    markdown_file_names = []
    pdf_file_names = []
    for report_file in report_files:
        markdown_file_name, pdf_file_name = generate_report(
            report_file["file"],
            report_file["template"],
            markdown_flag,
            **chain_output_dict,
        )

        markdown_file_names.append(markdown_file_name)
        pdf_file_names.append(pdf_file_name)
    return (markdown_file_names, pdf_file_names)


def generate_report(
    output_file,
    output_template,
    markdown,
    **chain_output_dict,
):
    markdown_output = output_template.format(**chain_output_dict)
    file_name = output_file or f"output-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
    markdown_file_name = f"{file_name}.md"
    pdf_file_name = f"{file_name}.pdf"

    # Save markdown content to file
    if markdown:
        with open(markdown_file_name, "w") as f:
            f.write(markdown_output)

    # Convert the markdown file to PDF
    md2pdf(pdf_file_name, md_content=markdown_output)

    # Return the names of the created files
    return markdown_file_name, pdf_file_name


def report_results(markdown, markdown_file_names, pdf_file_names, cb, duration):
    """
    Packages the results of the report generation into a dictionary.

    Parameters:
    - markdown (bool): If True, indicates markdown file was created.
    - markdown_file_name (str): The name of the markdown file.
    - pdf_file_name (str): The name of the PDF file.
    - cb (CallbackHandler): The callback handler used during report generation.
    - duration (float): The total runtime in seconds.

    Returns:
    - dict: A dictionary containing the results.
    """
    return {
        "markdown_file": markdown_file_names if markdown else None,
        "pdf_file": pdf_file_names,
        "total_tokens": cb.total_tokens,
        "total_cost": cb.total_cost,
        "runtime": duration,
    }
