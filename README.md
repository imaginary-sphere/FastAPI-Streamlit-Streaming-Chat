# Nova Chat

A ChatGPT-like web app that streams AI responses in real time. Built with FastAPI (backend + UI), served as a single service.

**Live:** https://nova-chat.onrender.com

---

## Project Structure

```
nova-chat/
├── app/
│   ├── main.py           # FastAPI app — serves UI and streaming /chat endpoint
│   ├── requirements.txt  # Dependencies
│   ├── .env              # Your API key (never commit this)
│   ├── .env.example      # Template for .env
│   └── static/
│       └── index.html    # Chat UI (HTML/CSS/JS)
└── .gitignore
```

---

## Prerequisites

- Python 3.10+
- An [OpenAI API key](https://platform.openai.com/api-keys)

---

## Local Setup

### 1. Add your API key

```bash
cp app/.env.example app/.env
```

Edit `app/.env`:

```
OPENAI_API_KEY=sk-...
```

### 2. Install dependencies and run

```bash
cd app
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Open **http://localhost:8000** — the chat UI loads directly.

---

## Features

- Real-time streaming responses (token by token)
- Full conversation history per session
- Model selector: `gpt-4o`, `gpt-4o-mini`, `gpt-3.5-turbo`
- Clear conversation button
- Error messages displayed inline if something goes wrong

---

## API Endpoints

| Method | Path      | Description                          |
|--------|-----------|--------------------------------------|
| GET    | `/`       | Serves the Nova Chat UI              |
| GET    | `/models` | Returns list of available models     |
| POST   | `/chat`   | Streams a chat completion via SSE    |
| GET    | `/docs`   | Swagger UI (interactive API testing) |

**POST /chat request body:**

```json
{
  "messages": [{"role": "user", "content": "Hello!"}],
  "model": "gpt-4o"
}
```

---

## Deployment (Render)

1. Push to GitHub (`imaginary-sphere/nova-chat`)
2. Render → New Web Service → connect repo
3. Set **Root Directory**: `app`
4. **Build command**: `pip install -r requirements.txt`
5. **Start command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add environment variable: `OPENAI_API_KEY` = your key
7. Deploy — Render auto-deploys on every push to `main`

---

## Security

- `.env` is excluded by `.gitignore` — never commit it
- API key lives only on the server (set as a Render environment variable)
- Key is never exposed to the browser or sent in API responses
