# AI Startup Trend Analysis Agent

An AI-powered research workflow that discovers recent startup and technology developments, summarizes the findings, and identifies emerging trends and potential startup opportunities.

This version is customized to run locally using **Qwen 2.5 0.5B through Ollama**, instead of requiring a cloud Gemini API key.

## Features

- 🔎 Recent startup and technology research
- 📰 Web-based information collection
- 📝 Automatic research summarization
- 📈 Emerging trend identification
- 🚀 Potential startup opportunity discovery
- 🤖 Local AI processing with Qwen 2.5 0.5B
- 🌐 Streamlit interface
- 🔐 No Google/Gemini API key required

## Workflow

```text
Startup Topic
      ↓
News Collector Agent
      ↓
Summary Writer Agent
      ↓
Trend Analyzer Agent
      ↓
Trends + Startup Opportunities

Tech Stack
Python
Agno
Ollama
Qwen 2.5 0.5B
DuckDuckGo
Newspaper4k
Streamlit
Setup
1. Start Ollama

Make sure Ollama is running and the model is available:

ollama pull qwen2.5:0.5b
2. Install dependencies
pip install -r requirements.txt
3. Run the application
python -m streamlit run startup_trends_agent.py

The application will open in your browser.