"""Two brains with the same interface: a mock one (no key needed) and Claude.

Claude mode is used when ANTHROPIC_API_KEY is set and NOVA_MODE is not "mock".
"""
import json
import os
import urllib.request
from typing import Optional

from . import demo_data as d

API_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = "claude-sonnet-5-5"


class MockLLM:
    name = "mock"

    def complete(self, agent_id: str, system: str, user: str) -> str:
        fn = getattr(self, "_" + agent_id, self._prime)
        return fn(user.lower())

    def choose(self, system: str, user: str) -> str:  # routing handled by keywords in mock mode
        return ""

    def _prime(self, q: str) -> str:
        if "brief" in q or "day" in q or "plan" in q:
            return morning_brief()
        return ("Happy to help. I lead a small team: Sterling (money), Tempo (time), Juno (messages), "
                "Kai (health), Axel (home and car) and Byte (tech). Ask about any of those and I'll "
                "pass it to the right person, or say \"morning brief\" for today's summary.")

    def _sterling(self, q: str) -> str:
        if "subscription" in q:
            idle = [s for s in d.SUBSCRIPTIONS if s["last_used_days"] > 30]
            save = sum(s["amount"] for s in idle)
            lines = [f"- {s['name']}: ${s['amount']:.2f}/mo, unused for {s['last_used_days']} days" for s in idle]
            return ("You have %d subscriptions. Two look idle:\n%s\nCancelling both saves $%.2f a month. "
                    "I've added this to **Needs you** so nothing changes until you say so."
                    % (len(d.SUBSCRIPTIONS), "\n".join(lines), save))
        if "bill" in q or "pay" in q:
            total = sum(b["amount"] for b in d.BILLS)
            lines = [f"- {b['name']}: ${b['amount']:.2f}, due {b['due']}" for b in d.BILLS]
            return ("Upcoming bills (total $%.2f):\n%s\nI never pay on my own. Each payment waits in "
                    "**Needs you** for your OK." % (total, "\n".join(lines)))
        over = [(k, v, d.BUDGET[k]) for k, v in d.SPENDING.items() if v > d.BUDGET[k]]
        spent, budget = sum(d.SPENDING.values()), sum(d.BUDGET.values())
        msg = f"This month you've spent ${spent} of a ${budget} budget."
        for k, v, b in over:
            msg += f" {k} is over by ${v - b}."
        return msg + " Everything else is on track."

    def _tempo(self, q: str) -> str:
        lines = [f"- {e['time']} {e['title']}" for e in d.CALENDAR]
        return ("Here's today:\n%s\nYou're free 10:30–12:30 and 16:00–18:00. Want me to protect one of "
                "those as a focus block?" % "\n".join(lines))

    def _juno(self, q: str) -> str:
        if "reply" in q or "draft" in q or "sam" in q:
            return ("Draft reply to Sam:\n> Hi Sam! Yes, still on for 12:30. See you at the usual place.\n"
                    "I'll keep it in drafts until you approve sending it.")
        urgent = [m for m in d.INBOX if m["urgent"]]
        lines = [f"- {m['from']}: {m['subject']}" for m in urgent]
        return ("%d new messages, %d need attention:\n%s\nThe rest can wait. Want a draft reply to any?"
                % (len(d.INBOX), len(urgent), "\n".join(lines)))

    def _kai(self, q: str) -> str:
        s = d.HEALTH["sleep_hours"]
        avg = sum(s) / len(s)
        left = d.HEALTH["steps_goal"] - d.HEALTH["steps_today"]
        return (f"Sleep averaged {avg:.1f} h this week (lowest {min(s)} h). You're {left} steps from "
                "today's goal, and the 18:30 easy run will cover it. Tonight, try screens off by 22:30.")

    def _axel(self, q: str) -> str:
        lines = [f"- {h['item']}: {h['due']}" for h in d.HOME]
        return ("Home and car upkeep:\n%s\nThe fridge filter is overdue; I can add it to your shopping list."
                % "\n".join(lines))

    def _byte(self, q: str) -> str:
        lines = [f"- {x['device']}: {x['note']}" for x in d.DEVICES]
        return ("Device check:\n%s\nYour phone backup is the one to fix first: plug in tonight on Wi-Fi "
                "and it will run on its own." % "\n".join(lines))


def morning_brief() -> str:
    spent, budget = sum(d.SPENDING.values()), sum(d.BUDGET.values())
    urgent = sum(1 for m in d.INBOX if m["urgent"])
    return ("Good morning! Here's your brief:\n"
            f"- **Tempo:** {len(d.CALENDAR)} things today, first real one at {d.CALENDAR[1]['time']}.\n"
            f"- **Sterling:** ${spent} of ${budget} spent this month; 2 idle subscriptions found.\n"
            f"- **Juno:** {urgent} messages need you (landlord, car garage).\n"
            "- **Kai:** sleep is a little short this week; easy run at 18:30.\n"
            "- **Axel:** fridge filter is overdue.\n"
            "- **Byte:** phone backup is 9 days old.")


class ClaudeLLM:
    name = "claude"

    def __init__(self, api_key: str, model: Optional[str] = None, opener=urllib.request.urlopen):
        self.api_key = api_key
        self.model = model or os.environ.get("NOVA_MODEL", DEFAULT_MODEL)
        self._open = opener

    def _call(self, system: str, user: str, max_tokens: int) -> str:
        body = json.dumps({
            "model": self.model, "max_tokens": max_tokens, "system": system,
            "messages": [{"role": "user", "content": user}],
        }).encode()
        req = urllib.request.Request(API_URL, data=body, method="POST", headers={
            "x-api-key": self.api_key, "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        })
        with self._open(req, timeout=60) as resp:
            data = json.loads(resp.read())
        return "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")

    def choose(self, system: str, user: str) -> str:
        return self._call(system, user, 16)

    def complete(self, agent_id: str, system: str, user: str) -> str:
        return self._call(system, user, 600)


def make_llm():
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if key and os.environ.get("NOVA_MODE", "").lower() != "mock":
        return ClaudeLLM(key)
    return MockLLM()
