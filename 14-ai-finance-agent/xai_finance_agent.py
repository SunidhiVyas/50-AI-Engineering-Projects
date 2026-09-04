from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.yfinance import YFinanceTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.os import AgentOS


# AI Finance Agent
agent = Agent(
    name="AI Finance Agent",
    model=Ollama(id="qwen2.5:0.5b"),
    tools=[
        DuckDuckGoTools(),
        YFinanceTools()
    ],
    instructions=[
        "You are an AI financial research assistant.",
        "Use YFinanceTools for stock prices, company information and financial data.",
        "Use web search when current news or market information is needed.",
        "Always use tables for financial and numerical data.",
        "Use bullet points for explanations.",
        "Clearly separate facts from analysis.",
        "Do not provide guaranteed investment returns.",
        "Keep answers concise and easy to understand."
    ],
    markdown=True,
    debug_mode=False,
)


# AgentOS application
agent_os = AgentOS(agents=[agent])
app = agent_os.get_app()


if __name__ == "__main__":
    agent_os.serve(app="xai_finance_agent:app", reload=True)