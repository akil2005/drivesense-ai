# src/rag/indexer.py

import os
import re
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MANUALS_DIR = os.path.join(BASE_DIR, "data", "manuals")
DB_DIR = os.path.join(BASE_DIR, "data", "vector_db")

# Standard OBD-II DTC regex pattern (e.g., P0171, U0100, B1234, C0021)
DTC_REGEX = r'\b[PBUC]\d{4}\b'

def extract_dtc_metadata(text: str) -> list:
    """Finds all standard diagnostic codes within a text block."""
    return list(set(re.findall(DTC_REGEX, text)))

def build_advanced_vector_database():
    print(f"Loading manuals from {MANUALS_DIR}...")
    
    txt_loader = DirectoryLoader(MANUALS_DIR, glob="**/*.txt", loader_cls=TextLoader)
    pdf_loader = DirectoryLoader(MANUALS_DIR, glob="**/*.pdf", loader_cls=PyPDFLoader)
    raw_documents = txt_loader.load() + pdf_loader.load()
    
    if not raw_documents:
        print("No manuals found in data/manuals/")
        return

    # Semantic splitter focusing on sentences and paragraphs first
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=75,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    split_chunks = text_splitter.split_documents(raw_documents)
    processed_chunks = []

    print("Injecting explicit metadata rules into chunks...")
    for chunk in split_chunks:
        # Scan the chunk text for alphanumeric codes
        found_dtcs = extract_dtc_metadata(chunk.page_content)
        
        # Enrich the existing metadata dictionary safely
        chunk.metadata["dtc_tags"] = ",".join(found_dtcs) if found_dtcs else "NONE"
        chunk.metadata["has_dtc"] = len(found_dtcs) > 0
        
        processed_chunks.append(chunk)

    print("Initializing embedding models locally...")
    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    print(f"Indexing {len(processed_chunks)} metadata-enriched blocks into ChromaDB...")
    db = Chroma.from_documents(
        documents=processed_chunks, 
        embedding=embedding_function, 
        persist_directory=DB_DIR
    )
    db.persist()
    print("Hybrid indexing complete.")

if __name__ == "__main__":
    build_advanced_vector_database()