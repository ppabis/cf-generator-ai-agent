CloudFormation Template Generator
=================================

Overview
--------

This script is designed to create and modify AWS CloudFormation templates using instructions provided to a Large Language Model (LLM). It allows users to generate new templates or transform existing ones while adhering to specific coding style guidelines.
At first the script downloads official CloudFormation schemas from AWS, transforms them from JSON to YAML removing some unnecessary fields and stores them in the `db` directory.

To control which region you download the schemas from, you can set the `AWS_REGION`/`AWS_DEFAULT_REGION` environment variable (most likely you won't need this).

Features
--------

- **Create New Templates**: Generate CloudFormation templates from scratch based on user-defined instructions.
- **Modify Existing Templates**: Transform existing templates by applying specified changes.
- **Style Conformance**: Optionally base the style of generated templates on previously provided sample templates to ensure consistency with company coding standards.

The LLM is given a tool that allows it to load the CloudFormation schema for a given resource type in order to reduce hallucinations, keep up to date with the latest resource types and properties or even expand its knowledge on a specific resource in case it
was "compressed out" during training.

Usage Instructions
------------------

1. **Install Dependencies**: Ensure that all required Python packages are installed. You may need to set up a virtual environment.

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run the Tool**:
   Execute the script using Python. You can provide optional arguments to customize its behavior:

    ```bash
    python main.py --sample <sample_template1.yml>
    python main.py --transform <template_to_transform.yml>
    ```

   - `--sample`: This argument allows you to specify one or more sample YAML files that the tool can use to base the style of the generated template on.
   - `--transform`: This argument specifies a file containing the CloudFormation template that you want to modify.

3. **Input Instructions**: When prompted, enter the instructions for the template you wish to create or modify. If you are using the `--transform` option, the tool will read the specified template file and then prompt you for the transformation instructions.
    Alternatively, you can pipe instructions directly into the tool using the `cat` command:

    ```bash
    cat instructions.txt | python main.py --transform <template_to_transform.yml>
    ```

4. **Output**:
   - For new files: the generated or transformed template will be saved to a new YAML file named with a timestamp, ensuring that you have a record of each generation,
   - For transformed files: the transformed template will be saved to the same file as the original template (**so make sure you do it in a Git repo**)

Examples
--------

### Creating a New Template

To create a new CloudFormation template for a VPC, you might run:

```bash
$ python main.py
Enter the template instructions: Create VPC with three private subnets in different AZs. For the VPC use CIDR block 10.20.0.0/16.
```

### Creating new template based on other template

If you want to include some hints for the LLM to follow, such as old CloudFormation template, you can do it like this:

```bash
$ python main.py --sample sample_template.yml
Enter the template instructions: Create VPC with three private subnets in different AZs.
```

### Transforming existing template

If you want to transform existing template, for example add a public subnet to the existing VPC, you can do it like this:

```bash
$ python main.py --transform existing_template.yml
Enter the transformation instructions: Add three public subnets to the VPC and make sure they are in different AZs.
```
