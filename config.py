"""Settings for Campus Saathi. Values come from environment variables or a local .env file."""
import os
import pathlib

BASE_DIR = pathlib.Path(__file__).resolve().parent


def _load_dotenv() -> None:
    env_file = BASE_DIR / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv()


def get(name: str, default: str = "") -> str:
    return os.getenv(name, default)


# --- Gnani AI (Prisma STT + Timbre TTS) ---------------------------------------
GNANI_BASE_URL = get("GNANI_BASE_URL", "https://api.vachana.ai")
STT_MODEL = get("GNANI_STT_MODEL", "prisma-v3.0")      # set to "prisma-v2.5" to use the default v2.5 model
STT_LANGUAGES = get("GNANI_STT_LANGUAGES", "hi-IN,en-IN")
STT_FORMAT = get("GNANI_STT_FORMAT", "codemix")        # codemix keeps English words in Latin script
TTS_MODEL = get("GNANI_TTS_MODEL", "timbre-v2.5")
TTS_VOICE_HI = get("GNANI_TTS_VOICE_HI", "Nalini")     # Hindi voice (from Gnani docs)
TTS_VOICE_EN = get("GNANI_TTS_VOICE_EN", "Kaveri")     # English voice (from Gnani docs)
TTS_SAMPLE_RATE = int(get("GNANI_TTS_SAMPLE_RATE", "24000"))

# --- Optional: Evon (open weights, self-hosted behind an OpenAI-compatible server) ---
EVON_BASE_URL = get("EVON_BASE_URL")                   # e.g. http://localhost:8000/v1
EVON_MODEL = get("EVON_MODEL", "gnani-ai/evon")
EVON_API_KEY = get("EVON_API_KEY")

INSTITUTE_NAME = get("INSTITUTE_NAME", "the institute")
CACHE_DIR = BASE_DIR / "cache"
MAX_UPLOAD_BYTES = 8 * 1024 * 1024
