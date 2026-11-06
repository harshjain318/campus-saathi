"""Thin client for Gnani AI's Prisma (speech-to-text) and Timbre (text-to-speech) REST APIs.

Endpoints and fields follow the official docs at https://docs.gnani.ai :
  STT  POST {base}/stt/v3                 multipart/form-data, header X-API-Key-ID
  TTS  POST {base}/api/v1/tts/inference   JSON body, header X-API-Key-ID, returns binary audio
"""
import hashlib
import os
import threading
import time

import requests

import config


class GnaniError(Exception):
    def __init__(self, message: str, status: int | None = None):
        super().__init__(message)
        self.status = status


# Some accounts are limited to one active request at a time (HTTP 429 otherwise),
# so every call to Gnani goes through one lock.
_lock = threading.Lock()
_RETRY_STATUS = {429, 500, 502, 503, 504}

_HINTS = {
    401: "Gnani API key is missing or invalid. Set GNANI_API_KEY (create one at app.gnani.ai).",
    402: "Gnani credits are exhausted for this account.",
    403: "Gnani key lacks permission or credits for this service.",
}


def api_key() -> str:
    key = os.getenv("GNANI_API_KEY", "").strip()
    if not key:
        raise GnaniError(_HINTS[401], 401)
    return key


def _error_text(resp: requests.Response) -> str:
    try:
        body = resp.json()
    except ValueError:
        return resp.text[:200]
    if isinstance(body, dict):
        detail = body.get("detail")
        if isinstance(detail, dict):
            return f"{detail.get('error_code', '')}: {detail.get('message', '')}".strip(": ")
        if isinstance(detail, list):
            return "; ".join(str(item.get("msg", item)) if isinstance(item, dict) else str(item) for item in detail)
        error = body.get("error")
        if isinstance(error, dict):
            return f"{error.get('type', '')}: {error.get('message', '')}".strip(": ")
        if isinstance(error, str):
            return f"{error}: {body.get('message', '')}".strip(": ")
    return str(body)[:200]


def _post(url: str, attempts: int = 3, **kwargs) -> requests.Response:
    last: GnaniError | None = None
    with _lock:
        for attempt in range(1, attempts + 1):
            try:
                resp = requests.post(url, timeout=60, **kwargs)
            except requests.RequestException as exc:
                last = GnaniError(f"Could not reach Gnani API: {exc}")
            else:
                if resp.status_code == 200:
                    return resp
                message = _HINTS.get(resp.status_code) or _error_text(resp)
                last = GnaniError(f"Gnani API error {resp.status_code}: {message}", resp.status_code)
                if resp.status_code not in _RETRY_STATUS:
                    raise last
            if attempt < attempts:
                time.sleep(1.5 * attempt)
    raise last  # type: ignore[misc]


def transcribe(audio: bytes, filename: str = "question.wav", mime: str = "audio/wav") -> dict:
    """Prisma speech-to-text. Audio must be 30 seconds or shorter. Returns the parsed JSON body."""
    data = {"language_code": config.STT_LANGUAGES}
    if config.STT_MODEL and config.STT_MODEL != "prisma-v2.5":
        data["model"] = config.STT_MODEL
        data["format"] = config.STT_FORMAT
    resp = _post(
        f"{config.GNANI_BASE_URL}/stt/v3",
        headers={"X-API-Key-ID": api_key()},
        files={"audio_file": (filename, audio, mime)},
        data=data,
    )
    body = resp.json()
    if not body.get("success", True):
        raise GnaniError(f"Speech recognition failed: {_error_text(resp)}")
    body["transcript"] = (body.get("transcript") or "").strip()
    return body


def synthesize(text: str, lang: str = "en") -> bytes:
    """Timbre text-to-speech. `lang` is "hi" or "en". Returns WAV bytes. Results are cached on disk."""
    language, voice = ("hi-IN", config.TTS_VOICE_HI) if lang == "hi" else ("en-IN", config.TTS_VOICE_EN)
    cache_key = hashlib.sha256(
        f"{config.TTS_MODEL}|{voice}|{language}|{config.TTS_SAMPLE_RATE}|{text}".encode("utf-8")
    ).hexdigest()
    cache_file = config.CACHE_DIR / f"{cache_key}.wav"
    if cache_file.exists():
        return cache_file.read_bytes()

    resp = _post(
        f"{config.GNANI_BASE_URL}/api/v1/tts/inference",
        headers={"X-API-Key-ID": api_key(), "Content-Type": "application/json"},
        json={
            "text": text,
            "model": config.TTS_MODEL,
            "voice": voice,
            "language": language,
            "speed": 1.0,
            "audio_config": {
                "sample_rate": config.TTS_SAMPLE_RATE,
                "num_channels": 1,
                "sample_width": 2,
                "encoding": "linear_pcm",
                "container": "wav",
            },
        },
    )
    if "json" in resp.headers.get("Content-Type", "").lower():
        raise GnaniError(f"Speech synthesis failed: {_error_text(resp)}")
    audio = resp.content
    config.CACHE_DIR.mkdir(exist_ok=True)
    cache_file.write_bytes(audio)
    return audio
