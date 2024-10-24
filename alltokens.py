from transformers import GPT2TokenizerFast

import os
import yaml

"""
This script counts the number of tokens in the most popular CloudFormation schemas in the db directory.
It will help you determine how many tokens you can use in your prompt assuming that you are allowed to
give 128k. This is the worst case scenario if the LLM requests to load all the schemas which is very unlikely.
"""

tokenizer = GPT2TokenizerFast.from_pretrained('Xenova/gpt-4')
text = ""
for yaml_file in os.listdir('db'):
    if (yaml_file.endswith('.yaml') or yaml_file.endswith('.yml') and 
        (yaml_file.startswith('aws-s3') or 
         yaml_file.startswith('aws-ec2') or 
         yaml_file.startswith('aws-rds') or 
         yaml_file.startswith('aws-iam'))
        and not yaml_file.startswith('aws-ec2-transit')):
        with open(os.path.join('db', yaml_file), 'r') as file:
            text += file.read() + "\n"  # Concatenate YAML file content as text
tokens = tokenizer.encode(text)
print(f"Number of tokens: {len(tokens)}")