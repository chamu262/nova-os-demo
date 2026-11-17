"""Nova Prime's routing: decide which specialist should take a request.

Mock mode scores keywords. Claude mode asks the model to pick, and falls back
to keywords if the answer is not a known agent id.
"""
import re
from typing import Dict, List, Tuple

from .agents import BY_ID, PRIME, SPECIALISTS


def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def score(text: str) -> Dict[str, int]:
    words = tokenize(text)
    return {a.id: sum(words.count(k) for k in a.keywords) for a in SPECIALISTS}


def route_by_keywords(text: str) -> Tuple[str, str]:
    """Return (agent_id, reason). Ties and zero scores stay with Nova Prime."""
    scores = score(text)
    best = max(scores.values()) if scores else 0
    if best == 0:
        return PRIME.id, "No specialist keywords matched, so Nova Prime answers directly."
    leaders = [aid for aid, s in scores.items() if s == best]
    if len(leaders) > 1:
        names = " and ".join(BY_ID[a].name for a in leaders)
        return PRIME.id, f"Tie between {names}, so Nova Prime answers and coordinates."
    aid = leaders[0]
    hits = sorted({w for w in tokenize(text) if w in BY_ID[aid].keywords})
    return aid, f"Matched {', '.join(hits)} → {BY_ID[aid].name}."


ROUTER_PROMPT = (
    "You are Nova Prime, the lead of a personal AI team. Pick the single best team member "
    "for the user's request. Reply with only their id. Options:\n"
    + "\n".join(f"- {a.id}: {a.role}" for a in [PRIME] + SPECIALISTS)
)


def parse_choice(reply: str) -> str:
    for word in tokenize(reply):
        if word in BY_ID:
            return word
    return ""
