from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import Manager
import multiprocessing
import ollama
import os

def load_dataset(wiki_dir='wiki/'):
    """
    Load the wiki as a dataset in memory
    """
    dataset = []

    for file_name in os.listdir(wiki_dir):
        file_path = os.path.join(wiki_dir, file_name)

        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    for line in file:
                        dataset.append(line)
            except Exception as e:
                print(f"Error reading {file_name}: {e}")

    return dataset

def add_chunk_to_database(chunk, embedding_model='hf.co/CompendiumLabs/bge-base-en-v1.5-gguf'):
    """
    Add given text chunk's embedding to vector db
    """
    embedding = ollama.embed(model=embedding_model, input=chunk)['embeddings'][0]
    return chunk, embedding

def worker(chunk, embedding_model, queue):
    """
    Worker function to compute embedding and put the result in the queue
    """
    try:
        chunk, embedding = add_chunk_to_database(chunk, embedding_model)
        queue.put((chunk, embedding))  # Thread-safe addition
    except Exception as e:
        print(f"Error processing chunk: {e}")

def gen_vector_db(embedding_model='hf.co/CompendiumLabs/bge-base-en-v1.5-gguf', wiki_dir='wiki/', max_workers=10):
    """
    Generate vector db object and store in memory using a thread-safe queue
    """
    print("[+] Generating vector DB")
    # Use multiprocessing.Manager to create a shared queue
    with Manager() as manager:
        db_queue = manager.Queue()
        
        # Dataset loading
        dataset = load_dataset(wiki_dir)
        
        # Use ProcessPoolExecutor for parallel processing
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(worker, chunk, embedding_model, db_queue) 
                for chunk in dataset
            ]
            
            # Wait for all futures to complete
            for i, future in enumerate(as_completed(futures)):
                try:
                    future.result()
                except Exception as e:
                    print(f"Error in future {i+1}: {e}")
        
        # Collect all items from the queue
        db = []
        while not db_queue.empty():
            db.append(db_queue.get())

    print("[+] Vector DB created") 
    return db

def cosine_similarity(a, b):
    dot_product = sum([x * y for x,y in zip(a, b)])
    norm_a = sum([x ** 2 for x in a]) ** 0.5
    norm_b = sum([x ** 2 for x in b]) ** 0.5
    return dot_product / (norm_a * norm_b)

def retrieve(vdb, query, top_n=3, embedding_model='hf.co/CompendiumLabs/bge-base-en-v1.5-gguf'):
    """
    Embed query and return topn most similar chunks
    """
    q_emb = ollama.embed(model=embedding_model, input=query)['embeddings'][0]
    similarities = []
    for chunk, embedding in vdb:
        similarity = cosine_similarity(q_emb, embedding)
        similarities.append((chunk, similarity))
    similarities.sort(key=lambda x: x[1], reverse=True)

    return similarities[:top_n]

if __name__ == "__main__":
    vdb = gen_vector_db()
    print(retrieve(vdb, "What is the command to find all windows workstations on a network using nmap?"))