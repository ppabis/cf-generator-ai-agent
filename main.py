from schemaindex import load_schemas
from update import update_database
from sample_templates import load_sample_templates
from datetime import datetime
import boto3
import argparse
import sys
from generator_agent import GeneratorAgent
from transformator_agent import TransformatorAgent
from config import Configuration
from models import get_model_id, get_choices

def write_template(template, filename: str = None):
    _filename = filename if filename else f"generated_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.yml"
    with open(_filename, "w") as f:
        f.write(template)

if __name__ == "__main__":
    # Update the CloudFormation schema index
    update_database()
    load_schemas()
    
    # Parse CLI arguments
    parser = argparse.ArgumentParser(description='Process or generate CloudFormation templates using LLMs', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--api', type=str, choices=['bedrock', 'openai'], help='Which API to use for LLM inference (bedrock or openai)', default='openai')
    parser.add_argument('--model', type=str, help=f"Which model to use for creating the template. Available models:\n" + "\n".join(get_choices()), default='mini')
    parser.add_argument('--sample', action='append', help='Sample YAML files to load to base the style on (creation only).\nBe careful with the token limit!', default=[])
    parser.add_argument('--output', type=str, help='Output file name for the generated template.', default=None)
    parser.add_argument('--transform', type=str, help='Transformation instructions for the generated template.', default=None)
    args = parser.parse_args()
    
    # Configure either for Amazon Bedrock or OpenAI
    if args.api == 'bedrock':
        bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
        # Fix the model name for the default if we are using Bedrock
        config = Configuration(
            commit_model = get_model_id('haiku'),
            agent_model = get_model_id('haiku') if args.model == 'mini' else get_model_id(args.model),
            client = bedrock
        )
    elif args.api == 'openai':
        config = Configuration(
            agent_model = get_model_id(args.model)
        )
    else:
        raise ValueError(f"Invalid API: {args.api}")
    
    # Load sample templates provided
    sample_values = args.sample if args.sample else []
    sample_templates = load_sample_templates(sample_values)

    # Read the template that is supposed to be transformed
    if args.transform:
        with open(args.transform, "r") as f:
            source_template = f.read()

    instructions = input() if not sys.stdin.isatty() else input("Enter the template instructions: ")

    # Run the agent
    if args.transform:
        transformator = TransformatorAgent(config)
        transformed_template = transformator.transform_template(instructions, source_template)
        write_template(transformed_template, args.output)
    else:
        generator = GeneratorAgent(config)
        created_template = generator.create_template(instructions, sample_templates)
        write_template(created_template, args.output)
    