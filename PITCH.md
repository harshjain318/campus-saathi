# Campus Saathi: a voice helpdesk for Indian college students

**Harsh Jain · Maulana Azad National Institute of Technology, Bhopal · Great Indian AI Internship Challenge 2026**

## Problem
Every semester, students lose hours finding simple answers: how to pay fees, where to apply for a scholarship, what to do after losing an ID card, who handles a hostel complaint. The answers exist, but they are scattered across notice boards, PDFs and portals, mostly written in formal English. Many students, especially first-years from smaller towns and Hindi-medium schools, think and speak in Hindi or Hinglish and find typing queries into portals slow and intimidating.

## Solution
Campus Saathi (कैंपस साथी) is a voice-first helpdesk. A student taps a mic and asks a question the way they would ask a senior: *"library kab khulti hai?"*, *"scholarship ka form kaise bharein"* or *"How do I pay my fees?"*. The app understands the speech, finds the verified answer and speaks it back in the same language. It also shows the transcript and answer as text, so the reply can be read or copied.

## How it uses Gnani AI models
| Step | Gnani model | What it does |
|---|---|---|
| Listen | **Prisma v3.0** (speech-to-text) | Transcribes Hindi, English and code-mixed Hinglish questions, with language hints `hi-IN,en-IN` and the `codemix` output style |
| Answer | FAQ retrieval (optional **Evon** rewrite when self-hosted) | Matches the question to the institute FAQ, tolerating Devanagari, romanised Hindi and small spelling or ASR variations |
| Speak | **Timbre v2.5** (text-to-speech) | Speaks the answer in a natural Hindi (Nalini) or Indian English (Kaveri) voice |

The answer engine only returns facts from the institute's own FAQ file, so the assistant does not invent policies. If it has no answer, it says so and points to the right office.

## Architecture
Browser mic → 16 kHz WAV → FastAPI server → Prisma STT → retrieval engine → Timbre TTS (cached on disk to save credits) → audio and text back to the browser. A text box and sample-question buttons work as a fallback when a microphone is unavailable.

## Impact
- Lowers the barrier for students who are more comfortable speaking than typing, and for those who prefer Hindi or Hinglish.
- Cuts repeated questions to department offices, because the common answers are available instantly at any hour.
- Easy to adopt: a college only edits one JSON file to publish its own verified answers. Adding a regional language only needs new answer text, since Prisma and Timbre already cover 10 Indian languages.

## Next steps
Connect Evon for fully conversational follow-ups, add live notice-board ingestion, streaming (WebSocket) STT/TTS for faster replies, and a phone-call or WhatsApp voice-note channel.

*Note: the FAQ content in the demo is sample data and must be replaced with verified institute information before real use.*
