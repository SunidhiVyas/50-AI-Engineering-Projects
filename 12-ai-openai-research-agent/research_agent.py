import streamlit as st
from datetime import datetime
from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.duckduckgo import DuckDuckGoTools


MODEL = "qwen2.5:0.5b"


st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🔍",
    layout="wide",
)

st.title("🔍 AI Research Agent")
st.subheader("Powered by Ollama + Qwen 0.5B")

st.markdown(
    """
This app uses a simple multi-agent workflow to research a topic
and generate a structured research report.

**Workflow:** Triage Agent → Research Agent → Editor Agent
"""
)


def create_agent(name, instructions, tools=None):
    return Agent(
        name=name,
        model=Ollama(id=MODEL),
        instructions=instructions,
        tools=tools or [],
        markdown=True,
    )


triage_agent = create_agent(
    "Triage Agent",
    """
    You are the coordinator of a research operation.

    Analyze the user's research topic and create a simple research plan.

    Include:
    1. Topic
    2. 3 useful search queries
    3. 3 important focus areas

    Keep the plan concise and practical.
    """,
)


research_agent = create_agent(
    "Research Agent",
    """
    You are a research assistant.

    Research the user's topic using the available web search tool.

    Summarize the most useful information clearly.
    Prefer recent and reliable sources.
    Do not invent facts or URLs.

    Keep the research concise so another agent can use it.
    """,
    tools=[DuckDuckGoTools()],
)


editor_agent = create_agent(
    "Editor Agent",
    """
    You are a senior research editor.

    Using the research provided to you, create a clear research report.

    Structure the report as:
    # Title

    ## Overview

    ## Key Findings

    ## Important Details

    ## Conclusion

    ## Sources

    Use markdown.

    IMPORTANT:
    Stay grounded in the supplied research.
    Do not invent sources, statistics, names or facts.
    """,
)


def run_agent(agent, prompt):
    response = agent.run(prompt)
    return response.content


with st.sidebar:
    st.header("Research Topic")

    user_topic = st.text_input(
        "Enter a topic to research:"
    )

    start_button = st.button(
        "Start Research",
        type="primary",
        disabled=not user_topic,
    )

    st.divider()

    st.subheader("Example Topics")

    examples = [
        "Latest developments in artificial intelligence",
        "Best affordable smartphones in India",
        "Future of electric vehicles",
    ]

    for example in examples:
        if st.button(example):
            user_topic = example
            start_button = True


if "research_done" not in st.session_state:
    st.session_state.research_done = False

if "report" not in st.session_state:
    st.session_state.report = ""

if start_button and user_topic:

    st.session_state.research_done = False
    st.session_state.report = ""

    st.header("Research Process")

    # -------------------------------------------------
    # 1. Triage Agent
    # -------------------------------------------------

    st.write("🔎 **Triage Agent:** Creating research plan...")

    triage_prompt = f"""
    Create a research plan for this topic:

    {user_topic}
    """

    triage_result = run_agent(
        triage_agent,
        triage_prompt,
    )

    with st.expander("Research Plan", expanded=True):
        st.markdown(triage_result)

    # -------------------------------------------------
    # 2. Research Agent
    # -------------------------------------------------

    st.write("🌐 **Research Agent:** Searching the web...")

    research_prompt = f"""
    Research this topic:

    {user_topic}

    Here is the research plan created by the Triage Agent:

    {triage_result}

    Search the web and provide useful factual information
    with source names or URLs when available.
    """

    research_result = run_agent(
        research_agent,
        research_prompt,
    )

    with st.expander("Research Results", expanded=True):
        st.markdown(research_result)

    # -------------------------------------------------
    # 3. Editor Agent
    # -------------------------------------------------

    st.write("📝 **Editor Agent:** Creating final report...")

    editor_prompt = f"""
    Create a research report about:

    {user_topic}

    Research plan:
    {triage_result}

    Research results:
    {research_result}

    Create the final report using only the information
    provided above.
    """

    final_report = run_agent(
        editor_agent,
        editor_prompt,
    )

    st.session_state.report = final_report
    st.session_state.research_done = True

    st.success("✅ Research completed!")


if st.session_state.research_done:

    st.header("📄 Research Report")

    st.markdown(st.session_state.report)

    st.download_button(
        label="Download Report",
        data=st.session_state.report,
        file_name=(
            f"research_report_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        ),
        mime="text/markdown",
    )