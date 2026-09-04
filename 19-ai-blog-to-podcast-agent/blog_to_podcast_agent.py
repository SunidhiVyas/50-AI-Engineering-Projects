import os
import tempfile

import requests
import streamlit as st
import pyttsx3
from bs4 import BeautifulSoup
from agno.agent import Agent
from agno.models.ollama import Ollama


MODEL_NAME = "qwen2.5:0.5b"


def extract_blog_text(url):
    """Extract readable article text from a blog URL."""
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove unnecessary page elements
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    # Try to find the main article
    article = soup.find("article")

    if article:
        text = article.get_text(" ", strip=True)
    else:
        text = soup.get_text(" ", strip=True)

    # Keep the input small for the lightweight local model
    return text[:12000]


def create_podcast_script(blog_text):
    """Create a conversational podcast script using local Qwen."""
    agent = Agent(
        name="Blog Podcast Writer",
        model=Ollama(id=MODEL_NAME),
        markdown=False,
        instructions=[
            "Convert the provided blog content into a short podcast script.",
            "Make it natural and conversational.",
            "Start with a short introduction.",
            "Explain the main ideas clearly.",
            "End with a short conclusion.",
            "Do not invent facts that are not present in the blog.",
            "Keep the script under approximately 1200 words.",
        ],
    )

    response = agent.run(
        f"""
Create a podcast script from this blog content:

{blog_text}
"""
    )

    return response.content


def create_audio(script):
    """Convert podcast script to a WAV audio file using Windows TTS."""
    engine = pyttsx3.init()

    # Slightly slower speech for easier listening
    engine.setProperty("rate", 165)

    output_file = tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False
    ).name

    engine.save_to_file(script, output_file)
    engine.runAndWait()
    engine.stop()

    return output_file


st.set_page_config(
    page_title="AI Blog to Podcast",
    page_icon="🎙️",
    layout="centered",
)

st.title("🎙️ AI Blog to Podcast")
st.write(
    "Convert any readable blog article into a short podcast "
    "using local AI and offline text-to-speech."
)

st.info(
    "Runs locally with Qwen 0.5B through Ollama and Windows offline TTS. "
    "No OpenAI or ElevenLabs API key is required."
)

url = st.text_input(
    "Blog URL",
    placeholder="https://example.com/blog/article",
)

if st.button("Generate Podcast", type="primary"):

    if not url:
        st.warning("Please enter a blog URL.")
        st.stop()

    try:
        with st.spinner("Reading the blog..."):
            blog_text = extract_blog_text(url)

        if len(blog_text.strip()) < 100:
            st.error("Could not extract enough text from this page.")
            st.stop()

        st.success("Blog content extracted successfully.")

        with st.spinner("Creating podcast script with Qwen..."):
            script = create_podcast_script(blog_text)

        st.subheader("📝 Podcast Script")
        st.write(script)

        with st.spinner("Generating audio..."):
            audio_file = create_audio(script)

        st.subheader("🎧 Podcast")

        with open(audio_file, "rb") as f:
            audio_bytes = f.read()

        st.audio(audio_bytes, format="audio/wav")

        st.download_button(
            label="⬇️ Download Podcast",
            data=audio_bytes,
            file_name="blog_podcast.wav",
            mime="audio/wav",
        )

        try:
            os.remove(audio_file)
        except OSError:
            pass

    except requests.RequestException as e:
        st.error(f"Could not access the blog: {e}")

    except Exception as e:
        st.error(f"Error: {e}")