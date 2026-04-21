"""AI chat clients for Mistral and DeepSeek."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Any

from dotenv import load_dotenv
from mistralai.client import Mistral

from logger import get_logger


try:
    from mistralai.client import APIConnectionError, APIStatusError, RateLimitError
except ImportError:  # pragma: no cover - keeps compatibility across SDK versions.
    class APIConnectionError(ConnectionError):  # type: ignore[no-redef]
        """Fallback when SDK-specific exceptions are unavailable."""

    class APIStatusError(Exception):  # type: ignore[no-redef]
        """Fallback when SDK-specific exceptions are unavailable."""

    class RateLimitError(Exception):  # type: ignore[no-redef]
        """Fallback when SDK-specific exceptions are unavailable."""


History = list[dict[str, str]]
logger = get_logger(__name__)


class ChatServiceError(Exception):
    """Friendly application-level exception for AI provider failures."""


class MistralChat:
    """Chat wrapper that supports Mistral by default and DeepSeek as an option."""

    def __init__(self, provider: str | None = None) -> None:
        load_dotenv()
        self.provider = (provider or os.getenv("CHAT_PROVIDER", "mistral")).strip().lower()
        self.model = "mistral-large-latest"
        self.deepseek_model = "deepseek-chat"
        self.client: Mistral | None = None

        if self.provider == "mistral":
            api_key = os.getenv("MISTRAL_API_KEY")
            if not api_key or api_key == "your_key_here":
                raise ChatServiceError("Please add your Mistral API key to .env.")
            self.client = Mistral(api_key=api_key)
            return

        if self.provider == "deepseek":
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key or api_key == "your_deepseek_key_here":
                raise ChatServiceError("Please add your DeepSeek API key to .env.")
            self.deepseek_api_key = api_key
            return

        raise ChatServiceError("Unknown provider. Use 'mistral' or 'deepseek'.")

    def chat(self, user_message: str, history: History) -> str:
        """Append a user message, call the selected provider, and return the reply."""
        if not user_message.strip():
            raise ChatServiceError("Please enter a message before sending.")

        history.append({"role": "user", "content": user_message})

        for attempt in range(3):
            try:
                if self.provider == "deepseek":
                    assistant_reply = self._chat_deepseek(history)
                else:
                    assistant_reply = self._chat_mistral(history)

                history.append({"role": "assistant", "content": assistant_reply})
                return assistant_reply
            except urllib.error.HTTPError as exc:
                if exc.code == 429 or 500 <= exc.code < 600:
                    self._handle_retryable_error(exc, attempt)
                    continue
                logger.exception("DeepSeek returned HTTP %s.", exc.code)
                raise ChatServiceError("DeepSeek rejected the request. Please try again.") from exc
            except (APIConnectionError, RateLimitError, urllib.error.URLError) as exc:
                self._handle_retryable_error(exc, attempt)
            except APIStatusError as exc:
                status_code = getattr(exc, "status_code", None)
                if status_code and 500 <= int(status_code) < 600:
                    self._handle_retryable_error(exc, attempt)
                    continue
                logger.exception("AI provider returned an API status error.")
                raise ChatServiceError("The AI service rejected the request. Please try again.") from exc
            except Exception as exc:
                logger.exception("Unexpected chat error.")
                raise ChatServiceError("Something went wrong while contacting the AI service.") from exc

        raise ChatServiceError("The AI service is busy. Please try again shortly.")

    def _chat_mistral(self, history: History) -> str:
        """Send the full conversation to Mistral and extract the first reply."""
        if self.client is None:
            raise ChatServiceError("Mistral client is not initialized.")

        response = self.client.chat.complete(model=self.model, messages=history)
        content = response.choices[0].message.content
        return str(content).strip()

    def _chat_deepseek(self, history: History) -> str:
        """Call DeepSeek's OpenAI-compatible chat endpoint with stdlib HTTP."""
        payload = json.dumps({"model": self.deepseek_model, "messages": history}).encode("utf-8")
        request = urllib.request.Request(
            "https://api.deepseek.com/chat/completions",
            data=payload,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.deepseek_api_key}",
                "Content-Type": "application/json",
            },
        )

        with urllib.request.urlopen(request, timeout=60) as response:
            data: dict[str, Any] = json.loads(response.read().decode("utf-8"))

        return str(data["choices"][0]["message"]["content"]).strip()

    def _handle_retryable_error(self, exc: BaseException, attempt: int) -> None:
        """Log transient failures and sleep with exponential backoff."""
        logger.warning("Transient AI provider error on attempt %s: %s", attempt + 1, exc)
        if attempt == 2:
            raise ChatServiceError("The AI service is temporarily unavailable. Please try again.") from exc

        time.sleep(2**attempt)
