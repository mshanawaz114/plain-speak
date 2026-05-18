# Plain Speak — 3-Minute Video Script & Shot List

**Total runtime target: 2 min 50 sec** (leaves a buffer; judges penalize anything over 3:00).
**Tools you need:** OBS Studio (free) or QuickTime screen recording, a USB mic or AirPods, the Plain Speak app running locally with `gemma4:9b` already pulled.

---

## The pitch arc

> Hook → Real person, real problem → Live demo of the magic → Why Gemma 4 specifically → Vision & impact → Call to action.

The judges are reviewing dozens of videos. The first 10 seconds decide whether they finish yours. Open with a face — yours, on camera — and a real document on the table. **Do not open with a logo.**

---

## SCENE 1 — Hook (0:00 – 0:15)

**Shot:** Webcam on you. You're holding up a real piece of mail (a confusing-looking letter — an IRS notice, a medical bill, anything that *looks* official). Set the letter down on the desk.

**Voiceover (on camera):**
> "Last month my mother got this letter. She speaks English, but she could not understand a single thing it said. And she's not alone — 130 million American adults are in the exact same situation, every single week."

**Pause. Cut to fullscreen text card (white background, large black type):**
> **130 million Americans can't read their own mail.**

---

## SCENE 2 — The problem (0:15 – 0:35)

**Shot:** Cut to a screen recording showing the *Mercy General Hospital* sample document (`samples/medical_bill.txt`) opened in a text editor or as a PDF. Slowly scroll.

**Voiceover (no camera):**
> "Plan discount. Allowed amount. Coinsurance. PR-1. CO-45. This is an Explanation of Benefits from a hospital. The Plain Writing Act of 2010 made plain language a federal requirement. Sixteen years later, almost no agency complies. And the people who get hurt by this — low-income families, immigrants, the elderly — are the same people who absolutely cannot upload a medical bill to ChatGPT."

**On screen (text overlay, lower third):**
> Plain Writing Act of 2010: still ignored.
> Cloud AI: not an option for these users.

---

## SCENE 3 — Live demo, the wow moment (0:35 – 1:35)

**This is the most important minute of the video. Do not skip steps.**

**Shot:** Full-screen recording of the Plain Speak app (`http://127.0.0.1:7860`). Browser at fullscreen, no other tabs visible.

**Action 1 (0:35 – 0:50):**
- Click the **Load sample** dropdown, pick `medical_bill.txt`, click **Load sample**.
- The pasted-text box fills with the confusing EOB.
- Click **Explain this in plain English**.

**Voiceover during the click:**
> "Watch this. I'm dropping that exact hospital bill into Plain Speak. The model is Gemma 4 — running entirely on this laptop. No internet. No account. No data leaving the machine."

**Action 2 (0:50 – 1:15):**
- Let Gemma 4 stream the eight sections live. Do not cut, do not speed up — judges need to see this is real, not pre-rendered.

**Voiceover while streaming:**
> "Here's what Plain Speak does: it forces Gemma 4 to write at a sixth-grade reading level, in eight fixed sections. What this is. Who sent it. What you need to do. Important dates. Money involved. What happens if you ignore it. This is the entire output. No jargon. No legalese."

**Action 3 (1:15 – 1:35):**
- Once the explanation finishes, scroll to the follow-up chat box.
- Type: *"What happens if I can't pay the deadline?"*
- Press Enter. Let Gemma stream the answer.

**Voiceover:**
> "And because the document stays in context, she can ask follow-up questions — and Gemma stays grounded in what's actually on the page, not making up legal advice."

---

## SCENE 4 — Why Gemma 4 specifically (1:35 – 2:10)

**Shot:** Quick montage. Show:
- A terminal window with `ollama pull gemma4:9b` and `ollama list` showing the local model.
- The `prompts.py` file open, scrolling through the system prompt.
- A close-up of your laptop's offline indicator / airplane mode toggle being switched on, then re-running the explanation to prove it still works offline.

