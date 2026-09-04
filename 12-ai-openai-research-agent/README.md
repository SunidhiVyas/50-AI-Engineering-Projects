# 🔍 AI OpenAI Research Agent

A local multi-agent research application that researches a topic, searches the web, and generates a structured research report.

This project is customized from the original `openai_research_agent` project to run locally using **Ollama + Qwen 0.5B**, without requiring an OpenAI API key.

## 🚀 Features

- 🤖 Multi-agent research workflow
- 🔎 Triage Agent for research planning
- 🌐 Research Agent for web search
- 📝 Editor Agent for report generation
- 📄 Markdown research reports
- ⬇️ Download reports as `.md`
- 🖥️ Simple Streamlit interface
- 🏠 Runs locally with Ollama
- 🔐 No OpenAI API key required

## 🏗️ Architecture

```text
User
  ↓
Streamlit UI
  ↓
Triage Agent
  ↓
Research Plan
  ↓
Research Agent
  ↓
DuckDuckGo Web Search
  ↓
Research Results
  ↓
Editor Agent
  ↓
Final Research Report
  ↓
Download Markdown Report

⚙️ Setup
1. Install dependencies
pip install -r requirements.txt
2. Install Ollama

Install Ollama and make sure it is running.

Pull the model:

ollama pull qwen2.5:0.5b
3. Run the application
python -m streamlit run research_agent.py

The application will open in your browser.