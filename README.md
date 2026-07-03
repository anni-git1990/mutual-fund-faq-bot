# Mutual Fund FAQ Assistant (Groww RAG Bot)

A trustworthy, compliant, facts-only Retrieval-Augmented Generation (RAG) assistant designed for **Groww** users. The bot retrieves factual mutual fund metrics from verified AMC sources and answers queries regarding expense ratios, exit loads, minimum SIPs, benchmarks, risk levels, and statement downloads, while strictly rejecting investment advice requests under SEBI regulations.

---

## 🚀 Key Features

* **Facts-Only RAG**: Answers objective queries using a local vector store built on the Hugging Face `BAAI/bge-small-en-v1.5` embeddings model.
* **SEBI Compliance Layer**: Intercepts queries using a Groq `llama-3.3-70b-versatile` intent classifier to instantly refuse advisory/portfolio questions (e.g., "Should I buy/sell?") and routes them to official educational links.
* **Output Sanitation**: Ensures all answers are at most 3 sentences long, strips generated URLs, and appends a single whitelisted Groww source URL alongside a last-updated footer date.
* **Modern Two-Column UI**: Features a beautiful split-pane workspace with a light/dark mode toggle. Includes a persistent sidebar of 6 clicking FAQ cards so users can ask multiple questions sequentially.
* **Automated Scheduler**: Provides a scheduled GitHub Actions workflow and a native local Python background runner with concurrency lock files to rebuild the index once every 24 hours.
* **E2E Regression Testing**: Includes a regression testing suite asserting intent accuracy, content formatting compliance, and request latency (<2.5 seconds).

---

## 📂 Project Structure

```text
mutual-fund-faq-bot/
├── .github/workflows/
│   └── daily_ingestion.yml      # Scheduled GitHub Actions daily ingestion
├── config/
│   └── corpus.yaml              # Supported scheme definitions & metadata aliases
├── data/
│   ├── raw/                     # Downloaded raw scheme HTML pages
│   ├── processed/               # Sectioned JSON and chunks mapping
│   └── index/                   # Local ChromaDB persistent database files
├── docs/
│   ├── problemStatement.md      # Project requirements
│   ├── architecture.md          # System design & sequence diagrams
│   ├── implementationPlan.md    # Multi-phase project roadmap
│   └── scheduler_setup.md       # Setup guide for automated updates
├── src/
│   ├── ingestion/               # ETL scripts (fetch, parse, chunk, index)
│   │   ├── fetch.py
│   │   ├── parse.py
│   │   ├── chunk.py
│   │   ├── index.py
│   │   └── run.py               # Ingestion pipeline coordinator CLI
│   ├── api/                     # Backend API & Guardrails
│   │   ├── main.py              # FastAPI server entry point
│   │   ├── chat.py              # Chat query handler
│   │   ├── guardrails.py        # Input classifier & output sanitizer
│   │   └── retriever.py         # Metadata-filtered hybrid vector search
│   └── scheduler.py             # Local background scheduler runner
├── static/                      # Frontend HTML/CSS/JS assets
├── tests/                       # Regression test suite
│   └── test_guardrails.py       # E2E classification & latency test matrix
└── requirements.txt             # Python dependency manifest
```

---

## 🛠️ Supported Schemes & Corpus

The bot answers queries for the following 5 target schemes on Groww, plus general platform reports:
1. **Nippon India Large Cap Fund Direct Growth**
2. **ICICI Prudential Nifty Next 50 Index Fund Direct Growth**
3. **HDFC Nifty 50 Index Fund Direct Growth**
4. **Groww Nifty Total Market Index Fund Direct Growth**
5. **ICICI Prudential Nifty Index Fund Direct Growth**
6. **Groww Platform Reports** (e.g. "How to download capital-gains statement?")

---

## ⚙️ Getting Started

