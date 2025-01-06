
from openai import OpenAI
import json
import os
from redcon.agents.IAgent import IAgent
from redcon.logger import Logger
from redcon.rag import VDBClient
import subprocess


class SummaryAgent(IAgent):
    def __init__(self, model="llama3.1:8b", *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.model = model
        if "llama3.1" in self.model:
            try:
                self.client = OpenAI(
                    base_url = 'http://localhost:11434/v1',
                    api_key='ollama', # required, but unused
                )
            except:
                print(f"[-] Could not connect to api at http://localhost:11434/v1")
                import sys; sys.exit(1)
        elif "gpt-4o" in self.model:
            self.set_api_key()
            self.client = OpenAI()

        self.init_tools()
        self.set_system_prompt(self.read_system_prompt("prompts/summary.txt"))
        self.logger = Logger()

    def add_tool(self):
        pass

    def init_tools(self):
        self.tools = None

    def update_short_term_memory(self):
        pass

    def update_long_term_memory(self):
        pass

    def handle_tool_calls(self):
        pass

    def call_api(self, prompt):
        """
        Call the API
        """
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            tools=self.tools
        )

        output = completion.choices[0].message
        if output.content == "":
            output.content = "No text output from prompt" 
        print(f"Returned output is: {output.content}")

    def build_prompt(self, doc):
        prompt = f"""
        ** Document Start **
        {doc}
        ** Document End **
        """
        return prompt

    def run(self):
        with open("wiki/Network-Internal-Methodology:-Active-Scanning.md") as f:
            doc = f.read()

        prompt = self.build_prompt(doc)
        self.call_api(prompt)
        print("\n===========\n")
