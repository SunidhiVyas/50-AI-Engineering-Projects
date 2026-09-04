# AI Finance Agent

An AI-powered financial research assistant built with **Agno, Ollama, YFinance, and DuckDuckGo**.

This project is a local alternative to the original xAI Finance Agent. Instead of using a paid cloud LLM, it uses **Qwen 2.5 0.5B through Ollama**.

## Features

- 📈 Stock price and financial data lookup
- 🏢 Company information and financial research
- 📰 Current financial news search
- 🔎 Web-based market research
- 📊 Financial data displayed in tables
- 🤖 Local AI reasoning with Qwen 2.5 0.5B
- 🔐 No OpenAI or xAI API key required
- ⚡ AgentOS API interface

## Tech Stack

- Python
- Agno
- Ollama
- Qwen 2.5 0.5B
- YFinance
- DuckDuckGo
- FastAPI
- AgentOS

## Architecture

```text
User
  ↓
AgentOS / FastAPI
  ↓
AI Finance Agent
  ↓
Qwen 2.5 0.5B (Ollama)
  ├── YFinance
  │    └── Stock & financial data
  │
  └── DuckDuckGo
       └── Current web/news research

Setup
1. Install Ollama

Make sure Ollama is installed and running.

Pull the model:

ollama pull qwen2.5:0.5b
2. Install Python dependencies
pip install -r requirements.txt
3. Start the agent
python xai_finance_agent.py