**Voiceover:**
> "Three things about Gemma 4 made this possible. One: native vision. My mom doesn't know what OCR is — she takes a phone photo of a letter, and Gemma 4 reads it directly. Two: the edge variants. Gemma 4 E4B runs on a five-year-old laptop with four gigabytes of RAM. That's the hardware reality in public libraries and community centers. Three: open weights. Legal aid clinics can audit our prompts, fine-tune for their state's documents, and deploy without paying anyone per request."

**On-screen text overlay during airplane mode shot:**
> ✈️ Airplane mode ON. Still works.

---

## SCENE 5 — Vision (2:10 – 2:35)

**Shot:** Back to webcam. You're looking at the camera again. Behind you, optional B-roll on a second monitor of an Android phone running the demo (only if you have time to set this up — otherwise skip and stay on camera).

**Voiceover (on camera):**
> "Next, we're porting Plain Speak to mobile through Cactus and LiteRT, adding Spanish, Tagalog, and Haitian Creole, and wiring up Gemma 4's tool calling to look up tenant-rights statutes and benefits-eligibility rules from a verified offline knowledge base. Same local-first guarantee. Same four-file architecture."

---

## SCENE 6 — Close (2:35 – 2:50)

**Shot:** Webcam. Hold up the same letter from Scene 1. Smile.

**Voiceover (on camera):**
> "Plain Speak is the boring AI product the people who most need AI cannot currently use. Gemma 4 is the first model that lets us actually ship it. Code is open source, link in the description. Thanks for watching."

**Fade to text card:**
> **Plain Speak**
> github.com/&lt;your-handle&gt;/plain-speak
> Built for the Gemma 4 Good Hackathon

---

## Recording checklist (read before you hit record)

- [ ] **Quiet room.** Close the door. Turn off notifications on the laptop you're recording (System Settings → Focus → Do Not Disturb).
- [ ] **Mic test.** Record 10 seconds, play it back. Adjust input level if anything clips.
- [ ] **Browser cleanup.** Close every tab except Plain Speak. Hide the bookmarks bar (Cmd-Shift-B).
- [ ] **Pre-pull the model.** Run `ollama pull gemma4:9b` *before* recording. You do not want to film the download.
- [ ] **Pre-warm the model.** Run one explain pass *before* hitting record so the model is loaded into RAM — the first call after a fresh start is much slower.
- [ ] **Aspect ratio.** Record at 1920×1080. YouTube punishes anything else.
- [ ] **Cut, don't redo.** If you mess up one line, pause, take a breath, re-record just that line. Edit the segments together in iMovie / DaVinci Resolve (free).
- [ ] **Upload as Unlisted first.** Watch the whole thing back end-to-end. *Then* flip to Public and grab the link.
- [ ] **YouTube description** should contain: 1-line project summary, GitHub link, hackathon name, Gemma 4 model used.

---

## YouTube title & description (copy-paste)

**Title:**
> Plain Speak — Gemma 4 Turns Confusing Government Mail Into Plain English (100% On-Device)

**Description:**
> 130 million American adults read at or below a 6th-grade level. Every week they get IRS notices, medical bills, and eviction letters written nowhere near that level — and they can't safely upload that paperwork to a cloud AI.
>
> Plain Speak runs Gemma 4 entirely on your own laptop via Ollama, turning a confusing official document into an 8-section plain-English explanation in seconds. Privacy-first, open source, four-file architecture.
>
> 🔗 Code: https://github.com/&lt;your-handle&gt;/plain-speak
> 🧠 Models: gemma4:9b (vision) and gemma4:e4b (edge)
> 🏆 Built for the Gemma 4 Good Hackathon — Digital Equity & Inclusivity track
>
> 0:00 The problem nobody talks about
> 0:35 Live demo on a real hospital bill
> 1:35 Why Gemma 4 specifically
> 2:10 What's next
