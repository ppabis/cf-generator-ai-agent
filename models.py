import sys
if sys.platform != "win32":
    from colorama import Fore, Style

# A list of models that can be used in either AWS Bedrock or OpenAI

# The actual ID of the model and its aliases that you can use in the CLI
MODEL_LIST = {
    "gpt-4o-mini": ["mini", "4o-mini", "mini4o", "gpt4o-mini", "gpt-4o-mini"],
    "gpt-4o": ["4o", "o4", "gpt4o", "gpt-4o"],
    "anthropic.claude-3-5-sonnet-20241022-v2:0": ["sonnet", "sonnet35", "sonnet-v2", "sonnetv2", "sonnet3.5", "sonnet-3.5", "anthropic.claude-3-5-sonnet-20241022-v2:0"],
    "anthropic.claude-3-5-haiku-20241022-v1:0": ["haiku35", "haiku-3.5", "anthropic.claude-3-5-haiku-20241022-v1:0"],
    "anthropic.claude-3-haiku-20240307-v1:0": ["haiku", "haiku3", "haiku-3", "anthropic.claude-3-haiku-20240307-v1:0"],
}

def get_model_id(model_name: str) -> str:
    for model_id, aliases in MODEL_LIST.items():
        if model_name in aliases:
            return model_id
    raise ValueError(f"Model {model_name} not found")


def get_choices() -> list[str]:
    if sys.platform == "win32":
        return [f"{v[0]} - {k}" for k, v in MODEL_LIST.items()]
    else:
        return [f"{Fore.LIGHTBLUE_EX}{Style.BRIGHT}{v[0]}{Fore.RESET}{Style.NORMAL} - {k}" for k, v in MODEL_LIST.items()]
