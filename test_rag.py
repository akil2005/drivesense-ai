# test_rag.py
from src.rag.retriever import query_vehicle_manuals_hybrid

def run_rag_evaluation():
    print("==================================================")
    print("EVALUATION 1: Test Deterministic DTC Filtering")
    print("==================================================")
    # Testing direct error code matching
    dtc_results = query_vehicle_manuals_hybrid(
        query_text="What are the diagnostic steps?", 
        active_dtc="P0128", 
        k=1
    )
    
    if dtc_results:
        print(f"✅ Success! Found match for P0128.")
        print(f"Content:\n{dtc_results[0].page_content}\n")
        print(f"Metadata associated: {dtc_results[0].metadata}\n")
    else:
        print("❌ Failed: No documents returned for explicit DTC filter.\n")

    print("==================================================")
    print("EVALUATION 2: Test Semantic Fallback (No DTC)")
    print("==================================================")
    # Testing natural language description without a code
    semantic_results = query_vehicle_manuals_hybrid(
        query_text="critical engine shutdown temperature limits", 
        active_dtc=None, 
        k=1
    )
    
    if semantic_results:
        print(f"✅ Success! Found semantically relevant chunk via Cosine Similarity.")
        print(f"Content:\n{semantic_results[0].page_content}\n")
    else:
        print("❌ Failed: Semantic fallback returned nothing.")

if __name__ == "__main__":
    run_rag_evaluation()