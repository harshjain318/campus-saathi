"""Campus Saathi web server.  Run:  uvicorn server:app --port 8000"""
import base64
import logging
import os
import time

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import answer
import config
import gnani_client
from gnani_client import GnaniError

log = logging.getLogger("campus-saathi")
app = FastAPI(title="Campus Saathi", version="1.0")

STATIC_DIR = config.BASE_DIR / "static"


class TextQuestion(BaseModel):
    text: str


def _ms(start: float) -> int:
    return int((time.perf_counter() - start) * 1000)


async def _answer_and_speak(transcript: str, timings: dict) -> dict:
    t = time.perf_counter()
    result = await run_in_threadpool(answer.respond, transcript)
    timings["answer_ms"] = _ms(t)

    audio_b64, tts_error = None, None
    t = time.perf_counter()
    try:
        audio = await run_in_threadpool(gnani_client.synthesize, result["text"], result["lang"])
        audio_b64 = base64.b64encode(audio).decode("ascii")
    except GnaniError as exc:
        log.warning("TTS failed: %s", exc)
        tts_error = str(exc)
    timings["tts_ms"] = _ms(t)

    return {
        "ok": True,
        "transcript": transcript,
        "answer": result["text"],
        "lang": result["lang"],
        "topic": result["title"],
        "engine": result["engine"],
        "match_score": result["score"],
        "audio_b64": audio_b64,
        "audio_mime": "audio/wav",
        "tts_error": tts_error,
        "timings": timings,
        "models": {
            "stt": config.STT_MODEL,
            "tts": config.TTS_MODEL,
            "reasoning": "Evon (self-hosted)" if result["engine"] == "evon" else "FAQ retrieval",
        },
    }


@app.get("/api/health")
def health():
    return {
        "ok": True,
        "gnani_key_set": bool(os.getenv("GNANI_API_KEY", "").strip()),
        "stt_model": config.STT_MODEL,
        "tts_model": config.TTS_MODEL,
        "evon_enabled": bool(config.EVON_BASE_URL),
    }


@app.get("/api/faq")
def faq():
    return {"suggestions": answer.knowledge().suggestions()}


@app.post("/api/ask")
async def ask_voice(audio: UploadFile = File(...)):
    data = await audio.read()
    if not data:
        raise HTTPException(400, "Empty recording.")
    if len(data) > config.MAX_UPLOAD_BYTES:
        raise HTTPException(413, "Recording is too large. Keep questions under 30 seconds.")

    timings: dict = {}
    t = time.perf_counter()
    try:
        stt = await run_in_threadpool(
            gnani_client.transcribe, data, audio.filename or "question.wav", audio.content_type or "audio/wav"
        )
    except GnaniError as exc:
        raise HTTPException(exc.status if exc.status in (401, 402, 403) else 502, str(exc))
    timings["stt_ms"] = _ms(t)

    transcript = stt["transcript"]
    if not transcript:
        return {"ok": False, "error": "no_speech", "message": "I could not hear anything. Please try again closer to the mic."}

    body = await _answer_and_speak(transcript, timings)
    body["detected_language"] = stt.get("detected_language_code")
    return body


@app.post("/api/ask-text")
async def ask_text(question: TextQuestion):
    text = question.text.strip()
    if not text:
        raise HTTPException(400, "Question is empty.")
    return await _answer_and_speak(text, {"stt_ms": 0})


app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
