"""The crew: Nova Prime (the lead) and the specialists it hands work to."""
from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class Agent:
    id: str
    name: str
    role: str
    color: str
    emoji: str
    keywords: List[str] = field(default_factory=list)
    persona: str = ""


PRIME = Agent(
    id="prime", name="Nova Prime", role="Lead, chief of staff", color="#7c5cff", emoji="✦",
    persona="You are Nova Prime, a calm and warm chief of staff. You answer general questions "
            "and say plainly when a specialist would help.",
)

SPECIALISTS = [
    Agent("sterling", "Sterling", "Money: budget, bills, spending", "#22c55e", "$",
          ["money", "budget", "spend", "spent", "bill", "bills", "pay", "payment", "cost",
           "subscription", "subscriptions", "save", "savings", "invoice", "rent", "bank"],
          "You are Sterling, a careful money specialist. You never move money yourself: "
          "any payment becomes a decision for the user to approve."),
    Agent("tempo", "Tempo", "Time: calendar, schedule, focus", "#f59e0b", "◷",
          ["calendar", "meeting", "meetings", "schedule", "today", "tomorrow",
           "free", "busy", "remind", "reminder", "time", "focus", "appointment"],
          "You are Tempo, who guards the user's time and plans their days."),
    Agent("juno", "Juno", "Comms: inbox, replies, messages", "#38bdf8", "✉",
          ["email", "emails", "inbox", "reply", "message", "messages", "draft", "write",
           "text", "letter", "mail"],
          "You are Juno, who triages messages and drafts short, friendly replies."),
    Agent("kai", "Kai", "Health: sleep, movement, habits", "#f472b6", "♥",
          ["sleep", "run", "running", "workout", "gym", "health", "steps", "walk", "habit",
           "water", "tired", "exercise", "diet"],
          "You are Kai, an encouraging health coach. You give general wellbeing tips, not medical advice."),
    Agent("axel", "Axel", "Home and car: upkeep, repairs", "#fb7185", "⌂",
          ["car", "oil", "tire", "tires", "service", "home", "house", "repair", "fix",
           "plumber", "filter", "garden", "warranty"],
          "You are Axel, who keeps the home and car in good shape and tracks upkeep."),
    Agent("byte", "Byte", "Tech: devices, accounts, automation", "#a3e635", "⌘",
          ["laptop", "computer", "wifi", "password", "passwords", "backup", "update",
           "phone", "script", "automate", "automation", "printer", "router", "2fa"],
          "You are Byte, a practical tech helper for devices, accounts and small automations."),
]

ALL = [PRIME] + SPECIALISTS
BY_ID = {a.id: a for a in ALL}
