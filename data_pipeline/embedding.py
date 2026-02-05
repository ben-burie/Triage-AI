from pathlib import Path
import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer

MODEL = "all-MiniLM-L6-v2"
chunks = []

def load_chunks(chunk_directory):
    for file in chunk_directory.iterdir():
        if file.is_file() and file.name != "_chunking_summary.txt":
            with open(file, 'r', encoding='utf-8') as current_file:
                content = current_file.read()
                chunks.append(content)

    return chunks

def chunk_embeddings(chunks):
    model = SentenceTransformer(MODEL)
    embeddings = model.encode(chunks)

    print(f"Embedding shape: {embeddings.shape}")
    for index, embedding in enumerate(embeddings):
        print(f"Embedding {index+1}: {embedding[:5]}")

    return embeddings

def save_embeddings(embeddings, chunks):
    directory = Path("vector_db")
    directory.mkdir(parents=True, exist_ok=True)
    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    faiss.write_index(index, str(directory / "embeddings.index"))

    with open(str(directory / "chunks.pk1"), "wb") as f:
        pickle.dump(chunks, f)

    print(f"Saved {len(chunks)} embeddings")

def embed_and_save():
    directory = Path("chunks")
    chunks = load_chunks(directory)
    embeddings = chunk_embeddings(chunks)
    save_embeddings(embeddings, chunks)

def search(query, top_k):
    model = SentenceTransformer(MODEL)
    directory = Path("vector_db")
    directory.mkdir(parents=True, exist_ok=True)

    query_embedding = model.encode([query])
    index = faiss.read_index(str(directory / "embeddings.index"))

    with open(str(directory / "chunks.pk1"), "rb") as f:
        chunks = pickle.load(f)
    
    distances, indicies = index.search(query_embedding, top_k)

    for i in indicies[0]:
        return chunks[i]

if __name__ == "__main__":
    chunks = search("Uw-Whitewater", 1)
    print(chunks)