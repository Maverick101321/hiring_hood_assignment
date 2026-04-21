"""Text-to-speech engine abstraction with pyttsx3 and gTTS fallback."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pyttsx3
from gtts import gTTS

from validator import validate_text


OUTPUT_DIR = Path(__file__).resolve().parent / "output"


class TTSEngine:
    """Generate speech using local pyttsx3 voices, with online gTTS fallback."""

    def __init__(self) -> None:
        """Initialize pyttsx3 and cache all voices available on this machine."""
        self.engine: Any | None = None
        self.voices: list[Any] = []

        try:
            self.engine = pyttsx3.init()
            self.voices = list(self.engine.getProperty("voices") or [])
        except Exception:
            # Some headless systems cannot initialize pyttsx3. The app can still
            # generate speech through gTTS when network access is available.
            self.engine = None
            self.voices = []

    def list_voices(self) -> list[dict[str, str]]:
        """Return installed voice metadata in a UI-friendly format."""
        voices: list[dict[str, str]] = []

        for voice in self.voices:
            voice_id = str(getattr(voice, "id", ""))
            voices.append(
                {
                    "id": voice_id,
                    "name": str(getattr(voice, "name", voice_id or "Unknown")),
                    "gender": str(getattr(voice, "gender", "Unknown") or "Unknown"),
                    "language": self._format_languages(
                        getattr(voice, "languages", []) or []
                    ),
                }
            )

        return voices

    def speak(
        self,
        text: str,
        voice_id: str | None = None,
        rate: int = 150,
        volume: float = 1.0,
        save_path: str | Path = OUTPUT_DIR / "result.wav",
        lang: str = "en",
    ) -> Path:
        """Validate text, generate speech, and save it to the output folder.

        Args:
            text: User text to synthesize.
            voice_id: pyttsx3 voice id selected by the user.
            rate: Speech rate in words per minute.
            volume: Volume between 0.0 and 1.0.
            save_path: Target output file. pyttsx3 writes WAV; gTTS fallback
                writes an MP3 with the same stem.
            lang: Language/accent code used by the gTTS fallback.

        Returns:
            The actual generated audio path. This is ``save_path`` for pyttsx3
            and a sibling ``.mp3`` path if gTTS fallback was needed.
        """
        cleaned_text = validate_text(text)
        output_path = self._resolve_output_path(save_path, suffix=".wav")

        try:
            if self.engine is None:
                raise RuntimeError("pyttsx3 engine is not available")

            if voice_id:
                self.engine.setProperty("voice", voice_id)
            self.engine.setProperty("rate", int(rate))
            self.engine.setProperty("volume", max(0.0, min(1.0, float(volume))))

            self.engine.save_to_file(cleaned_text, str(output_path))
            self.engine.runAndWait()

            if not output_path.exists():
                raise RuntimeError("pyttsx3 did not create an audio file")

            return output_path
        except Exception:
            fallback_path = output_path.with_suffix(".mp3")
            tts = gTTS(text=cleaned_text, lang=lang)
            tts.save(str(fallback_path))
            return fallback_path

    @staticmethod
    def _format_languages(languages: list[Any]) -> str:
        """Normalize pyttsx3 language values, which differ by platform."""
        formatted: list[str] = []

        for language in languages:
            if isinstance(language, bytes):
                formatted.append(language.decode("utf-8", errors="ignore").strip())
            else:
                formatted.append(str(language).strip())

        return ", ".join(filter(None, formatted)) or "Unknown"

    @staticmethod
    def _resolve_output_path(save_path: str | Path, suffix: str) -> Path:
        """Keep generated audio files inside the project output directory."""
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        requested_path = Path(save_path)
        if not requested_path.is_absolute():
            requested_path = OUTPUT_DIR / requested_path.name

        if requested_path.parent.resolve() != OUTPUT_DIR.resolve():
            requested_path = OUTPUT_DIR / requested_path.name

        return requested_path.with_suffix(suffix)
