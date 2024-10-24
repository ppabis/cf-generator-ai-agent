CloudFormation Template Generator
=================================

Overview
--------

This tool is designed to create and modify AWS CloudFormation templates using instructions provided to a Large Language Model (LLM). It allows users to generate new templates or transform existing ones while adhering to specific coding style guidelines.

Features
--------

- **Create New Templates**: Generate CloudFormation templates from scratch based on user-defined instructions.
- **Modify Existing Templates**: Transform existing templates by applying specified changes.
- **Style Conformance**: Optionally base the style of generated templates on previously provided sample templates to ensure consistency with company coding standards.

Usage Instructions
------------------

1. **Install Dependencies**: Ensure that all required Python packages are installed. You may need to set up a virtual environment.
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
