from pypdf import PdfReader
from pathlib import Path
import re

def extract_text_from_pdf(input_pdf):
    with open(input_pdf, 'rb') as file:
        reader = PdfReader(file)

        full_text = ""

        for page in reader.pages:
            full_text += page.extract_text() or ""

        metadata = extract_metadata(reader)

    return full_text, metadata

def clean_pdf_text(text):
    text = re.sub(r' +', ' ', text)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    cleaned_text = '\n'.join(lines)

    return cleaned_text

def extract_metadata(reader):
    metadata = reader.metadata
            
    return {
        'title': metadata.get('/Title', 'Unknown'),
        'author': metadata.get('/Author', 'Unknown'),
        'subject': metadata.get('/Subject', 'Unknown'),
        'creator': metadata.get('/Creator', 'Unknown'),
        'producer': metadata.get('/Producer', 'Unknown'),
        'creation_date': metadata.get('/CreationDate', 'Unknown'),
        'num_pages': len(reader.pages)
    }

def process_document_bucket():
    document_bucket_dir = Path("document_bucket")
    metadata_file = "raw_text/metadata.txt"
    output_path = "raw_text/extracted_text.txt"
    processed_count = 0

    for file in document_bucket_dir.iterdir():
        if file.is_file():
            extracted_text, metadata = extract_text_from_pdf(file)
            cleaned_text = clean_pdf_text(extracted_text)

            with open(metadata_file, 'a', encoding='utf-8') as meta_out:
                    meta_out.write(f"\n{'='*80}\n")
                    meta_out.write(f"FILE: {file.name}\n")
                    meta_out.write(f"{'-'*80}\n")
                    for key, value in metadata.items():
                        meta_out.write(f"{key}: {value}\n")

            with open(output_path, 'a', encoding='utf-8') as output_file:
                output_file.write(f"\nDOCUMENT: {file.name}\n")
                output_file.write(cleaned_text)

            processed_count += 1
            print("Files Processed: ", processed_count)