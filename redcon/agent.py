import json
from logger import Logger
import os
from openai import OpenAI
from rag import VDBClient
import subprocess

class Agent:
    def __init__(self):
        self.set_api_key()
        self.client = OpenAI()
        self.memory = []
        self.max_memory = 10
        self.set_system_prompt(self.read_system_prompt("system_prompt.txt"))
        self.init_tools()
        self.logger = Logger()
        self.vdbc = VDBClient()

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

    def add_tool(self, tool: dict):
        """
        Add a tool to the agent, not really used as of now. Really only here if you want to dynamically add tools later
        """
        self.tools.append(tool)

    def init_tools(self):
        """
        Initialize base tools and add them to store
        """
        tools = [
        {
            "type": "function",
            "function": {
                "name": "run_nmap_scan",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "args": {"type": "string"}
                        },
                    },
                },
            },
        {
            "type": "function",
            "function": {
                "name": "update_memory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "memory": {"type": "string"}
                        },
                    },
                },
            },
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string"}
                        },
                    },
                },
            },
        {
            "type": "function",
            "function": {
                "name": "mkdir",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"}
                        },
                    },
                },
            },
        {
            "type": "function",
            "function": {
                "name": "rmdir",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"}
                        },
                    },
                },
            },
        {
            "type": "function",
            "function": {
                "name": "write_analysis",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "analysis": {"type": "string"}
                        },
                    },
                },
            },
        {
            "type": "function",
            "function": {
                "name": "rag_query",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"}
                        },
                    },
                },
            },
        ]
        
        self.tools = tools

    def rag_query(self, arguments: dict) -> str:
        """
        Query vector DB for RAG
        """
        query = arguments.get("query")
        return self.vdbc.retrieve(query)

    def write_analysis(self, arguments: dict):
        """
        Write analysis to analysis.txt
        """
        try:
            with open("analysis.txt", "w", encoding="utf-8") as file:
                for key, value in arguments.items():
                    file.write(f"{key}: {value}\n")
        except Exception as e:
            print(f"An error occurred while writing to the file: {e}")

    def mkdir(self, arguments: dict) -> str:
        """
        Make the directory, return if succeeded
        """
        dir_name = arguments.get("name")
        if not dir_name:
            print("[-] Directory name not provided.")
            return False
        
        # Ensure the directory is created in the current directory
        target_path = os.path.join(os.getcwd(), dir_name)
        
        try:
            os.mkdir(target_path)
            return f"[+] Directory '{dir_name}' created successfully."
        except FileExistsError:
            return f"[-] Directory '{dir_name}' already exists."
        except PermissionError:
            return f"[-] Permission denied to create '{dir_name}'."
        except Exception as e:
            return f"[-] Error creating directory '{dir_name}': {e}"

    def rmdir(self, arguments: dict) -> bool:
        """
        Remove the directory, return if succeeded
        """
        dir_name = arguments.get("name")
        if not dir_name:
            print("[-] Directory name not provided.")
            return False
        
        # Ensure the directory is targeted within the current directory
        target_path = os.path.join(os.getcwd(), dir_name)
        
        try:
            # Check if the target path is a directory
            if not os.path.isdir(target_path):
                return f"[-] '{dir_name}' is not a directory or does not exist."
            os.rmdir(target_path)
            return f"[+] Directory '{dir_name}' removed successfully."
        except OSError:
            return f"[-] Directory '{dir_name}' is not empty or cannot be removed."
        except PermissionError:
            return f"[-] Permission denied to remove '{dir_name}'."
        except Exception as e:
            return f"[-] Error removing directory '{dir_name}': {e}"

    def run_nmap_scan(self, arguments: dict) -> str:
        """
        Run nmap scan with provided args
        NOTE: This jawn runs code, be careful

        arguments: dict that maps str -> args
        """
        args = arguments['args']
        cmd = f"nmap {args}"
        cmd = cmd.split(" ")
        result = subprocess.run(cmd, capture_output=True, text=True)

        return str({
            "output": result.stdout,
            "error": result.stderr,
            "return_code": result.returncode
        })


    def update_memory(self, arguments: dict | str):
        """
        Add to self memory
        """
        memory = arguments['memory'] if isinstance(arguments, dict) else arguments
        self.memory.append(memory)
        self.memory = self.memory[-self.max_memory:]
        print(f"Updated memory with {memory}")

    def read_file(self, arguments: dict) -> str:
        """
        Read file, restricted to the current directory, exclude .env
        """
        filename = arguments['filename']
        base_directory = os.getcwd()
        file_path = os.path.abspath(os.path.join(base_directory, filename))

        # Check if the file is in the current directory
        if not file_path.startswith(base_directory):
            raise ValueError("Access to files outside the current directory is restricted.")

        # Exclude the .env file
        if os.path.basename(file_path) == ".env":
            raise ValueError("Access to '.env' file is restricted.")

        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file '{filename}' does not exist.")

        # Read and return the file content
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        return content 
    
    def handle_tool_calls(self, tool_calls):
        for call in tool_calls:
            # Log tool call
            data = f"Tool call: {call.function.name} {call.function.arguments}"
            print(data)
            # Dynamically get the method name, requires the tool name and method are equal
            try:
                method = getattr(self, call.function.name)
                output = method(json.loads(call.function.arguments))
            except AttributeError:
                print(f"[-] Method '{call.function.name}' not found.")
                output = None
            except Exception as e:
                print(f"[-] Error calling method '{call.function.name}': {e}")
                output = None
            self.logger.log(data, output)
            self.update_memory(f"Tool call: {call.function.name} {call.function.arguments}\nOutput: {output}")


    def call_api(self, prompt: str):
        """
        Call the API
        """
        completion = self.client.chat.completions.create(
            model="gpt-4o",
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
        self.logger.log(prompt, output.content)
        print(f"Returned output is : {output.content}")
        if "FINISHED" in str(output.content):
            return False
        # TODO: Make this async?
        if output.tool_calls is not None:
            self.handle_tool_calls(output.tool_calls)
        return True

    def build_prompt(self) -> str:
        context = "\n".join(self.memory)
        prompt = f"""
        Your goal is to perform reconaissance on the given scope found in './scope.txt'. You will autonomously perform these actions.
        Here is a list of previous actions taken:
        {context}

        Instructions:
        - Always give a written justification for you task
        - Decide whether to use a tool, update memory, or read memory
        - Only use tools when you are confident in your action and have a clear plan with a justification for doing so
        - Avoid using nmap scripts unless explicitly whitelisted
        - Organize all scan results in the scans/ directory
        - When you overall task is completed, return with a message saying "FINISHED". Do not add any formatting or additional characters
        - You have access to your organization's testing methodology, you can access this through a tool call to the vector database


        You are currently in development. In development, the scope of your duties are abridged. For this overall task, find all domain controllers on the current network.
        """
        # You are currently in development. In development, the scope of your duties are abridged. For this overall task, only identify the available hosts, and the services available on the hosts. Once hosts are services are identified, consolidate the information and descrive the network, machines, and services in 'analysis.txt'. Provide relavent data.

        return prompt

    def run(self):
        running = True
        while running:
            prompt = self.build_prompt()
            running = self.call_api(prompt)
            print("\n===========\n")
