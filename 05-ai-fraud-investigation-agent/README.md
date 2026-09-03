# 🔍 AI Fraud Investigation Agent

A customized AI-powered anomaly investigation system for childcare providers.

This project is based on the original Surelock Homes concept, but has been adapted to run locally using **Ollama + Qwen 2.5 0.5B**, making it suitable for lightweight local environments.

## 🚀 Features

- 🔎 Search licensed childcare providers
- 🏠 Retrieve Cook County property information
- 📐 Calculate estimated maximum childcare capacity
- 📍 Optional Google Maps geocoding
- 🗺️ Optional Google Street View analysis
- ⭐ Optional Google Places information
- 🏢 Check Illinois business registration information
- 🤖 Local AI investigation using Ollama
- ⚠️ Identify potential anomalies and investigation flags
- 📝 Explain evidence and assumptions

## 🧠 Investigation Flow

```text
ZIP Code
   ↓
Illinois Childcare Licensing Data
   ↓
Provider Information
   ↓
Cook County Property Data
   ↓
Building Capacity Calculation
   ↓
Optional Google Maps Evidence
   ↓
Business Registration Cross-Check
   ↓
Local Qwen Analysis
   ↓
Investigation Findings