# Project Context: Mutual Fund FAQ Assistant

This document provides the business, product, regulatory, and technical domain context for the Mutual Fund FAQ Assistant, using **Groww** as the reference product context and target schemes.

---

## 1. Business & Industry Context

### Mutual Funds in India
A Mutual Fund is a financial vehicle that pools money from multiple investors to purchase securities (stocks, bonds, money market instruments). In India, mutual funds are regulated by the **Securities and Exchange Board of India (SEBI)** and managed by **Asset Management Companies (AMCs)**. 

### Direct vs. Regular Plans
* **Direct Plans**: Offered directly by the AMC. They do not involve distributor commissions, leading to a lower expense ratio and higher Net Asset Value (NAV) over time. All mutual funds on Groww are **Direct Plans**.
* **Regular Plans**: Sold through distributors/brokers. They include commissions, which are factored into a higher expense ratio.

### Growth vs. IDCW
* **Growth Option**: Profits made by the fund are reinvested back into the scheme, increasing the NAV over time. No dividends are paid.
* **IDCW (Income Distribution cum Capital Withdrawal) Option**: Profits are periodically distributed to investors as dividends. 
* All target funds for this chatbot are **Growth Options**.

---

## 2. Product Context: Groww

**Groww** is one of India's leading investment platforms, allowing users to invest in direct mutual funds, stocks, ETFs, and IPOs. For the purpose of this RAG assistant, Groww serves as the reference product interface and context. 

When users query mutual fund details, they expect the data to match the factual information shown on Groww, which is sourced from official AMC disclosures.

### Core Mutual Fund Metrics on Groww
Users typically look for the following parameters when checking a fund's details:
* **Net Asset Value (NAV)**: The market value per unit of a mutual fund scheme.
* **Expense Ratio**: The annual fee charged by the AMC to manage the fund, expressed as a percentage of assets.
* **Exit Load**: A fee charged to investors when they redeem or switch out of a fund before a specified period.
* **Minimum SIP Amount**: The lowest amount required to start a Systematic Investment Plan (monthly investment).
* **Riskometer**: A visual scale showing the level of risk associated with the fund (e.g., Low, Moderately Low, Moderate, Moderately High, High, Very High).
* **Benchmark**: The standard index (e.g., NIFTY 50, NIFTY Next 50) against which the fund's performance and composition are compared.

---

## 3. Selected Mutual Fund Schemes (Scope)

The RAG chatbot retrieves information and answers FAQs for the following 5 specific schemes:

| Scheme Name | AMC | Primary Category | Benchmark | Groww URL |
|---|---|---|---|---|
| **Nippon India Large Cap Fund Direct Growth** | Nippon India Mutual Fund | Equity - Large Cap | S&P BSE 100 TRI | [Groww Link](https://groww.in/mutual-funds/nippon-india-large-cap-fund-direct-growth) |
| **ICICI Prudential Nifty Next 50 Index Fund Direct Growth** | ICICI Prudential Mutual Fund | Equity - Index Fund | NIFTY Next 50 TRI | [Groww Link](https://groww.in/mutual-funds/icici-prudential-nifty-next-50-index-fund-direct-growth) |
| **HDFC Nifty 50 Index Fund Direct Growth** | HDFC Mutual Fund | Equity - Index Fund | NIFTY 50 TRI | [Groww Link](https://groww.in/mutual-funds/hdfc-nifty-50-index-fund-direct-growth) |
| **Groww Nifty Total Market Index Fund Direct Growth** | Groww Mutual Fund | Equity - Index Fund | Nifty Total Market TRI | [Groww Link](https://groww.in/mutual-funds/groww-nifty-total-market-index-fund-direct-growth) |
| **ICICI Prudential Nifty Index Fund Direct Growth** | ICICI Prudential Mutual Fund | Equity - Index Fund | NIFTY 50 TRI | [Groww Link](https://groww.in/mutual-funds/icici-prudential-nifty-index-fund-direct-growth) |

---

## 4. Regulatory & Compliance Context

The most critical constraint on this project is the **SEBI Investment Advisers Regulations**. Under these rules:
1. **No Investment Advice**: Providing opinions on whether to buy, hold, or sell a mutual fund requires registration as an Investment Adviser. The assistant must *never* say a fund is "good", "better than others", or "recommended".
2. **No Return Predictions**: The bot must not predict future returns or claim guaranteed growth.
3. **No PII Storage**: Personal Identifiable Information (PAN, Aadhaar, account balances) must not be processed or collected to protect investor privacy.
4. **Facts-Only Retrieval**: The bot only acts as a page content retriever and summarizer for the target Groww scheme pages. It answers objective queries (e.g., "What is the exit load?") and declines subjective queries (e.g., "Should I invest in HDFC Nifty 50?") with a polite facts-only refusal and a relevant educational link (`https://groww.in/blog/mutual-funds-for-beginners-investor-education`).

---

## 5. Ground Truth Corpus (Groww URLs Only)

To ensure absolute accuracy, the RAG chatbot retrieves information strictly from the 5 Groww URLs provided, and cites the corresponding Groww page URL in every response:
* **Nippon India Large Cap Fund Direct Growth**: [Groww URL](https://groww.in/mutual-funds/nippon-india-large-cap-fund-direct-growth)
* **ICICI Prudential Nifty Next 50 Index Fund Direct Growth**: [Groww URL](https://groww.in/mutual-funds/icici-prudential-nifty-next-50-index-fund-direct-growth)
* **HDFC Nifty 50 Index Fund Direct Growth**: [Groww URL](https://groww.in/mutual-funds/hdfc-nifty-50-index-fund-direct-growth)
* **Groww Nifty Total Market Index Fund Direct Growth**: [Groww URL](https://groww.in/mutual-funds/groww-nifty-total-market-index-fund-direct-growth)
* **ICICI Prudential Nifty Index Fund Direct Growth**: [Groww URL](https://groww.in/mutual-funds/icici-prudential-nifty-index-fund-direct-growth)

Additionally, general platform FAQ queries like **How to download capital-gains statement?** are supported through static platform guides, citing:
* **Capital-Gains Statement Guide**: [Groww Help Guide](https://groww.in/help/mutual-funds/reports-and-statements/how-to-download-capital-gains-statement)

