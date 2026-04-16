from __future__ import annotations

import asyncio
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Union

import discord
from discord import app_commands

ResponseHandler = Callable[[], Union[str, dict]]


@dataclass(frozen=True)
class SlashCommandSpec:
    name: str
    description: str
    handler: ResponseHandler

@dataclass
class DiscordBotConfig:
    intents: discord.Intents | None = None
    allow_dm_commands: bool = False
    leave_unexpected_guild: bool = True
    response_chunk_limit: int = 1900
    max_images_per_response: int = 10
    defer_thinking: bool = True
    thread_name_prefix: str = "discord-bot"


_BOT_THREADS: dict[str, threading.Thread] = {}
_BOT_LOCK = threading.Lock()


def _split_response_text(text: str, limit: int = 1900) -> list[str]:
    if len(text) <= limit:
        return [text]
    chunks: list[str] = []
    while text:
        if len(text) <= limit:
            chunks.append(text)
            break
        cut = text.rfind("\n", 0, limit)
        if cut <= 0:
            cut = limit
        chunks.append(text[:cut])
        text = text[cut:].lstrip("\n")
    return chunks


class DiscordSlashBot(discord.Client):
    def __init__(
        self,
        *,
        token: str,
        commands: list[SlashCommandSpec],
        config: DiscordBotConfig,
        guild_id: int | None = None,
        owner_user_id: int | None = None,
        logger: Callable[[str], None] | None = None,
    ) -> None:
        intents = config.intents
        if intents is None:
            intents = discord.Intents.none()
            intents.guilds = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self._token = token
        self._config = config
        self._guild_id = guild_id
        self._owner_user_id = owner_user_id
        self._commands = commands
        self._logger = logger or (lambda _msg: None)
        self._register_commands()

    def _register_commands(self) -> None:
        for spec in self._commands:
            self._add_command(spec)

    def _add_command(self, spec: SlashCommandSpec) -> None:
        @self.tree.command(name=spec.name, description=spec.description)
        async def _command(interaction: discord.Interaction) -> None:
            await self._run_command(interaction, spec.handler)

    async def setup_hook(self) -> None:
        if self._guild_id is not None:
            guild = discord.Object(id=self._guild_id)
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            self._logger(f"Discord commands synced to guild {self._guild_id}: {len(synced)}")
            return
        synced = await self.tree.sync()
        self._logger(f"Discord global commands synced: {len(synced)}")

    async def on_ready(self) -> None:
        self._logger(f"Discord bot connected as {self.user}")

    async def on_guild_join(self, guild: discord.Guild) -> None:
        if self._guild_id is not None and guild.id != self._guild_id and self._config.leave_unexpected_guild:
            self._logger(f"Joined unexpected guild '{guild.name}' ({guild.id}), leaving.")
            await guild.leave()

    async def _run_command(self, interaction: discord.Interaction, handler: ResponseHandler) -> None:
        if self._owner_user_id is not None and interaction.user.id != self._owner_user_id:
            await interaction.response.send_message("Unauthorized.", ephemeral=True)
            return
        if interaction.guild_id is None and not self._config.allow_dm_commands:
            await interaction.response.send_message("Use this command in the bot server.", ephemeral=True)
            return
        if self._guild_id is not None and interaction.guild_id != self._guild_id:
            await interaction.response.send_message("This bot is not available in this server.", ephemeral=True)
            return
        await interaction.response.defer(thinking=self._config.defer_thinking)
        try:
            response = await asyncio.to_thread(handler)
        except Exception as exc:
            self._logger(f"Discord command failed: {exc}")
            await interaction.followup.send(f"Command failed: {exc}")
            return
        await self._send_response(interaction, response)

    async def _send_response(self, interaction: discord.Interaction, response: str | dict) -> None:
        text = "Done"
        image_paths: list[str] = []
        if isinstance(response, dict):
            text = str(response.get("text") or response.get("message") or "Done")
            raw_images = response.get("image_paths") or []
            if isinstance(raw_images, list):
                image_paths = [str(path) for path in raw_images if path]
        else:
            text = str(response)

        chunks = _split_response_text(text or "Done", limit=max(1, int(self._config.response_chunk_limit)))
        for chunk in chunks:
            await interaction.followup.send(chunk)

        valid_files = [
            discord.File(Path(p), filename=Path(p).name)
            for p in image_paths[: max(0, int(self._config.max_images_per_response))]
            if Path(p).exists()
        ]
        if valid_files:
            await interaction.followup.send(files=valid_files)

    def run_bot(self) -> None:
        self.run(self._token, log_handler=None)


def start_discord_bot(
    *,
    token: str,
    commands: list[SlashCommandSpec] | None = None,
    config: DiscordBotConfig | None = None,
    guild_id: int | None = None,
    owner_user_id: int | None = None,
    instance_key: str = "default",
    logger: Callable[[str], None] | None = None,
) -> threading.Thread:
    resolved_commands = commands or []
    resolved_config = config or DiscordBotConfig()
    key = (instance_key or "default").strip() or "default"

    def _run() -> None:
        bot = DiscordSlashBot(
            token=token,
            commands=resolved_commands,
            config=resolved_config,
            guild_id=guild_id,
            owner_user_id=owner_user_id,
            logger=logger,
        )
        bot.run_bot()

    with _BOT_LOCK:
        existing = _BOT_THREADS.get(key)
        if existing is not None and existing.is_alive():
            return existing
        thread_name = f"{resolved_config.thread_name_prefix}:{key}"
        thread = threading.Thread(target=_run, name=thread_name, daemon=True)
        thread.start()
        _BOT_THREADS[key] = thread
        return thread
