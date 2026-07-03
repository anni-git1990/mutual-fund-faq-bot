import os
import json
import yaml
import datetime

def load_corpus_config(config_path="config/corpus.yaml"):
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def chunk_sections(slug, processed_dir="data/processed"):
    config = load_corpus_config()
    scheme_config = next((s for s in config.get("schemes", []) if s["slug"] == slug), None)
    if not scheme_config:
        print(f"Scheme config not found in corpus.yaml for {slug}")
        return []
        
    scheme_name = scheme_config["name"]
    source_url = scheme_config["source_url"]
    last_updated = datetime.datetime.now().strftime("%d-%b-%Y")
    
    if slug == "groww-platform":
        return [
            {
                "id": "groww-platform#capital_gains_statement#0",
                "text": (
                    f"Scheme: Groww Platform\nSection: capital_gains_statement\n"
                    f"Source: {source_url}\n\n"
                    f"To download your capital gains statement on Groww, follow these steps:\n"
                    f"1. Log in to your Groww account (via mobile app or website).\n"
                    f"2. Go to your Profile icon on the top right and click on 'Reports'.\n"
                    f"3. Select 'Capital Gains Report' under the Mutual Funds section.\n"
                    f"4. Choose the relevant financial year (FY) and click on 'Download PDF' or 'Send to Email'."
                ),
                "scheme_name": scheme_name,
                "source_url": source_url,
                "section": "capital_gains_statement",
                "last_updated": last_updated,
                "token_estimate": 100
            },
            {
                "id": "groww-platform#mutual_fund_statement#0",
                "text": (
                    f"Scheme: Groww Platform\nSection: mutual_fund_statement\n"
                    f"Source: {source_url}\n\n"
                    f"To download your consolidated mutual fund statement on Groww, follow these steps:\n"
                    f"1. Open your Groww profile and navigate to the 'Reports' dashboard.\n"
                    f"2. Select 'Consolidated Account Statement (CAS)' under statements.\n"
                    f"3. Choose the date range or financial year and submit your request to generate the report."
                ),
                "scheme_name": scheme_name,
                "source_url": source_url,
                "section": "mutual_fund_statement",
                "last_updated": last_updated,
                "token_estimate": 90
            },
            {
                "id": "groww-platform#supported_schemes#0",
                "text": (
                    f"Scheme: Groww Platform\nSection: supported_schemes\n"
                    f"Source: https://groww.in\n\n"
                    f"The Mutual Fund FAQ Assistant supports the following 5 mutual fund schemes on Groww:\n"
                    f"1. Nippon India Large Cap Fund Direct Growth\n"
                    f"2. ICICI Prudential Nifty Next 50 Index Fund Direct Growth\n"
                    f"3. HDFC Nifty 50 Index Fund Direct Growth\n"
                    f"4. Groww Nifty Total Market Index Fund Direct Growth\n"
                    f"5. ICICI Prudential Nifty Index Fund Direct Growth"
                ),
                "scheme_name": scheme_name,
                "source_url": "https://groww.in",
                "section": "supported_schemes",
                "last_updated": last_updated,
                "token_estimate": 110
            }
        ]

    sections_path = os.path.join(processed_dir, slug, "sections.json")
    if not os.path.exists(sections_path):
        print(f"Sections file not found for {slug} at {sections_path}")
        return []
        
    with open(sections_path, "r", encoding="utf-8") as f:
        sections = json.load(f)
        
    chunks = []
    
    # Process regular sections
    regular_keys = ["overview", "expense_ratio", "exit_load", "minimum_investment", "benchmark", "riskometer", "investment_objective"]
    for key in regular_keys:
        text_content = sections.get(key, "").strip()
        if not text_content or text_content == "N/A":
            continue
            
        chunk_text = f"Scheme: {scheme_name}\nSection: {key}\nSource: {source_url}\n\n{text_content}"
        chunk_id = f"{slug}#{key}#0"
        
        chunks.append({
            "id": chunk_id,
            "text": chunk_text,
            "scheme_name": scheme_name,
            "source_url": source_url,
            "section": key,
            "last_updated": last_updated,
            "token_estimate": len(chunk_text) // 4
        })
        
    # Process fund_management (split one chunk per manager)
    managers = sections.get("fund_management", [])
    for idx, mgr in enumerate(managers):
        m_name = mgr.get("name")
        m_bio = mgr.get("bio")
        
        chunk_text = f"Scheme: {scheme_name}\nSection: fund_management\nSource: {source_url}\n\n{m_bio}"
        chunk_id = f"{slug}#fund_management#{idx}"
        
        chunks.append({
            "id": chunk_id,
            "text": chunk_text,
            "scheme_name": scheme_name,
            "source_url": source_url,
            "section": "fund_management",
            "manager_name": m_name,
            "last_updated": last_updated,
            "token_estimate": len(chunk_text) // 4
        })
        
    return chunks

def chunk_all(processed_dir="data/processed"):
    config = load_corpus_config()
    schemes = config.get("schemes", [])
    total_chunks = 0
    
    for scheme in schemes:
        slug = scheme["slug"]
        print(f"Chunking sections for {slug}...")
        
        chunks = chunk_sections(slug, processed_dir)
        if chunks:
            slug_dir = os.path.join(processed_dir, slug)
            os.makedirs(slug_dir, exist_ok=True)
            chunks_path = os.path.join(slug_dir, "chunks.json")
            with open(chunks_path, "w", encoding="utf-8") as f:
                json.dump(chunks, f, indent=2)
                
            print(f"Successfully saved {len(chunks)} chunks to {chunks_path}")
            total_chunks += len(chunks)
            
    print(f"Chunking complete. Generated {total_chunks} chunks total.")

if __name__ == "__main__":
    chunk_all()
