import streamlit as st
from agno.agent import Agent
from agno.models.ollama import Ollama


MODEL = "qwen2.5:0.5b"


st.set_page_config(
    page_title="Mixture of Agents",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 Mixture-of-Agents LLM App")
st.subheader("Powered by Ollama + Qwen 0.5B")

st.markdown(
    """
This app demonstrates a **Mixture-of-Agents** architecture.

Instead of depending on multiple cloud models, several specialized
agents running on the same local LLM independently analyze the question.
A final Aggregator Agent combines their responses into one answer.
"""
)


def create_agent(name, instructions):
    return Agent(
        name=name,
        model=Ollama(id=MODEL),
        instructions=instructions,
        markdown=True,
    )


# Agent 1: Analytical perspective
analysis_agent = create_agent(
    "Analysis Agent",
    """
    Analyze the user's question carefully.

    Break the problem into important parts.
    Identify key facts, assumptions, advantages, disadvantages,
    and possible conclusions.

    Give a clear and structured answer.
    Do not invent facts.
    """,
)


# Agent 2: Critical perspective
critical_agent = create_agent(
    "Critical Agent",
    """
    Critically evaluate the user's question.

    Look for limitations, risks, alternative viewpoints,
    incorrect assumptions, and edge cases.

    Provide a balanced and practical response.
    Do not invent facts.
    """,
)


# Agent 3: Practical perspective
practical_agent = create_agent(
    "Practical Agent",
    """
    Approach the user's question from a practical perspective.

    Give useful examples, actionable recommendations,
    and simple explanations.

    Focus on what would be most useful to the user.
    Do not invent facts.
    """,
)


# Final aggregator
aggregator_agent = create_agent(
    "Aggregator Agent",
    """
    You are the final answer synthesizer.

    You will receive multiple independent responses to the same question.

    Combine the useful information into ONE high-quality answer.

    Carefully compare the responses.
    Remove contradictions and unnecessary repetition.
    Do not blindly copy any response.
    Prefer information that is supported consistently.

    Structure the final answer clearly using markdown.

    Do not mention that multiple agents were used unless necessary.
    Do not invent information that was not present in the supplied responses.
    """,
)


def run_agent(agent, prompt):
    response = agent.run(prompt)
    return response.content


def run_mixture(user_question):
    # Run the three independent perspectives
    analysis_response = run_agent(
        analysis_agent,
        f"""
        Question:

        {user_question}
        """,
    )

    critical_response = run_agent(
        critical_agent,
        f"""
        Question:

        {user_question}
        """,
    )

    practical_response = run_agent(
        practical_agent,
        f"""
        Question:

        {user_question}
        """,
    )

    # Combine responses for the aggregator
    combined_responses = f"""
    ORIGINAL QUESTION:
    {user_question}

    ==============================
    ANALYSIS AGENT RESPONSE
    ==============================

    {analysis_response}

    ==============================
    CRITICAL AGENT RESPONSE
    ==============================

    {critical_response}

    ==============================
    PRACTICAL AGENT RESPONSE
    ==============================

    {practical_response}
    """

    final_response = run_agent(
        aggregator_agent,
        f"""
        Synthesize the following responses into one final answer.

        {combined_responses}
        """,
    )

    return (
        analysis_response,
        critical_response,
        practical_response,
        final_response,
    )


# Sidebar
with st.sidebar:
    st.title("About")

    st.markdown(
        """
        This application demonstrates a
        **Mixture-of-Agents (MoA)** architecture.

        Multiple agents independently answer the
        same question from different perspectives.

        A final Aggregator Agent then combines
        those responses into a single answer.
        """
    )

    st.subheader("Architecture")

    st.markdown(
        """
        1. User asks a question
        2. Analysis Agent responds
        3. Critical Agent responds
        4. Practical Agent responds
        5. Aggregator Agent synthesizes everything
        6. Final answer is displayed
        """
    )


# User input
user_question = st.text_area(
    "Enter your question:",
    placeholder="Example: What are the advantages and disadvantages of electric vehicles?",
    height=120,
)


if st.button("Get Answer", type="primary"):

    if not user_question.strip():
        st.warning("Please enter a question.")

    else:
        with st.spinner("Running multiple agents..."):

            (
                analysis_response,
                critical_response,
                practical_response,
                final_response,
            ) = run_mixture(user_question)

        st.success("✅ Mixture-of-Agents completed!")

        st.header("Individual Agent Responses")

        with st.expander("🔎 Analysis Agent"):
            st.markdown(analysis_response)

        with st.expander("⚠️ Critical Agent"):
            st.markdown(critical_response)

        with st.expander("💡 Practical Agent"):
            st.markdown(practical_response)

        st.header("🎯 Aggregated Response")

        st.markdown(final_response)