import os
import time
import yaml
import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive"
}

def load_corpus_config(config_path="config/corpus.yaml"):
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def fetch_and_save_scheme(scheme, raw_dir="data/raw"):
    slug = scheme["slug"]
    if slug == "groww-platform":
        print(f"Skipping fetch for static platform entry: {slug}")
        return True
        
    url = scheme["source_url"]
    print(f"Fetching URL for {slug}: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        os.makedirs(raw_dir, exist_ok=True)
        file_path = os.path.join(raw_dir, f"{slug}.html")
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(response.text)
            
        print(f"Successfully fetched and saved to {file_path}")
        return True
    except Exception as e:
        print(f"Error fetching {slug} from {url}: {e}")
        return False

def fetch_all():
    config = load_corpus_config()
    schemes = config.get("schemes", [])
    success_count = 0
    
    for scheme in schemes:
        if fetch_and_save_scheme(scheme):
            success_count += 1
        time.sleep(2) # rate limiting
        
    print(f"Fetched {success_count}/{len(schemes)} schemes successfully.")
    return success_count == len(schemes)

if __name__ == "__main__":
    fetch_all()
