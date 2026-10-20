import json
import os
import requests
import streamlit as st

API_BASE = "http://localhost:8000"

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="AI Chat", page_icon="💬", layout="wide")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Settings")

    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        value=os.getenv("OPENAI_API_KEY", ""),
        placeholder="sk-...",
        help="Your key is never stored — it's sent directly to the API per request.",
    )

    # Fetch model list from backend; fall back to defaults if backend is offline
    try:
        available_models = requests.get(f"{API_BASE}/models", timeout=2).json()["models"]
    except Exception:
        available_models = ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]

    model = st.selectbox("Model", available_models)

    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("Backend: `uvicorn main:app --reload --port 8000`")

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Render existing conversation ──────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Chat input ────────────────────────────────────────────────────────────────
user_input = st.chat_input(
    "Message AI..." if api_key else "Enter your API key in the sidebar first",
    disabled=not api_key,
)

if user_input:
    # Display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Build history for the API call
    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

    # Stream assistant response
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        error_msg = None

        try:
            resp = requests.post(
                f"{API_BASE}/chat",
                json={"messages": history, "model": model, "api_key": api_key},
                stream=True,
                timeout=60,
            )
            resp.raise_for_status()

            buffer = ""
            for raw_bytes in resp.iter_content(chunk_size=None):
                buffer += raw_bytes.decode("utf-8")
                # SSE events are separated by double newlines
                while "\n\n" in buffer:
                    event, buffer = buffer.split("\n\n", 1)
                    for line in event.splitlines():
                        if not line.startswith("data: "):
                            continue
                        payload = line[6:].strip()
                        if payload == "[DONE]":
                            break
                        data = json.loads(payload)
                        if "error" in data:
                            error_msg = data["error"]
                            break
                        if "content" in data:
                            full_response += data["content"]
                            placeholder.markdown(full_response + "▋")
                    if error_msg:
                        break

        except requests.exceptions.ConnectionError:
            error_msg = "Cannot reach the backend. Is `uvicorn main:app --reload` running on port 8000?"
        except requests.exceptions.HTTPError as e:
            try:
                detail = resp.json().get("detail", str(e))
            except Exception:
                detail = str(e)
            error_msg = f"API error: {detail}"
        except Exception as e:
            error_msg = str(e)

        if error_msg:
            placeholder.error(error_msg)
            full_response = f"⚠️ {error_msg}"
        else:
            placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
