# Technical Internship Assignment — TTS & AI API Integration

This repository contains the work for a two-part technical internship assignment. Each task is self-contained in its own folder with its own setup instructions, dependencies, and README.

---

## 📁 Repository Structure

.
├── tts_project/          # Task 1: Text-to-Speech Implementation
│   └── README.md
├── mistral_chat/         # Task 2: DeepSeek / Mistral API Integration
│   └── README.md
└── README.md             # ← You are here

---

## Task 1 — Text-to-Speech (TTS) Implementation

**Folder:** `tts_project/`

A Python-based Text-to-Speech system that converts user-provided text into spoken audio, with a fully interactive web interface built using Streamlit.

### What it does

- Converts any text input into speech and saves it as an audio file
- Supports **voice selection** — choose from available system voices (male/female, language variants)
- Offers **speech rate and volume control** via interactive sliders
- Validates text input to handle special characters, empty inputs, and length limits
- Provides a **Streamlit web app** where users can type text, configure settings, and play back the generated audio directly in the browser

### Tech Stack

| Purpose | Library |
|---|---|
| Core TTS engine | `pyttsx3` |
| Accent / language fallback | `gTTS` |
| Web interface | `Streamlit` |
| Unit testing | `pytest` |

> For setup and usage, refer to [`tts_project/README.md`](./tts_project/README.md)

---

## Task 2 — DeepSeek / Mistral API Integration

**Folder:** `mistral_chat/`

A Python-based AI chat application powered by the **Mistral API**, available both as a command-line tool and a browser-based chat interface.

### What it does

- Connects to the Mistral API and handles multi-turn conversations with full context memory
- Supports a **CLI chat mode** where users can have extended sessions, switch response formats, and clear history
- Formats AI responses as plain text, bullet points, or numbered lists based on user preference
- Implements **robust error handling** — API timeouts, rate limits, and connection failures are caught, logged, and surfaced with friendly messages
- All errors are written to a persistent log file for debugging
- Includes a **web-based chat interface** (HTML/CSS/JS + Flask) with a clean chat bubble UI, typing indicators, and real-time responses via `fetch()`

### Tech Stack

| Purpose | Library / Tool |
|---|---|
| AI API | Mistral API (`mistralai` SDK) |
| CLI interface | Python `logging`, standard I/O |
| Web backend | `Flask` |
| Web frontend | HTML, CSS, Vanilla JS |
| Config management | `python-dotenv` |

> For setup and usage, refer to [`mistral_chat/README.md`](./mistral_chat/README.md)

---

## General Setup

Each task has its own `requirements.txt` and virtual environment. It is recommended to set them up independently.

```bash
# Task 1
cd tts_project
pip install -r requirements.txt

# Task 2
cd mistral_chat
pip install -r requirements.txt