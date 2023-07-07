# Business Modeler

Business Modeler is a Python-based command-line tool that generates business models from "hunch" brief.

Using OpenAI's GPT-3.5 or GPT-4 model, the tool generates a business model based on the hunch brief. The hunch brief contains the initial idea or input for the business model.

The resulting business models include the following elements:

* The original hunch brief
* A Lean Canvs summarizing the business model
* Assumptions about the business model
* Key risks based on the assumptions
* A list of experiments to test the assumptions
* Alternative business models based on the hunch brief

The output report is saved as a PDF, and optionally as a Markdown file. The tool utilizes templates and configurations that are customizable for different use cases.

## Why? 

Generating a testable business models can be time consuming and tricky for entrepreneurs and innovators. This tool helps accelerate the process of generating business models with fewer inputs. 

The quality of the generated business models is dependent on the quality of the hunch brief. The tool is best suited for generating business models for early-stage ideas.

The tool is designed to speed up the brainstorming process, and does not replace the need for human input and judgement.

## Installation

1. Make sure you have Python 3.7 or newer installed. You can download it from [here](https://www.python.org/downloads/).

2. Clone the repository to your local machine:
   ```sh
   git clone https://github.com/<your_username>/business-modeler.git
   cd business-modeler
   ```

3. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Setting up the API Key

This tool requires an API key to communicate with the OpenAI language model. Please make sure you have an API key. Create an account [here](https://platform.openai.com/overview).


To set up the API key:

1. Create a `.env` file in the root directory of the project.
   
2. Add your API key in the `.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

The .env file will be ignored via the .gitignore file in this project, so you don't have to worry about accidentally committing your API key. But make sure you don't share your API key with anyone.

## Directory Structure

The project has the following directory structure:

```
business-modeler/
│
├── business_modeler.py            # Main script file
├── config.yaml                    # Configuration file
├── templates/                     # Directory for prompt templates
│   ├── _common.txt
│   └── ...
├── examples/                      # Directory for example seed files
│   ├── example1.md
│   └── ...
└── .env                           # Environment file for API key
```

## Usage

Use the `business_modeler.py` script to generate a business model. You need to provide a seed file, which contains the initial idea or input for the business model. The script will then use this seed to generate a report.

Use the following command to run the Business Modeler:

```sh
python business_modeler.py --seed-file examples/example1.md --output-file my_report
```

Here's a breakdown of the options you can use:

- `--seed-file`: Path to the seed file, which contains your initial ideas.
- `--output-file`: Specify the base name of the output file (optional).
- `--markdown`: If set, the output will be saved as Markdown as well as PDF.
- `--verbose`: If set, enables verbose output.
- `--config-file`: Path to the configuration file (default is `config.yaml`).
- `--temperature`: Set the temperature for the language model (controls randomness).
- `--model-name`: Set the name of the language model to be used.

Example usage:

```sh
python business_modeler.py --seed-file examples/example1.md --output-file my_report --markdown
```

This will generate a business model based on the seed file `examples/example1.md`, and save it as `my_report.pdf` and `my_report.md`.

## Customization

You can customize the prompt templates by editing the files in the `templates/` directory.

Additionally, you can customize the configuration of the chains by editing the `config.yaml` file.

## Contributing

Contributions to Business Modeler are very welcome! Here's how you can help:

1. **Fork and Clone**: Start by forking the repository and then clone your fork locally.

   ```sh
   git clone https://github.com/<your_username>/business-modeler.git
   cd business-modeler
   ```

2. **Create a Branch**: Create a new branch for the feature, bugfix, or documentation enhancement you are working on.

   ```sh
   git checkout -b your_new_branch_name
   ```

3. **Install Dependencies**: Ensure you've installed all the required dependencies as mentioned in the [Installation](#installation) section.

4. **Make Changes**: Make the necessary code or documentation changes. Test to make sure that your changes do not break existing functionality.

5. **Commit Your Changes**: Add and commit your changes. Use a clear and meaningful commit message.

   ```sh
   git add .
   git commit -m "A brief description of the changes"
   ```

6. **Push to GitHub**: Push your branch to GitHub.

   ```sh
   git push origin your_new_branch_name
   ```

7. **Create a Pull Request**: Go to the GitHub page of your fork. Click 'New Pull Request' and select your branch. Fill out the PR form, explaining the purpose of your changes. Make sure any relevant issues are linked.

8. **Code Review**: Maintainers will review your code. Engage in the conversation, and address any feedback they provide.

9. **Merge**: Once your pull request is approved, it will be merged into the main codebase.

10. **Celebrate**: Congratulations! You’ve just contributed to the Business Modeler project. Your efforts are appreciated by the community.


## Support

Give a ⭐️ if this project helped you!

## License

This project is [MIT](LICENSE) licensed.

## Support

Give a ⭐️ if this project helped you!