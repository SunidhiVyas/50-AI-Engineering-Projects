# 💼 AI Recruitment Agent Team

A Streamlit application that simulates a full-service recruitment team using multiple AI agents to automate and streamline the hiring process. Each agent represents a different recruitment specialist role - from resume analysis and candidate evaluation to interview scheduling and communication - working together to provide comprehensive hiring solutions. The system combines the expertise of technical recruiters, HR coordinators, and scheduling specialists into a cohesive automated workflow.

A lightweight AI-powered recruitment system that analyzes resumes against job roles using a local LLM.

## 🚀 Features

- 📄 Upload a candidate resume in PDF format
- 🎯 Select a target job role
- 🤖 Analyze the resume using Qwen 2.5
- 📊 Generate a resume match score
- ✅ Identify matching skills
- ❌ Identify missing skills
- 💬 Generate recruiter-style feedback
- 🎯 Provide a hiring recommendation
- 🔒 Runs locally without OpenAI or cloud LLM APIs

## 🏗️ Architecture

Resume PDF  
↓  
PDF Text Extraction  
↓  
Recruitment Agent  
↓  
Qwen 2.5 0.5B via Ollama  
↓  
Resume Analysis  
↓  
Match Score + Skills + Feedback + Recommendation

## 🛠️ Tech Stack

- Python
- Streamlit
- Agno
- Ollama
- Qwen 2.5 0.5B
- PyPDF

## 📋 Supported Roles

### AI/ML Engineer
- Python
- PyTorch / TensorFlow
- Machine Learning
- Deep Learning
- Data Preprocessing
- MLOps
- RAG
- LLMs
- Fine-tuning
- Prompt Engineering

### Frontend Engineer
- React / Vue / Angular
- HTML
- CSS
- JavaScript / TypeScript
- Responsive Design
- State Management
- Testing

### Backend Engineer
- Python / Java / Node.js
- REST APIs
- Database Design
- System Architecture
- Cloud
- Kubernetes
- Docker
- CI/CD

## ⚙️ Setup

Install dependencies:

```bash
pip install -r requirements.txt