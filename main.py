from data_pipeline.textChunking import chunk_documents
from data_pipeline.readPDF import process_document_bucket
from data_pipeline.embedding import embed_and_save

INPUT_FILE = "raw_text/extracted_text.txt"
OUTPUT_DIR = "chunks"
MAX_SIZE = 4000

if __name__ == "__main__":
    process_document_bucket()
    chunk_documents(INPUT_FILE, OUTPUT_DIR, MAX_SIZE)
    embed_and_save()