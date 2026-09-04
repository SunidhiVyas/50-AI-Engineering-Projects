import json
import os
import tempfile

import streamlit as st
from agno.agent import Agent
from agno.models.ollama import Ollama
from midiutil import MIDIFile


MODEL_NAME = "qwen2.5:0.5b"


def create_music_plan(prompt):
    """Ask Qwen to convert the idea into a simple MIDI music plan."""

    agent = Agent(
        name="AI Music Composer",
        model=Ollama(id=MODEL_NAME),
        markdown=False,
        instructions=[
            "You are a simple music composition assistant.",
            "Convert the user's music idea into a JSON music plan.",
            "Choose a tempo between 60 and 160 BPM.",
            "Choose a scale from C major, G major, A minor, or E minor.",
            "Create 8 to 16 notes.",
            "Each note must have a pitch between 48 and 84.",
            "Use note durations of 0.5, 1, or 2 beats.",
            "Return ONLY valid JSON.",
            "Do not include markdown or explanations.",
        ],
    )

    response = agent.run(
        f"""
Create a simple MIDI music plan for:

{prompt}

Use exactly this JSON structure:

{{
  "title": "short title",
  "tempo": 100,
  "scale": "C major",
  "notes": [
    {{"pitch": 60, "duration": 1}},
    {{"pitch": 64, "duration": 1}}
  ]
}}
"""
    )

    text = response.content.strip()

    # Remove accidental markdown fences
    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()

    return json.loads(text)


def create_midi(plan):
    """Convert the AI music plan into a MIDI file."""

    midi = MIDIFile(1)

    track = 0
    channel = 0
    time = 0

    tempo = int(plan.get("tempo", 100))
    midi.addTempo(track, time, tempo)

    notes = plan.get("notes", [])

    for note in notes:
        pitch = max(48, min(84, int(note.get("pitch", 60))))
        duration = float(note.get("duration", 1))

        midi.addNote(
            track,
            channel,
            pitch,
            time,
            duration,
            100,
        )

        time += duration

    output_file = tempfile.NamedTemporaryFile(
        suffix=".mid",
        delete=False,
    ).name

    with open(output_file, "wb") as file:
        midi.writeFile(file)

    return output_file


st.set_page_config(
    page_title="AI Music Generator",
    page_icon="🎵",
    layout="centered",
)

st.title("🎵 AI Music Generator")

st.write(
    "Turn a natural-language music idea into a simple MIDI composition "
    "using local AI."
)

st.info(
    "Runs locally with Qwen 2.5 0.5B through Ollama. "
    "No OpenAI or ModelsLab API key is required."
)

prompt = st.text_area(
    "Describe your music",
    "Create a calm piano melody for a relaxing evening",
    height=120,
)

if st.button("Generate Music 🎶", type="primary"):

    if not prompt.strip():
        st.warning("Please describe the music you want.")
        st.stop()

    try:
        with st.spinner("Composing music with Qwen... 🎼"):
            plan = create_music_plan(prompt)

        st.success("Music composition created!")

        st.subheader("🎼 Music Plan")

        st.write(f"**Title:** {plan.get('title', 'AI Composition')}")
        st.write(f"**Tempo:** {plan.get('tempo', 100)} BPM")
        st.write(f"**Scale:** {plan.get('scale', 'C major')}")

        with st.expander("View generated notes"):
            st.json(plan.get("notes", []))

        with st.spinner("Creating MIDI file..."):
            midi_file = create_midi(plan)

        with open(midi_file, "rb") as file:
            midi_bytes = file.read()

        st.success("MIDI music generated successfully! 🎵")

        st.download_button(
            label="⬇️ Download MIDI",
            data=midi_bytes,
            file_name="ai_generated_music.mid",
            mime="audio/midi",
        )

        os.remove(midi_file)

    except json.JSONDecodeError:
        st.error(
            "The AI returned an invalid music plan. "
            "Please try the prompt again."
        )

    except Exception as e:
        st.error(f"Error: {e}")