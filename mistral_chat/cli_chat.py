"""Command-line chat interface."""

from __future__ import annotations

import itertools
import threading
import time
from pathlib import Path

from formatter import format_response
from logger import get_logger
from mistral_client import ChatServiceError, History, MistralChat


logger = get_logger(__name__)
SESSION_LOG = Path(__file__).resolve().parent / "logs" / "session.log"
VALID_FORMATS = {"plain", "bullets", "numbered", "auto"}


class ThinkingIndicator:
    """Tiny terminal spinner shown while the API call is in progress."""

    def __init__(self) -> None:
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        self._running = True
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=0.2)
        print("\r", end="", flush=True)

    def _spin(self) -> None:
        for frame in itertools.cycle(("...thinking   ", "...thinking.  ", "...thinking.. ", "...thinking...")):
            if not self._running:
                break
            print(f"\r{frame}", end="", flush=True)
            time.sleep(0.25)


def save_session(history: History) -> None:
    """Persist the current session history to logs/session.log."""
    SESSION_LOG.parent.mkdir(parents=True, exist_ok=True)
    with SESSION_LOG.open("a", encoding="utf-8") as file:
        file.write("\n--- New Session ---\n")
        for item in history:
            file.write(f"{item['role'].upper()}: {item['content']}\n")


def main() -> None:
    """Run the interactive CLI chat loop."""
    print("Welcome to Mistral Chat.")
    print("Commands: exit, clear, format [plain|bullets|numbered|auto]")

    try:
        chat_client = MistralChat()
    except ChatServiceError as exc:
        logger.error("Startup failed: %s", exc)
        print(f"Error: {exc}")
        return

    history: History = []
    format_mode = "plain"

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() == "exit":
            save_session(history)
            print("Session saved to logs/session.log. Goodbye.")
            break

        if user_input.lower() == "clear":
            history.clear()
            print("Chat history cleared.")
            continue

        if user_input.lower().startswith("format "):
            requested_format = user_input.split(maxsplit=1)[1].lower()
            if requested_format in VALID_FORMATS:
                format_mode = requested_format
                print(f"Format mode set to {format_mode}.")
            else:
                print("Use one of: plain, bullets, numbered, auto.")
            continue

        indicator = ThinkingIndicator()
        indicator.start()
        try:
            reply = chat_client.chat(user_input, history)
        except ChatServiceError as exc:
            logger.error("Chat failed: %s", exc)
            print(f"\nError: {exc}")
            continue
        finally:
            indicator.stop()

        print(f"\nAI: {format_response(reply, format_mode)}")


if __name__ == "__main__":
    main()
