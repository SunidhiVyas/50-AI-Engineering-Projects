import asyncio
import streamlit as st

from autogen_core.models import UserMessage
from autogen_ext.models.ollama import OllamaChatCompletionClient


MODEL_NAME = "qwen2.5:0.5b"


async def ask_ai(client, system_prompt, user_prompt):
    messages = [
        UserMessage(
            content=f"{system_prompt}\n\n{user_prompt}",
            source="user",
        )
    ]

    result = await client.create(messages)

    if hasattr(result, "content"):
        return str(result.content)

    return str(result)


async def generate_recovery_plan(
    breakup_situation,
    days_since_breakup,
    contact_status,
    biggest_challenge,
    support_system,
):
    client = OllamaChatCompletionClient(
        model=MODEL_NAME,
    )

    try:
        context = f"""
Breakup situation:
{breakup_situation}

Days since breakup:
{days_since_breakup}

Current contact with ex:
{contact_status}

Biggest challenge:
{biggest_challenge}

Support system:
{support_system}
"""

        # Agent 1: Emotional Assessment
        assessment = await ask_ai(
            client,
            """
You are an Emotional Assessment Agent.

Help the user understand what they may be experiencing after a breakup.
Be empathetic, practical, and non-judgmental.

Do NOT diagnose mental health conditions.
Do NOT pretend to be a therapist.
Do NOT make assumptions about the user's exact emotions.

Give a short assessment and identify 2-3 areas that may need attention.
""",
            context,
        )

        # Agent 2: Recovery Actions
        actions = await ask_ai(
            client,
            """
You are a Recovery Action Agent.

Create simple, realistic actions that can help someone rebuild their
daily routine after a breakup.

Focus on:
- daily routine
- sleep and meals
- exercise or movement
- reducing unhealthy rumination
- hobbies and productive activities
- healthy social connection

Keep the suggestions practical and achievable.
""",
            f"""
User information:
{context}

Emotional assessment:
{assessment}

Create 5-7 practical recovery actions.
""",
        )

        # Agent 3: Long-Term Recovery Planner
        recovery_plan = await ask_ai(
            client,
            """
You are a Long-Term Recovery Planner.

Create a simple recovery plan based on the user's situation.

Divide it into:
1. Today
2. This Week
3. Next 2-4 Weeks

The goal is gradual emotional recovery and rebuilding a healthy routine.

Do not promise that the user will recover within a specific period.
Do not provide medical diagnosis or treatment.
""",
            f"""
User information:
{context}

Assessment:
{assessment}

Recommended actions:
{actions}

Create a clear and encouraging recovery plan.
""",
        )

        return assessment, actions, recovery_plan

    finally:
        await client.close()


def main():
    st.set_page_config(
        page_title="AI Breakup Recovery Agent",
        page_icon="💙",
        layout="wide",
    )

    st.title("💙 AI Breakup Recovery Agent")
    st.write(
        "A local AI assistant that helps you reflect, rebuild your routine, "
        "and create practical recovery steps after a breakup."
    )

    st.info(
        "This is a supportive AI tool, not a replacement for a qualified "
        "mental-health professional. If you are in immediate danger or "
        "thinking about harming yourself, contact local emergency services "
        "or a trusted person immediately."
    )

    st.subheader("Tell me about your situation")

    breakup_situation = st.text_area(
        "What happened?",
        placeholder="I recently went through a breakup and I'm having trouble focusing on my daily routine.",
        height=120,
    )

    col1, col2 = st.columns(2)

    with col1:
        days_since_breakup = st.number_input(
            "Days since the breakup",
            min_value=0,
            max_value=10000,
            value=7,
        )

        contact_status = st.selectbox(
            "Are you currently in contact with your ex?",
            [
                "No contact",
                "Occasional contact",
                "Regular contact",
                "We are still figuring things out",
            ],
        )

    with col2:
        biggest_challenge = st.selectbox(
            "What is your biggest challenge right now?",
            [
                "Missing my ex",
                "Overthinking",
                "Difficulty focusing",
                "Feeling lonely",
                "Maintaining my routine",
                "Moving forward",
                "Something else",
            ],
        )

        support_system = st.selectbox(
            "How much support do you currently have?",
            [
                "Strong support from friends/family",
                "Some support",
                "Very little support",
                "Mostly dealing with it alone",
            ],
        )

    if st.button("💙 Create My Recovery Plan", type="primary"):
        if not breakup_situation.strip():
            st.warning("Please describe your situation first.")
            return

        with st.spinner("Creating your personalized recovery plan..."):
            try:
                assessment, actions, recovery_plan = asyncio.run(
                    generate_recovery_plan(
                        breakup_situation,
                        days_since_breakup,
                        contact_status,
                        biggest_challenge,
                        support_system,
                    )
                )

                st.success("Your recovery plan is ready.")

                st.subheader("🧠 Emotional Assessment")
                st.write(assessment)

                st.subheader("🌱 Practical Recovery Actions")
                st.write(actions)

                st.subheader("📅 Your Recovery Plan")
                st.write(recovery_plan)

                st.caption(
                    "Take the suggestions that feel useful and ignore anything "
                    "that does not fit your situation."
                )

            except Exception as e:
                st.error(f"Something went wrong: {e}")


if __name__ == "__main__":
    main()