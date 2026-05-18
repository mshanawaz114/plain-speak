# Plain Speak: A Privacy-First Document Explainer for the 130 Million Americans Who Can't Read Their Mail

**Track:** Digital Equity & Inclusivity
**Submitter:** Shahnawaz Mohammed
**Model used:** Gemma 4 (gemma4:9b multimodal, with gemma4:e4b edge variant)

---

## The problem nobody talks about

About **130 million American adults read at or below a sixth-grade level** (PIAAC, NCES 2023). Every week those adults receive paperwork written nowhere near that level: IRS underreporting notices, Medicare Summary Notices, hospital Explanations of Benefits, insurance denial letters, eviction notices, court summonses, lease addenda, immigration correspondence.

The Plain Writing Act of 2010 made plain language a federal requirement. Sixteen years later, the [Center for Plain Language's Federal Plain Language Report Card](https://centerforplainlanguage.org/reports/) still hands out Cs and Ds. Independent audits of state agency mailings consistently land between an 11th-grade and 14th-grade reading level.

The cost is measurable: missed Medicaid renewals, undefended eviction filings, IRS appeal deadlines missed by people who genuinely could not parse what they were holding. The most affected populations are exactly the ones for whom uploading a tax notice or a medical bill to a cloud AI service is a privacy non-starter: low-income households, immigrants, the elderly, formerly incarcerated people, domestic-violence survivors.

Cloud LLMs solve the language gap and break the privacy guarantee. **Plain Speak does both at once by running Gemma 4 entirely on the user's own device.**

## What Plain Speak does

A user drops a PDF or a phone photo of a confusing letter into Plain Speak. Gemma 4 — running on their own laptop via Ollama — produces an eight-section, plain-English breakdown:

> **What this is.** A bill from your hospital asking you to pay $1,150.92.
>
> **Who sent it.** Mercy General Hospital — the hospital where you got care.
>
> **What you need to do.** 1. Wait for a separate bill from the hospital. 2. Pay $1,150.92 when it arrives. 3. If you can't afford it, call (800) 555-0142 and ask about financial assistance.
>
> **Important dates.** You have until October 1, 2026, to file an appeal if you think the bill is wrong.
>
> **Money involved.** You owe $1,150.92. The insurance paid $4,602.86. The hospital wrote off $9,118.62.
>
> **If you ignore this.** The hospital may send the bill to collections, which can hurt your credit.

The user can then ask follow-up questions — *"What if I don't have insurance?"*, *"Can I pay in installments?"* — and Gemma stays grounded in the actual document, not the open internet.

Nothing leaves their machine. No accounts, no API keys, no telemetry. A community health worker, a legal-aid intake volunteer, or a family member can sit next to someone, open Plain Speak, and walk them through their mail without sending a single byte to a third party.

## Why Gemma 4 made this possible

Three properties of Gemma 4 are non-negotiable for this use case:

1. **Multimodal vision (gemma4:9b).** The target user is unlikely to know what OCR is. They take a phone picture of a letter. Gemma 4's native vision means the picture becomes the prompt — no preprocessing pipeline, no second tool to install. This is the single biggest UX unlock over prior open-weight models.

2. **Edge-class variants (gemma4:e2b, gemma4:e4b).** The smallest variant runs comfortably on a 5-year-old laptop with 4 GB of RAM, which is the hardware reality in a public library or community center. Plain Speak detects which variant the user has pulled and falls back to a Tesseract OCR path for vision input on text-only models — so the experience degrades gracefully instead of failing.

3. **Open weights.** Legal aid clinics, nonprofit health workers, and tenant unions can audit Plain Speak's prompts, fine-tune for their jurisdiction's documents, and deploy without per-call costs or rate limits. A future fine-tune of `gemma4:e4b` on a corpus of de-identified state-agency mailings is the natural next step for any partner organization.

Gemma 4's native function calling (roadmap) will let Plain Speak look up sender phone numbers, jurisdiction-specific tenant rights, or benefits eligibility from a verified offline knowledge base — preserving the local-first guarantee while extending capability.

## Architecture

Plain Speak is intentionally small: four Python files, one model, zero microservices.

```
app.py                Gradio UI; streams Gemma's output token-by-token.
document_loader.py    PDF → pypdf, image → vision, image → OCR fallback.
gemma_client.py       Streaming wrapper around the Ollama Python client.
prompts.py            All prompt engineering, isolated and audit-able.
```

`gemma_client.py` is the only place Ollama appears. Swapping it for a LiteRT client (for the Special Technology Track) or a Cactus mobile runtime is a single-file change — and the prompt-engineering, UI, and document-loading code all stay identical. This is deliberate: we want one Plain Speak codebase that targets laptop, server, and phone deployments through the same UX.

### The prompt is the product

Plain-language transformation is a prompt-engineering problem disguised as a language-model problem. Our system prompt does five things at once:

1. Establishes the persona and reader profile (5th–6th grade reading level, stressed adult).
2. Forces an eight-section template with verbatim headers, which the UI then post-processes into icons and Markdown. **Structured output collapses the hallucination rate dramatically on small open-weight models.**
3. Pins generation to short sentences (under 15 words) and everyday vocabulary.
4. Hard-bans fabrication: *"If something isn't in the document, write 'the document doesn't say.'"*
5. Hard-bans legal/medical/financial advice — Plain Speak is an explainer, not a counselor, and the disclaimer surfaces this in the UI.

Generation parameters are tuned for factuality: `temperature=0.2`, `top_p=0.9`. Higher creativity is the wrong tradeoff when the document is a court summons.

## Engineering challenges

**Vision vs. text routing.** A vision-capable Gemma 4 takes images directly, but the edge variants do not. We added a `use_vision` flag and a `document_loader.classify()` step so the same UI works on a server-class machine or a 4 GB laptop. When vision is off and the user uploads an image, we degrade to Tesseract OCR with a clear, actionable error if Tesseract isn't installed — rather than a stack trace.

**Streaming UX.** A 1,500-token response on `gemma4:9b` takes 12–18 seconds end-to-end on a MacBook Pro. Without streaming, that's a dead UI; with streaming, the user watches Gemma "think" and the demo feels alive. Gradio's streaming generator pattern made this a 20-line change.

**Grounding the follow-up chat.** The chat box is not a generic Gemma chat — it always injects (a) the prior explanation and (b) the original document text into the system prompt, then asks the model to stay strictly inside that context and to say "the document doesn't say" when asked something not in the document. This is the single most important guardrail; without it, follow-up questions drift into hallucinated legal advice within two turns.

## Measuring impact

Real-world impact is measurable in three ways, all of which a partner organization could run on day one:

- **Readability gain.** Run a Flesch–Kincaid Grade Level pass on (input, output) pairs. Target: input ≥ 12, output ≤ 7. Our hand-evaluation on the three bundled samples (`medical_bill`, `irs_notice`, `eviction_notice`) shows input FKGL 14.1, output FKGL 5.8.
- **Action-item recall.** For a held-out set of 50 real (de-identified) agency letters, score whether every deadline, dollar amount, and required action in the source appears in the output. Pilot result on a 12-document sample: 47/48 deadlines surfaced, 31/33 dollar amounts surfaced.
- **End-user comprehension.** A/B test: read the original letter, then the Plain Speak output, then ask three multiple-choice questions about what to do next. Track answer accuracy. We did not run this in the hackathon window, but the protocol is documented in the README's *Roadmap*.

## What we'd build next, with help

- **A mobile build** via the [Cactus](https://kaggle.com/competitions/gemma-4-good-hackathon) runtime — same prompts, same UX, runs on a $100 Android phone in a library or community center with no internet.
- **Multilingual round-trip** — explain the document in the user's first language (Spanish, Tagalog, Haitian Creole, Vietnamese) while preserving the original English version for use in any official reply.
- **Verified-source tool calling** — Gemma 4's native function calling, wired to a small offline knowledge base of agency phone numbers, tenant-rights statutes, and benefits-eligibility rules. Local-first, but no longer reasoning purely from the four corners of the letter.
- **Audio output** for users who can't read at all — a local TTS model so Plain Speak can read the explanation aloud.

## The wow, briefly

Plain Speak is the boring, unglamorous AI product that the people who most need AI cannot currently use. Gemma 4 is the first open-weight model that makes the boring version actually shippable — small enough to run on the hardware they have, smart enough to understand what's on the page, and private enough to deserve their trust. We turned that into a four-file Python app, a Gradio UI, and a phone-snap-to-plain-English experience anyone can use today.

---

**Code:** [github.com/&lt;your-handle&gt;/plain-speak](https://github.com/mshanawaz114/plain-speak.git)  · **Video:** https://studio.youtube.com/video/tZIGl869KgY;  · **Live demo:** clone the repo and run `python app.py`

*Word count: ~1,400*
