# Telegram bot (Python)

Telegram bot using long polling. It supports `/start`, `/help`, `/menu`, `/id`, `/time` (UTC), `/dice`, `/random [maximum]`, and `/feedback`. Feedback is forwarded to the admin's Telegram account by numeric user ID.

## Setup

Create a bot with [@BotFather](https://t.me/BotFather), then set `TELEGRAM_BOT_TOKEN` and the admin's numeric `ADMIN_ID` in `bot-python/.env`. The admin must open the bot and press Start once. Keep `.env` private.

Requires Python 3.10 or later. No third-party packages are needed.

Run from the project root with:

```powershell
.\run.ps1
```

Or run `python bot.py` from `bot-python` after loading the variables from `.env` into your shell.
