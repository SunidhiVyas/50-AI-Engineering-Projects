import streamlit as st
import asyncio

from autogen_core.models import UserMessage
from autogen_ext.models.ollama import OllamaChatCompletionClient


# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="AI Mental Wellbeing Support",
    page_icon="🧠",
    layout="wide"
)


# ---------------------------------------------------------
# Local Model Configuration
# ---------------------------------------------------------

MODEL_NAME = "qwen2.5:0.5b"


def create_client():
    """Create a local Ollama client."""
    return OllamaChatCompletionClient(
        model=MODEL_NAME
    )


# ---------------------------------------------------------
# Agent Function
# ---------------------------------------------------------

async def ask_agent(client, role, instructions, context):
    """Send a task to one specialized AI agent."""

    prompt = f"""
You are the {role} in a supportive mental wellbeing application.

IMPORTANT SAFETY RULES:
- You are not a doctor, therapist, or emergency service.
- Do not diagnose mental health conditions.
- Do not claim clinical certainty.
- Do not perform medical screening or diagnosis.
- Provide general supportive and wellness-oriented guidance.
- Encourage professional help when appropriate.
- Never shame or judge the user.
- If the situation suggests immediate danger or self-harm,
  encourage the person to contact local emergency services,
  a trusted person, or an appropriate crisis service immediately.

YOUR ROLE:
{instructions}

USER INFORMATION:
{context}

Write a concise, empathetic and practical response.
Focus only on your assigned role.
"""

    result = await client.create(
        [
            UserMessage(
                content=prompt,
                source="user"
            )
        ]
    )

    return result.content


# ---------------------------------------------------------
# Three-Agent Workflow
# ---------------------------------------------------------

async def generate_support_plan(user_context):
    """
    Run the three-agent workflow:

    Assessment Agent
            ↓
    Action Agent
            ↓
    Follow-up Agent
    """

    client = create_client()

    try:

        # -------------------------------------------------
        # Agent 1: Assessment
        # -------------------------------------------------

        assessment = await ask_agent(
            client,
            "Assessment Agent",
            """
Understand the user's current situation.

Summarize:
- emotional state
- stress level
- sleep
- support system
- recent life changes
- current concerns

Identify areas where additional support may be useful.

Do not diagnose the user.
Do not label the user with a mental health condition.
""",
            user_context
        )


        # -------------------------------------------------
        # Agent 2: Action
        # -------------------------------------------------

        action_context = f"""
ORIGINAL USER INFORMATION:

{user_context}


ASSESSMENT AGENT SUMMARY:

{assessment}
"""

        action = await ask_agent(
            client,
            "Action Agent",
            """
Create practical short-term wellbeing steps.

Include:
- simple coping strategies
- healthy daily routines
- ways to use the user's support system
- reasonable self-care activities
- professional support suggestions when appropriate

Prioritize realistic actions.
Do not overwhelm the user with too many recommendations.
""",
            action_context
        )


        # -------------------------------------------------
        # Agent 3: Follow-up
        # -------------------------------------------------

        followup_context = f"""
ORIGINAL USER INFORMATION:

{user_context}


ASSESSMENT:

{assessment}


ACTION PLAN:

{action}
"""

        followup = await ask_agent(
            client,
            "Follow-up Agent",
            """
Create a simple longer-term wellbeing strategy.

Include:
- sustainable habits
- progress check-ins
- ways to handle difficult days
- support-network planning
- maintaining healthy routines
- ways to adjust the plan over time

Focus on sustainable progress rather than perfection.
""",
            followup_context
        )


        return assessment, action, followup

    finally:
        await client.close()


# ---------------------------------------------------------
# Application Header
# ---------------------------------------------------------

st.title("🧠 AI Mental Wellbeing Support")

st.caption(
    "A three-agent supportive wellbeing workflow "
    "powered by local Ollama + Qwen"
)


# ---------------------------------------------------------
# Safety Notice
# ---------------------------------------------------------

st.warning(
    """
This application provides general wellbeing support only.

It is NOT a medical diagnostic, treatment, or emergency system.

If you are experiencing an immediate crisis or believe you
may be in danger, contact your local emergency services,
a trusted person, or an appropriate crisis support service.
"""
)


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

st.sidebar.title("🤖 AI Agent Team")

st.sidebar.info(
    f"""
**Local Model**

{MODEL_NAME}

**Agent Workflow**

1. 🧠 Assessment Agent
2. 🎯 Action Agent
3. 🔄 Follow-up Agent

**Technology**

- Streamlit
- AutoGen
- Ollama
- Qwen 2.5 0.5B

No OpenAI API key is required.
"""
)


# ---------------------------------------------------------
# User Input
# ---------------------------------------------------------

st.subheader("Tell us about your current situation")

col1, col2 = st.columns(2)


with col1:

    mental_state = st.text_area(
        "How have you been feeling recently?",
        placeholder=(
            "Describe your emotional state, "
            "thoughts, or concerns..."
        )
    )


    sleep_pattern = st.slider(
        "Sleep (hours per night)",
        min_value=0,
        max_value=12,
        value=7
    )


    recent_changes = st.text_area(
        "Any significant life changes recently?",
        placeholder=(
            "Job changes, relationships, studies, "
            "losses, etc..."
        )
    )


with col2:

    stress_level = st.slider(
        "Current Stress Level",
        min_value=1,
        max_value=10,
        value=5
    )


    support_system = st.multiselect(
        "Current Support System",
        [
            "Family",
            "Friends",
            "Therapist",
            "Support Groups",
            "None"
        ]
    )


    current_concerns = st.multiselect(
        "Current Concerns",
        [
            "Anxiety",
            "Low Mood",
            "Insomnia",
            "Fatigue",
            "Loss of Interest",
            "Difficulty Concentrating",
            "Changes in Appetite",
            "Social Withdrawal",
            "Mood Changes",
            "Physical Discomfort"
        ]
    )


# ---------------------------------------------------------
# Generate Support Plan
# ---------------------------------------------------------

if st.button(
    "🧠 Generate Support Plan",
    type="primary"
):

    user_context = f"""
Emotional State:
{mental_state if mental_state else "Not provided"}

Sleep:
{sleep_pattern} hours per night

Stress Level:
{stress_level}/10

Support System:
{
    ", ".join(support_system)
    if support_system
    else "None reported"
}

Recent Changes:
{
    recent_changes
    if recent_changes
    else "None reported"
}

Current Concerns:
{
    ", ".join(current_concerns)
    if current_concerns
    else "None reported"
}
"""


    with st.spinner(
        "🧠 AI agents are preparing your support plan..."
    ):

        try:

            assessment, action, followup = asyncio.run(
                generate_support_plan(user_context)
            )


            # -------------------------------------------------
            # Results
            # -------------------------------------------------

            st.success(
                "Support plan generated successfully."
            )


            with st.expander(
                "🔎 Situation Assessment",
                expanded=True
            ):
                st.markdown(assessment)


            with st.expander(
                "🎯 Action Plan & Resources",
                expanded=True
            ):
                st.markdown(action)


            with st.expander(
                "🔄 Long-term Support Strategy",
                expanded=True
            ):
                st.markdown(followup)


        except Exception as e:

            st.error(
                f"Unable to generate the support plan: {str(e)}"
            )

            st.info(
                "Please make sure Ollama is running and "
                f"the `{MODEL_NAME}` model is installed."
            )


# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------

st.divider()

st.caption(
    "Built with Streamlit, AutoGen and Ollama. "
    "Educational/supportive use only."
)