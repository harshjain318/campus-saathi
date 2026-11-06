"""Offline tests (no Gnani calls). Run from the project folder:  python -m unittest discover -s tests -v"""
import base64
import pathlib
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import answer  # noqa: E402
import gnani_client  # noqa: E402
from knowledge import Knowledge, detect_language  # noqa: E402


class RetrievalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kb = Knowledge()

    def top(self, question):
        return self.kb.best(question)[1]

    def test_english_questions(self):
        cases = {
            "When does the library open?": "library",
            "How do I pay my semester fees?": "fees",
            "I lost my ID card, what should I do?": "id_card",
            "How can I apply for a scholarship?": "scholarship",
            "My Wi-Fi is not working": "wifi",
            "How do I report ragging?": "ragging",
            "Where can I see exam results?": "exams",
        }
        for question, expected in cases.items():
            with self.subTest(question):
                entry = self.top(question)
                self.assertIsNotNone(entry)
                self.assertEqual(entry["id"], expected)

    def test_hindi_devanagari_questions(self):
        cases = {
            "लाइब्रेरी कब खुलती है?": "library",
            "सेमेस्टर की फीस कैसे जमा करें?": "fees",
            "मेरा आईडी कार्ड खो गया है": "id_card",
            "स्कॉलरशिप के लिए आवेदन कैसे करें": "scholarship",
            "मेरा वाई-फाई नहीं चल रहा है": "wifi",
            "मेस के खाने की शिकायत कहाँ करें": "mess",
        }
        for question, expected in cases.items():
            with self.subTest(question):
                entry = self.top(question)
                self.assertIsNotNone(entry)
                self.assertEqual(entry["id"], expected)

    def test_romanised_hinglish(self):
        cases = {
            "library kab khulti hai": "library",
            "hostel mein room ki problem hai": "hostel",
            "scholarship ka form kaise bharein": "scholarship",
        }
        for question, expected in cases.items():
            with self.subTest(question):
                entry = self.top(question)
                self.assertIsNotNone(entry)
                self.assertEqual(entry["id"], expected)

    def test_typo_tolerance(self):
        self.assertEqual(self.top("when does the librery open")["id"], "library")

    def test_unrelated_question_falls_back(self):
        self.assertIsNone(self.top("who won the cricket world cup"))
        self.assertEqual(answer.respond("who won the cricket world cup")["engine"], "fallback")

    def test_language_detection(self):
        self.assertEqual(detect_language("लाइब्रेरी कब खुलती है"), "hi")
        self.assertEqual(detect_language("when does the library open"), "en")

    def test_hindi_answer_for_hindi_question(self):
        result = answer.respond("फीस कैसे जमा करें")
        self.assertEqual(result["lang"], "hi")
        self.assertEqual(result["entry_id"], "fees")


class ServerTests(unittest.TestCase):
    def setUp(self):
        from fastapi.testclient import TestClient
        import server

        self.client = TestClient(server.app)

    def test_health_and_faq(self):
        self.assertTrue(self.client.get("/api/health").json()["ok"])
        self.assertGreater(len(self.client.get("/api/faq").json()["suggestions"]), 5)

    def test_voice_flow_with_mocked_gnani(self):
        fake_wav = b"RIFF....WAVEfake"
        with mock.patch.object(gnani_client, "transcribe", return_value={"transcript": "लाइब्रेरी कब खुलती है", "detected_language_code": "hi-IN"}), \
             mock.patch.object(gnani_client, "synthesize", return_value=fake_wav):
            r = self.client.post("/api/ask", files={"audio": ("q.wav", b"x" * 100, "audio/wav")})
        body = r.json()
        self.assertEqual(r.status_code, 200)
        self.assertTrue(body["ok"])
        self.assertEqual(body["lang"], "hi")
        self.assertEqual(base64.b64decode(body["audio_b64"]), fake_wav)
        self.assertEqual(body["models"]["tts"], "timbre-v2.5")

    def test_tts_failure_still_returns_text(self):
        with mock.patch.object(gnani_client, "synthesize", side_effect=gnani_client.GnaniError("boom")):
            body = self.client.post("/api/ask-text", json={"text": "how do I pay fees"}).json()
        self.assertTrue(body["ok"])
        self.assertIsNone(body["audio_b64"])
        self.assertIn("boom", body["tts_error"])

    def test_silence_returns_friendly_error(self):
        with mock.patch.object(gnani_client, "transcribe", return_value={"transcript": ""}):
            body = self.client.post("/api/ask", files={"audio": ("q.wav", b"x" * 100, "audio/wav")}).json()
        self.assertFalse(body["ok"])
        self.assertEqual(body["error"], "no_speech")

    def test_missing_key_is_reported(self):
        with mock.patch.dict("os.environ", {"GNANI_API_KEY": ""}):
            r = self.client.post("/api/ask", files={"audio": ("q.wav", b"x" * 100, "audio/wav")})
        self.assertEqual(r.status_code, 401)


if __name__ == "__main__":
    unittest.main()
