from typing import List
import ell
from ell.types import ToolCall
from schemaindex import get_cloudformation_schema
from config import Configuration
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

class GeneratorAgent:
    """
    This agent creates a new template based on provided instructions and sample templates to match style.
    It also selects the appropriate prompt whether the user provides sample templates or not.
    """
    
    def __init__(self, config: Configuration):
        self.model = config.agent_model
        self.client = config.client


    def cfn_template_creator(self, message_history: List[ell.Message], sample_templates: bool = False) -> List[ell.Message]:
        @ell.complex(model=self.model, tools=[get_cloudformation_schema], temperature=0.4, client=self.client)
        def _create_template(messages: List[ell.Message]) -> List[ell.Message]:
            return messages

        return _create_template([
            ell.system(SYSTEM_PROMPT_STYLED if sample_templates else SYSTEM_PROMPT_PLAIN),
        ] + message_history)


    def create_template(self, initial_prompt: str, sample_templates: str = None):
        
        prompt = f"{initial_prompt}\n\n---{sample_templates}" if sample_templates else initial_prompt
        conversation = [ ell.user(prompt) ]

        response: ell.Message = self.cfn_template_creator(conversation, sample_templates is not None)
        
        max_iterations = 30
        while max_iterations > 0 and (response is ToolCall or response.tool_calls):
            tool_results = response.call_tools_and_collect_as_message()
            # Include what the user wanted, what the assistant requsted to run and what the tool returned
            conversation = conversation + [response, tool_results]
            response = self.cfn_template_creator(conversation)
            max_iterations -= 1
    
        if max_iterations <= 0:
            raise Exception("Too many iterations, probably stuck in a loop.")
        
        return response.text
