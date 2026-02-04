import re
from pathlib import Path
from typing import List

def chunk_documents(input_file, output_dir, max_chunk_size=4000, overlap=200):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    doc_pattern = r"DOCUMENT:\s*(.*)"
    matches = list(re.finditer(doc_pattern, content))
    
    documents = {}

    for i, match in enumerate(matches):
        raw_name = match.group(1).strip()
        doc_label = raw_name if raw_name else f"document_{i+1}"
        
        start_index = match.end()
        end_index = matches[i+1].start() if i + 1 < len(matches) else len(content)
        doc_text = content[start_index:end_index].strip()

        doc_key = f"DOCUMENT_{i+1}_{doc_label}"

        if len(doc_text) <= max_chunk_size:
            documents[doc_key] = [doc_text]
        else:
            documents[doc_key] = _split_large_document(doc_text, max_chunk_size, overlap)
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    total_chunks = 0
    for doc_name, chunks in documents.items():
        clean_name = "".join([c if c.isalnum() or c in (' ', '_', '-') else '_' for c in doc_name])
        
        for i, chunk_text in enumerate(chunks):
            if len(chunks) == 1:
                filename = f"{clean_name}.txt"
            else:
                filename = f"{clean_name}_part{i+1}.txt"
            
            filepath = output_path / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(chunk_text)
            total_chunks += 1

    _write_summary(output_path, documents, max_chunk_size, overlap, total_chunks)
    
    print(f"Processed {len(documents)} documents")
    print(f"Created {total_chunks} chunks")
    return documents

def _write_summary(output_path, documents, max_chunk_size, overlap, total_chunks):
    summary_path = output_path / "_chunking_summary.txt"
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(f"Chunking Summary\n{'='*80}\n")
        f.write(f"Max size: {max_chunk_size} | Overlap: {overlap}\n")
        f.write(f"Docs: {len(documents)} | Chunks: {total_chunks}\n\n")
        for doc_name, chunks in documents.items():
            f.write(f"{doc_name}: {len(chunks)} chunk(s)\n")

def _split_large_document(text: str, max_size: int, overlap: int) -> List[str]:
    chunks = []
    
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    current_chunk = []
    current_size = 0
    
    for para in paragraphs:
        para_size = len(para)
        
        if para_size > max_size:
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = []
                current_size = 0
            
            chunks.extend(_split_by_sentences(para, max_size, overlap))
        
        elif current_size + para_size + 2 > max_size and current_chunk:
            chunks.append('\n\n'.join(current_chunk))
            
            if len(current_chunk) > 0 and len(current_chunk[-1]) < overlap:
                current_chunk = [current_chunk[-1], para]
                current_size = len(current_chunk[-1]) + para_size + 2
            else:
                current_chunk = [para]
                current_size = para_size
        else:
            current_chunk.append(para)
            current_size += para_size + 2
    
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
    
    return chunks

def _split_by_sentences(text: str, max_size: int, overlap: int) -> List[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = []
    current_size = 0
    
    for sentence in sentences:
        sentence_size = len(sentence)

        if sentence_size > max_size:
            if current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_size = 0
            
            chunks.extend(_split_by_words(sentence, max_size, overlap))

        elif current_size + sentence_size + 1 > max_size and current_chunk:
            chunks.append(' '.join(current_chunk))

            overlap_text = ' '.join(current_chunk[-2:]) if len(current_chunk) >= 2 else current_chunk[-1] if current_chunk else ""
            if overlap_text and len(overlap_text) < overlap:
                current_chunk = current_chunk[-2:] + [sentence]
                current_size = len(overlap_text) + sentence_size + 1
            else:
                current_chunk = [sentence]
                current_size = sentence_size
        else:
            current_chunk.append(sentence)
            current_size += sentence_size + 1
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def _split_by_words(text: str, max_size: int, overlap: int) -> List[str]:
    words = text.split()
    chunks = []
    current_chunk = []
    current_size = 0
    
    for word in words:
        word_size = len(word) + 1
        
        if current_size + word_size > max_size and current_chunk:
            chunks.append(' '.join(current_chunk))

            overlap_words = []
            overlap_size = 0
            for w in reversed(current_chunk):
                if overlap_size + len(w) + 1 < overlap:
                    overlap_words.insert(0, w)
                    overlap_size += len(w) + 1
                else:
                    break
            
            current_chunk = overlap_words + [word]
            current_size = overlap_size + word_size
        else:
            current_chunk.append(word)
            current_size += word_size
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks