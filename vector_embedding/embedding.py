from pathlib import Path
from sentence_transformers import SentenceTransformer

chunks = []

def load_chunks(chunk_directory):
    for file in chunk_directory.iterdir():
        if file.is_file() and file.name != "_chunking_summary.txt":
            with open(file, 'r', encoding='utf-8') as current_file:
                content = current_file.read()
                chunks.append(content)

def chunk_embeddings(chunks):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(chunks)

    print(f"Embedding shape: {embeddings.shape}")
    for index, embedding in enumerate(embeddings):
        print(f"Embedding {index+1}: {embedding[:5]}")

    return embeddings

def save_embeddings(embeddings):
    # TO DO - fill in next
    return

if __name__ == "__main__":
    directory = Path("chunks")
    load_chunks(directory)
    embeddings = chunk_embeddings(chunks)