# Campus Saathi · कैंपस साथी

A voice helpdesk for college students in Hindi, Hinglish and English. Ask out loud, hear the answer back.

Built for the **Great Indian AI Internship Challenge 2026** with **Gnani AI** models.
`#GnaniAI #GreatIndianAIInternshipChallenge`

**Pitch:** see [PITCH.md](PITCH.md) (1 page).

## Gnani AI models and APIs used

| Purpose | Model | API |
|---|---|---|
| Speech to text | **Prisma v3.0** (set `GNANI_STT_MODEL=prisma-v2.5` for v2.5) | `POST https://api.vachana.ai/stt/v3` |
| Text to speech | **Timbre v2.5** | `POST https://api.vachana.ai/api/v1/tts/inference` |
| Reasoning (optional) | **Evon** open weights, self-hosted | Any OpenAI-compatible server via `EVON_BASE_URL` |

By default the answer step is retrieval over `data/faq.json`, which needs no extra infrastructure and cannot invent facts. Evon is not available on Gnani's API platform, so it is only used if you host the open weights yourself.

## How it works

```
Browser mic ──WAV 16 kHz──▶ FastAPI ──▶ Prisma STT ──▶ FAQ retrieval (or Evon) ──▶ Timbre TTS ──▶ audio + text
```

- `server.py` : FastAPI app and API routes (`/api/ask`, `/api/ask-text`, `/api/faq`, `/api/health`)
- `gnani_client.py` : Prisma and Timbre calls with retries, one-request-at-a-time lock and on-disk TTS cache
- `knowledge.py` / `answer.py` : multilingual retrieval (Devanagari, romanised Hindi, English, typo tolerant) and optional Evon rewrite
- `data/faq.json` : the institute knowledge base (**sample data, replace with verified information**)
- `static/index.html` : the web UI (mic recording, transcript, answer, audio player)
- `cli.py` : command line access and an end-to-end self-test

## Run it

Requires Python 3.10+.

```bash
cd campus-saathi
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env          # then put your key in .env  (GNANI_API_KEY=...)
# Get a key at https://app.gnani.ai/voice  (3 free keys per account)

python cli.py --selftest      # optional: checks Prisma + Timbre end to end with your key
uvicorn server:app --port 8000
```

Open <http://localhost:8000> in Chrome and allow the microphone. Questions must be 30 seconds or shorter (the UI stops at 28 s).

## Tests

```bash
python -m unittest discover -s tests -v
```

These run offline (Gnani calls are mocked) and cover multilingual retrieval, fallback behaviour and the server flow.

## Customising for your college

Edit `data/faq.json`. Each entry has `keywords` (mix English, romanised Hindi and Devanagari), a sample question in each language, and `answer_en` / `answer_hi`. Keep answers to two short sentences and write numbers as words, which makes Timbre pronounce them correctly. Set `INSTITUTE_NAME` in `.env`.

## Notes and limits

- Gnani accounts may allow only one active request at a time; the client serialises calls and retries on HTTP 429.
- Synthesised answers are cached in `cache/`, so repeated questions cost no TTS credits.
- Hindi replies are written in Devanagari and spoken with `language=hi-IN`; English replies use `en-IN`.
- The knowledge base shipped here is generic sample content, not official institute information.
