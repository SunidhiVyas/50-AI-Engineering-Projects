import requests
import streamlit as st
from bs4 import BeautifulSoup
from agno.agent import Agent
from agno.models.ollama import Ollama


MODEL_NAME = "qwen2.5:0.5b"


def scrape_website(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=20
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove unnecessary content
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    text = soup.get_text(" ", strip=True)

    # Keep input manageable for the small local model
    return text[:12000]


def analyze_content(content, user_prompt):
    agent = Agent(
        name="Web Scraping AI Agent",
        model=Ollama(id=MODEL_NAME),
        markdown=True,
        instructions=[
            "Analyze only the information provided from the webpage.",
            "Answer the user's question using the scraped content.",
            "Do not invent information.",
            "If the requested information is not present, clearly say so.",
            "Keep the answer concise and useful."
        ],
    )

    response = agent.run(
        f"""
Webpage content:

{content}

User request:

{user_prompt}
"""
    )

    return response.content


st.set_page_config(
    page_title="Web Scraping AI Agent",
    page_icon="🕵️",
    layout="centered"
)

st.title("🕵️ Web Scraping AI Agent")

st.caption(
    "Scrape a public webpage and ask questions about its content "
    "using local Qwen AI."
)

st.info(
    "Runs locally with Qwen 2.5 0.5B through Ollama. "
    "No external AI API key is required."
)

url = st.text_input(
    "Website URL",
    placeholder="https://example.com"
)

user_prompt = st.text_area(
    "What do you want to find?",
    placeholder="Summarize the main points of this webpage."
)

if st.button("🔍 Scrape & Analyze", type="primary"):

    if not url.strip():
        st.warning("Please enter a website URL.")
        st.stop()

    if not user_prompt.strip():
        st.warning("Please enter what you want the AI to find.")
        st.stop()

    try:
        with st.spinner("Scraping website..."):
            content = scrape_website(url)

        if len(content.strip()) < 100:
            st.error("Could not extract enough readable content.")
            st.stop()

        st.success("Website scraped successfully.")

        with st.spinner("Analyzing with Qwen..."):
            answer = analyze_content(content, user_prompt)

        st.subheader("🤖 AI Answer")
        st.markdown(answer)

        with st.expander("View scraped content"):
            st.write(content)

    except requests.RequestException as e:
        st.error(f"Could not access the website: {e}")

    except Exception as e:
        st.error(f"Error: {e}")