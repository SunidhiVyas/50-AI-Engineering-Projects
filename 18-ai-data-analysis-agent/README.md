# AI Data Analysis Agent

An AI-powered data analyst that lets users upload CSV or Excel files and ask questions about their data using natural language.

This version is customized to run locally with **Qwen 2.5 0.5B through Ollama**, with DuckDB and Pandas handling the data analysis.

## Features

- 📁 CSV and Excel file upload
- 📊 Interactive data preview
- 🔍 Natural-language data queries
- 🐼 Pandas-based analysis
- 🦆 DuckDB SQL-based analysis
- 🤖 Local Qwen 2.5 0.5B model
- 🔐 No OpenAI API key required
- 🌐 Streamlit interface
- 📈 Clear numerical results and tables

## Workflow

```text
CSV / Excel File
       ↓
Data Preprocessing
       ↓
Pandas + DuckDB
       ↓
AI Data Analyst
       ↓
Natural-Language Answer

Tech Stack
Python
Streamlit
Pandas
DuckDB
Agno
Ollama
Qwen 2.5 0.5B
OpenPyXL
Setup
1. Start Ollama

Make sure Ollama is running and the model is available:

ollama pull qwen2.5:0.5b
2. Install dependencies
pip install -r requirements.txt
3. Run the application
python -m streamlit run ai_data_analyst.py