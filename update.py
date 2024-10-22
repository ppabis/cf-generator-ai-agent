import json, yaml, os, requests, zipfile, io
from datetime import datetime, timezone

def now() -> int:
    return int(datetime.now(timezone.utc).timestamp())

def last_update(create: bool = False) -> int:
    """
    Args:
        create: Whether to write a new .lastupdated file for current timestamp.
    
    If the db directory does not exist it will create it.
    Checks the last update date of the database.
    If there's no .lastupdated file it will return 0.
    """
    db_path = os.path.join(os.getcwd(), "db")
    if not os.path.exists(db_path):
        os.makedirs(db_path)

    last_update_path = os.path.join(db_path, ".lastupdated")
    if create:
        unix_timestamp = now()
        with open(last_update_path, "w") as f:
            f.write(str(unix_timestamp))
        return unix_timestamp
    else:
        if os.path.exists(last_update_path):
            with open(last_update_path, "r") as f:
                try:
                    return int(f.read())
                except:
                    return 0
        return 0


def download_zip(region: str):
    """
    Downloads the zip from AWS with CloudFormation schemas for a given region.
    Returns a zip file that you can browse.
    """
    URL = f"https://schema.cloudformation.{region}.amazonaws.com/CloudformationSchema.zip"
    response = requests.get(URL)
    if response.status_code != 200:
        raise Exception(f"Failed to download zip from {URL}")
    
    content = response.content
    zip_buffer = io.BytesIO(content)
    return zipfile.ZipFile(zip_buffer)


def load_file(zip: zipfile.ZipFile, name: str):
    """
    Loads and decodes a file from the zip - YAML or JSON.
    """
    if name.endswith(".json"):
        return json.loads(zip.read(name).decode("utf-8"))
    elif name.endswith(".yaml") or name.endswith(".yml"):
        return yaml.safe_load(zip.read(name).decode("utf-8"))
    else:
        return None


def cleanup_schema(schema: dict) -> dict:
    """
    Sort the YAML schema by the specified keys and leave other keys in whatever order at the end.
    Also get rid of unnecessary keys.
    """
    for key in ['handlers', 'propertyTransforms', 'sourceUrl']:
        schema.pop(key, None)
    
    sorted_content = {}
    
    for key in [
        'typeName', 
        'description', 
        'properties', 
        'definitions', 
        'createOnlyProperties', 
        'additionalProperties', 
        'readOnlyProperties', 
        'writeOnlyProperties'
    ]:
        value = schema.pop(key, None)
        if value:
            sorted_content[key] = value

    if not sorted_content.get('additionalProperties', False):
        sorted_content.pop('additionalProperties', None)
    
    sorted_content.update(schema)

    return sorted_content


def update_schema_file(zip: zipfile.ZipFile, file: str):
    """
    Updates a single schema file and saves it to the db directory.
    """
    content = load_file(zip, file)
    if content:
        content = cleanup_schema(content)
        content = inline_definitions(content)
        new_filename = file.replace(".json", ".yml")
        with open(os.path.join(os.getcwd(), "db", new_filename), "w") as f:
            yaml.dump(content, f, default_flow_style=False, sort_keys=False, width=1000)


def inline_definitions(schema: dict) -> dict:
    def replace_ref(obj):
        if isinstance(obj, dict):
            if '$ref' in obj:
                ref = obj['$ref'].split('/')[-1]
                if ref in schema.get('definitions', {}):
                    inlined: dict = {'$ref': ref}
                    inlined.update(schema['definitions'][ref].copy())
                    return inlined
            return {k: replace_ref(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [replace_ref(item) for item in obj]
        else:
            return obj

    inlined_schema = schema.copy()
    inlined_schema['properties'] = replace_ref(inlined_schema.get('properties', {}))
    inlined_schema.pop('definitions', None)
    return inlined_schema


AWS_REGION = os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "us-east-1"))

def update_database():
    if now() - last_update() > 60 * 60 * 24:
        print("Updating database...")
        with download_zip(AWS_REGION) as zip:
            for file in zip.namelist():
                update_schema_file(zip, file)
        last_update(create=True)
    else:
        print("Database is up to date.")
