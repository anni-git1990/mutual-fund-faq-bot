# Problem Statement: Mutual Fund FAQ Assistant (Facts-Only Q&A)

## Overview

The objective of this project is to build a facts-only Mutual Fund FAQ Assistant using **Groww** as the reference product context. The assistant will help users get quick, clear, and verified answers to common mutual fund-related questions such as expense ratio, exit load, minimum SIP, ELSS lock-in period, riskometer, benchmark, and statement download process.

The assistant will retrieve information only from official public sources such as **AMC websites, AMFI, and SEBI**. It must not provide investment advice, opinions, fund recommendations, buy/sell suggestions, or return comparisons. Every response must include one clear source link to ensure transparency and trust.

## Objective

Build a lightweight Retrieval-Augmented Generation (RAG)-based FAQ assistant that:

| Objective Area | Description |
|---|---|
| Facts-only answers | Answer only objective and verifiable mutual fund questions |
| Official sources | Use only AMC, AMFI, and SEBI public sources |
| Source-backed response | Include exactly one clear citation link in every answer |
| Compliance-safe behavior | Refuse advisory or opinion-based questions politely |
| Simple user experience | Provide a minimal and easy-to-use FAQ interface |

## Target Users

| User Segment | Need |
|---|---|
| Retail investors | Want quick factual information about mutual fund schemes |
| First-time mutual fund users | Need simple explanations of scheme details and documents |
| Customer support teams | Need help answering repetitive mutual fund questions |
| Content teams | Need verified source-backed facts for FAQs and educational content |

## Scope of Work

| Area | Requirement |
|---|---|
| Product context | Use Groww as the reference product context |
| AMC selection | Multiple AMCs (Nippon India, ICICI Prudential, HDFC, Groww) |
| Scheme selection | 5 specific mutual fund schemes from Groww (Large Cap, Nifty 50, Nifty Next 50, Total Market Index) |
| Source collection | Restrict sources strictly to the 5 specific Groww mutual fund URLs provided |
| Assistant type | Build a Retrieval-Augmented Generation-based FAQ assistant |
| UI | Create a simple interface with welcome message, example questions, input box, answer area, and disclaimer |

### Selected Mutual Fund Schemes

The RAG chatbot will support the following mutual fund schemes:

1. **Nippon India Large Cap Fund Direct Growth**
   - Groww URL: [nippon-india-large-cap-fund-direct-growth](https://groww.in/mutual-funds/nippon-india-large-cap-fund-direct-growth) (Note: original input had `growthno` at the end)
2. **ICICI Prudential Nifty Next 50 Index Fund Direct Growth**
   - Groww URL: [icici-prudential-nifty-next-50-index-fund-direct-growth](https://groww.in/mutual-funds/icici-prudential-nifty-next-50-index-fund-direct-growth)
3. **HDFC Nifty 50 Index Fund Direct Growth**
   - Groww URL: [hdfc-nifty-50-index-fund-direct-growth](https://groww.in/mutual-funds/hdfc-nifty-50-index-fund-direct-growth)
4. **Groww Nifty Total Market Index Fund Direct Growth**
   - Groww URL: [groww-nifty-total-market-index-fund-direct-growth](https://groww.in/mutual-funds/groww-nifty-total-market-index-fund-direct-growth)
5. **ICICI Prudential Nifty Index Fund Direct Growth**
   - Groww URL: [icici-prudential-nifty-index-fund-direct-growth](https://groww.in/mutual-funds/icici-prudential-nifty-index-fund-direct-growth)

### Corpus Definition

The corpus for the RAG chatbot is defined strictly by the following reference product URLs:

#### Reference Product URLs (Groww Scheme Pages)
- **Nippon India Large Cap Fund Direct Growth**: [Groww URL](https://groww.in/mutual-funds/nippon-india-large-cap-fund-direct-growth)
- **ICICI Prudential Nifty Next 50 Index Fund Direct Growth**: [Groww URL](https://groww.in/mutual-funds/icici-prudential-nifty-next-50-index-fund-direct-growth)
- **HDFC Nifty 50 Index Fund Direct Growth**: [Groww URL](https://groww.in/mutual-funds/hdfc-nifty-50-index-fund-direct-growth)
- **Groww Nifty Total Market Index Fund Direct Growth**: [Groww URL](https://groww.in/mutual-funds/groww-nifty-total-market-index-fund-direct-growth)
- **ICICI Prudential Nifty Index Fund Direct Growth**: [Groww URL](https://groww.in/mutual-funds/icici-prudential-nifty-index-fund-direct-growth)

## Supported Question Types

| Question Type | Example |
|---|---|
| Expense ratio | "What is the expense ratio of this scheme?" |
| Exit load | "What is the exit load?" |
| Minimum SIP | "What is the minimum SIP amount?" |
| ELSS lock-in | "What is the lock-in period for ELSS?" |
| Riskometer | "What is the risk level of this fund?" |
| Benchmark | "What benchmark does this fund follow?" |
| Statement download | "How can I download my mutual fund statement?" |
| Capital gains report | "How can I download my capital gains statement?" |

## Response Rules

| Rule | Requirement |
|---|---|
| Answer length | Maximum 3 sentences |
| Citation | Include exactly one official source link |
| Last updated | Add: `Last updated from sources: <date>` |
| Tone | Clear, neutral, and factual |
| Advice restriction | No investment advice, opinions, or recommendations |

## Refusal Handling

The assistant must politely refuse questions that ask for advice, prediction, comparison, or personal recommendation.

Examples of questions to refuse:

| Advisory Question |
|---|
| "Should I invest in this fund?" |
| "Which fund is better?" |
| "Will this fund give high returns?" |
| "Should I buy or sell this mutual fund?" |
| "How much should I invest?" |

### Sample Refusal Message

```text
I can help with factual mutual fund information, but I cannot provide investment advice, recommendations, or return predictions. Please refer to official investor education resources before making investment decisions.

Source: https://groww.in/blog/mutual-funds-for-beginners-investor-education
Last updated from sources: <date>
```

## Key Constraints

| Constraint | Description |
|---|---|
| Public sources only | Use only the provided Groww mutual fund URLs |
| No third-party sources | Do not use blogs, news sites, forums, or aggregator content |
| No PII | Do not collect or store PAN, Aadhaar, account number, OTP, email, or phone number |
| No advice | Do not suggest whether to buy, sell, hold, or choose a fund |
| No performance claims | Do not calculate, compare, or predict returns |
| Transparency | Every answer must be source-backed and include last updated date |

## Expected Deliverables

| Deliverable | Description |
|---|---|
| Working prototype | A small facts-only Mutual Fund FAQ Assistant |
| Curated corpus | The 5 provided Groww URLs |
| Minimal UI | Welcome message, 3 example questions, disclaimer, input and answer area |
| README | Setup instructions, selected AMC/schemes, architecture, limitations |
| Disclaimer | `Facts-only. No investment advice.` |

## Success Criteria

| Success Area | Criteria |
|---|---|
| Accuracy | Answers are retrieved from official sources only |
| Compliance | No investment advice or recommendations are given |
| Citation quality | Every answer includes one valid source link |
| Refusal quality | Advisory questions are rejected politely |
| Simplicity | UI is clean, minimal, and easy to use |

## Final Problem Statement

Build a trustworthy, transparent, and compliance-safe Mutual Fund FAQ Assistant for Groww users that answers only factual mutual fund questions using official public sources. The assistant should provide short, source-backed responses while refusing investment advice, opinion-based questions, personal recommendations, and performance comparisons.
