# Submission checklist (do today)

Deadline per Gnani's blog: **11:59 PM IST, 10 November 2026** (no extensions). Aim to submit today so there is time to fix anything.

## 1. Get the app running (about 15 min)
- [ ] Sign in at https://app.gnani.ai/voice with your institutional email (or personal email and keep your student ID ready) and create an API key
- [ ] `cp .env.example .env` and paste the key
- [ ] `pip install -r requirements.txt`
- [ ] `python cli.py --selftest` (confirms Prisma + Timbre work with your key and credits)
- [ ] `uvicorn server:app --port 8000`, open http://localhost:8000 in Chrome, ask 3-4 questions by voice
- [ ] If anything fails, the error message on screen names the cause (bad key, no credits, rate limit)

## 2. Make it yours (about 15 min)
- [ ] Replace the sample answers in `data/faq.json` with real, verified information from your institute (fees portal, scholarship cell, library timings, helpline numbers)
- [ ] Re-run `python -m unittest discover -s tests -v` (some tests check specific topics; keep the entry ids unchanged)

## 3. Publish the code (Form Q5)
- [ ] Create a **public** GitHub repo `campus-saathi` and push this folder (`.env` is git-ignored, so your key is not uploaded)
- [ ] Make sure `PITCH.md` (and `PITCH.pdf`) are in the repo root
- [ ] Form Q5 answer = the GitHub repo URL

## 4. Record the demo (Form Q6)
- [ ] Follow `DEMO_SCRIPT.md`; record 2-3 minutes
- [ ] Upload to YouTube (Unlisted) or Google Drive set to "Anyone with the link"; open the link in a private window to confirm it plays
- [ ] Form Q6 answer = that video link

## 5. Post publicly (Form Q7, bonus awards)
- [ ] Post the 60-second cut on LinkedIn (and/or X) using `LINKEDIN_POST.md`
- [ ] Tag Gnani and include **#GnaniAI** and **#GreatIndianAIInternshipChallenge**
- [ ] Make sure the post is public; ask friends to engage early
- [ ] Form Q7 answer = the LinkedIn post URL

## 6. Submit
- [ ] Submit the Project Submission Form (Q5, Q6, Q7 above; your institute is already filled in)
- [ ] Name the models you used, as the rules require: **Prisma v3.0 (STT) and Timbre v2.5 (TTS)**, with Evon only if you actually self-host it
- [ ] Screenshot the confirmation page

Anything above that involves your accounts (Gnani sign-in, GitHub, YouTube, LinkedIn, the form itself) has to be done by you.
