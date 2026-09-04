# AI Reasoning Agent

A local AI reasoning agent built with **Agno, Ollama, and Qwen 2.5 0.5B**.

The project demonstrates how an AI agent can approach problems step-by-step instead of simply producing a direct answer.

## Features

- 🧠 Reasoning-focused AI agent
- 🤖 Local Qwen 2.5 0.5B model
- 🔒 No OpenAI API key required
- 🧩 Breaks complex problems into smaller steps
- ✅ Checks answers before responding
- 🌐 Interactive Agno Playground UI
- 💻 Runs completely on the local machine

## Architecture

```text
User
  ↓
Agno Playground
  ↓
AI Reasoning Agent
  ↓
Qwen 2.5 0.5B (Ollama)
  ↓
Reasoned Answer

Tech Stack
Python
Agno
Ollama
Qwen 2.5 0.5B
Agno Playground
Setup
1. Start Ollama

Make sure Ollama is running and the model is available:

ollama pull qwen2.5:0.5b
2. Install dependencies
pip install -r requirements.txt
3. Run the agent
python local_ai_reasoning_agent.py