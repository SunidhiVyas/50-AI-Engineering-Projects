import streamlit as st
from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.newspaper4k import Newspaper4kTools


st.set_page_config(
    page_title="AI Startup Trend Analysis Agent",
    page_icon="🚀"
)

st.title("🚀 AI Startup Trend Analysis Agent")
st.caption(
    "Discover emerging trends and potential startup opportunities "
    "from recent web information."
)

topic = st.text_input(
    "Enter an area of interest:",
    placeholder="Example: AI in healthcare"
)


if st.button("Generate Analysis"):

    if not topic:
        st.warning("Please enter a topic.")
    else:

        with st.spinner("Analyzing startup trends..."):

            try:
                model = Ollama(id="qwen2.5:0.5b")

                # Step 1: Collect recent information
                news_collector = Agent(
                    name="News Collector",
                    role="Collects recent information about the topic",
                    model=model,
                    tools=[DuckDuckGoTools()],
                    instructions=[
                        "Find recent and relevant information about the topic.",
                        "Focus on startups, products, technologies and market developments.",
                        "Return the most useful findings with source names when possible."
                    ],
                    markdown=True,
                )

                news_response = news_collector.run(
                    f"Find recent startup and technology news about {topic}"
                )

                articles = news_response.content

                # Step 2: Summarize information
                summary_writer = Agent(
                    name="Summary Writer",
                    role="Summarizes research findings",
                    model=model,
                    instructions=[
                        "Summarize the provided research.",
                        "Keep important facts and remove unnecessary details.",
                        "Use short bullet points."
                    ],
                    markdown=True,
                )

                summary_response = summary_writer.run(
                    f"Summarize this research about {topic}:\n\n{articles}"
                )

                summaries = summary_response.content

                # Step 3: Analyze trends and opportunities
                trend_analyzer = Agent(
                    name="Trend Analyzer",
                    role="Identifies emerging trends and startup opportunities",
                    model=model,
                    instructions=[
                        "Analyze the research summaries.",
                        "Identify emerging technology and market trends.",
                        "Suggest realistic startup opportunities.",
                        "For each opportunity explain the problem, target users and possible solution.",
                        "Clearly separate observations from suggestions.",
                        "Keep the final answer concise."
                    ],
                    markdown=True,
                )

                trend_response = trend_analyzer.run(
                    f"Analyze these summaries and identify startup opportunities:\n\n{summaries}"
                )

                analysis = trend_response.content

                st.subheader("📈 Startup Trend Analysis")
                st.markdown(analysis)

                with st.expander("View Research Summary"):
                    st.markdown(summaries)

            except Exception as e:
                st.error(f"An error occurred: {e}")