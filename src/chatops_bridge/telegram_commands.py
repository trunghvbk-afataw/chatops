from __future__ import annotations


def parse_telegram_command(text: str) -> tuple[str, list[str]]:
    """Parse /command args from Telegram message text.

    Supports bot mentions such as /status@my_bot.
    """
    raw = (text or "").strip()
    if not raw.startswith("/"):
        return "", []
    parts = raw.split()
    if not parts:
        return "", []
    cmd_token = parts[0][1:].strip().lower()
    cmd = cmd_token.split("@", 1)[0]
    args = parts[1:]
    return cmd, args
