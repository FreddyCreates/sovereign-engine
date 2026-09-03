# Sovereign Books web UI

Next.js + shadcn/ui + [dither-kit](https://www.tripwire.sh/dither-kit).

## Layout

- **Left** — collapsible nav (Dashboard, Books, Chat, Grants, Settings)
- **Center** — main view
- **Right** — artifacts preview pane (opens from chat / grants / books)

Theme is forced dark, monochrome (black / grey / white only).

## Run

```bash
# Terminal 1 — books API (Plaid + SQLite)
cd .. && .venv/bin/python sovereign_dashboard_server.py

# Terminal 2 — UI
cd web && npm run dev
```

Open http://localhost:3000

Optional: `NEXT_PUBLIC_BOOKS_API=http://localhost:8090` (default).
