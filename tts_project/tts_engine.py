"""Text-to-speech engine abstraction with pyttsx3 and gTTS fallback."""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import wave
from typing import Any

import pyttsx3

from validator import validate_text


OUTPUT_DIR = Path(__file__).resolve().parent / "output"


class TTSEngine:
    """Generate speech using local pyttsx3 voices, with online gTTS fallback."""

    def __init__(self) -> None:
        """Initialize pyttsx3 and cache all voices available on this machine."""
        self.voices: list[Any] = []

        try:
            engine = pyttsx3.init()
            self.voices = list(engine.getProperty("voices") or [])
            engine.stop()
        except Exception:
            # Some headless systems cannot initialize pyttsx3. The app can still
            # generate speech through gTTS when network access is available.
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
        fallback_path = output_path.with_suffix(".mp3")

        try:
            output_path.unlink(missing_ok=True)
            fallback_path.unlink(missing_ok=True)

            engine = pyttsx3.init()
            if voice_id:
                engine.setProperty("voice", voice_id)
            engine.setProperty("rate", int(rate))
            engine.setProperty("volume", max(0.0, min(1.0, float(volume))))

            engine.save_to_file(cleaned_text, str(output_path))
            engine.runAndWait()
            engine.stop()

            if not output_path.exists():
                raise RuntimeError("pyttsx3 did not create an audio file")

            self._normalize_audio_file(output_path)
            self._validate_audio_output(output_path)
            return output_path
        except Exception:
            from gtts import gTTS

            fallback_path.unlink(missing_ok=True)
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

    @staticmethod
    def _normalize_audio_file(audio_path: Path) -> None:
        """Convert mislabeled pyttsx3 output into a browser-playable WAV file."""
        header = audio_path.read_bytes()[:12]
        is_aiff = header.startswith(b"FORM") and header[8:12] in {b"AIFF", b"AIFC"}

        if not is_aiff:
            return

        afconvert_path = shutil.which("afconvert")
        if afconvert_path is None:
            raise RuntimeError(
                "pyttsx3 produced AIFF audio, but 'afconvert' is unavailable to convert it."
            )

        converted_path = audio_path.with_name(f"{audio_path.stem}_converted.wav")

        try:
            subprocess.run(
                [
                    afconvert_path,
                    "-f",
                    "WAVE",
                    "-d",
                    "LEI16",
                    str(audio_path),
                    str(converted_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            converted_path.replace(audio_path)
        finally:
            converted_path.unlink(missing_ok=True)

    @staticmethod
    def _validate_audio_output(audio_path: Path) -> None:
        """Reject empty or malformed WAV files so the caller can fall back."""
        if audio_path.stat().st_size < 1024:
            raise RuntimeError("Generated audio file is unexpectedly small.")

        with wave.open(str(audio_path), "rb") as wav_file:
            frame_rate = wav_file.getframerate()
            frame_count = wav_file.getnframes()

        if frame_rate <= 0 or frame_count <= 0:
            raise RuntimeError("Generated audio file contains no playable frames.")
