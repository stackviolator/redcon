from abc import ABC, abstractmethod
import os

class IAgent(ABC):
    def set_api_key(self, filepath: str = '.env'):
        """
        Set the OpenAI API key
        """
        with open(filepath, 'r') as f:
            for line in f:
                if line.startswith("OPENAI_API_KEY"):
                    os.environ['OPENAI_API_KEY'] = line.strip().split("=")[-1].strip("\"")

        assert os.environ['OPENAI_API_KEY'] is not None or os.environ['OPENAI_API_KEY'] != ""

    def read_system_prompt(self, filepath: str = "system_prompt.txt") -> str:
        """
        Read system prompt from file
        """
        prompt = ""
        with open(filepath, 'r') as f:
            for line in f:
                prompt += line

        return prompt

    def set_system_prompt(self, prompt: str | None = None):
        """
        Set the agent's system prompt
        """
        self.system_prompt = prompt

        @abstractmethod
        def add_tool(self):
            pass

        @abstractmethod
        def init_tools(self):
            pass

        @abstractmethod
        def update_short_term_memory(self):
            pass

        @abstractmethod
        def update_long_term_memory(self):
            pass

        @abstractmethod
        def handle_tool_calls(self):
            pass

        @abstractmethod
        def build_prompt(self):
            pass

        @abstractmethod
        def call_api(self):
            pass

