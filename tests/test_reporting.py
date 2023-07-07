import os

# import tempfile
from unittest.mock import Mock, patch

from business_modeler import generate_report, report_results


@patch("business_modeler.md2pdf")
@patch("business_modeler.read_template")
def test_generate_report(mock_read_template, mock_md2pdf):
    mock_read_template.return_value = "Template content {key}"
    chain_output_dict = {"key": "value"}
    output_file = "test_file"

    # Test with markdown=True
    markdown_file_name, pdf_file_name = generate_report(
        output_file, True, **chain_output_dict
    )

    assert markdown_file_name == "test_file.md"
    assert pdf_file_name == "test_file.pdf"
    assert os.path.exists(markdown_file_name)
    mock_md2pdf.assert_called_once()

    # Cleanup
    if os.path.exists(markdown_file_name):
        os.remove(markdown_file_name)


@patch("business_modeler.click.secho")
def test_report_results(mock_secho):
    markdown = True
    markdown_file_name = "markdown_file.md"
    pdf_file_name = "pdf_file.pdf"
    cb = Mock()
    cb.total_tokens = 100
    cb.total_cost = 10.0
    duration = 2.5

    report_results(markdown, markdown_file_name, pdf_file_name, cb, duration)

    # Assert that click.secho was called 5 times (Markdown file, PDF file, Total tokens, Total cost, Runtime)
    assert mock_secho.call_count == 5
