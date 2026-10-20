# FastAPI + Streamlit Streaming Chat

A ChatGPT-like web app that streams responses in real time. FastAPI handles the backend API and OpenAI integration; Streamlit renders the chat UI.

---

## Project Structure

```
fastapi-streamlit-chat/
├── backend/
│   ├── main.py           # FastAPI app with /chat streaming endpoint
│   ├── requirements.txt  # Backend dependencies
│   ├── .env              # Your API key (never commit this)
│   └── .env.example      # Template for .env
└── frontend/
    ├── app.py            # Streamlit chat UI
    └── requirements.txt  # Frontend dependencies
```

---

## Prerequisites

- Python 3.10+
- An [OpenAI API key](https://platform.openai.com/api-keys)

---

## Setup

### 1. Add your API key

Open `backend/.env` and replace the placeholder with your real key:

```
OPENAI_API_KEY=sk-...
```

### 2. Install backend dependencies

```bash
cd fastapi-streamlit-chat/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Install frontend dependencies

```bash
cd fastapi-streamlit-chat/frontend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Running the App

Open **two terminals**.

**Terminal 1 — Backend:**

```bash
cd fastapi-streamlit-chat/backend
source .venv/bin/activate
uvicorn main:app --reload --port 8000
```

**Terminal 2 — Frontend:**

```bash
cd fastapi-streamlit-chat/frontend
source .venv/bin/activate
streamlit run app.py
```

Then open **http://localhost:8501** in your browser.

---

## Features

- Real-time streaming responses (token by token)
- Full conversation history sent with every request
- Model selector: `gpt-4o`, `gpt-4o-mini`, `gpt-3.5-turbo`
- API key input in sidebar (or loaded from `.env`)
- Clear conversation button
- Error handling for invalid keys and network failures

---

## API Docs (Swagger)

With the backend running, open:

- **http://localhost:8000/docs** — Swagger UI (interactive, test endpoints directly in the browser)
- **http://localhost:8000/redoc** — ReDoc (clean read-only reference)

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/models` | Returns list of available models |
| POST | `/chat` | Streams a chat completion via SSE |

**POST /chat request body:**

```json
{
  "messages": [{"role": "user", "content": "Hello!"}],
  "model": "gpt-4o",
  "api_key": "sk-..."
}
```

---

## Security Notes

- Never commit your `.env` file — it is excluded by `.gitignore`
- API keys are never stored server-side; they are used per request only
- Do not share your API key in chat, email, or version control
- For production: store the key in a server environment variable and remove the UI key input
