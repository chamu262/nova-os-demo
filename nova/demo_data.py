"""Made-up demo data so the app works with no accounts connected. Nothing here is real."""

CALENDAR = [
    {"time": "08:00", "title": "Morning brief with Nova", "agent": "prime"},
    {"time": "09:30", "title": "Focus block: side project", "agent": "tempo"},
    {"time": "12:30", "title": "Lunch with Sam", "agent": "tempo"},
    {"time": "15:00", "title": "Dentist check-up", "agent": "kai"},
    {"time": "18:30", "title": "5 km easy run", "agent": "kai"},
]

BILLS = [
    {"name": "Rent", "amount": 1450.00, "due": "Dec 1"},
    {"name": "Electricity", "amount": 82.40, "due": "Nov 21"},
    {"name": "Phone plan", "amount": 35.00, "due": "Nov 24"},
]

SUBSCRIPTIONS = [
    {"name": "Video streaming", "amount": 15.99, "last_used_days": 41},
    {"name": "Music", "amount": 10.99, "last_used_days": 1},
    {"name": "Cloud storage", "amount": 2.99, "last_used_days": 3},
    {"name": "Fitness app", "amount": 12.99, "last_used_days": 63},
]

SPENDING = {"Groceries": 412, "Eating out": 186, "Transport": 94, "Fun": 120, "Home": 75}
BUDGET = {"Groceries": 450, "Eating out": 150, "Transport": 120, "Fun": 150, "Home": 100}

INBOX = [
    {"from": "Landlord", "subject": "Heating check on Thursday", "urgent": True},
    {"from": "Sam", "subject": "Lunch still on?", "urgent": False},
    {"from": "Bookshop", "subject": "Your order has shipped", "urgent": False},
    {"from": "Car garage", "subject": "Service reminder", "urgent": True},
]

HEALTH = {"sleep_hours": [7.1, 6.2, 6.8, 7.5, 5.9, 7.0, 7.3], "steps_today": 6240, "steps_goal": 9000}

HOME = [
    {"item": "Car oil change", "due": "in 400 km", "status": "soon"},
    {"item": "Smoke alarm battery", "due": "in 3 weeks", "status": "ok"},
    {"item": "Fridge water filter", "due": "overdue 5 days", "status": "late"},
]

DEVICES = [
    {"device": "Laptop", "note": "2 updates waiting", "status": "soon"},
    {"device": "Phone backup", "note": "last backup 9 days ago", "status": "late"},
    {"device": "Home router", "note": "firmware up to date", "status": "ok"},
]
