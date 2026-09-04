## ModelsLab Music Generator

This is a Streamlit-based application that allows users to generate music using the ModelsLab API and OpenAI's GPT-4 model. Users can input a prompt describing the type of music they want to generate, and the application will generate a music track in MP3 format based on the given prompt.


A lightweight AI-powered music generation project that converts a natural-language music idea into a structured music plan and generates a downloadable MIDI file.

This version is optimized for local execution on low-resource systems using **Qwen 2.5 0.5B + Ollama** instead of heavy music-generation models.

## 🚀 Features

- 🎼 Generate music from a natural-language prompt
- 🤖 Uses Qwen 2.5 0.5B locally through Ollama
- 🎹 Generates a structured melody
- 🥁 Supports tempo and musical scale
- 📄 Creates a standard MIDI file
- ⬇️ Download the generated MIDI
- 🔒 No OpenAI or cloud AI API required
- 💻 Lightweight and suitable for systems with limited RAM

## 🏗️ How It Works

User Music Prompt  
↓  
AI Music Planning Agent  
↓  
Qwen 2.5 0.5B via Ollama  
↓  
Structured Music Plan  
↓  
MIDI Generation  
↓  
Downloadable `.mid` File

## 🛠️ Tech Stack

- Python
- Streamlit
- Agno
- Ollama
- Qwen 2.5 0.5B
- MIDIUtil

## ⚙️ Setup

Install dependencies:

```bash
pip install -r requirements.txt

Run the application:

python -m streamlit run music_generator_agent.py