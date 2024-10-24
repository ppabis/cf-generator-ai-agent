from schemaindex import load_schemas
from update import update_database
from generator_agent import create_template
from transformator_agent import transform_template
from sample_templates import load_sample_templates
from datetime import datetime
import ell
import argparse
import sys

ell.init(store="log", autocommit=True)

if __name__ == "__main__":
    update_database()
    load_schemas()
    
    parser = argparse.ArgumentParser(description='Process or generate CloudFormation templates using LLMs')
    parser.add_argument('--sample', action='append', help='Sample YAML files to load to base the style on (creation only). Be careful with the token limit!', default=[])
    parser.add_argument('--transform', type=str, help='Transformation instructions for the generated template.', default=None)
    args = parser.parse_args()
    
    sample_values = args.sample if args.sample else []
    sample_templates = load_sample_templates(sample_values)

    if args.transform:
        with open(args.transform, "r") as f:
            source_template = f.read()

    instructions = input() if not sys.stdin.isatty() else input("Enter the template instructions: ")

    if args.transform:
        transformed_template = transform_template(instructions, source_template)
        with open(args.transform, "w") as f:
            f.write(transformed_template)
    else:
        created_template = create_template(instructions, sample_templates)
        with open(f"generated_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.yml", "w") as f:
            f.write(created_template)
    