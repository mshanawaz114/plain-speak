# Plain Speak

> A privacy-first AI that turns confusing official documents into plain English. Runs **entirely on your computer** using Gemma 4.

[![Gemma 4](https://img.shields.io/badge/Powered_by-Gemma_4-4285F4)](https://ai.google.dev/gemma)
[![Ollama](https://img.shields.io/badge/Runs_on-Ollama-000000)](https://ollama.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Built for the **Gemma 4 Good Hackathon** — Digital Equity & Inclusivity track.

---

## The problem

Roughly **130 million American adults** read at or below a sixth-grade level. Every week they receive documents written nowhere near that level: IRS notices, Medicare letters, hospital bills, insurance EOBs, eviction notices, court summonses. The U.S. Plain Writing Act of 2010 made plain language a federal requirement — sixteen years later, almost no agency complies.

The cost is human. People miss deadlines, pay bills they don't owe, ignore court summonses, lose benefits, sign things they should not have signed. Cloud AI tools could help, but uploading a medical bill or an immigration letter to a remote server is a privacy non-starter for the people who need this help most.

## What Plain Speak does

You drag in a PDF or a photo of a confusing letter. Gemma 4 reads it on your machine and produces a structured plain-English explanation:

| Section | What it tells you |
|---|---|
| **What this is** | A one-sentence summary in everyday words |
| **Who sent it** | The sender and what kind of organization they are |
| **What you need to do** | Concrete, numbered actions |
| **Important dates** | Every deadline, with what happens at each one |
| **Money involved** | Every dollar amount, and what it's for |
| **If you ignore this** | Honest consequences, not scare-mongering |
| **Questions to ask them** | Three things to ask the sender directly |
| **Plain-English summary** | A short paragraph you could explain to a friend |

You can then ask follow-up questions in conversation — *"What happens if I can't pay by the deadline?"* — and Gemma stays grounded in the document.

Nothing leaves your machine. No accounts, no API keys, no logs in someone else's data center.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                       Plain Speak (UI)                        │
│                     Gradio · single file                      │
└────────────────┬─────────────────────────────────┬───────────┘
                 │                                 │
        ┌────────▼────────┐               ┌────────▼────────┐
        │ document_loader │               │  gemma_client   │
        │  · pypdf (PDF)  │               │  · Ollama HTTP  │
        │  · PIL (image)  │               │  · streaming    │
        │  · OCR fallback │               │  · vision input │
        └────────┬────────┘               └────────┬────────┘
                 │                                 │
                 └──────────┬──────────────────────┘
                            ▼
              ┌──────────────────────────────┐
              │       Ollama (localhost)      │
              │   gemma4:9b (vision + tools)  │
              │   gemma4:e4b (edge, CPU)      │
              │   gemma4:e2b (tiny edge)      │
              └──────────────────────────────┘
```

Three small modules, no microservices, no cloud:

- **`app.py`** — Gradio UI. Streams Gemma's output token-by-token so the demo feels alive.
- **`document_loader.py`** — Detects file type and prepares input. Text PDFs go through `pypdf`; images go straight to a vision-capable Gemma 4 model, or fall back to Tesseract OCR for text-only edge variants.
- **`gemma_client.py`** — Thin streaming wrapper around the Ollama Python client. Swappable: replacing this file is all it takes to retarget LiteRT, llama.cpp, or Cactus for the [Special Technology Tracks](https://kaggle.com/competitions/gemma-4-good-hackathon).
- **`prompts.py`** — The prompt engineering, isolated and commented so anyone (judges included) can audit exactly how we steer Gemma 4.

### Why Gemma 4 specifically

- **Multimodal vision (gemma4:9b)** — users can snap a phone photo of a letter and skip OCR entirely. This matters because the people Plain Speak serves are unlikely to know how to run a separate OCR step.
- **Edge variants (gemma4:e2b/e4b)** — the smallest variant runs comfortably on a laptop with 4 GB of RAM, making Plain Speak deployable in libraries, community centers, and refugee resettlement offices that lack modern hardware.
- **Open weights** — community health workers and legal aid clinics can audit, fine-tune, and deploy without per-call costs or rate limits.
- **Native tool calling (roadmap)** — future versions can call out to verified sources (e.g., looking up an IRS form number, fetching a state's tenant-protection page) without breaking the local-first guarantee.

## Quick start

### 1. Install Ollama and pull Gemma 4

```bash
# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh
ollama pull gemma4:9b        # ~5GB — vision + tool calling
# or for low-resource machines:
ollama pull gemma4:e4b       # ~3GB — text only, edge-class
```

### 2. Install Python deps

```bash
git clone https://github.com/<your-handle>/plain-speak.git
cd plain-speak
pip install -r requirements.txt
```

### 3. Run

```bash
python app.py
```

The app opens at `http://127.0.0.1:7860`. Drop in a document or click **Load sample** to try one of the bundled mock letters.

### Optional: Tesseract for OCR fallback

If you choose a text-only model (`gemma4:e4b` / `gemma4:e2b`) and upload an image, Plain Speak uses Tesseract OCR.

```bash
# macOS
brew install tesseract
# Ubuntu / Debian
sudo apt install tesseract-ocr
# Windows
# https://github.com/UB-Mannheim/tesseract/wiki
```

## Sample documents

The `samples/` directory ships three mock documents (entirely fictional, no real PII) so judges and contributors can try Plain Speak without exposing personal paperwork:

- `samples/medical_bill.txt` — a confusing hospital EOB
- `samples/irs_notice.txt` — a CP2000 underreporting notice
- `samples/eviction_notice.txt` — a 14-day pay-or-quit notice

## Roadmap

- **Tool calling** — Gemma 4 native function calling to look up sender phone numbers, tenant-rights resources, and federal benefit eligibility from verified sources.
- **Audio output** — text-to-speech for users with visual impairment or limited reading ability, using locally available TTS.
- **Mobile build** — a Cactus / LiteRT port so the same experience runs on a $100 Android phone with no internet.
- **Multilingual round-trip** — explain the document in the user's first language (Spanish, Tagalog, Vietnamese, Haitian Creole), while keeping the original English alongside for use in official replies.

## License

MIT. See [LICENSE](LICENSE).

## Acknowledgements

Built on Google DeepMind's [Gemma 4](https://ai.google.dev/gemma) open models, served locally via [Ollama](https://ollama.com), wrapped in [Gradio](https://gradio.app). Inspired by the work of [Center for Plain Language](https://centerforplainlanguage.org/), [PlainLanguage.gov](https://www.plainlanguage.gov/), and every legal aid attorney who has translated a confusing letter for a stranger.
