import yaml
import os
from fuzzywuzzy import process
import ell
from pydantic import Field

schemas = None

class SchemaIndex:
    """
    A class to manage and retrieve schema definitions from YAML files.

    This class loads YAML files from a specified directory, storing their
    type names in a dictionary for quick access. It provides functionality
    to find the closest matching type name based on a given input and to
    retrieve the content of the corresponding YAML file.

    Attributes:
        type_name_dict (dict): A dictionary mapping lowercase type names to their corresponding YAML file names.
    """

    def __init__(self, directory='db'):
        self.type_name_dict = {}
        self.load_yaml_files(directory)


    def load_yaml_files(self, directory):
        if os.path.exists(directory):
            yaml_files = [file for file in os.listdir(directory) if file.endswith('.yaml') or file.endswith('.yml')]
            for yaml_file in yaml_files:
                with open(os.path.join(directory, yaml_file), 'r') as file:
                    try:
                        yaml_content = yaml.safe_load(file)
                        type_name = yaml_content.get('typeName')
                        if type_name:
                            self.type_name_dict[type_name.lower()] = yaml_file
                            # Also add the type name without the AWS:: prefix
                            self.type_name_dict[type_name.lower().replace("aws::", "")] = yaml_file
                        else:
                            print(f"No typeName found in {yaml_file}")
                    except yaml.YAMLError as e:
                        print(f"Error parsing {yaml_file}: {e}")


    def _closest_key(self, type_name) -> str | None:
        """
        Find the closest matching key in the type_name_dict.
        """
        if type_name.lower() in self.type_name_dict:
            return type_name.lower()
        else:
            closest_match, score = process.extractOne(type_name.lower(), self.type_name_dict.keys())
            if score > 70:
                return closest_match
            else:
                return None


    def get(self, type_name) -> str:
        """
        Look up a type name in the type_name_dict and load the corresponding YAML file.
        
        Args:
        type_name (str): The type name to look up (case-insensitive).
        
        Returns:
        str: The file content as string.
        """
        closest_key = self._closest_key(type_name)
        if closest_key:
            yaml_file = self.type_name_dict[closest_key]
            try:
                with open(os.path.join('db', yaml_file), 'r') as file:
                    return file.read()
            except IOError as e:
                return f"Error opening {yaml_file}: {e}. Failed to get definition of {type_name}"
        else:
            return f"No schema file found for {type_name}"

def load_schemas():
    global schemas
    schemas = SchemaIndex()

@ell.tool()
def get_cloudformation_schema(
    type_name: str = Field(description="The type name to get the schema for, e.g. AWS::S3::Bucket but can also be fuzzy such as 's3 bucket'")
) -> str:
    """
    Get the CloudFormation schema for a given type name.
    The resulting schema is a YAML document.
    It contains all the properties and descriptions for a given CloudFormation resource type.
    """
    if schemas is None:
        load_schemas()
    return schemas.get(type_name)
