import json
from logger import Logger
import nmap
import os
from openai import OpenAI
from rag import VDBClient
import subprocess

class Agent:
    def __init__(self, model="llama3.1:8b"):
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
        self.memory = []
        self.max_memory = 10
        self.set_system_prompt(self.read_system_prompt("system_prompt.txt"))
        self.init_tools()
        self.logger = Logger()
        self.vdbc = VDBClient()
        self.retrieved = ""

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
        with open('redcon/tools.json', 'r') as f:
            data = json.load(f)

        self.tools = data

    def rag_query(self, arguments: dict) -> str:
        """
        Query vector DB for RAG
        """
        query = arguments.get("query")
        texts = self.vdbc.retrieve(query)
        self.retrieved = texts
        return texts # This is pretty much always discarded, really only for debugging

    def write_analysis(self, arguments: dict):
        """
        Write analysis to analysis.txt
        """
        try:
            with open("analysis.md", "w", encoding="utf-8") as file:
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
        NOTE: This jawn runs code, be careful. Experimented with sandboxed python-nmap, but its output is really bad.

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

    def update_short_term_memory(self, arguments: dict | str):
        """
        Add to self memory
        """
        memory = arguments['memory'] if isinstance(arguments, dict) else arguments # if the model calls this itself, the arg is a dict
        self.memory.append(memory)
        self.memory = self.memory[-self.max_memory:]

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
                output = f"[-] Error calling method '{call.function.name}': {e}"
            self.logger.log("Tool call", data, output, self.model)
            self.update_memory(f"Tool call: {call.function.name} {call.function.arguments}\nOutput: {output}")


    def call_api(self, prompt: str):
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
        self.logger.log("Prompt", prompt, output.content, self.model)
        print(f"Returned output is: {output.content}")
        # TODO: Make this async?
        if output.tool_calls is not None:
            self.handle_tool_calls(output.tool_calls)
        if "FINISHED" in str(output.content):
            return False
        return True

    def build_prompt(self) -> str:
        context = "\n- ".join(self.memory)
        prompt = f"Your goal is to perform reconaissance on an internal netowork. When needed, the scope can found in './scope.txt'. You will autonomously perform these actions.\nHere is a list of previous actions taken:\n- "
        prompt += context
        prompt += """\nInstructions:
        - Always give a written justification for you task
        - Decide whether to use a tool, update memory, or read memory
        - Only use tools when you are confident in your action and have a clear plan with a justification for doing so
        - Avoid using nmap scripts unless explicitly whitelisted
        - Ensure scanning is efficient as possible. Take into consideration the resilency of the targets if increasing scan speeds.
        - Organize all scan results in the scans/ directory
        - When you overall task is completed, return with a message saying "FINISHED". Do not add any formatting or additional characters
        - You have access to your organization's testing methodology, you can access this through a tool call to the vector database
        - When you write your analysis, include pertinent information such as hosts, services, ports, and vulnerabilities that were found during recon. Use markdown format for your analysis.
        - Queried documentation is denoted by ** Start documentation ** and ** End documentation **

    You are currently in development. In development, the scope of your duties are abridged. Your current objectives are the following:
    - Find and note all domain controllers 
    - Find all alive hosts
    - Document the services on each host
    - Make predictions about the type of each server based off of their services
    
    Use documentation if needed. When finished, synthesize all of your findings to analysis.txt
    """
        if self.retrieved != "":
            prompt += "\n** Start documentation: **\n"
            for r in self.retrieved:
                prompt += r
            prompt += "\n** End documentation: **\n"
        self.retrieved = ""
        return prompt

    def run(self):
        running = True
        while running:
            prompt = self.build_prompt()
            running = self.call_api(prompt)
            print("\n===========\n")
