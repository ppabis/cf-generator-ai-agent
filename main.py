from schemaindex import load_schemas
from update import update_database
from sample_templates import load_sample_templates
from datetime import datetime
import ell
import boto3
import argparse
import sys
from generator_agent import GeneratorAgent
from transformator_agent import TransformatorAgent
from config import Configuration


if __name__ == "__main__":
    # Update the CloudFormation schema index
    update_database()
    load_schemas()
    
    # Parse CLI arguments
    parser = argparse.ArgumentParser(description='Process or generate CloudFormation templates using LLMs')
    parser.add_argument('--api', type=str, choices=['bedrock', 'openai'], help='Which API to use for LLM inference (bedrock or openai)', default='openai')
    parser.add_argument('--sample', action='append', help='Sample YAML files to load to base the style on (creation only). Be careful with the token limit!', default=[])
    parser.add_argument('--transform', type=str, help='Transformation instructions for the generated template.', default=None)
    args = parser.parse_args()
    
    # Configure either for Amazon Bedrock or OpenAI
    if args.api == 'bedrock':
        bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
        config = Configuration(commit_model="anthropic.claude-3-haiku-20240307-v1:0", agent_model="anthropic.claude-3-haiku-20240307-v1:0", client=bedrock)
    elif args.api == 'openai':
        config = Configuration()
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
        with open(args.transform, "w") as f:
            f.write(transformed_template)
    else:
        generator = GeneratorAgent(config)
        created_template = generator.create_template(instructions, sample_templates)
        with open(f"generated_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.yml", "w") as f:
            f.write(created_template)
    