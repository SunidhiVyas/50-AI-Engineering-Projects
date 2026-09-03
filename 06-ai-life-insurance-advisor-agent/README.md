# 🛡️ AI Life Insurance Advisor

A local AI-powered life insurance coverage advisor built with **Agno, Ollama, Qwen 2.5 0.5B, and Streamlit**.

The application estimates the amount of life insurance coverage a person may need based on income, dependents, debt, savings, existing insurance, and an income-replacement horizon. It can also optionally research current term-life insurance options using Firecrawl.

> ⚠️ **Educational project only.** This application does not provide licensed financial advice. Actual insurance needs, eligibility, premiums, and policy terms should be verified with a qualified professional and the insurer.

---

## 🚀 Features

- 🤖 **Local AI Agent** using Ollama + Qwen 2.5 0.5B
- 🧮 **Local coverage calculation** for reliable and transparent results
- 💰 Supports USD, CAD, EUR, GBP, AUD, and INR
- 👨‍👩‍👧 Considers dependents and income replacement needs
- 🏠 Considers outstanding debt
- 💵 Accounts for savings and existing life insurance
- 🔎 Optional **Firecrawl** research for term-life insurance options
- 📊 Step-by-step coverage calculation
- 🖥️ Simple Streamlit interface
- 🔐 No OpenAI API key required
- 🛡️ Graceful fallback when AI research is unavailable

---

## 🧠 How It Works

The application collects a basic financial profile:

- Age
- Annual income
- Number of dependents
- Location
- Outstanding debt
- Savings and investments
- Existing life insurance
- Income replacement horizon
- Currency

It then calculates an estimated coverage requirement using a discounted income-replacement approach.

### Coverage Formula

```text
Estimated Coverage
=
Discounted Income Replacement
+ Outstanding Debt
- Savings
- Existing Life Insurance