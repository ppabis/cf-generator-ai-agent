from typing import List
import ell
from ell.types import ToolCall
from schemaindex import get_cloudformation_schema
from config import Configuration

SYSTEM_PROMPT = """You are an AI assistant that modifies CloudFormation templates based on given instructions.
                You are provided with a tool that you can call in order to ensure what can be done with each resource in CloudFormation.
                Instead of hallucinating, you can verify that with the tool. Everything you generate should be a valid YAML document.
                Use comments to communicate with the user instead of leaving plain text around YAML code. As the last message where you verified everything
                with the tools RESPOND ONLY WITH THE YAML CODE WITHOUT MARKDOWN OR ANY OTHER TEXT. JUST THE YAML CODE AND COMMENTS INSIDE.
                Focus especially on commenting the changes you performed on the template."""

class TransformatorAgent:
    """
    This agent transforms a given CloudFormation template based on provided instructions.
    """

    def __init__(self, config: Configuration):
        self.model = config.agent_model
        self.client = config.client

    def cfn_template_transformer(self, message_history: List[ell.Message]) -> List[ell.Message]:
        @ell.complex(model=self.model, tools=[get_cloudformation_schema], temperature=0.4, client=self.client)
        def _transform(messages: List[ell.Message]) -> List[ell.Message]:
            return messages

        return _transform([
            ell.system(SYSTEM_PROMPT),
        ] + message_history)

    def transform_template(self, initial_prompt: str, source_template: str):
        
        conversation = [ ell.user(f"{source_template}\n\n---{initial_prompt}") ]
        
        response: ell.Message = self.cfn_template_transformer(conversation)
        
        max_iterations = 30
        while max_iterations > 0 and (response is ToolCall or response.tool_calls):
            tool_results = response.call_tools_and_collect_as_message()
            # Include what the user wanted, what the assistant requsted to run and what the tool returned
            conversation = conversation + [response, tool_results]
            response = self.cfn_template_transformer(conversation)
            max_iterations -= 1
        
        if max_iterations <= 0:
            raise Exception("Too many iterations, probably stuck in a loop.")
        
        return response.text
