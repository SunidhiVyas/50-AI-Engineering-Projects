# 🎙️ AI Blog to Podcast Agent

Convert a blog article into a short podcast using **local AI** and **offline text-to-speech**.

## ✨ Features

- 🌐 Extracts content from a public blog/article URL
- 🤖 Uses **Qwen 2.5 0.5B** through Ollama
- 📝 Generates a conversational podcast script
- 🎙️ Converts the script into speech using Windows offline TTS
- ▶️ Plays the generated podcast directly in Streamlit
- ⬇️ Allows the podcast to be downloaded as a WAV file
- 🔐 No OpenAI or ElevenLabs API key required

## 🏗️ Architecture

```text
Blog URL
   ↓
Requests + BeautifulSoup
   ↓
Article Text Extraction
   ↓
Qwen 2.5 0.5B + Ollama
   ↓
Podcast Script
   ↓
pyttsx3 / Windows TTS
   ↓
WAV Audio
   ↓
Streamlit Audio Player

🛠️ Tech Stack
Python
Streamlit
Agno
Ollama
Qwen 2.5 0.5B
BeautifulSoup
Requests
pyttsx3
Windows SAPI Text-to-Speech
🚀 Setup
1. Install Ollama

Install Ollama and make sure it is running.

Then download the model:

ollama pull qwen2.5:0.5b
2. Install dependencies
pip install -r requirements.txt
3. Run the application
python -m streamlit run blog_to_podcast_agent.py

🛠️ Tech Stack
Python
Streamlit
Agno
Ollama
Qwen 2.5 0.5B
BeautifulSoup
Requests
pyttsx3
Windows SAPI Text-to-Speech
🚀 Setup
1. Install Ollama

Install Ollama and make sure it is running.

Then download the model:

ollama pull qwen2.5:0.5b
2. Install dependencies
pip install -r requirements.txt
3. Run the application
python -m streamlit run blog_to_podcast_agent.py