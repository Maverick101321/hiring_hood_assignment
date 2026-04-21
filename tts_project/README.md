# TTS Project

A small Python text-to-speech project with input validation, local speech generation through `pyttsx3`, online fallback through `gTTS`, a Streamlit web interface, and pytest coverage for text validation.

## Setup

```bash
pip install -r requirements.txt
```

## Run The Streamlit App

From inside the `tts_project/` directory:

```bash
streamlit run app.py
```

Enter text, select a local voice if available, choose the speech rate and volume, then click **🎙️ Generate Speech**. Audio is saved in the `output/` folder and played directly in the browser.

## Run Tests

From inside the `tts_project/` directory:

```bash
pytest tests/
```

## File Guide

- `tts_engine.py`: Defines `TTSEngine`, lists installed pyttsx3 voices, generates `.wav` output locally, and falls back to gTTS `.mp3` output if pyttsx3 fails.
- `validator.py`: Defines `validate_text()`, which rejects empty input, strips whitespace, removes unsupported TTS characters, trims excessive symbol bursts, and truncates text longer than 5000 characters with a warning.
- `app.py`: Streamlit web app with text input, voice selection, speech rate and volume controls, and browser audio playback.
- `tests/test_validator.py`: Pytest unit tests for empty input, whitespace input, special character cleanup, normal cleanup, and truncation behavior.
- `requirements.txt`: Python dependencies needed for the app, TTS engines, audio playback support, and tests.
- `output/`: Destination folder for generated audio files.
