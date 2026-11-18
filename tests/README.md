# `tests/`: automated checks

Run them from the repo root with:

```bash
python3 -m unittest -v
```

They use only the standard library, need no API key, and never call the internet. CI (`.github/workflows/ci.yml`) runs the same command on Python 3.10 and 3.13.

## Files

- `__init__.py`: empty. It lets Python find the tests.
- `test_nova.py`: all the tests, grouped by what they check:
  - **RouterTests**: questions go to the right agent; unknown questions and ties stay with Nova Prime; Claude's pick is read correctly.
  - **TeamTests**: a full request gives the right answer in mock mode; asking about subscriptions creates exactly one decision; approve and decline work, and a decision can't be decided twice; empty messages are rejected; the morning brief covers every specialist.
  - **ClaudeModeTests**: uses a fake API (no network) to check the request Claude mode sends and that Claude's pick is followed. When the API fails, the app falls back to the mock answer.
  - **ServerTests**: starts the real server on a free port and checks the page, `/api/state`, `/api/chat`, the decisions endpoint, and that an empty message gets a 400 error.
