import os
import json
import chromadb

def verify_and_view_embeddings(index_dir="data/index"):
    # 1. Load active collection pointer
    active_json_path = os.path.join(index_dir, "active.json")
    if not os.path.exists(active_json_path):
        print(f"Error: active.json not found at {active_json_path}. Ingestion index must be built first.")
        return
        
    with open(active_json_path, "r", encoding="utf-8") as f:
        active_info = json.load(f)
    active_collection_name = active_info["active_collection"]
    print(f"Active Collection Name: {active_collection_name}")
    print(f"Created At: {active_info.get('created_at', 'Unknown')}\n")
    
    # 2. Connect to ChromaDB
    chroma_path = os.path.join(index_dir, "chroma")
    chroma_client = chromadb.PersistentClient(path=chroma_path)
    collection = chroma_client.get_collection(name=active_collection_name)
    
    # 3. Retrieve all items with their embeddings
    print("Fetching stored items and embeddings from ChromaDB...")
    results = collection.get(include=["documents", "metadatas", "embeddings"])
    
    ids = results.get("ids", [])
    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])
    embeddings = results.get("embeddings", [])
    
    total_items = len(ids)
    print(f"Total Chunks Found: {total_items}\n")
    
    if total_items == 0:
        print("Error: No items found in collection.")
        return
        
    # 4. Verify embeddings parameters
    print("="*60)
    print("EMBEDDING VERIFICATION AND METRICS")
    print("="*60)
    
    all_valid = True
    for idx, (cid, doc, meta, emb) in enumerate(zip(ids, documents, metadatas, embeddings)):
        if emb is None:
            print(f"[FAIL] Chunk ID {cid}: Embedding vector is missing (None)!")
            all_valid = False
            continue
            
        emb_dim = len(emb)
        if emb_dim != 384:
            print(f"[FAIL] Chunk ID {cid}: Embedding dimension is {emb_dim} (Expected: 384 for BGE-small)!")
            all_valid = False
            continue
            
        # Display first 5 chunks details, summarize the rest
        if idx < 5:
            print(f"\n[{idx+1}] Chunk ID: {cid}")
            print(f"    Scheme: {meta.get('scheme_name')}")
            print(f"    Section: {meta.get('section')}")
            print(f"    Text Preview: {doc[:100].replace(chr(10), ' ')}...")
            print(f"    Embedding Coordinates (first 5 dims): {emb[:5]}")
            print(f"    Total Vector Dims: {emb_dim} (Valid: Yes)")
            
    if all_valid:
        print("\n" + "="*60)
        print(f"SUCCESS: All {total_items} chunks verified. Dimensions are exactly 384.")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("VERIFICATION FAILED: Some chunks contain missing or malformed embedding vectors.")
        print("="*60)

if __name__ == "__main__":
    verify_and_view_embeddings()
