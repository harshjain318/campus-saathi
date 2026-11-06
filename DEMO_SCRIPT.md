# Demo video script

The Google Form needs a **2-3 minute** video of the build. For the post and the "best 60-second demo" award, cut the 60-second version from it (marked ⭐ below). Record your screen with your voice (QuickTime on Mac, Win+G on Windows, or OBS). Use Chrome at full screen, 1080p.

**Before recording:** run `python cli.py --selftest` once (it warms the cache), start the server, ask each question you plan to show once so replies are cached and play instantly, and close other tabs. Use headphones to stop the speaker reply feeding back into the mic.

## Timeline (about 2 min 30 s)

| Time | On screen | Say |
|---|---|---|
| 0:00 ⭐ | Title card or the app homepage | "I'm Harsh, a student at MANIT Bhopal. Finding a simple answer on campus, like how to pay fees, can take hours. So I built Campus Saathi, a voice helpdesk that answers in Hindi, Hinglish and English, powered by Gnani AI's Prisma and Timbre." |
| 0:15 ⭐ | Tap the mic and ask in Hinglish: *"Scholarship ka form kaise bharein?"* | (speak the question) |
| 0:25 ⭐ | The three steps light up, then the answer appears and the voice plays | "Prisma transcribes my Hinglish, the app finds the verified answer, and Timbre speaks it back in a natural Hindi voice." |
| 0:45 ⭐ | Ask in English: *"I lost my ID card, what should I do?"* | "Same app, English question, English voice reply." |
| 1:00 ⭐ | Point at the timing chips under the answer | "You can see the latency for each Gnani model right here." |
| 1:10 | Ask something it doesn't know: *"Who won the cricket match?"* | "If it doesn't know, it says so and points to the right office instead of guessing." |
| 1:30 | Click a Hindi sample chip (switch to हिन्दी) | "Students can also tap sample questions, or type if a mic isn't available." |
| 1:45 | Show the code editor with `data/faq.json` | "A college only edits this one file to publish its own answers." |
| 2:05 | Show `gnani_client.py` (the two endpoints) | "Under the hood: Prisma v3.0 for speech to text and Timbre v2.5 for text to speech, with retries and a cache to save credits." |
| 2:25 ⭐ | Back to the app | "Campus Saathi makes campus information as easy as asking a friend. Code and pitch are in the link. Thank you, Gnani AI." |

## Tips for engagement (selection uses verified engagement on your post)
- Put the 60-second cut as a native video upload on LinkedIn or X (not just a link), with captions on.
- Hook in the first 3 seconds: start by asking the question out loud.
- Post between 8 and 10 PM IST on a weekday, and ask classmates, your department group and mentors to react and comment in the first hour.
