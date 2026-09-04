import json

import streamlit as st
from pypdf import PdfReader
from agno.agent import Agent
from agno.models.ollama import Ollama


MODEL_NAME = "qwen2.5:0.5b"


ROLE_REQUIREMENTS = {
    "AI/ML Engineer": [
        "Python",
        "Machine Learning",
        "Deep Learning",
        "PyTorch or TensorFlow",
        "Data preprocessing",
        "MLOps",
        "RAG",
        "LLM",
        "Prompt Engineering",
    ],
    "Frontend Engineer": [
        "React",
        "JavaScript",
        "TypeScript",
        "HTML",
        "CSS",
        "Responsive design",
        "State management",
        "Frontend testing",
    ],
    "Backend Engineer": [
        "Python, Java, or Node.js",
        "REST APIs",
        "Database design",
        "System architecture",
        "Cloud services",
        "Docker",
        "Kubernetes",
        "CI/CD",
    ],
}


def extract_resume_text(pdf_file):
    """Extract text from an uploaded PDF resume."""
    reader = PdfReader(pdf_file)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def analyze_resume(resume_text, role):
    """Analyze a resume using local Qwen."""

    requirements = ROLE_REQUIREMENTS[role]

    agent = Agent(
        name="Resume Analyzer",
        model=Ollama(id=MODEL_NAME),
        markdown=False,
        instructions=[
            "You are an AI technical recruiter.",
            "Analyze the resume against the selected job role.",
            "Consider projects and practical experience.",
            "Do not invent experience or skills.",
            "Return ONLY valid JSON.",
        ],
    )

    prompt = f"""
Analyze this resume for the role: {role}

Required skills:
{requirements}

Resume:
{resume_text[:12000]}

Return exactly this JSON format:

{{
    "match_score": 0,
    "selected": false,
    "experience_level": "junior",
    "matching_skills": [],
    "missing_skills": [],
    "feedback": "short explanation",
    "recommendation": "short recommendation"
}}

Rules:
- match_score must be between 0 and 100.
- selected should be true if the candidate appears reasonably suitable.
- Do not invent information.
- Consider projects as practical experience.
- Keep feedback concise.
- Return ONLY JSON.
"""

    response = agent.run(prompt)

    result = response.content.strip()

    # Remove accidental markdown formatting
    if result.startswith("```"):
        result = result.replace("```json", "")
        result = result.replace("```", "")
        result = result.strip()

    return json.loads(result)


st.set_page_config(
    page_title="AI Recruitment Agent",
    page_icon="👩‍💻",
    layout="centered",
)


st.title("🤖 AI Recruitment Agent")

st.write(
    "Analyze a candidate's resume against a selected software "
    "engineering role using local AI."
)

st.info(
    "Runs locally with Qwen 2.5 0.5B through Ollama. "
    "No OpenAI, Zoom, or email API keys are required."
)


role = st.selectbox(
    "Select the role",
    list(ROLE_REQUIREMENTS.keys()),
)


with st.expander("📋 View Required Skills"):
    for skill in ROLE_REQUIREMENTS[role]:
        st.write(f"• {skill}")


resume_file = st.file_uploader(
    "Upload candidate resume",
    type=["pdf"],
)


if resume_file:

    st.success(f"Resume uploaded: {resume_file.name}")

    if st.button("🔍 Analyze Resume", type="primary"):

        try:

            with st.spinner("Extracting resume text..."):
                resume_text = extract_resume_text(resume_file)

            if not resume_text.strip():
                st.error("Could not extract text from this PDF.")
                st.stop()

            with st.spinner("Analyzing resume with Qwen..."):

                result = analyze_resume(
                    resume_text,
                    role,
                )

            st.subheader("📊 Recruitment Analysis")

            score = int(result.get("match_score", 0))

            st.metric(
                "Resume Match Score",
                f"{score}%",
            )

            if result.get("selected"):
                st.success("✅ Candidate recommended for the next stage.")
            else:
                st.warning("⚠️ Candidate needs further evaluation.")

            st.write(
                f"**Experience Level:** "
                f"{result.get('experience_level', 'Not specified')}"
            )

            st.subheader("✅ Matching Skills")

            matching_skills = result.get("matching_skills", [])

            if matching_skills:
                for skill in matching_skills:
                    st.write(f"• {skill}")
            else:
                st.write("No matching skills identified.")

            st.subheader("📚 Missing Skills")

            missing_skills = result.get("missing_skills", [])

            if missing_skills:
                for skill in missing_skills:
                    st.write(f"• {skill}")
            else:
                st.write("No major missing skills identified.")

            st.subheader("💬 Recruiter Feedback")

            st.write(
                result.get(
                    "feedback",
                    "No feedback generated.",
                )
            )

            st.subheader("🎯 Recommendation")

            st.write(
                result.get(
                    "recommendation",
                    "No recommendation generated.",
                )
            )

        except json.JSONDecodeError:

            st.error(
                "The AI returned an invalid response. "
                "Please try the analysis again."
            )

        except Exception as e:

            st.error(f"Error: {e}")


st.divider()

st.caption(
    "⚠️ This tool is a portfolio/demo project and should not be "
    "used as the sole basis for real hiring decisions."
)