"""
Plain Speak — a privacy-first document explainer for low-literacy readers.

Built for the Gemma 4 Good Hackathon (Digital Equity & Inclusivity track).

Usage:
    ollama pull gemma4:9b
    pip install -r requirements.txt
    python app.py
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

# Stay fully offline. Plain Speak's whole point is local-first — we
# disable Gradio analytics and HuggingFace Hub network calls before any
# import so Gradio cannot block startup waiting on the network. This
# also matters for users on restricted networks or behind firewalls.
os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

import gradio as gr

import document_loader
import gemma_client
import prompts

APP_TITLE = "Plain Speak"
APP_TAGLINE = (
    "Upload a confusing official document — Gemma 4 will explain it in plain "
    "English. Everything runs on your computer. Nothing leaves your device."
)

# Models we expose in the sidebar dropdown. The first is the default.
SUPPORTED_MODELS = [
    "gemma4:e2b",  # tiny edge variant — most accessible, our default
    "gemma4:e4b",  # edge, slightly larger
    "gemma4:9b",   # vision + tool calling
    "gemma4:26b",  # MoE, bigger workstations
    "gemma4:31b",  # server class
]

SAMPLES_DIR = Path(__file__).parent / "samples"


# ---------------------------------------------------------------------------
# Core handlers
# ---------------------------------------------------------------------------

def explain(
    file_obj,
    pasted_text: str,
    model: str,
    use_vision: bool,
):
    """Stream a plain-language explanation. Yields (markdown, state) tuples
    so the chat box can keep the document context for follow-up Q&A."""

    # ---- 1. Figure out what the user gave us ------------------------------
    document_text = ""
    image_bytes = None
    source_label = ""

    if file_obj is not None:
        path = file_obj if isinstance(file_obj, str) else file_obj.name
        try:
            document_text, image_bytes, kind = document_loader.load_document(
                path, use_vision=use_vision
            )
            source_label = f"`{Path(path).name}` — read as **{kind}**"
        except Exception as e:
            yield f"### Couldn't read that file\n\n{e}", None, gr.update()
            return
    elif pasted_text.strip():
        document_text = pasted_text.strip()
        source_label = "Pasted text"
    else:
        yield (
            "### Nothing to explain yet\n\nUpload a file or paste text "
            "from your document, then click **Explain**.",
            None,
            gr.update(),
        )
        return

    # ---- 2. Build the prompt ---------------------------------------------
    if image_bytes is not None:
        user_message = prompts.build_vision_user_message()
    else:
        user_message = prompts.build_user_message(document_text)

    # ---- 3. Stream the answer --------------------------------------------
    accumulated = ""
    header = (
        f"**Source:** {source_label}  \n"
        f"**Model:** `{model}` (running locally via Ollama)\n\n---\n\n"
    )
    yield header + "_Reading the document..._", None, gr.update(visible=False)

    try:
        for chunk in gemma_client.explain_document(
            document_text=document_text,
            image_bytes=image_bytes,
            system_prompt=prompts.SYSTEM_PROMPT,
            user_message=user_message,
            model=model,
        ):
            accumulated += chunk
            yield (
                header + _prettify_sections(accumulated),
                None,
                gr.update(visible=False),
            )
    except Exception as e:
        yield (
            header + f"### Something went wrong calling the model\n\n"
            f"`{e}`\n\n"
            "Check that Ollama is running (`ollama serve`) and the model is "
            f"pulled (`ollama pull {model}`).",
            None,
            gr.update(visible=False),
        )
        return

    # ---- 4. Save context for follow-up Q&A -------------------------------
    state = {
        "document_text": document_text or "(image-only document)",
        "explanation": accumulated,
        "model": model,
    }
    yield (
        header + _prettify_sections(accumulated),
        state,
        gr.update(visible=True),
    )


def _prettify_sections(raw: str) -> str:
    """Turn the eight ALL-CAPS section headers into Markdown ## headers
    with little icons. Pure cosmetic; keeps the demo looking sharp."""
    icons = {
        "WHAT THIS IS": "📄 What this is",
        "WHO SENT IT": "👤 Who sent it",
        "WHAT YOU NEED TO DO": "✅ What you need to do",
        "IMPORTANT DATES": "📅 Important dates",
        "MONEY INVOLVED": "💵 Money involved",
        "IF YOU IGNORE THIS": "⚠️ If you ignore this",
        "QUESTIONS TO ASK THEM": "❓ Questions to ask them",
        "PLAIN-ENGLISH SUMMARY": "📝 Plain-English summary",
    }
    out = raw
    for header, pretty in icons.items():
        # Match the header at line start, with optional trailing colon
        for variant in (f"{header}:", header):
            out = out.replace(variant, f"\n\n## {pretty}\n")
    return out.strip()


def ask_followup(question: str, history: list, state, model_dropdown: str):
    """Chatbot handler. Streams an answer grounded in the previous
    explanation + the original document text."""
    if not question.strip():
        return history, ""
    if not state:
        history = history + [
            {"role": "user", "content": question},
            {
                "role": "assistant",
                "content": "Please run **Explain** on a document first, "
                "then ask follow-up questions about it.",
            },
        ]
        return history, ""

    sys_prompt = prompts.FOLLOWUP_SYSTEM_PROMPT.format(
        prior_explanation=state["explanation"],
        document_text=state["document_text"][:8000],  # truncate to keep ctx sane
    )

    # Convert Gradio chat history into Ollama-style messages
    ollama_history: list[dict] = []
    for turn in history:
        ollama_history.append({"role": turn["role"], "content": turn["content"]})
    ollama_history.append({"role": "user", "content": question})

    # Add the user turn to the visible chat immediately
    history = history + [
        {"role": "user", "content": question},
        {"role": "assistant", "content": ""},
    ]
    yield history, ""

    accumulated = ""
    try:
        for chunk in gemma_client.followup(
            history=ollama_history,
            system_prompt=sys_prompt,
            model=model_dropdown,
        ):
            accumulated += chunk
            history[-1]["content"] = accumulated
            yield history, ""
    except Exception as e:
        history[-1]["content"] = f"_Error calling model:_ `{e}`"
        yield history, ""


def load_sample(sample_name: str):
    """Populate the textarea with one of the bundled mock documents so the
    demo recording does not require a real personal document."""
    if not sample_name or sample_name == "(none)":
        return ""
    path = SAMPLES_DIR / sample_name
    if not path.exists():
        return f"Sample not found: {sample_name}"
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

CSS = """
#header-bar { text-align: center; padding: 16px 0; }
#header-bar h1 { margin: 0; font-size: 32px; }
#header-bar p  { margin: 6px 0 0; color: #555; }
#privacy-badge {
    display: inline-block; background: #e8f5e9; color: #1b5e20;
    padding: 4px 12px; border-radius: 999px; font-weight: 600;
    font-size: 13px; margin-top: 8px;
}
.gradio-container { max-width: 1100px !important; }
"""


def build_ui() -> gr.Blocks:
    samples = ["(none)"] + sorted(
        p.name for p in SAMPLES_DIR.glob("*.txt")
    ) if SAMPLES_DIR.exists() else ["(none)"]

    with gr.Blocks(title=APP_TITLE, css=CSS, theme=gr.themes.Soft()) as demo:
        gr.HTML(
            f"""
            <div id="header-bar">
              <h1>{APP_TITLE}</h1>
              <p>{APP_TAGLINE}</p>
              <span id="privacy-badge">🔒 100% on-device · powered by Gemma 4</span>
            </div>
            """
        )

        with gr.Row():
            # -------- Left: input ------------------------------------------
            with gr.Column(scale=1):
                gr.Markdown("### 1. Give Plain Speak a document")
                file_in = gr.File(
                    label="Upload PDF or image",
                    file_types=[".pdf", ".png", ".jpg", ".jpeg", ".webp", ".txt"],
                    type="filepath",
                )
                gr.Markdown("…or paste the text:")
                text_in = gr.Textbox(
                    label="Pasted text",
                    placeholder="Paste the confusing document here…",
                    lines=8,
                )
                with gr.Row():
                    sample_dd = gr.Dropdown(
                        choices=samples,
                        value="(none)",
                        label="Or try a sample",
                        scale=2,
                    )
                    load_btn = gr.Button("Load sample", scale=1)

                gr.Markdown("### 2. Pick a model")
                model_dd = gr.Dropdown(
                    choices=SUPPORTED_MODELS,
                    value=SUPPORTED_MODELS[0],
                    label="Gemma 4 variant (must be pulled in Ollama)",
                )
                vision_cb = gr.Checkbox(
                    value=False,
                    label="Use vision for image uploads "
                    "(only enable if your model has vision, e.g. gemma4:9b — "
                    "otherwise OCR is used)",
                )

                explain_btn = gr.Button(
                    "Explain this in plain English", variant="primary", size="lg"
                )

            # -------- Right: output ----------------------------------------
            with gr.Column(scale=1):
                gr.Markdown("### 3. Plain-English explanation")
                output = gr.Markdown(
                    "_Your explanation will appear here._",
                    height=520,
                )
                state = gr.State(value=None)

                followup_box = gr.Group(visible=False)
                with followup_box:
                    gr.Markdown("### 4. Ask a follow-up question")
                    chat = gr.Chatbot(
                        type="messages",
                        height=240,
                        label="Conversation",
                    )
                    with gr.Row():
                        q_in = gr.Textbox(
                            placeholder="e.g. What happens if I can't pay by the deadline?",
                            scale=4,
                            show_label=False,
                        )
                        ask_btn = gr.Button("Ask", scale=1, variant="primary")

        gr.Markdown(
            "---\n"
            "**Disclaimer.** Plain Speak helps you *understand* documents. "
            "It is not a lawyer, doctor, or financial advisor. For decisions "
            "with serious consequences, talk to a qualified human."
        )

        # ---- Wire it up ---------------------------------------------------
        load_btn.click(load_sample, inputs=sample_dd, outputs=text_in)
        explain_btn.click(
            explain,
            inputs=[file_in, text_in, model_dd, vision_cb],
            outputs=[output, state, followup_box],
        )
        ask_btn.click(
            ask_followup,
            inputs=[q_in, chat, state, model_dd],
            outputs=[chat, q_in],
        )
        q_in.submit(
            ask_followup,
            inputs=[q_in, chat, state, model_dd],
            outputs=[chat, q_in],
        )

    return demo


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Plain Speak — local document explainer")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host")
    parser.add_argument("--port", type=int, default=7860, help="Bind port")
    parser.add_argument("--share", action="store_true", help="Create a public Gradio share link")
    args = parser.parse_args()

    demo = build_ui()
    demo.queue().launch(
        server_name=args.host,
        server_port=args.port,
        share=args.share,
        inbrowser=True,
        show_api=False,  # avoids a JSON-schema → Python-type bug on older Python
        show_error=True,
        quiet=False,
    )


if __name__ == "__main__":
    main()
