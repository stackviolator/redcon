from redcon.agents.ReasoningAgent import ReasoningAgent
from redcon.agents.SummaryAgent import SummaryAgent
from smolagents import (
    CodeAgent,
    HfApiModel,
)
from redcon.tools.RetrieverTool import RetrieverTool

if __name__ == "__main__":
    gpt = "gpt-4o"
    llama = "llama3.1:8b"

    hf_model = HfApiModel()
    rag_agent = CodeAgent(tools=[RetrieverTool()], model=hf_model)

    agent = ReasoningAgent(model=gpt)
    # agent.run()
    # sagent = SummaryAgent(model=llama)
    # sagent.run()

    rag_agent.run("What are is the command to find all domain controllers in the network?")