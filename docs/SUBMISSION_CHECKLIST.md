# Submission Checklist — Plain Speak

**Deadline: May 18, 2026 at 7:59 PM EDT** (that's 11:59 PM UTC).

Work through this top to bottom. Each step has a time estimate. **Total: ~6 hours of focused work**, leaving buffer for sleep and the inevitable thing that goes wrong.

---

## Phase 1 — Get it running locally (45 min)

- [ ] **Install Ollama.** Run in Terminal:
      ```bash
      curl -fsSL https://ollama.com/install.sh | sh
      ```
      Then verify with `ollama --version`.

- [ ] **Pull the model.** This is the long step — 5 GB download, allow 10–20 min:
      ```bash
      ollama pull gemma4:9b
      ```
      If your laptop has less than 16 GB RAM, also pull the edge variant as a fallback:
      ```bash
      ollama pull gemma4:e4b
      ```

- [ ] **Start Ollama (it usually autostarts):**
      ```bash
      ollama serve &
      ```
      In a separate terminal, sanity-check it:
      ```bash
      ollama run gemma4:9b "Hello in one sentence"
      ```

- [ ] **Install Python deps.** From the `plain-speak/` folder:
      ```bash
      python3 -m venv .venv && source .venv/bin/activate
      pip install -r requirements.txt
      ```

- [ ] **Run the app.**
      ```bash
      python app.py
      ```
      Browser opens to `http://127.0.0.1:7860`. Click **Load sample → medical_bill.txt → Explain**. Confirm you see the eight sections stream in.

- [ ] **Pre-warm the model** by running the explain step once before you start recording — the first call is slow, subsequent ones are snappy.

---

## Phase 2 — Push code to GitHub (15 min)

You already created the repo at `github.com/<your-handle>/plain-speak`. Now push the files:

- [ ] From the `plain-speak/` folder:
      ```bash
      git add .
      git commit -m "Plain Speak — Gemma 4 Good Hackathon submission"
      git push origin main
      ```

- [ ] Open the repo in your browser. Verify the README renders, you can see `app.py`, `prompts.py`, `samples/`, and `docs/`.

- [ ] On the repo's main page, click the gear icon next to **About** (top right). Add:
      - **Description:** the one from the README's first line
      - **Website:** your YouTube video URL (after Phase 4)
      - **Topics:** `gemma`, `gemma4`, `ollama`, `accessibility`, `digital-equity`, `offline-ai`, `multimodal`, `hackathon`

---

## Phase 3 — Record the video (90 min)

Follow `docs/VIDEO_SCRIPT.md` exactly. Time budget breakdown:

- [ ] **15 min** — Setup: quiet room, mic check, browser cleanup, pre-warm Gemma.
- [ ] **30 min** — Record. Expect to retake at least one segment. Don't rerecord the whole thing — record in segments, stitch in iMovie/DaVinci.
- [ ] **20 min** — Edit. Cut dead air, add the three text cards mentioned in the script.
- [ ] **15 min** — Export at 1080p, watch the whole thing back end-to-end. Check audio levels, check the demo is actually visible.
- [ ] **10 min** — Upload to YouTube as **Unlisted**, copy/paste the title and description from `docs/VIDEO_SCRIPT.md`, add the chapters listed there.

- [ ] **Watch it once more** as if you were a judge. Then flip it to **Public** and grab the URL.

---

## Phase 4 — Create the Kaggle writeup (30 min)

- [ ] Go to https://kaggle.com/competitions/gemma-4-good-hackathon and click **New Writeup**.

- [ ] **Title:** `Plain Speak: A Privacy-First Document Explainer for the 130 Million Americans Who Can't Read Their Mail`

- [ ] **Subtitle:** `Gemma 4 running 100% on-device turns confusing official documents into plain English.`

- [ ] **Track:** `Digital Equity & Inclusivity` (this is mandatory — without it, the writeup is invalid).

- [ ] **Body:** open `docs/KAGGLE_WRITEUP.md`, copy everything from the H1 onward, paste into the Kaggle editor. Replace the two `<your-handle>` placeholders with your actual GitHub handle, and the `<your-video-id>` with your YouTube ID.

- [ ] **Cover image:** required. Take a screenshot of the Plain Speak app showing an explanation rendered (use the `medical_bill.txt` sample). Upload it as the cover.

- [ ] **Media Gallery → Attach Video:** paste your YouTube URL.

- [ ] **Project Links → Code Repository:** paste your GitHub URL.

- [ ] **Project Links → Live Demo:** paste your GitHub URL (the README's *Quick start* counts as a live demo — judges can clone and run in 5 minutes). If you have time, deploy to Hugging Face Spaces and use that URL instead.

- [ ] Click **Save**.

---

## Phase 5 — Final verification (15 min)

Open your Kaggle writeup in a private/incognito window — that's how the judges will see it.

- [ ] Cover image renders.
- [ ] Video plays (YouTube is set to Public, not Unlisted).
- [ ] GitHub link opens to a public repo.
- [ ] README on GitHub renders cleanly.
- [ ] Track is set to Digital Equity & Inclusivity.
- [ ] Writeup is under 1,500 words. Paste into https://wordcounter.net/ to check.

---

## Phase 6 — SUBMIT (2 min)

- [ ] On the Kaggle writeup page, click **Submit** in the top right corner. **A saved Writeup is not a submission. Without clicking Submit, the judges will not see it.**

- [ ] Take a screenshot of the confirmation. Save it somewhere safe.

- [ ] You can edit and re-submit as many times as you want before the deadline — so submit early, even if rough, then keep polishing.

---

## Emergency tips

- **`ollama pull gemma4:9b` is too slow / not finishing.** Cancel it and pull `gemma4:e4b` instead. Update the model dropdown default in `app.py` (line 30) to `"gemma4:e4b"` and uncheck the vision checkbox in the demo.

- **Gradio won't start — port in use.** Run `python app.py --port 7861`.

- **The model gives weird, drifting output.** Check that `prompts.py` was pushed and isn't being shadowed. Lower `temperature` in `gemma_client.py` from 0.2 to 0.1 if drift persists.

- **YouTube upload is stuck processing.** Submit the Kaggle writeup with the YouTube link anyway — by the time judges open it, processing will be done.

- **You're running out of time.** Submit *something* before the deadline. A submission with a rough video is reviewable; no submission isn't. You can edit and resubmit up to the deadline.
