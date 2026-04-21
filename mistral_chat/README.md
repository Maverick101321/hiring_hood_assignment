# Mistral Chat

A small AI chat app with a CLI and Flask web UI. It uses the Mistral SDK by default and also supports DeepSeek as an optional provider through its chat completions API.

## Setup

```bash
cd mistral_chat
pip install -r requirements.txt
```

Add your keys to `.env`:

```bash
MISTRAL_API_KEY=your_real_mistral_key
DEEPSEEK_API_KEY=your_real_deepseek_key
CHAT_PROVIDER=mistral
```

Use `CHAT_PROVIDER=deepseek` to switch to DeepSeek.

## Run The CLI

```bash
python cli_chat.py
```

Commands:

- `exit` saves the session to `logs/session.log` and quits.
- `clear` resets conversation history.
- `format plain`, `format bullets`, `format numbered`, or `format auto` changes reply formatting.

## Run The Web App

```bash
python server.py
```

Open [http://localhost:5000](http://localhost:5000).

## Files

- `mistral_client.py` loads `.env`, initializes the selected AI provider, sends multi-turn chat history, logs provider errors, and retries transient failures with exponential backoff.
- `formatter.py` formats replies as plain text, bullets, numbered lists, or automatic list-preserving output.
- `cli_chat.py` provides the terminal chat loop, command handling, spinner, history, formatting, and session logging.
- `server.py` serves the Flask app, exposes `/chat` and `/clear`, handles CORS, validates JSON, and logs requests and errors.
- `logger.py` configures shared logging to console and `logs/errors.log`.
- `templates/index.html` contains the web chat layout.
- `static/script.js` sends messages with `fetch()`, maintains local history, displays typing state, handles errors, and updates the chat without page reloads.
- `static/style.css` provides the responsive chat design with bubbles, fixed header, fixed input bar, hover states, and smooth scrolling.
- `logs/` stores runtime logs and saved CLI sessions.

## Features

- Multi-turn conversation history in CLI and browser.
- Mistral model `mistral-large-latest`.
- Optional DeepSeek provider.
- Friendly error messages with detailed logs.
- Retry behavior for transient connection, rate limit, and server-side failures.
- Smooth web chat experience powered by `fetch()` with no page reloads.
