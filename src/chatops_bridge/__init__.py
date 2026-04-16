"""chatops_bridge public API."""

from .discord import send_discord_message
from .discord_channels import send_to_discord_env_channel
from .discord_bot import DiscordBotConfig, SlashCommandSpec
from .telegram import chat_id_matches, extract_update_text, fetch_telegram_updates, send_telegram_message
from .telegram_commands import parse_telegram_command
from .telegram_poller import TelegramCommandSpec, TelegramPollerConfig, start_telegram_poller

__all__ = [
    "chat_id_matches",
    "extract_update_text",
    "fetch_telegram_updates",
    "parse_telegram_command",
    "DiscordBotConfig",
    "SlashCommandSpec",
    "TelegramCommandSpec",
    "TelegramPollerConfig",
    "send_discord_message",
    "send_telegram_message",
    "send_to_discord_env_channel",
    "start_telegram_poller",
]
