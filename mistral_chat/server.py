"""Flask web server for the chat UI."""

from __future__ import annotations

from typing import Any

from flask import Flask, Response, jsonify, render_template, request

from formatter import format_response
from logger import get_logger
from mistral_client import ChatServiceError, History, MistralChat


app = Flask(__name__)
logger = get_logger(__name__)


try:
    chat_client = MistralChat()
except ChatServiceError as exc:
    chat_client = None
    logger.error("Chat client startup failed: %s", exc)


@app.after_request
def add_cors_headers(response: Response) -> Response:
    """Allow browser fetch calls without adding another dependency."""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


@app.before_request
def log_request() -> None:
    logger.info("%s %s", request.method, request.path)


@app.route("/", methods=["GET"])
def index() -> str:
    return render_template("index.html")


@app.route("/chat", methods=["POST", "OPTIONS"])
def chat() -> tuple[Response, int] | Response:
    if request.method == "OPTIONS":
        return jsonify({}), 204

    if chat_client is None:
        return jsonify({"error": "Chat client is not configured. Check your .env file."}), 500

    payload: dict[str, Any] = request.get_json(silent=True) or {}
    message = str(payload.get("message", "")).strip()
    history = payload.get("history", [])
    format_mode = str(payload.get("format", "plain"))

    if not message:
        return jsonify({"error": "Message is required."}), 400

    if not isinstance(history, list):
        return jsonify({"error": "History must be a list."}), 400

    try:
        typed_history: History = [
            {"role": str(item["role"]), "content": str(item["content"])}
            for item in history
            if isinstance(item, dict) and "role" in item and "content" in item
        ]
        reply = chat_client.chat(message, typed_history)
        return jsonify({"reply": format_response(reply, format_mode), "history": typed_history})
    except ChatServiceError as exc:
        logger.error("Chat request failed: %s", exc)
        return jsonify({"error": str(exc)}), 503
    except Exception as exc:
        logger.exception("Unhandled server error.")
        return jsonify({"error": "Unexpected server error."}), 500


@app.route("/clear", methods=["POST", "OPTIONS"])
def clear() -> tuple[Response, int] | Response:
    if request.method == "OPTIONS":
        return jsonify({}), 204

    logger.info("Chat history cleared from web client.")
    return jsonify({"history": []})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
