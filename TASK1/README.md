# LinguaShift — Language Translation Tool
**Code Alpha Internship · Task 1**

A full-stack language translation web app built with Python Flask and the (unofficial) Google Translate API — no API key required.

---

## Features
- **80+ languages** with auto-detect for the source
- **Swap** source ↔ target languages (and their text) in one click
- **Copy** translated text to clipboard
- **Text-to-Speech** on both source and translated panels
- **Quick-pick chips** for common target languages
- **Ctrl + Enter** keyboard shortcut to translate
- Character counter (max 5 000 chars)
- Fully responsive — works on mobile

---

## Project Structure
```
translation-tool/
├── app.py               ← Flask backend + translation logic
├── requirements.txt
├── templates/
│   └── index.html       ← Jinja2 HTML template
└── static/
    ├── css/style.css    ← Styling
    └── js/main.js       ← Frontend logic
```

---

## Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the server
```bash
python app.py
```

### 3. Open in browser
```
http://127.0.0.1:5000
```

---

## How it works
1. User types text and selects source / target languages.
2. On clicking **Translate** (or pressing Ctrl+Enter), the frontend sends a `POST /translate` JSON request to Flask.
3. Flask calls the public Google Translate endpoint (`translate.googleapis.com`) — no API key needed.
4. The translated text is returned as JSON and displayed on screen.
5. The user can **copy** the result or hear it via the browser's **Web Speech API**.

---

## Optional Upgrade — Official Google Translate API
To use the official API (higher rate limits, SLA):
```bash
pip install google-cloud-translate
```
Then replace the `google_translate()` function in `app.py` with the `google.cloud.translate_v2` client and set your `GOOGLE_APPLICATION_CREDENTIALS` env variable.

---

## Tech Stack
| Layer    | Technology |
|----------|-----------|
| Backend  | Python 3 · Flask |
| Translation | Google Translate (unofficial endpoint) |
| Frontend | Vanilla HTML / CSS / JS |
| TTS      | Web Speech API (browser built-in) |
