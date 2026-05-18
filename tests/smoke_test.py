"""
Smoke test for Plain Speak — runs WITHOUT a live Ollama daemon.

We stub gemma_client._client() with a fake that replays canned chunks,
then exercise the full request path:
    document_loader → prompts → gemma_client → app.explain()

What we're checking:
  1. Every module imports cleanly (catches typos, missing imports).
  2. document_loader correctly parses the bundled sample .txt files.
  3. prompts.build_user_message / build_vision_user_message produce sane
     strings that contain the document text and the right framing.
  4. gemma_client.explain_document() correctly assembles the messages
     and forwards them to the (stubbed) ollama client.
  5. The streamed concatenation is what we expect.

Run with:
    python tests/smoke_test.py
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import document_loader  # noqa: E402
import prompts          # noqa: E402
import gemma_client     # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PASS = "\033[92m✓\033[0m"
FAIL = "\033[91m✗\033[0m"
INFO = "\033[94mℹ\033[0m"

failures: list[str] = []

def check(label: str, condition: bool, detail: str = ""):
    if condition:
        print(f"  {PASS} {label}")
    else:
        print(f"  {FAIL} {label}  {detail}")
        failures.append(label)


# ---------------------------------------------------------------------------
# 1. Imports already happened above — if we got here, they succeeded.
# ---------------------------------------------------------------------------

print(f"\n{INFO} Section 1: imports")
check("document_loader importable", hasattr(document_loader, "load_document"))
check("prompts importable", hasattr(prompts, "SYSTEM_PROMPT"))
check("gemma_client importable", hasattr(gemma_client, "explain_document"))


# ---------------------------------------------------------------------------
# 2. Sample document loading
# ---------------------------------------------------------------------------

print(f"\n{INFO} Section 2: document_loader on bundled samples")

samples_dir = ROOT / "samples"
expected = ["medical_bill.txt", "irs_notice.txt", "eviction_notice.txt"]

for name in expected:
    path = samples_dir / name
    check(f"sample exists: {name}", path.exists())
    if path.exists():
        text, img, kind = document_loader.load_document(str(path), use_vision=False)
        check(f"  loads as text ({name})", kind == "text" and img is None and len(text) > 100,
              detail=f"kind={kind} len={len(text)} img={img is not None}")


# ---------------------------------------------------------------------------
# 3. Prompt construction
# ---------------------------------------------------------------------------

print(f"\n{INFO} Section 3: prompt builders")

doc_text = "Sample document text 12345"
user_msg = prompts.build_user_message(doc_text)
check("build_user_message contains document", doc_text in user_msg)
check("build_user_message contains template framing",
      "eight-section template" in user_msg or "DOCUMENT START" in user_msg)

vision_msg = prompts.build_vision_user_message()
check("build_vision_user_message non-empty", len(vision_msg) > 50)
check("vision message mentions image", "image" in vision_msg.lower())

# Format the followup prompt and make sure the placeholders get filled
followup = prompts.FOLLOWUP_SYSTEM_PROMPT.format(
    prior_explanation="EXP_TEST_TOKEN",
    document_text="DOC_TEST_TOKEN",
)
check("followup prompt fills prior_explanation", "EXP_TEST_TOKEN" in followup)
check("followup prompt fills document_text", "DOC_TEST_TOKEN" in followup)


# ---------------------------------------------------------------------------
# 4. gemma_client with a fake ollama client
# ---------------------------------------------------------------------------

print(f"\n{INFO} Section 4: gemma_client with stubbed Ollama")

# Build a fake module that pretends to be `ollama`.
captured = {}

class _FakeOllama:
    @staticmethod
    def chat(*, model, messages, stream, options):
        captured["model"] = model
        captured["messages"] = messages
        captured["stream"] = stream
        captured["options"] = options
        # Yield three chunks that look like the real ollama stream shape
        for piece in ["WHAT THIS IS\n", "A sample reply\n", "with three parts.\n"]:
            yield {"message": {"content": piece}}

    @staticmethod
    def list():
        return {"models": [{"model": "gemma4:9b"}, {"model": "gemma4:e4b"}]}

gemma_client._client = lambda: _FakeOllama  # type: ignore

# Text mode
chunks = list(gemma_client.explain_document(
    document_text="hello world",
    image_bytes=None,
    system_prompt=prompts.SYSTEM_PROMPT,
    user_message=prompts.build_user_message("hello world"),
    model="gemma4:9b",
))
combined = "".join(chunks)
check("text-mode streams chunks", len(chunks) == 3)
check("text-mode chunks concatenate cleanly", combined.startswith("WHAT THIS IS"))
check("text-mode forwards model", captured["model"] == "gemma4:9b")
check("text-mode has system+user turns", len(captured["messages"]) == 2)
check("text-mode user message contains document", "hello world" in captured["messages"][1]["content"])
check("text-mode does NOT attach images", "images" not in captured["messages"][1])
check("text-mode requests streaming", captured["stream"] is True)
check("text-mode sets low temperature", captured["options"]["temperature"] <= 0.3)

# Vision mode
captured.clear()
list(gemma_client.explain_document(
    document_text="",
    image_bytes=b"\x89PNG\r\n\x1a\nFAKEBYTES",
    system_prompt=prompts.SYSTEM_PROMPT,
    user_message=prompts.build_vision_user_message(),
    model="gemma4:9b",
))
check("vision-mode attaches image bytes", "images" in captured["messages"][1])
check("vision-mode image is bytes", isinstance(captured["messages"][1]["images"][0], (bytes, bytearray)))

# list_local_models
models = gemma_client.list_local_models()
check("list_local_models returns names", "gemma4:9b" in models)


# ---------------------------------------------------------------------------
# 5. End-to-end: invoke app.explain() generator with the stub
# ---------------------------------------------------------------------------

print(f"\n{INFO} Section 5: end-to-end through app.explain()")

import app  # noqa: E402

# Run the explain generator on the medical_bill sample
sample_path = str(samples_dir / "medical_bill.txt")
gen = app.explain(
    file_obj=sample_path,
    pasted_text="",
    model="gemma4:9b",
    use_vision=False,
)
final_md = None
final_state = None
for md, state, _ in gen:
    final_md = md
    if state is not None:
        final_state = state

check("app.explain yields markdown", final_md is not None and isinstance(final_md, str))
check("app.explain returns chat-context state at end", final_state is not None)
check("state captured explanation", final_state and "WHAT THIS IS" in final_state["explanation"])
check("state captured document text", final_state and "Mercy General" in final_state["document_text"])
check("rendered markdown shows source", final_md and "medical_bill.txt" in final_md)
check("rendered markdown shows model name", final_md and "gemma4:9b" in final_md)


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

print()
if failures:
    print(f"\033[91m{len(failures)} check(s) failed:\033[0m")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
else:
    print("\033[92mAll smoke-test checks passed.\033[0m")
