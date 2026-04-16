from __future__ import annotations

import os
from typing import Callable

from .discord import send_discord_message

LoggerFn = Callable[[str], None]


def send_to_discord_env_channel(
    channel_env_var: str,
    content: str,
    *,
    image_paths: list[str] | None = None,
    logger: LoggerFn | None = None,
    strict_env: bool = False,
) -> bool:
    """Send a message to a Discord webhook URL stored in an environment variable."""
    webhook_url = os.getenv(channel_env_var, "").strip()
    if strict_env and not webhook_url:
        raise ValueError(f"Environment variable '{channel_env_var}' is missing or empty")
    return send_discord_message(webhook_url, content, image_paths=image_paths, logger=logger)
