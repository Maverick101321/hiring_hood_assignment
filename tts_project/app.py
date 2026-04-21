"""Streamlit app for generating text-to-speech audio."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from tts_engine import TTSEngine


OUTPUT_PATH = Path("output") / "result.wav"


@st.cache_resource
def get_tts_engine() -> TTSEngine:
    """Create a single TTS engine instance for the Streamlit session."""
    return TTSEngine()


def main() -> None:
    """Render the Streamlit interface and handle speech generation."""
    st.set_page_config(page_title="TTS Generator", page_icon="🎙️")
    st.title("Text-to-Speech Generator")
    st.write("Type some text, choose a voice, and generate playable speech.")

    engine = get_tts_engine()
    voices = engine.list_voices()

    text = st.text_area(
        "Text to speak",
        height=180,
        placeholder="Enter the text you want to convert to speech...",
    )

    if voices:
        voice_labels = [
            f"{voice['name']} ({voice['language']}, {voice['gender']})"
            for voice in voices
        ]
        selected_voice_index = st.selectbox(
            "Voice",
            range(len(voice_labels)),
            format_func=lambda index: voice_labels[index],
        )
        selected_voice_id = voices[selected_voice_index]["id"]
    else:
        st.info("No local pyttsx3 voices were detected. The app will try gTTS.")
        selected_voice_id = None

    rate = st.slider("Speech rate (WPM)", min_value=50, max_value=300, value=150)
    volume = st.slider("Volume", min_value=0.0, max_value=1.0, value=1.0)
    language = st.text_input(
        "Fallback gTTS language/accent code",
        value="en",
        help="Used only if pyttsx3 fails. Examples: en, en-uk, hi, es, fr.",
    )

    if st.button("🎙️ Generate Speech"):
        try:
            generated_path = engine.speak(
                text=text,
                voice_id=selected_voice_id,
                rate=rate,
                volume=volume,
                save_path=OUTPUT_PATH,
                lang=language,
            )
            st.success(f"Speech generated successfully: {generated_path.name}")

            if generated_path.suffix == ".wav":
                st.audio("output/result.wav")
            else:
                st.audio(str(generated_path))
                st.info("pyttsx3 was unavailable, so audio was saved as MP3 via gTTS.")
        except Exception as error:
            st.error(f"Could not generate speech: {error}")


if __name__ == "__main__":
    main()
