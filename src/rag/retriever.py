# src/rag/retriever.py

import os
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_DIR = os.path.join(BASE_DIR, "data", "vector_db")

def query_vehicle_manuals_hybrid(query_text: str, active_dtc: str = None, k: int = 2):
    """
    Queries ChromaDB utilizing a deterministic metadata filter if a DTC is present,
    falling back entirely to cosine semantic search if no code exists.
    """
    if not os.path.exists(DB_DIR):
        return []

    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    db = Chroma(persist_directory=DB_DIR, embedding_function=embedding_function)
    
    # Construct metadata filter if a fault code is passed
    search_filter = None
    if active_dtc:
        search_filter = {"dtc_tags": active_dtc}
        
    results = db.similarity_search(
        query_text, 
        k=k,
        filter=search_filter  # Chroma filters out non-matching chunks instantly
    )
    
    # Fallback to standard search if metadata filtering returned empty due to strict index mismatch
    if not results and search_filter:
        results = db.similarity_search(query_text, k=k)
        
    return results