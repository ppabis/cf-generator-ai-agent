from typing import List
import ell
from ell.types import ToolCall
from schemaindex import get_cloudformation_schema

SYSTEM_PROMPT_PLAIN = """You are an AI assistant that generates CloudFormation templates based on given instructions.
                Moreover, you are provided with a tool that you can call in order to ensure what can be done
                with each resource in CloudFormation. Instead of hallucinating, you can verify that with the tool.
                Everything you generate should be a valid YAML document. Use comments to communicate with the user
                instead of leaving plain text around YAML code. As the last message where you verified everything
                with the tools RESPOND ONLY WITH THE YAML CODE WITHOUT MARKDOWN OR ANY OTHER TEXT. JUST THE YAML
                CODE AND COMMENTS INSIDE."""

SYSTEM_PROMPT_STYLED = """You are an AI assistant that generates CloudFormation templates based on given instructions.
                User provided you with sample templates so KEEP THE STYLE SIMILAR TO THE PROVIDED SAMPLES.
                Moreover, you are provided with a tool that you can call in order to ensure what can be done
                with each resource in CloudFormation. Instead of hallucinating, you can verify that with the tool.
                Everything you generate should be a valid YAML document. Use comments to communicate with the user
                instead of leaving plain text around YAML code. As the last message where you verified everything
                with the tools RESPOND ONLY WITH THE YAML CODE WITHOUT MARKDOWN OR ANY OTHER TEXT. JUST THE YAML
                CODE AND COMMENTS INSIDE. REMEMBER TO KEEP THE STYLE SIMILAR TO THE PROVIDED SAMPLES.
                YOU DO NOT have to copy all the resources from the samples just follow the principles.
                FOCUS ON USER'S INSTRUCTIONS FOR GENERATION MORE."""

@ell.complex(model="gpt-4o-mini", tools=[ get_cloudformation_schema ], temperature=0.4)
def cfn_template_creator(message_history: List[ell.Message], sample_templates: bool = False) -> List[ell.Message]:
    return [
        ell.system(SYSTEM_PROMPT_STYLED if sample_templates else SYSTEM_PROMPT_PLAIN),
    ] + message_history

def create_template(initial_prompt: str, sample_templates: str = None):
    prompt = f"{initial_prompt}\n\n---{sample_templates}" if sample_templates else initial_prompt
    conversation = [ ell.user(prompt) ]
    response: ell.Message = cfn_template_creator(conversation, sample_templates is not None)
    
    max_iterations = 30
    while max_iterations > 0 and (response is ToolCall or response.tool_calls):
        tool_results = response.call_tools_and_collect_as_message()
        # Include what the user wanted, what the assistant requsted to run and what the tool returned
        conversation = conversation + [response, tool_results]
        response = cfn_template_creator(conversation)
        max_iterations -= 1
    
    if max_iterations <= 0:
        raise Exception("Too many iterations, probably stuck in a loop.")
    
    return response.text
