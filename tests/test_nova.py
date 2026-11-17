import io
import json
import threading
import unittest
import urllib.request
from http.server import ThreadingHTTPServer

from nova.llm import ClaudeLLM, MockLLM
from nova.router import parse_choice, route_by_keywords
from nova.server import make_handler
from nova.team import Team


class RouterTests(unittest.TestCase):
    def test_routes_to_specialists(self):
        cases = {
            "How much did I spend on my budget?": "sterling",
            "What's on my calendar tomorrow?": "tempo",
            "Draft a reply to that email": "juno",
            "How did I sleep?": "kai",
            "How did I sleep this week?": "kai",
            "When is the car oil change?": "axel",
            "Is my laptop backup done?": "byte",
        }
        for text, want in cases.items():
            self.assertEqual(route_by_keywords(text)[0], want, text)

    def test_unknown_and_ties_stay_with_prime(self):
        self.assertEqual(route_by_keywords("Tell me a joke")[0], "prime")
        aid, reason = route_by_keywords("calendar budget")
        self.assertEqual(aid, "prime")
        self.assertIn("Tie", reason)

    def test_parse_choice(self):
        self.assertEqual(parse_choice("kai"), "kai")
        self.assertEqual(parse_choice("I'd pick Sterling."), "sterling")
        self.assertEqual(parse_choice("nobody"), "")


class TeamTests(unittest.TestCase):
    def setUp(self):
        self.team = Team(llm=MockLLM())

    def test_handle_returns_routed_reply(self):
        r = self.team.handle("What's on my calendar today?")
        self.assertEqual(r["agent"], "tempo")
        self.assertIn("Lunch with Sam", r["reply"])
        self.assertEqual(r["mode"], "mock")

    def test_money_move_creates_decision_once(self):
        r1 = self.team.handle("Any subscriptions I don't use?")
        r2 = self.team.handle("Cancel those subscriptions")
        self.assertIsNotNone(r1["decision"])
        self.assertEqual(r1["decision"]["id"], r2["decision"]["id"])
        self.assertEqual(r1["decision"]["status"], "waiting")

    def test_decide(self):
        did = self.team.decisions[0]["id"]
        self.assertEqual(self.team.decide(did, True)["status"], "approved")
        with self.assertRaises(ValueError):
            self.team.decide(did, False)
        with self.assertRaises(KeyError):
            self.team.decide(999, True)

    def test_empty_message_rejected(self):
        with self.assertRaises(ValueError):
            self.team.handle("   ")

    def test_morning_brief_mentions_every_specialist(self):
        reply = self.team.handle("Morning brief")["reply"]
        for name in ["Tempo", "Sterling", "Juno", "Kai", "Axel", "Byte"]:
            self.assertIn(name, reply)


class FakeResp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class ClaudeModeTests(unittest.TestCase):
    def test_request_shape_and_routing(self):
        sent = []

        def opener(req, timeout=0):
            sent.append(json.loads(req.data))
            self.assertEqual(req.get_header("X-api-key"), "test-key")
            text = "axel" if len(sent) == 1 else "Oil change is due soon."
            return FakeResp(json.dumps({"content": [{"type": "text", "text": text}]}).encode())

        team = Team(llm=ClaudeLLM("test-key", model="test-model", opener=opener))
        r = team.handle("Something about my vehicle")
        self.assertEqual(r["agent"], "axel")
        self.assertEqual(r["reply"], "Oil change is due soon.")
        self.assertEqual(sent[0]["model"], "test-model")
        self.assertIn("demo", sent[1]["system"])

    def test_falls_back_to_mock_when_api_fails(self):
        def opener(req, timeout=0):
            raise OSError("offline")

        team = Team(llm=ClaudeLLM("k", opener=opener))
        r = team.handle("How did I sleep?")
        self.assertEqual(r["agent"], "kai")
        self.assertIn("Claude unavailable", r["reply"])


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(Team(llm=MockLLM())))
        cls.base = "http://127.0.0.1:%d" % cls.httpd.server_address[1]
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()

    def post(self, path, body):
        req = urllib.request.Request(self.base + path, data=json.dumps(body).encode(), method="POST",
                                     headers={"Content-Type": "application/json"})
        return json.loads(urllib.request.urlopen(req).read())

    def test_index_and_state(self):
        html = urllib.request.urlopen(self.base + "/").read().decode()
        self.assertIn("Nova OS", html)
        state = json.loads(urllib.request.urlopen(self.base + "/api/state").read())
        self.assertEqual(len(state["agents"]), 7)

    def test_chat_and_decide(self):
        r = self.post("/api/chat", {"message": "Is my phone backed up?"})
        self.assertEqual(r["agent"], "byte")
        d = self.post("/api/decisions/2", {"approve": False})
        self.assertEqual(d["status"], "declined")

    def test_bad_request(self):
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self.post("/api/chat", {"message": ""})
        self.assertEqual(ctx.exception.code, 400)


if __name__ == "__main__":
    unittest.main()
