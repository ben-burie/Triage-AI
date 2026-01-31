from pypdf import PdfReader
from pathlib import Path
import re

def extract_text_from_pdf(input_pdf):
    with open(input_pdf, 'rb') as file:
        reader = PdfReader(file)

        full_text = ""

        for page in reader.pages:
            full_text += page.extract_text() or ""

    return full_text

def clean_pdf_text(text):
    text = re.sub(r' +', ' ', text)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    cleaned_text = '\n'.join(lines)

    return cleaned_text

def main():
    document_bucket_dir = Path("document_bucket")

    for file in document_bucket_dir.iterdir():
        if file.is_file():
            extracted_text = extract_text_from_pdf(file)
            cleaned_text = clean_pdf_text(extracted_text)

            with open('extracted_text.txt', 'a', encoding='utf-8') as output_file:
                output_file.write("\n\n----------------NEW DOCUMENT STARTS HERE: " + file.name + "-----------------------\n\n")
                output_file.write(cleaned_text)

if __name__ == "__main__":
    main()