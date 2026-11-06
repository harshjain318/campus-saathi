"""Command line access to the same pipeline.

  python cli.py --selftest                 # end-to-end check: Timbre speaks a question, Prisma hears it, answer is spoken back
  python cli.py --audio question.wav       # ask with a recording (max 30 seconds)
  python cli.py --text "library kab khulti hai"
"""
import argparse
import pathlib
import sys

import answer
import gnani_client

SELFTEST_QUESTIONS = [
    ("en", "How do I pay my semester fees?"),
    ("hi", "लाइब्रेरी कब खुलती है?"),
]


def run_pipeline(transcript: str, out: pathlib.Path) -> None:
    result = answer.respond(transcript)
    print(f"  topic      : {result['title']} (engine={result['engine']}, score={result['score']})")
    print(f"  answer     : {result['text']}")
    audio = gnani_client.synthesize(result["text"], result["lang"])
    out.write_bytes(audio)
    print(f"  spoken (Timbre) -> {out}")


def selftest() -> int:
    ok = True
    for i, (lang, question) in enumerate(SELFTEST_QUESTIONS, start=1):
        print(f"\n[{i}] Question ({lang}): {question}")
        spoken = gnani_client.synthesize(question, lang)
        pathlib.Path(f"selftest_question_{i}.wav").write_bytes(spoken)
        stt = gnani_client.transcribe(spoken, "selftest.wav")
        print(f"  heard (Prisma, {stt.get('model')}): {stt['transcript']!r}")
        if not stt["transcript"]:
            ok = False
            continue
        run_pipeline(stt["transcript"], pathlib.Path(f"selftest_answer_{i}.wav"))
    print("\nSelf-test", "passed" if ok else "had problems")
    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Campus Saathi CLI")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--audio")
    parser.add_argument("--text")
    parser.add_argument("--out", default="reply.wav")
    args = parser.parse_args()

    try:
        if args.selftest:
            return selftest()
        if args.audio:
            path = pathlib.Path(args.audio)
            stt = gnani_client.transcribe(path.read_bytes(), path.name)
            print(f"Heard: {stt['transcript']!r}")
            run_pipeline(stt["transcript"], pathlib.Path(args.out))
            return 0
        if args.text:
            run_pipeline(args.text, pathlib.Path(args.out))
            return 0
    except gnani_client.GnaniError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
