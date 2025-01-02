import pymilvus
from pymilvus import MilvusClient
from pymilvus import model
import ollama
import os

def populate_db(embedding_fn, client, collection_name, wiki_dir='wiki/'):
    """
    Load the dataset and embed as vectors. Insert embedded vectors to the db
    """
    print("[+] Loading dataset in DB...")
    dataset = []

    # Get all file names
    for file_name in os.listdir(wiki_dir):
        file_path = os.path.join(wiki_dir, file_name)

        # If file is valid, add each line to "dataset"
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    for line in file:
                        dataset.append(line)
            except Exception as e:
                print(f"Error reading {file_name}: {e}")

            # Embed all lines and insert into db
            vectors = embedding_fn.encode_documents(dataset)
            data = [
                {"id": i, "vector": vectors[i], "text": dataset[i], "subject": "internal network"}
                for i in range(len(vectors))
            ]

            client.insert(collection_name=collection_name, data=data)
            # Reset dataset
            dataset = []

def gen_vector_db(embedding_fn=model.DefaultEmbeddingFunction(), dim=768, collection_name="default", db="redcon.db"):
    """
    Generate vector db object and store in memory using a thread-safe queue
    """
    print("[+] Generating vector DB")
    try:
        client = MilvusClient(db)
    except pymilvus.exceptions.ConnectionConfigException:
        print("[-] Could not connect to vector DB")
        import sys; sys.exit(-1)
    
    # If collection doesn't exist, create and populate it
    if not client.has_collection(collection_name=collection_name):
        print(f"[-] Collection name {collection_name} not found. Creating new...")
        client.create_collection(
            collection_name =collection_name,
            dimension=dim,
        )
        populate_db(embedding_fn, client, collection_name=collection_name)

    # Prompt user to reinsert data, default is no
    while True:
        b_insert = input(f"[+] Vector DB found with collection \"{collection_name}\", do you want to re-insert the dataset? y/N\n>> ")
        if b_insert == "n" or b_insert == "N" or b_insert == "":
            break
        elif b_insert == "y" or b_insert == "Y":
            populate_db(embedding_fn, client, collection_name=collection_name)
            break

    print(f"[+] Vector DB created successfully")

def retrieve(query, client, collection_name, embedding_fn=model.DefaultEmbeddingFunction(), top_n=3):
    """
    Embed query and return topn most similar chunks
    """
    q_vec = embedding_fn.encode_queries([query])

    res = client.search(
        collection_name=collection_name,
        data=q_vec,
        filter="subject == internal network",
        limit=top_n,
        output_fields = ["text", "subject"],
    )

    print(res)

if __name__ == "__main__":
    gen_vector_db()
    # print(retrieve(vdb, "What is the command to find all windows workstations on a network using nmap?"))