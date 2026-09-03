import asyncio
import streamlit as st
from PIL import Image as PILImage

from autogen_core.models import UserMessage
from autogen_ext.models.ollama import OllamaChatCompletionClient


MODEL_NAME = "qwen2.5:0.5b"


async def ask_ai(prompt):
    client = OllamaChatCompletionClient(
        model=MODEL_NAME,
    )

    try:
        result = await client.create(
            [
                UserMessage(
                    content=prompt,
                    source="user",
                )
            ]
        )

        if hasattr(result, "content"):
            return str(result.content)

        return str(result)

    finally:
        await client.close()


def analyze_image(description):
    prompt = f"""
You are an educational medical imaging assistant.

IMPORTANT:
You cannot directly see or interpret the uploaded image.
Do not claim to diagnose the image.
Do not invent findings, measurements, abnormalities, or diagnoses.

The user has uploaded a medical image and provided this description:

{description}

Based ONLY on the user's description, provide educational guidance using:

## 1. Imaging Context
Explain what type of information is normally evaluated in this kind of
medical imaging.

## 2. Important Things Radiologists Evaluate
List the general features a qualified radiologist may examine.

## 3. Questions to Ask a Healthcare Professional
Give useful questions the patient can ask about their scan.

## 4. Patient-Friendly Explanation
Explain why professional interpretation of medical images is important.

## 5. Important Disclaimer
Clearly state that this response is educational and cannot replace a
radiologist or healthcare professional.

Keep the answer concise and easy to understand.
"""

    return asyncio.run(ask_ai(prompt))


def main():
    st.set_page_config(
        page_title="AI Medical Imaging Assistant",
        page_icon="🩻",
        layout="wide",
    )

    st.title("🩻 AI Medical Imaging Assistant")

    st.write(
        "Upload a medical image and provide a short description. "
        "The local AI assistant will provide educational guidance about "
        "what a healthcare professional may evaluate."
    )

    st.warning(
        "⚠️ This demo does NOT diagnose medical images. "
        "The local Qwen 0.5B model used here is text-only and cannot "
        "interpret the pixels of an X-ray, CT, MRI, or ultrasound. "
        "Always rely on a qualified healthcare professional for medical "
        "image interpretation."
    )

    st.subheader("1. Upload Medical Image")

    uploaded_file = st.file_uploader(
        "Upload an image",
        type=["jpg", "jpeg", "png"],
        help="Supported formats: JPG, JPEG and PNG.",
    )

    if uploaded_file is not None:
        image = PILImage.open(uploaded_file)

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.image(
                image,
                caption="Uploaded Medical Image",
                use_container_width=True,
            )

        st.success("Image uploaded successfully.")

        st.subheader("2. Describe the Image")

        description = st.text_area(
            "What type of scan is this or what did your doctor tell you?",
            placeholder=(
                "Example: This is a chest X-ray taken during a routine "
                "check-up. My doctor asked me to discuss the report."
            ),
            height=120,
        )

        if st.button(
            "🔍 Generate Educational Guidance",
            type="primary",
            use_container_width=True,
        ):
            if not description.strip():
                st.warning(
                    "Please provide a short description before continuing."
                )
                return

            with st.spinner(
                "Generating educational guidance with local Qwen..."
            ):
                try:
                    result = analyze_image(description)

                    st.subheader("📋 Educational Guidance")
                    st.markdown("---")
                    st.markdown(result)
                    st.markdown("---")

                    st.caption(
                        "This output is educational only and is not a "
                        "medical diagnosis or treatment recommendation."
                    )

                except Exception as e:
                    st.error(f"Analysis error: {e}")

    else:
        st.info("👆 Please upload a medical image to begin.")


if __name__ == "__main__":
    main()