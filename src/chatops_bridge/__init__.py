"""chatops_bridge public API."""

from __future__ import annotations

from .discord import send_discord_message
from .discord_channels import send_to_discord_env_channel
from .telegram import chat_id_matches, extract_update_text, fetch_telegram_updates, send_telegram_message
from .telegram_commands import parse_telegram_command
from .telegram_poller import TelegramCommandSpec, TelegramPollerConfig, start_telegram_poller

__all__ = [
    "chat_id_matches",
    "extract_update_text",
    "fetch_telegram_updates",
    "parse_telegram_command",
    "TelegramCommandSpec",
    "TelegramPollerConfig",
    "send_discord_message",
    "send_telegram_message",
    "send_to_discord_env_channel",
    "start_telegram_poller",
]

_DISCORD_IMPORT_ERROR: ModuleNotFoundError | None = None

# discord.py is an optional dependency (installed via chatops-bridge[discord-bot]).
# Keep telegram/webhook-only imports working even when discord extra is not installed.
try:
    from .discord_bot import DiscordBotConfig, SlashCommandSpec
except ModuleNotFoundError as exc:
    if exc.name != "discord":
        raise
    _DISCORD_IMPORT_ERROR = exc
else:
    __all__.extend(["DiscordBotConfig", "SlashCommandSpec"])


def __getattr__(name: str):
    if name in {"DiscordBotConfig", "SlashCommandSpec"} and _DISCORD_IMPORT_ERROR is not None:
        raise ModuleNotFoundError(
            "Discord bot features require the optional dependency. Install with: "
            'pip install "chatops-bridge[discord-bot]"'
        ) from _DISCORD_IMPORT_ERROR
    raise AttributeError(name)
