import subprocess
import sys
import os
import json
from typing import Dict, List, Optional

try:
    import anthropic
except ImportError:
    user_input = input("The 'together' library is required. Install it now? [y/N]: ")
    if user_input.lower() == 'y':
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "anthropic"])
            import anthropic
        except subprocess.CalledProcessError:
            print("Failed to install 'anthropic'. Please install it manually using 'pip install anthropic'.")
            sys.exit(1)
    else:
        print("The required 'anthropic' library is not installed.")
        sys.exit(1)

from mem0.llms.base import LLMBase
from mem0.configs.llms.base import BaseLlmConfig


class AnthropicLLM(LLMBase):
    def __init__(self, config: Optional[BaseLlmConfig] = None):
        super().__init__(config)

        if not self.config.model:
            self.config.model = "claude-3-5-sonnet-20240620"

        api_key = self.config.api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate_response(
        self,
        messages: List[Dict[str, str]],
        response_format=None,
        tools: Optional[List[Dict]] = None,
        tool_choice: str = "auto",
    ):
        """
        Generate a response based on the given messages using Anthropic.

        Args:
            messages (list): List of message dicts containing 'role' and 'content'.
            response_format (str or object, optional): Format of the response. Defaults to "text".
            tools (list, optional): List of tools that the model can call. Defaults to None.
            tool_choice (str, optional): Tool choice method. Defaults to "auto".

        Returns:
            str: The generated response.
        """
        # Separate system message from other messages
        system_message = ""
        filtered_messages = []
        for message in messages:
            if message['role'] == 'system':
                system_message = message['content']
            else:
                filtered_messages.append(message)

        params = {
            "model": self.config.model,
            "messages": filtered_messages,
            "system": system_message,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "top_p": self.config.top_p,
        }
        if tools: # TODO: Remove tools if no issues found with new memory addition logic
            params["tools"] = tools
            params["tool_choice"] = tool_choice

        response = self.client.messages.create(**params)
        return response.content[0].text
