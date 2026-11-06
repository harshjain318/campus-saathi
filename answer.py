"""Turns a transcript into a spoken-style answer.

Default: retrieval over the FAQ (fast, no extra infrastructure, never makes things up).
Optional: if EVON_BASE_URL points to an OpenAI-compatible server running Gnani's open-weight
Evon model, Evon rewrites the retrieved facts into a natural reply in the user's language.
If Evon is not configured or fails, the retrieved answer is used unchanged.
"""
import requests

import config
from knowledge import Knowledge, detect_language

_kb = Knowledge()


def knowledge() -> Knowledge:
    return _kb


def _evon_rewrite(question: str, entry: dict, lang: str) -> str | None:
    if not config.EVON_BASE_URL:
        return None
    language = "Hindi (Devanagari script)" if lang == "hi" else "English"
    system = (
        f"You are Campus Saathi, a voice helpdesk for students of {config.INSTITUTE_NAME}. "
        f"Answer ONLY from the facts provided. Reply in {language}, in at most two short sentences, "
        "plain spoken style, no lists, no digits written as numerals. If the facts do not answer the "
        "question, say you are not sure and suggest asking the relevant office."
    )
    facts = f"{entry['answer_en']}\n{entry['answer_hi']}"
    headers = {"Content-Type": "application/json"}
    if config.EVON_API_KEY:
        headers["Authorization"] = f"Bearer {config.EVON_API_KEY}"
    try:
        resp = requests.post(
            config.EVON_BASE_URL.rstrip("/") + "/chat/completions",
            headers=headers,
            json={
                "model": config.EVON_MODEL,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": f"Facts:\n{facts}\n\nStudent question: {question}"},
                ],
                "temperature": 0.2,
                "max_tokens": 200,
            },
            timeout=30,
        )
        resp.raise_for_status()
        text = resp.json()["choices"][0]["message"]["content"].strip()
        return text or None
    except (requests.RequestException, KeyError, IndexError, ValueError):
        return None


def respond(question: str) -> dict:
    """Return {text, lang, entry_id, title, score, engine} for a question."""
    lang = detect_language(question)
    score, entry = _kb.best(question)
    if entry is None:
        return {
            "text": _kb.fallback[lang],
            "lang": lang,
            "entry_id": None,
            "title": None,
            "score": 0.0,
            "engine": "fallback",
        }
    text = _evon_rewrite(question, entry, lang)
    engine = "evon" if text else "retrieval"
    return {
        "text": text or entry[f"answer_{lang}"],
        "lang": lang,
        "entry_id": entry["id"],
        "title": entry["title"],
        "score": round(score, 2),
        "engine": engine,
    }
