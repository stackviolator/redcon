from smolagents import Tool
from redcon.rag import VDBClient

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