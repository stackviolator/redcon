import pymilvus
from pymilvus import MilvusClient
from pymilvus import model
import os
import re

class VDBClient:
    def __init__(self, db="redcon.db", dim=768, collection_name="default", embedding_fn=model.DefaultEmbeddingFunction()):
        self.dim = dim
        self.collection_name=collection_name
        self.embedding_fn = embedding_fn

        print("[+] Generating vector DB")
        try:
            self.client = MilvusClient(db)
        except pymilvus.exceptions.ConnectionConfigException:
            print("[-] Could not connect to vector DB")
            import sys; sys.exit(-1)
        self.gen_vector_db()


    def populate_db(self, wiki_dir='wiki/'):
        """
        Load the dataset and embed as vectors. Insert embedded vectors to the db
        """
        def split_by_markdown_heading(text):
            """
            Use rege to split line starting with # (markdown heading)
            """
            return re.split(r'(?m)^#', text)
        
        def split_by_tokens(text, tokenizer, max_tokens=512):
            """
            Split the input text into max_tokens chunks
            """
            max_tokens = max_tokens - 10 # milnus does not specify their default tokenizer :( -- therefore splitting at the max token level can cause a mismatch

            # Lazy import to avoid parallelism error
            from transformers import AutoTokenizer
            tokenizer = AutoTokenizer.from_pretrained(tokenizer)

            tokens = tokenizer.encode(text, add_special_tokens=False)
            token_chunks = [tokens[i:i + max_tokens] for i in range(0, len(tokens), max_tokens)]
            text_chunks = [tokenizer.decode(chunk, skip_special_tokens=True) for chunk in token_chunks]

            return text_chunks

        print("[+] Loading dataset into DB...")
        dataset = []

        # Get all file names
        for file_name in os.listdir(wiki_dir):
            file_path = os.path.join(wiki_dir, file_name)

            # If file is valid, add each line to "dataset"
            if os.path.isfile(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        sections = split_by_markdown_heading(content)
                        for section in sections:
                            if section.strip():
                                dataset.extend(split_by_tokens(section, tokenizer="GPTCache/paraphrase-albert-small-v2"))
                except Exception as e:
                    print(f"Error reading {file_name}: {e}")

                # Embed all lines and insert into db
                vectors = self.embedding_fn.encode_documents(dataset)
                data = [
                    {"id": i, "vector": vectors[i], "text": dataset[i], "subject": "internal network"}
                    for i in range(len(vectors))
                ]

                self.client.insert(collection_name=self.collection_name, data=data)
                # Reset dataset
                dataset = []

    def gen_vector_db(self):
        """
        Generate vector db object and store in memory using a thread-safe queue
        """
        # If collection doesn't exist, create and populate it
        if not self.client.has_collection(collection_name=self.collection_name):
            print(f"[-] Collection name {self.collection_name} not found. Creating new...")
            self.client.create_collection(
                collection_name =self.collection_name,
                dimension=self.dim,
            )
            self.populate_db()

        # Prompt user to reinsert data, default is no
        else:
            while True:
                b_insert = input(f"[+] Vector DB found with collection \"{self.collection_name}\", do you want to recreate it? y/N\n>> ")
                if b_insert == "n" or b_insert == "N" or b_insert == "":
                    break
                elif b_insert == "y" or b_insert == "Y":
                    self.client.drop_collection(collection_name=self.collection_name)
                    self.client.create_collection(
                        collection_name =self.collection_name,
                        dimension=self.dim,
                    )
                    self.populate_db(wiki_dir="temp/")
                    break

        print(f"[+] Vector DB created successfully")

    def retrieve(self, query, top_n=5):
        """
        Embed query and return topn most similar chunks
        """
        q_vec = self.embedding_fn.encode_queries([query])

        res = self.client.search(
            collection_name=self.collection_name,
            data=q_vec,
            filter="subject == 'internal network'",
            limit=top_n,
            output_fields = ["text", "subject"],
        )

        # Res is a list of dicts with a sub dict which contains the outputted text, extract and return just the text
        return [l['entity']['text'] for d in res for l in d]

if __name__ == "__main__":
    vdb = VDBClient()
    res = vdb.retrieve("Nmap scan to show all windwos hosts")