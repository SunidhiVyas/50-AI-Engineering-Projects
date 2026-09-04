# 🕵️ Web Scraping AI Agent

An AI-powered web scraping application that extracts information from a public webpage and answers questions about it using a local LLM.

## ✨ Features

- 🌐 Scrapes public webpages
- 🧹 Extracts readable webpage content
- 🤖 Uses Qwen 2.5 0.5B through Ollama
- 💬 Ask questions about scraped content
- 📋 Displays the AI-generated answer
- 🔍 Allows the raw scraped content to be inspected
- 🔐 No OpenAI or other cloud AI API key required
- ⚡ Lightweight implementation designed for local systems

## 🏗️ Architecture

```text
User
  ↓
Streamlit UI
  ↓
Website URL
  ↓
Requests
  ↓
BeautifulSoup
  ↓
Clean Webpage Text
  ↓
Qwen 2.5 0.5B + Ollama
  ↓
AI Analysis
  ↓
Answer + Scraped Content

🛠️ Tech Stack
Python
Streamlit
Requests
BeautifulSoup
Agno
Ollama
Qwen 2.5 0.5B
🚀 Setup
1. Install Ollama

Make sure Ollama is installed and running.

Download the model:

ollama pull qwen2.5:0.5b
2. Install dependencies
pip install -r requirements.txt
3. Run the application
python -m streamlit run local_ai_scrapper.py
💡 How It Works
Enter a public webpage URL.
The application downloads the webpage using Requests.
BeautifulSoup removes unnecessary HTML elements.
The readable webpage text is extracted.
The content is sent to the local Qwen model through Ollama.
Qwen analyzes the content according to the user's request.
The answer is displayed in the Streamlit interface.
The original scraped content can also be viewed.