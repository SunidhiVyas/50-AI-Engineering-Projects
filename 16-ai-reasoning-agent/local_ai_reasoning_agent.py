from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.playground import Playground, serve_playground_app


reasoning_agent = Agent(
    name="AI Reasoning Agent",
    model=Ollama(id="qwen2.5:0.5b"),
    reasoning=True,
    markdown=True,
    instructions=[
        "Solve problems carefully.",
        "Break complex problems into smaller steps.",
        "Check your answer before responding.",
        "Give a concise explanation of the reasoning."
    ],
)


app = Playground(
    agents=[reasoning_agent]
).get_app()


if __name__ == "__main__":
    serve_playground_app(
        "local_ai_reasoning_agent:app",
        reload=True
    )