from typing import Optional
from smolagents import (
    CodeAgent,
    HfApiModel,
    tool,
    Tool,
    DuckDuckGoSearchTool,
    LiteLLMModel,
    GradioUI
)
import os
from redcon.rag import VDBClient

class RagAgent():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_api_key()
        model = LiteLLMModel(model_id="openai/gpt-4o") # Could use 'gpt-4o'
        model = HfApiModel()
        rettool = RetrieverTool()
        self.agent = CodeAgent(tools=[rettool], model=model, max_steps=4, verbose=True)

    def set_api_key(self, filepath: str = '.env'):
        """
        Set the OpenAI API key
        """
        with open(filepath, 'r') as f:
            for line in f:
                if line.startswith("OPENAI_API_KEY"):
                    os.environ['OPENAI_API_KEY'] = line.strip().split("=")[-1].strip("\"")

class RetrieverTool(Tool):
    name = "retriever"
    description = "Uses semantic search to retrieve parts of penetration testing documentations which can be relevant to the query."
    inputs = {
        "query": {
            "type" : "string",
            "description" : "The query to perform. This should be semantically close to your target documents. Use the affirmative rather than a question."
        },
        "topn": {
            "type" : "integer",
            "description" : "The number of exmaples to return."
        }
    }
    output_type = "string"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vdbc = VDBClient()

    def forward(self, query: str, topn: int) -> str:
        assert isinstance(query, str), "The query must be a string"

        docs = self.vdbc.retrieve(query, top_n=topn)

        return "\nRetrieved documents:\n" + "".join(
            [
                f"\n\n===== Document {str(i)} =====\n" + doc
                for i, doc in enumerate(docs)
            ]
        )


if __name__ == "__main__":
    agent = RagAgent()
    GradioUI(agent.agent).launch()