import os
import json
import yaml
import chromadb
from sentence_transformers import SentenceTransformer

class MutualFundRetriever:
    def __init__(self, corpus_path="config/corpus.yaml", index_dir="data/index"):
        self.corpus_path = corpus_path
        self.index_dir = index_dir
        
        # Load corpus config
        with open(self.corpus_path, "r", encoding="utf-8") as f:
            self.corpus_config = yaml.safe_load(f)
            
        # Get active collection
        active_json_path = os.path.join(self.index_dir, "active.json")
        if not os.path.exists(active_json_path):
            raise FileNotFoundError(f"Active collection pointer not found at {active_json_path}. Run ingestion first.")
            
        with open(active_json_path, "r", encoding="utf-8") as f:
            active_info = json.load(f)
        self.active_collection_name = active_info["active_collection"]
        
        # Load BGE embedding model
        print("Loading SentenceTransformer model for retrieval...")
        self.model = SentenceTransformer("BAAI/bge-small-en-v1.5")
        
        # Initialize Chroma persistent client
        chroma_path = os.path.join(self.index_dir, "chroma")
        self.chroma_client = chromadb.PersistentClient(path=chroma_path)
        self.collection = self.chroma_client.get_collection(name=self.active_collection_name)
        print(f"Retriever initialized with collection: {self.active_collection_name}")

    def detect_scheme_slug(self, query):
        """
        Scans the query for keywords/aliases of the 5 schemes.
        Returns the matching scheme slug, or None if no match.
        """
        query_lower = query.lower()
        schemes = self.corpus_config.get("schemes", [])
        
        # Exact match or alias scan
        for scheme in schemes:
            slug = scheme["slug"]
            if slug in query_lower:
                return slug
            aliases = scheme.get("aliases", [])
            for alias in aliases:
                if alias.lower() in query_lower:
                    return slug
                    
        return None

    def retrieve(self, query, limit=3):
        """
        Retrieves matching chunks from ChromaDB.
        Applies metadata filtering by scheme slug if detected in the query.
        """
        detected_slug = self.detect_scheme_slug(query)
        
        # BGE query prefix
        prefixed_query = f"Represent this sentence for searching relevant passages: {query}"
        
        # Generate query embedding
        query_embedding = self.model.encode(prefixed_query, normalize_embeddings=True).tolist()
        
        # Setup metadata filter
        where_filter = None
        if detected_slug:
            print(f"Detected query targets scheme: '{detected_slug}'. Applying metadata filter.")
            where_filter = {"scheme_slug": detected_slug}
        else:
            print("No specific scheme detected in query. Searching across all schemes.")
            
        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            where=where_filter
        )
        
        # Format results cleanly
        retrieved_items = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            ids = results["ids"][0]
            distances = results["distances"][0] if "distances" in results else [0.0] * len(docs)
            
            for i in range(len(docs)):
                retrieved_items.append({
                    "id": ids[i],
                    "text": docs[i],
                    "metadata": metas[i],
                    "score": 1.0 - distances[i] # Cosine similarity score
                })
                
        # Simple Keyword Boosting / Re-ranking (to prioritize exact section matches)
        # e.g., if query contains "exit load", push exit_load section to the front
        keywords_to_sections = {
            "exit load": "exit_load",
            "expense ratio": "expense_ratio",
            "minimum sip": "minimum_investment",
            "minimum lumpsum": "minimum_investment",
            "benchmark": "benchmark",
            "riskometer": "riskometer",
            "risk level": "riskometer",
            "objective": "investment_objective",
            "manager": "fund_management"
        }
        
        boosted_items = []
        normal_items = []
        query_lower = query.lower()
        
        matched_sections = [sec for kw, sec in keywords_to_sections.items() if kw in query_lower]
        
        for item in retrieved_items:
            item_section = item["metadata"].get("section")
            if item_section in matched_sections:
                boosted_items.append(item)
            else:
                normal_items.append(item)
                
        # Combine boosted items first, maintaining their similarity rank, followed by rest
        final_items = boosted_items + normal_items
        return final_items[:limit]

if __name__ == "__main__":
    # Dry-run test of retriever
    try:
        retriever = MutualFundRetriever()
        
        test_queries = [
            "What is the exit load of HDFC Nifty 50?",
            "Who manages groww total market index fund?",
            "What is the expense ratio for Nippon India Large Cap?"
        ]
        
        for q in test_queries:
            print("\n" + "="*50)
            print(f"Query: {q}")
            results = retriever.retrieve(q, limit=2)
            print(f"Retrieved {len(results)} items:")
            for idx, res in enumerate(results):
                print(f"\n[{idx+1}] ID: {res['id']} (Score: {res['score']:.4f})")
                print(f"Link: {res['metadata']['source_url']}")
                print(f"Snippet: {res['text'][:150]}...")
    except Exception as e:
        print(f"Retrieval dry-run failed: {e}")
