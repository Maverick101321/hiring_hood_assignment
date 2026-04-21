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
    st.write("Type some text and generate browser-friendly speech audio.")

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
        st.caption("Local voice selection is used only if gTTS is unavailable.")
    else:
        st.info("No local pyttsx3 voices were detected. gTTS remains the primary engine.")
        selected_voice_id = None

    rate = st.slider("Speech rate (WPM)", min_value=50, max_value=300, value=150)
    volume = st.slider("Volume", min_value=0.0, max_value=1.0, value=1.0)
    language = st.text_input(
        "gTTS language/accent code",
        value="en",
        help="Primary engine setting. Examples: en, en-uk, hi, es, fr.",
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
            audio_bytes = generated_path.read_bytes()

            if generated_path.suffix == ".wav":
                st.audio(audio_bytes, format="audio/wav")
                st.info("gTTS was unavailable, so local pyttsx3 fallback created a WAV file.")
            else:
                st.audio(audio_bytes, format="audio/mpeg")
                st.info("Audio was generated with gTTS and saved as MP3 for browser playback.")
        except Exception as error:
            st.error(f"Could not generate speech: {error}")


if __name__ == "__main__":
    main()
