"""
Plain Speak — Gemma 4 client.

Thin wrapper around the Ollama Python client. We keep this small and
focused so swapping inference backends (Ollama → LiteRT → llama.cpp →
cloud) only touches this file.

Supported models (May 2026):
  - gemma4:e2b    ~2GB RAM, edge-class, text only
  - gemma4:e4b    ~4GB RAM, edge-class, text only
  - gemma4:9b     ~9GB RAM, vision + tool calling (recommended default)
  - gemma4:26b    bigger, MoE with 4B active
  - gemma4:31b    largest, server-class

We default to gemma4:9b because it has the multimodal capability that
makes Plain Speak's "snap a photo of a letter" UX possible.
"""

from __future__ import annotations

from typing import Generator, Optional

DEFAULT_MODEL = "gemma4:e2b"

# Generation params tuned for factual, structured output. Low temperature
# because we explicitly do not want creative additions to government docs.
GENERATION_OPTIONS = {
    "temperature": 0.2,
    "top_p": 0.9,
    "num_predict": 1500,  # plenty for the eight-section template
}


def _client():
    """Lazy-import Ollama so the module loads even if ollama is missing
    (e.g., during unit tests that monkey-patch this function)."""
    import ollama
    return ollama


def list_local_models() -> list[str]:
    """Return tags of models the local Ollama server has pulled."""
    try:
        resp = _client().list()
    except Exception:
        return []
    # The Ollama client returns either a dict or an object depending on
    # version. Handle both shapes defensively.
    models = getattr(resp, "models", None) or resp.get("models", [])
    out = []
    for m in models:
        name = getattr(m, "model", None) or m.get("model") or m.get("name")
        if name:
            out.append(name)
    return out


def explain_document(
    *,
    document_text: str,
    image_bytes: Optional[bytes],
    system_prompt: str,
    user_message: str,
    model: str = DEFAULT_MODEL,
) -> Generator[str, None, None]:
    """Stream a plain-language explanation token-by-token.

    Yields incremental text chunks so the UI can render progressively —
    important for the demo: judges see Gemma 4 thinking in real time
    rather than waiting 15 seconds for a wall of text.
    """
    ollama = _client()

    user_turn = {"role": "user", "content": user_message}
    if image_bytes is not None:
        # Ollama's Python client accepts a list of image bytes/paths per
        # message. Gemma 4 vision models pick them up automatically.
        user_turn["images"] = [image_bytes]

    messages = [
        {"role": "system", "content": system_prompt},
        user_turn,
    ]

    stream = ollama.chat(
        model=model,
        messages=messages,
        stream=True,
        options=GENERATION_OPTIONS,
    )
    for chunk in stream:
        # Ollama yields {'message': {'content': '...'}, ...}
        msg = chunk.get("message") if isinstance(chunk, dict) else getattr(chunk, "message", None)
        if not msg:
            continue
        content = msg.get("content") if isinstance(msg, dict) else getattr(msg, "content", "")
        if content:
            yield content


def followup(
    *,
    history: list[dict],
    system_prompt: str,
    model: str = DEFAULT_MODEL,
) -> Generator[str, None, None]:
    """Stream a follow-up reply given a chat history."""
    ollama = _client()
    messages = [{"role": "system", "content": system_prompt}] + history
    stream = ollama.chat(
        model=model,
        messages=messages,
        stream=True,
        options=GENERATION_OPTIONS,
    )
    for chunk in stream:
        msg = chunk.get("message") if isinstance(chunk, dict) else getattr(chunk, "message", None)
        if not msg:
            continue
        content = msg.get("content") if isinstance(msg, dict) else getattr(msg, "content", "")
        if content:
            yield content
