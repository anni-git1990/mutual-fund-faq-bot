import argparse
from src.ingestion.fetch import fetch_all
from src.ingestion.parse import parse_all
from src.ingestion.chunk import chunk_all
from src.ingestion.index import build_index

def main():
    parser = argparse.ArgumentParser(description="Mutual Fund FAQ Bot Ingestion Pipeline")
    parser.add_argument("--fetch-only", action="store_true", help="Only fetch raw HTML data")
    parser.add_argument("--parse-only", action="store_true", help="Only parse raw HTML into sections")
    parser.add_argument("--chunk-only", action="store_true", help="Only chunk parsed sections")
    parser.add_argument("--index-only", action="store_true", help="Only embed and index chunks into vector database")
    args = parser.parse_args()
    
    if args.fetch_only:
        print("Starting Data Fetching...")
        fetch_all()
    elif args.parse_only:
        print("Starting Data Parsing...")
        parse_all()
    elif args.chunk_only:
        print("Starting Chunking...")
        chunk_all()
    elif args.index_only:
        print("Starting Indexing...")
        build_index()
    else:
        print("Running full ingestion pipeline (Fetch -> Parse -> Chunk -> Index)...")
        fetch_success = fetch_all()
        if fetch_success:
            parse_all()
            chunk_all()
            build_index()
            print("Ingestion pipeline completed successfully!")
        else:
            print("Pipeline aborted because fetching failed.")

if __name__ == "__main__":
    main()
