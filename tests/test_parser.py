import unittest

from parse import parse_template

test_text = """
---
description: 
  Sample multi-line
  description for testing.
output: test_output
---
Sample template content for testing purposes.

---
description: Single line description.
output: single_line
---
Another sample template for testing.

---
file: test_filename.pdf
---
File related template content.
"""


class TestParseTemplate(unittest.TestCase):
    def test_parse_template(self):
        # Expected output
        expected_prompts = [
            {
                "description": "Sample multi-line\ndescription for testing.",
                "output": "test_output",
                "template": "Sample template content for testing purposes.",
            },
            {
                "description": "Single line description.",
                "output": "single_line",
                "template": "Another sample template for testing.",
            },
        ]

        expected_files = [
            {"file": "test_filename", "template": "File related template content."},
        ]

        # Testing the function
        prompts, files, errors = parse_template(test_text)

        # Check prompts in the result against the expected prompts
        for i, (actual, expected) in enumerate(zip(prompts, expected_prompts)):
            with self.subTest(i=i, type="prompt"):
                self.assertDictEqual(
                    actual,
                    expected,
                    f"Failed at index {i} for prompts. Expected: {expected}. Got: {actual}.",
                )

        # Check files in the result against the expected files
        for i, (actual, expected) in enumerate(zip(files, expected_files)):
            with self.subTest(i=i, type="file"):
                self.assertDictEqual(
                    actual,
                    expected,
                    f"Failed at index {i} for files. Expected: {expected}. Got: {actual}.",
                )

        # Ensure there are no unexpected errors
        self.assertEqual(errors, [], f"Unexpected errors: {errors}")


# Running the modified unit test
if __name__ == "__main__":
    unittest.main(argv=[""], verbosity=2)


# import unittest

# from parse import parse_template

# test_text = """
# ---
# description:
#   Sample multi-line
#   description for testing.
# output: test_output
# ---
# Sample template content for testing purposes.

# ---
# description: Single line description.
# output: single_line
# ---

# Another sample template for testing.

# ---
# file: test_filename.pdf
# ---
# File related template content.
# """


# class TestParseTemplate(unittest.TestCase):
#     def test_parse_template(self):
#         # Sample input text

#         # Expected output
#         expected_result = [
#             {
#                 "description": "Sample multi-line\ndescription for testing.",
#                 "output": "test_output",
#                 "template": "Sample template content for testing purposes.",
#             },
#             {
#                 "description": "Single line description.",
#                 "output": "single_line",
#                 "template": "Another sample template for testing.",
#             },
#             {"file": "test_filename", "template": "File related template content."},
#         ]

#         # Testing the function
#         result, errors = parse_template(test_text)
#         print(result)
#         print(errors)

#         # Check each item in the result against the expected result
#         for i, (actual, expected) in enumerate(zip(result, expected_result)):
#             with self.subTest(i=i):
#                 self.assertDictEqual(
#                     actual,
#                     expected,
#                     f"Failed at index {i}. Expected: {expected}. Got: {actual}.",
#                 )


# # Running the modified unit test
# unittest.main(argv=[""], verbosity=2, exit=False)
