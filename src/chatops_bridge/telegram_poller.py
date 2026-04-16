"""Telegram bot poller with background thread management."""

from __future__ import annotations

import json
import os
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Union

from .telegram import fetch_telegram_updates, send_telegram_message, chat_id_matches
from .telegram_commands import parse_telegram_command

TelegramCommandHandler = Callable[[list[str]], Union[str, dict]]


@dataclass
class TelegramCommandSpec:
    """Specification for a Telegram bot command."""

    name: str
    """Command name (e.g., "status", "trade")."""

    description: str
    """Human-readable description."""

    handler: TelegramCommandHandler
    """Function that handles the command. Receives list of args, returns response."""


@dataclass
class TelegramPollerConfig:
    """Configuration for Telegram polling behavior."""

    poll_timeout_seconds: int = 30
    """Timeout for long polling (0-based)."""

    max_retries: int = 3
    """Max retries on network error before giving up for that cycle."""

    retry_delay_seconds: int = 5
    """Delay between retries."""

    allowed_updates: list[str] | None = None
    """Filter updates (e.g., ["message", "callback_query"]). None = all."""

    offset_file: str | None = None
    """Path to file for persisting offset (auto-created if missing)."""

    thread_name_prefix: str = "telegram-poller"
    """Prefix for thread naming."""


_TELEGRAM_POLLERS: dict[str, threading.Thread] = {}
"""Map of instance_key -> polling thread."""


def _load_offset(offset_file: str | None) -> int:
    """Load saved offset from file, or 0 if missing."""
    if not offset_file:
        return 0
    path = Path(offset_file)
    if path.exists():
        try:
            return int(path.read_text().strip())
        except (ValueError, OSError):
            return 0
    return 0


def _save_offset(offset_file: str | None, offset: int) -> None:
    """Save offset to file."""
    if not offset_file:
        return
    path = Path(offset_file)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(str(offset))
    except OSError:
        pass


def _run_telegram_poller(
    token: str,
    commands: list[TelegramCommandSpec],
    config: TelegramPollerConfig,
    logger: Callable[[str], None] | None = None,
    stop_event: threading.Event | None = None,
) -> None:
    """Background polling loop for Telegram updates."""

    def log(msg: str) -> None:
        if logger:
            logger(f"[telegram-poller] {msg}")

    offset = _load_offset(config.offset_file)
    log(f"Starting polling with offset={offset}")

    command_map: dict[str, TelegramCommandHandler] = {cmd.name: cmd.handler for cmd in commands}

    while not (stop_event and stop_event.is_set()):
        try:
            updates = fetch_telegram_updates(
                token=token,
                timeout=config.poll_timeout_seconds,
                allowed_updates=config.allowed_updates,
                offset=offset,
                retries=config.max_retries,
                retry_delay=config.retry_delay_seconds,
            )

            for update in updates:
                try:
                    message = update.get("message", {})
                    if not message:
                        continue

                    text = message.get("text", "").strip()
                    chat_id = message.get("chat", {}).get("id")

                    if not text or not chat_id:
                        continue

                    # Parse command
                    cmd, args = parse_telegram_command(text)
                    if not cmd:
                        continue

                    # Dispatch to handler
                    handler = command_map.get(cmd)
                    if not handler:
                        log(f"Unknown command: /{cmd} from chat {chat_id}")
                        continue

                    log(f"Handling /{cmd} with args {args} from chat {chat_id}")
                    response = handler(args)

                    # Send response
                    if isinstance(response, dict):
                        response_text = json.dumps(response)
                    else:
                        response_text = str(response)

                    send_telegram_message(token, chat_id, response_text)

                except Exception as e:
                    log(f"Error handling update {update.get('update_id')}: {e}")
                    continue

                # Update offset after successful processing
                offset = update.get("update_id", offset) + 1
                _save_offset(config.offset_file, offset)

        except Exception as e:
            log(f"Polling error: {e}")
            time.sleep(config.retry_delay_seconds)


def start_telegram_poller(
    *,
    token: str,
    commands: list[TelegramCommandSpec],
    config: TelegramPollerConfig | None = None,
    logger: Callable[[str], None] | None = None,
    instance_key: str = "default",
) -> threading.Thread:
    """
    Start a background Telegram polling thread.

    Args:
        token: Telegram bot token.
        commands: List of TelegramCommandSpec for command handlers.
        config: TelegramPollerConfig for polling behavior. Defaults to TelegramPollerConfig().
        logger: Optional logger function.
        instance_key: Unique key for this poller instance (allows multiple pollers per process).

    Returns:
        The polling thread (already started).

    Raises:
        ValueError: If instance_key is already in use (to prevent duplicate pollers).

    Example:
        >>> config = TelegramPollerConfig(poll_timeout_seconds=30, offset_file="/tmp/tg_offset")
        >>> commands = [
        ...     TelegramCommandSpec("status", "Get status", handler=on_status),
        ...     TelegramCommandSpec("trade", "Execute trade", handler=on_trade),
        ... ]
        >>> thread = start_telegram_poller(token=token, commands=commands, config=config)
        >>> # Thread is now running in background
    """
    if config is None:
        config = TelegramPollerConfig()

    if instance_key in _TELEGRAM_POLLERS:
        raise ValueError(f"Telegram poller with instance_key='{instance_key}' already running")

    stop_event = threading.Event()
    thread = threading.Thread(
        name=f"{config.thread_name_prefix}-{instance_key}",
        target=_run_telegram_poller,
        args=(token, commands, config, logger, stop_event),
        daemon=True,
    )
    thread.start()
    _TELEGRAM_POLLERS[instance_key] = thread

    return thread
