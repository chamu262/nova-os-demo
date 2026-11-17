"""The team: Nova Prime takes every request, routes it, and keeps the shared state."""
import itertools
import json
import threading
import time
from typing import Dict, List

from . import demo_data as d
from .agents import ALL, BY_ID, PRIME
from .llm import MockLLM, make_llm, morning_brief
from .router import ROUTER_PROMPT, parse_choice, route_by_keywords

CONTEXT = {
    "sterling": {"bills": d.BILLS, "subscriptions": d.SUBSCRIPTIONS, "spending": d.SPENDING, "budget": d.BUDGET},
    "tempo": {"calendar": d.CALENDAR},
    "juno": {"inbox": d.INBOX},
    "kai": {"health": d.HEALTH},
    "axel": {"home": d.HOME},
    "byte": {"devices": d.DEVICES},
}

# Phrases that turn into a decision the user must approve. Money always needs a yes.
DECISION_TRIGGERS = {
    "sterling": ("subscription", "Cancel 2 idle subscriptions (save $28.98/mo)"),
    "juno": ("reply", "Send drafted reply to Sam"),
}


class Team:
    def __init__(self, llm=None):
        self.llm = llm or make_llm()
        self.lock = threading.Lock()
        self._ids = itertools.count(1)
        self.decisions: List[Dict] = [
            {"id": next(self._ids), "agent": "sterling", "text": "Pay electricity bill ($82.40, due Nov 21)", "status": "waiting"},
            {"id": next(self._ids), "agent": "tempo", "text": "Move dentist to Friday 10:00?", "status": "waiting"},
        ]
        self.activity: List[Dict] = []
        self.status = {a.id: "idle" for a in ALL}

    # --- routing -----------------------------------------------------------
    def route(self, message: str):
        aid, reason = route_by_keywords(message)
        if not isinstance(self.llm, MockLLM):
            try:
                pick = parse_choice(self.llm.choose(ROUTER_PROMPT, message))
                if pick:
                    aid, reason = pick, f"Claude picked {BY_ID[pick].name}."
            except Exception as exc:  # network trouble: keep the keyword choice
                reason += f" (Claude router unavailable: {type(exc).__name__})"
        return aid, reason

    def handle(self, message: str) -> Dict:
        message = (message or "").strip()
        if not message:
            raise ValueError("empty message")
        aid, reason = self.route(message)
        agent = BY_ID[aid]
        self._log("prime", f"Routed “{message[:48]}” to {agent.name}")
        system = agent.persona + "\nUse only this (made-up demo) data where relevant:\n" + json.dumps(CONTEXT.get(aid, {}))
        if aid == PRIME.id and not isinstance(self.llm, MockLLM) and "brief" in message.lower():
            system += "\nToday's summary:\n" + morning_brief()
        try:
            reply = self.llm.complete(aid, system, message)
        except Exception as exc:
            reply = MockLLM().complete(aid, system, message) + f"\n\n_(Claude unavailable: {type(exc).__name__}; showing mock answer.)_"
        decision = None
        trig = DECISION_TRIGGERS.get(aid)
        if trig and trig[0] in message.lower():
            decision = self.add_decision(aid, trig[1])
        self._log(aid, f"Answered: {reply.splitlines()[0][:60]}")
        return {"agent": aid, "agent_name": agent.name, "reason": reason, "reply": reply,
                "decision": decision, "mode": self.llm.name}

    # --- decisions ("Needs you") --------------------------------------------
    def add_decision(self, agent_id: str, text: str) -> Dict:
        with self.lock:
            for x in self.decisions:
                if x["text"] == text and x["status"] == "waiting":
                    return x
            item = {"id": next(self._ids), "agent": agent_id, "text": text, "status": "waiting"}
            self.decisions.append(item)
        return item

    def decide(self, decision_id: int, approve: bool) -> Dict:
        with self.lock:
            for x in self.decisions:
                if x["id"] == decision_id:
                    if x["status"] != "waiting":
                        raise ValueError("already decided")
                    x["status"] = "approved" if approve else "declined"
                    self._log(x["agent"], f"{x['status'].title()} by you: {x['text']}")
                    return x
        raise KeyError(decision_id)

    def _log(self, agent_id: str, text: str):
        self.activity.insert(0, {"agent": agent_id, "text": text, "at": time.strftime("%H:%M")})
        del self.activity[30:]

    def snapshot(self) -> Dict:
        return {
            "mode": self.llm.name,
            "agents": [{"id": a.id, "name": a.name, "role": a.role, "color": a.color, "emoji": a.emoji} for a in ALL],
            "decisions": self.decisions,
            "activity": self.activity,
            "today": d.CALENDAR,
        }
