# chatops-bridge

Reusable Telegram and Discord utilities for Python applications.

This package was extracted from production automation code and generalized for multi-purpose ChatOps use.
Transport-level Telegram/Discord sending is reused from `awesome-notify-bridge`.

## Features

- Telegram send/poll helpers:
  - send text and images
  - split long text by Telegram limit
  - poll updates and extract message text
  - robust chat id matching
- Discord webhook sender:
  - send message chunks safely
  - upload image files
- Discord slash bot:
  - register any slash commands dynamically
  - optional owner and guild restriction
- Plain text formatter helpers for chat-friendly output

## Install

Requires Python 3.9+.

```bash
pip install chatops-bridge
```

For slash-bot support:

```bash
pip install "chatops-bridge[discord-bot]"
```

Install from GitHub:

```bash
pip install git+https://github.com/<your-org>/chatops-bridge.git
```

## Quick Start

### Telegram

```python
from chatops_bridge.telegram import send_telegram_message

send_telegram_message(
    chat_id="123456789",
    token="<telegram-bot-token>",
    text="Hello from chatops-bridge",
)
```

Send with images:

```python
send_telegram_message(
  chat_id="123456789",
  token="<telegram-bot-token>",
  text="Report attached",
  image_paths=["./charts/btc.png", "./charts/eth.png"],
)
```

### Discord webhook

```python
from chatops_bridge.discord import send_discord_message

send_discord_message(
    webhook_url="https://discord.com/api/webhooks/...",
    content="Hello from chatops-bridge",
)
```

Return value is `True` on success and `False` on failure.

### Discord env-based channel

```python
from chatops_bridge.discord_channels import send_to_discord_env_channel

# export DISCORD_ALERT_WEBHOOK_URL=...
send_to_discord_env_channel("DISCORD_ALERT_WEBHOOK_URL", "Alert triggered")

# strict mode: fail fast if env var is missing
send_to_discord_env_channel("DISCORD_ALERT_WEBHOOK_URL", "Alert triggered", strict_env=True)
```

Useful when you want channel routing from environment variables instead of hardcoding webhook URLs.

## Telegram Update Polling

```python
from chatops_bridge.telegram import fetch_telegram_updates, extract_update_text

updates = fetch_telegram_updates(
    token="<telegram-bot-token>",
    offset=None,
    timeout_seconds=10,
    allowed_updates=["message", "edited_message"],
)

for update in updates:
    text, message = extract_update_text(update)
    if text:
        print("message:", text)
```

## Discord Slash Bot

`chatops_bridge.discord_bot.start_discord_bot(...)` starts a background thread for a Discord bot using your command list.

```python
import discord

from chatops_bridge.discord_bot import DiscordBotConfig, SlashCommandSpec, start_discord_bot

def ping() -> str:
  return "pong"

def report() -> dict:
  return {"text": "Report done", "image_paths": ["./out/chart.png"]}

start_discord_bot(
  token="<discord-bot-token>",
  commands=[
    SlashCommandSpec(name="ping", description="Health check", handler=ping),
    SlashCommandSpec(name="report", description="Generate report", handler=report),
  ],
  config=DiscordBotConfig(
    intents=discord.Intents(guilds=True),
    allow_dm_commands=False,
    leave_unexpected_guild=True,
    response_chunk_limit=1900,
    max_images_per_response=10,
    defer_thinking=True,
  ),
  guild_id=None,
  owner_user_id=None,
  instance_key="primary",
)
```

You can also run the bot with `commands=[]` (or omit `commands`) when your app only needs Discord client events/background tasks.

`instance_key` is used to manage bot thread instances by key. Calling `start_discord_bot` again with the same key returns the existing live thread.

## Slash Bot Example

See [examples/discord_bot_example.py](examples/discord_bot_example.py).

## Telegram Poller Bot

`chatops_bridge.telegram_poller.start_telegram_poller(...)` starts a background polling thread that automatically handles Telegram updates and dispatches them to your command handlers.

```python
from chatops_bridge.telegram_poller import TelegramCommandSpec, TelegramPollerConfig, start_telegram_poller

def handle_status(args: list[str]) -> str:
    return "Status: OK"

def handle_trade(args: list[str]) -> str:
    amount = float(args[0]) if args else 100.0
    return f"Trading {amount} units"

start_telegram_poller(
    token="<telegram-bot-token>",
    commands=[
        TelegramCommandSpec(
            name="status",
            description="Get bot status",
            handler=handle_status,
        ),
        TelegramCommandSpec(
            name="trade",
            description="Execute trade",
            handler=handle_trade,
        ),
    ],
    config=TelegramPollerConfig(
        poll_timeout_seconds=30,
        max_retries=3,
        retry_delay_seconds=5,
        allowed_updates=["message", "edited_message"],
        offset_file="/tmp/telegram_offset.txt",  # Persist offset on restart
    ),
    logger=print,  # Optional logger
)
```

The poller:
- Runs in background thread(s)
- Automatically saves offset to persist progress across restarts
- Retries on network errors with configurable backoff
- Filters update types (e.g., messages only, skip reactions)
- Parses `/command arg1 arg2` style messages
- Dispatches to appropriate handler
- Sends response back to the originating chat

Handlers receive a list of arguments and return `str` or `dict` (JSON-serialized if dict).

## Telegram Poller Example

See [examples/telegram_poller_example.py](examples/telegram_poller_example.py).

## Common Environment Variables

- `DISCORD_BOT_TOKEN`: bot token used by the slash-bot example.
- `DISCORD_BOT_GUILD_ID`: optional guild restriction.
- `DISCORD_BOT_OWNER_USER_ID`: optional owner-only restriction.
- `TELEGRAM_BOT_TOKEN`: polling bot token.
- `TELEGRAM_BOT_OFFSET_FILE`: optional path to persist polling offset (for restart safety).
- Custom webhook URL variables (for env-based routing), for example:
  - `DISCORD_ALERT_WEBHOOK_URL`
  - `DISCORD_SIGNAL_WEBHOOK_URL`

## License

MIT

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup
- Making changes and submitting PRs
- Release procedures

For questions, open an issue on [GitHub](https://github.com/trunghvbk-afataw/chatops/issues).
