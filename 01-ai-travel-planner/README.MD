# 🌍 AI Smart Travel Planner

An AI-powered travel planning assistant that creates personalized day-by-day itineraries using a local LLM and real-time web research.

## ✨ Features

- 🌍 Destination-based trip planning
- 📅 Custom number of travel days
- 💰 Budget planning in Indian Rupees (₹)
- 🎯 Personalized travel interests
- 🔎 Real-time web research using SerpAPI
- 🤖 Local AI inference using Ollama
- 📋 Morning, afternoon and evening itinerary
- 🏨 Accommodation suggestions
- 🍴 Food recommendations
- 💵 Estimated trip costs
- 📆 Downloadable `.ics` calendar
- 🔐 Local LLM — no OpenAI API required

## 🛠️ Tech Stack

- Python
- Streamlit
- Agno
- Ollama
- Qwen 2.5 0.5B
- SerpAPI
- iCalendar

## 🏗️ How It Works

1. User enters destination, trip duration, budget and interests.
2. The Research Agent searches the web for relevant travel information.
3. The Planner Agent uses the research to create a personalized itinerary.
4. The application displays the complete travel plan.
5. The itinerary can be downloaded as an `.ics` calendar file.

## 🚀 Run Locally

### 1. Install dependencies

```bash
pip install -r requirements.txt