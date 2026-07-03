# Automated Data Ingestion Scheduler Setup

This document explains how to configure and enable automated daily mutual fund data ingestion. Two methods are supported:
1. **GitHub Actions Workflow** (Recommended for cloud/production setups)
2. **Local Python background daemon** (Recommended for local testing/self-hosted VM servers)

---

## 1. GitHub Actions Scheduler (Automated)

We have configured a GitHub Actions workflow at [.github/workflows/daily_ingestion.yml](file:///d:/anita/product-AI-training/RAG_Project/mutual-fund-faq-bot/.github/workflows/daily_ingestion.yml). This workflow executes the full pipeline and commits index updates back to the repository.

### How to Enable:
1. **Push code to GitHub**: Push the repository to GitHub.
2. **Workflow schedule**: By default, the workflow is scheduled to run daily at **5:00 AM UTC** (`0 5 * * *` / **10:30 AM IST**). No manual configuration is needed for the cron trigger once pushed to the default branch.
3. **Verify Settings**:
   * Go to your repository settings on GitHub.
   * Navigate to **Settings** > **Actions** > **General**.
   * Under **Workflow permissions**, ensure **"Read and write permissions"** is selected. This is required to allow the workflow to commit the updated database index files in `data/index/` back to the repository.

### How to Trigger Manually:
1. Navigate to the **Actions** tab on your GitHub repository.
2. Select the workflow **"Daily Mutual Fund Data Ingestion"** in the sidebar.
3. Click the **Run workflow** dropdown button, select the target branch, and click **Run workflow**.

---

## 2. Local Python Scheduler (Daemon)

If you are hosting the chatbot on a local server or a virtual machine (VM) without GitHub Actions, you can run the background python scheduler script at [src/scheduler.py](file:///d:/anita/product-AI-training/RAG_Project/mutual-fund-faq-bot/src/scheduler.py).

### How to Run:
Run the scheduler script in your terminal using the virtual environment python runner:
```bash
.venv\Scripts\python.exe -m src.scheduler
```
*(For Linux/macOS, use `.venv/bin/python -m src.scheduler`)*

### Behavior:
* **Target Scheduling**: Calculates the delay until the next occurrence of **10:30 AM local time** and sleeps until then.
* **Interval Loop**: Executes the pipeline and then sleeps until 10:30 AM of the next day.
* **Concurrency Locking**: Utilizes a lock-file mechanism (`data/ingestion.lock`) to prevent duplicate executions if a manual pipeline run is active.
