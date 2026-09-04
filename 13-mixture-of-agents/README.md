\# 🤖 Mixture-of-Agents LLM App



A local \*\*Mixture-of-Agents (MoA)\*\* application that uses multiple specialized AI agents to independently analyze a question and then combines their responses into one final answer.



This project is customized from the original `mixture\_of\_agents` project to run locally using \*\*Ollama + Qwen 0.5B\*\*, without requiring a Together AI API key.



\## 🚀 Features



\- 🤖 Multiple specialized AI agents

\- 🔎 Analysis Agent

\- ⚠️ Critical Agent

\- 💡 Practical Agent

\- 🎯 Aggregator Agent

\- 🏠 Local Ollama inference

\- 🧠 Qwen 0.5B model

\- 🖥️ Streamlit interface

\- 📊 Individual agent responses

\- ✨ Final synthesized response



\## 🏗️ Architecture



```text

&#x20;                   User Question

&#x20;                        │

&#x20;                        ▼

&#x20;               ┌─────────────────┐

&#x20;               │   Streamlit UI  │

&#x20;               └────────┬────────┘

&#x20;                        │

&#x20;         ┌──────────────┼──────────────┐

&#x20;         ▼              ▼              ▼

&#x20;  ┌────────────┐ ┌────────────┐ ┌────────────┐

&#x20;  │  Analysis  │ │  Critical  │ │ Practical  │

&#x20;  │   Agent    │ │   Agent    │ │   Agent    │

&#x20;  └──────┬─────┘ └──────┬─────┘ └──────┬─────┘

&#x20;         │              │              │

&#x20;         └──────────────┼──────────────┘

&#x20;                        ▼

&#x20;               ┌─────────────────┐

&#x20;               │    Aggregator   │

&#x20;               │      Agent      │

&#x20;               └────────┬────────┘

&#x20;                        │

&#x20;                        ▼

&#x20;                 Final Answer



🧠 How It Works

1\. Analysis Agent



Analyzes the question from a logical and analytical perspective.



It focuses on:



Important parts of the problem

Key facts

Assumptions

Advantages and disadvantages

Possible conclusions

2\. Critical Agent



Reviews the question from a critical perspective.



It looks for:



Limitations

Risks

Alternative viewpoints

Incorrect assumptions

Edge cases

3\. Practical Agent



Approaches the question from a practical perspective.



It focuses on:



Real-world examples

Actionable recommendations

Simple explanations

Practical considerations

4\. Aggregator Agent



Receives all three independent responses and synthesizes them into one final answer.



It:



Compares the responses

Removes unnecessary repetition

Handles contradictions

Combines useful information

Produces the final structured answer

🔄 Mixture-of-Agents Workflow

Question

&#x20;  ↓

┌───────────────────────┐

│ Multiple AI Agents    │

│                       │

│ Analysis              │

│ Critical              │

│ Practical             │

└───────────┬───────────┘

&#x20;           ↓

&#x20;   Independent Answers

&#x20;           ↓

┌───────────────────────┐

│   Aggregator Agent    │

└───────────┬───────────┘

&#x20;           ↓

&#x20;     Final Answer



The important idea is that the agents independently approach the same question from different perspectives before a final agent combines their outputs.



🛠️ Tech Stack

Python

Streamlit

Agno

Ollama

Qwen 0.5B

⚙️ Setup

1\. Install dependencies

pip install -r requirements.txt

2\. Install Ollama



Make sure Ollama is installed and running.



Pull the model:



ollama pull qwen2.5:0.5b

3\. Run the application

python -m streamlit run mixture-of-agents.py



The application will open in your browser.

