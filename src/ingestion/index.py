import os
import json
import time
import datetime
import yaml
import chromadb
from sentence_transformers import SentenceTransformer

def load_corpus_config(config_path="config/corpus.yaml"):
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def build_scheme_metadata(processed_dir="data/processed"):
    config = load_corpus_config()
    schemes = config.get("schemes", [])
    
    metadata = {}
    last_fetched_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for scheme in schemes:
        slug = scheme["slug"]
        metadata[slug] = {
            "slug": slug,
            "name": scheme["name"],
            "category": scheme["category"],
            "source_url": scheme["source_url"],
            "last_fetched_at": last_fetched_at
        }
        
    metadata_path = os.path.join(processed_dir, "metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
        
    print(f"Successfully saved scheme metadata index to {metadata_path}")
    return metadata

def build_index(processed_dir="data/processed", index_dir="data/index"):
    os.makedirs(index_dir, exist_ok=True)
    
    # 1. Build metadata index
    build_scheme_metadata(processed_dir)
    
    # 2. Gather all chunks
    config = load_corpus_config()
    schemes = config.get("schemes", [])
    all_chunks = []
    
    for scheme in schemes:
        slug = scheme["slug"]
        chunks_path = os.path.join(processed_dir, slug, "chunks.json")
        if not os.path.exists(chunks_path):
            print(f"Chunks file not found for {slug} at {chunks_path}. Skipping.")
            continue
            
        with open(chunks_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)
            all_chunks.extend(chunks)
            
    if not all_chunks:
        print("No chunks found to index. Indexing aborted.")
        return False
        
    print(f"Loaded {len(all_chunks)} chunks to embed and index.")
    
    # 3. Load Embedding Model
    print("Loading SentenceTransformer model 'BAAI/bge-small-en-v1.5'...")
    model = SentenceTransformer("BAAI/bge-small-en-v1.5")
    
    # 4. Generate Embeddings
    print("Generating embeddings for all chunks...")
    texts = [chunk["text"] for chunk in all_chunks]
    embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)
    
    # Convert embeddings to float lists for Chroma
    embeddings_list = [emb.tolist() for emb in embeddings]
    
    # 5. Initialize Chroma DB Client and Collection Swap
    chroma_path = os.path.join(index_dir, "chroma")
    chroma_client = chromadb.PersistentClient(path=chroma_path)
    
    timestamp = int(time.time())
    new_collection_name = f"mutual_funds_index_{timestamp}"
    print(f"Creating new Chroma collection: {new_collection_name}")
    
    collection = chroma_client.create_collection(
        name=new_collection_name,
        metadata={"hnsw:space": "cosine"} # cosine similarity is recommended for BGE
    )
    
    # Prepare documents, ids, and metadata for Chroma
    ids = [chunk["id"] for chunk in all_chunks]
    
    # Clean metadatas: make sure there are no lists or complex dicts
    metadatas = []
    for chunk in all_chunks:
        meta = {
            "scheme_slug": chunk["id"].split("#")[0],
            "scheme_name": chunk["scheme_name"],
            "source_url": chunk["source_url"],
            "section": chunk["section"],
            "last_updated": chunk["last_updated"]
        }
        if "manager_name" in chunk:
            meta["manager_name"] = chunk["manager_name"]
        metadatas.append(meta)
        
    # Add to collection
    print(f"Adding documents to Chroma collection {new_collection_name}...")
    collection.add(
        ids=ids,
        embeddings=embeddings_list,
        metadatas=metadatas,
        documents=texts
    )
    
    # 6. Update active.json
    active_path = os.path.join(index_dir, "active.json")
    active_info = {
        "active_collection": new_collection_name,
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(active_path, "w", encoding="utf-8") as f:
        json.dump(active_info, f, indent=2)
        
    print(f"Updated pointer file {active_path} to collection {new_collection_name}")
    
    # 7. Clean up old collections
    print("Cleaning up old collections...")
    for col in chroma_client.list_collections():
        if col.name != new_collection_name:
            print(f"Deleting stale collection: {col.name}")
            chroma_client.delete_collection(name=col.name)
            
    print("Index build and collection swap completed successfully!")
    return True

if __name__ == "__main__":
    build_index()