### Prerequisites
* Python 3.10 or 3.11
* A Groq API Key (get one from [console.groq.com](https://console.groq.com/))

### Installation
1. Clone the repository to your local machine.
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate      # Windows
   source .venv/bin/activate    # Linux/macOS
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the root directory by copying `.env.example`:
   ```bash
   copy .env.example .env       # Windows
   cp .env.example .env         # Linux/macOS
   ```
5. Open `.env` and add your Groq API Key:
   ```env
   GROQ_API_KEY=gsk_your_key_here
   ```

---

## 💻 Running the Application

### 1. Rebuild the Vector Index (ETL Pipeline)
Re-fetch the corpus pages, parse scheme details, chunk sections, and embed them into the local Chroma store:
```bash
python -m src.ingestion.run
```

### 2. Start the Backend API & Web UI
Launch the FastAPI uvicorn server:
```bash
python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```
Open **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** in your browser to interact with the frontend.

### 3. Run the Regression Test Suite
Verify intent classifier accuracy, formatting compliance, and query latencies:
```bash
python -m tests.test_guardrails
```

### 4. Run the Background Scheduler locally
Start the local Python background scheduler to execute indexing once every 24 hours:
```bash
python -m src.scheduler
```

---

## 🌐 Production Deployment Guide

### hosting the Backend API
For staging and production environments, run the FastAPI application behind a production ASGI server like `gunicorn` with `uvicorn` workers:
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.api.main:app --bind 0.0.0.0:8000
```
Use a reverse proxy like **Nginx** in front of the application to handle SSL certificates and static asset caching.

### Deploying the Automated Scheduler
* **Cloud VM**: Run the local python background runner `src/scheduler.py` as a system service (e.g., `systemd` daemon on Linux) to guarantee it restarts automatically on host reboots.
* **GitHub Actions Schedule**: Commit and push the project to GitHub. Enable read/write permissions on workflow settings to allow [.github/workflows/daily_ingestion.yml](file:///d:/anita/product-AI-training/RAG_Project/mutual-fund-faq-bot/.github/workflows/daily_ingestion.yml) to push the daily database index updates back to your repository branch. See [scheduler_setup.md](file:///d:/anita/product-AI-training/RAG_Project/mutual-fund-faq-bot/docs/scheduler_setup.md) for full instructions.

---

## ⚠️ Known Limitations & Boundaries

To ensure strict SEBI compliance and high response accuracy, the bot operates within the following boundaries:

1. **Anti-Advisory Refusals (SEBI Guardrails)**:
   * The bot is strictly restricted to factual answers. Any query classified as `ADVISORY` (requesting recommendation, opinion, prediction, comparison to decide, or buy/sell actions) is immediately blocked by the Llama-3 intent classifier. 
   * It returns a standard polite refusal referencing the Groww investor education blog link.
2. **Strict Scope Limitations (Asset & Scheme Whitelist)**:
   * Factual queries are only answered for the **5 supported mutual fund schemes** (Nippon India Large Cap, ICICI Prudential Nifty Next 50, HDFC Nifty 50, Groww Nifty Total Market, and ICICI Prudential Nifty Index).
   * Queries regarding general stocks, crypto, external mutual funds, or general knowledge are classified as `OUT_OF_SCOPE` and refused.
3. **Conciseness Constraints**:
   * All factual responses are limited to a **maximum of 3 sentences** before formatting the footer. This ensures the LLM does not add excessive text that could be interpreted as financial advice.
4. **URL Citation Integrity**:
   * Every factual response is whitelisted to contain **exactly one source URL** pointing to the matching official Groww page. Multiple URLs or external non-whitelisted domains are stripped out post-generation.
5. **Static Platform FAQ Scope**:
   * General platform queries (e.g. statement downloads and available funds list) rely on static pre-injected document chunks in [chunk.py](file:///d:/anita/product-AI-training/RAG_Project/mutual-fund-faq-bot/src/ingestion/chunk.py) rather than dynamic web scraping.