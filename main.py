from data_pipeline.textChunking import chunk_documents
from data_pipeline.readPDF import process_document_bucket
from data_pipeline.embedding import embed_and_save
from llm_Interaction import query_llm

INPUT_FILE = "raw_text/extracted_text.txt"
OUTPUT_DIR = "chunks"
MAX_SIZE = 4000

def ask_question():
    user_prompt = input("\n\nAsk a question: ")
    response = query_llm(user_prompt)
    print(response)

if __name__ == "__main__":
    process_document_bucket()
    chunk_documents(INPUT_FILE, OUTPUT_DIR, MAX_SIZE)
    embed_and_save()
    ask_question()