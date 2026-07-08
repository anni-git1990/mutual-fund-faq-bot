# Streamlit Deployment Guide

This document describes how to run and deploy the **Mutual Fund FAQ Assistant** using **Streamlit**. Streamlit provides a fast, lightweight Python interface that interacts directly with our RAG and guardrails pipeline without needing a separate FastAPI server.

---

## 💻 1. Running Locally

### Step 1: Install Streamlit
Ensure you have `streamlit` installed in your virtual environment:
```bash
pip install streamlit
```
*(Streamlit is already added to `requirements.txt`)*

### Step 2: Run the App
Launch the Streamlit app:
```bash
streamlit run streamlit_app.py
```

Streamlit will automatically spin up a local server (typically at **[http://localhost:8501](http://localhost:8501)**) and open it in your browser.

---

## ☁️ 2. Deploying to Streamlit Community Cloud (Free Hosting)

Streamlit offers a free hosting platform that deploys directly from your GitHub repository.

### Step 1: Push Code to GitHub
Ensure the codebase is pushed to your remote repository on GitHub.
*(The index files are ignored by default. However, once the daily scheduled GitHub Actions workflow executes, the updated index files in `data/index/` will be committed back to your branch automatically.)*

### Step 2: Set Up Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io/) and log in using your GitHub account.
2. Click the **"New app"** button.
3. Select your repository, the target branch (e.g. `main`), and set the main file path to:
   ```text
   streamlit_app.py
   ```

### Step 3: Configure Environment Secrets
Streamlit Cloud uses a secure **Secrets Manager** to store API keys instead of reading a `.env` file.
1. Before clicking deploy, click on **"Advanced settings..."** on the Streamlit setup screen.
2. In the **Secrets** text box, add your Groq API Key in TOML format:
   ```toml
   GROQ_API_KEY = "gsk_your_real_groq_api_key_here"
   ```
3. Click **"Save"**, and then click **"Deploy!"**.

Streamlit will provision a container, install the dependencies listed in `requirements.txt`, read the cached index from `data/index/`, and launch the live bot URL.

---

## 🛠️ Troubleshooting

* **Missing Chroma Database Index**: If the app displays a warning that the Chroma Index is not initialized, run the ingestion coordinator locally to generate it before pushing to GitHub:
  ```bash
  python -m src.ingestion.run
  ```
  And commit the index files:
  ```bash
  git add data/index/
  git commit -m "chore: pre-build vector index"
  git push
  ```
* **Groq API Rate Limits**: Streamlit Cloud shares resources. If you hit Groq rate limits, configure the Groq model configuration in your environment variable to use Llama-3 models (`llama-3.3-70b-versatile`).
