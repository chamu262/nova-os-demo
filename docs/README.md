# `docs/`: images for the READMEs

- `screenshots/`: pictures of the running app, all using made-up demo data.

| File | Shows |
|---|---|
| `hero.png` | The main screen after "Morning brief" and a question about subscriptions. Sterling has added a decision to "Needs you". |
| `calendar.png` | A calendar question routed to Tempo. |
| `reply.png` | Juno drafting a reply that waits for approval. |
| `decisions.png` | The routing line on each answer, plus one decision already approved. |
| `phone.png` | The layout on a phone-sized screen. |

They were taken with headless Chrome and the `?ask=` address trick described in [../nova/static/README.md](../nova/static/README.md). To retake them, start the app with `python3 -m nova` and capture the same views.
