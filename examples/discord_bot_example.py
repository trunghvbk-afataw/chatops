from __future__ import annotations

import os
import time

import discord

from chatops_bridge.discord_bot import DiscordBotConfig, SlashCommandSpec, start_discord_bot


def _health() -> str:
    return "Bot is healthy"


def _report() -> dict:
    return {"text": "Daily report generated", "image_paths": []}


def _echo() -> str:
    return "Echo from generic command"


def _commands() -> list[SlashCommandSpec]:
    return [
        SlashCommandSpec(name="health", description="Check service health", handler=_health),
        SlashCommandSpec(name="report", description="Generate latest report", handler=_report),
        SlashCommandSpec(name="echo", description="Return a test message", handler=_echo),
    ]


def main() -> None:
    token = os.getenv("DISCORD_BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("Set DISCORD_BOT_TOKEN first")

    guild_id_raw = os.getenv("DISCORD_BOT_GUILD_ID", "").strip()
    owner_id_raw = os.getenv("DISCORD_BOT_OWNER_USER_ID", "").strip()

    guild_id = int(guild_id_raw) if guild_id_raw.isdigit() else None
    owner_user_id = int(owner_id_raw) if owner_id_raw.isdigit() else None

    intents = discord.Intents.none()
    intents.guilds = True

    start_discord_bot(
        token=token,
        commands=_commands(),
        config=DiscordBotConfig(
            intents=intents,
            allow_dm_commands=False,
            leave_unexpected_guild=True,
            response_chunk_limit=1900,
            max_images_per_response=10,
            defer_thinking=True,
        ),
        guild_id=guild_id,
        owner_user_id=owner_user_id,
        instance_key="example",
        logger=print,
    )

    print("Discord bot started. Keep process alive.")
    while True:
        time.sleep(60)


if __name__ == "__main__":
    main()
