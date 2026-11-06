"""Small retrieval engine over the campus FAQ. No heavy dependencies.

Speech-to-text output can arrive in Devanagari, romanised Hindi or English, and may contain small
spelling variations, so matching is keyword based with an IDF weight and a fuzzy fallback.
"""
import difflib
import json
import math
import re
import unicodedata

import config

FAQ_PATH = config.BASE_DIR / "data" / "faq.json"
MIN_SCORE = 1.0

_TOKEN_RE = re.compile(r"[a-z0-9ऀ-ॿ]+")
_DEVANAGARI_RE = re.compile(r"[ऀ-ॿ]")

_STOPWORDS = set(
    """
    the is a an of to in for my me i how what when where can do does about please tell show
    am are was be and or on at it this that with from have has need want
    kya hai hain ka ki ke ko se mein me kab kaise kahan aur mujhe mera meri kripya batao batayiye
    kaun kahaan hota hoti hote karna kare karen kijiye
    क्या है हैं का की के को से में मैं कब कैसे कहाँ कहां और मुझे मेरा मेरी कृपया बताइए बताओ बताइये
    कौन होता होती होते करना करें करे कीजिए कैसा मेरे
    """.split()
)


def _normalise(text: str) -> str:
    text = unicodedata.normalize("NFC", text).lower()
    # nukta and chandrabindu variants differ between speech models; drop them for matching
    return text.replace("़", "").replace("ँ", "ं")


def tokenize(text: str) -> list[str]:
    return [t for t in _TOKEN_RE.findall(_normalise(text)) if t not in _STOPWORDS]


def has_devanagari(text: str) -> bool:
    return bool(_DEVANAGARI_RE.search(text))


def detect_language(text: str) -> str:
    """'hi' when the text contains Devanagari, otherwise 'en'."""
    return "hi" if has_devanagari(text) else "en"


class Knowledge:
    def __init__(self, path=FAQ_PATH):
        data = json.loads(path.read_text(encoding="utf-8"))
        self.fallback = data["fallback"]
        self.entries = data["entries"]
        self._tokens = []
        for entry in self.entries:
            tokens = set()
            for phrase in entry["keywords"] + [entry["title"]]:
                tokens.update(tokenize(phrase))
            self._tokens.append(tokens)
        n = len(self.entries)
        df: dict[str, int] = {}
        for tokens in self._tokens:
            for t in tokens:
                df[t] = df.get(t, 0) + 1
        self._idf = {t: math.log(1 + n / (1 + c)) + 1.0 for t, c in df.items()}

    def search(self, query: str, k: int = 3):
        """Return up to k (score, entry) pairs, best first. Score 0 means no match."""
        q_tokens = set(tokenize(query))
        results = []
        for entry, tokens in zip(self.entries, self._tokens):
            score = 0.0
            for q in q_tokens:
                if q in tokens:
                    score += self._idf.get(q, 1.0)
                elif len(q) >= 4:
                    close = difflib.get_close_matches(q, [t for t in tokens if len(t) >= 4], n=1, cutoff=0.84)
                    if close:
                        score += 0.7 * self._idf.get(close[0], 1.0)
            if score > 0:
                results.append((score, entry))
        results.sort(key=lambda item: item[0], reverse=True)
        return results[:k]

    def best(self, query: str):
        hits = self.search(query, k=1)
        if hits and hits[0][0] >= MIN_SCORE:
            return hits[0]
        return 0.0, None

    def suggestions(self):
        return [
            {"id": e["id"], "title": e["title"], "q_en": e["q_en"], "q_hi": e["q_hi"]}
            for e in self.entries
            if e["id"] != "hello"
        ]
