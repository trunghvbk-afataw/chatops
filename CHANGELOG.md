# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2026-04-16

### Added

- `DiscordBotConfig` authorization check flags to enable/disable guard checks:
  - `enforce_owner_check: bool = True` — Control owner user ID validation
  - `enforce_guild_restriction: bool = True` — Control guild availability check
  - `enforce_server_only: bool = True` — Control DM restriction check

## [0.1.1] - 2026-04-16

### Fixed

- Telegram poller now calls `fetch_telegram_updates` with the correct function signature from `awesome-notify-bridge`.
- Added configurable retry loop around polling failures instead of passing unsupported retry keyword arguments.

### Added

- `TelegramPollerConfig.allowed_chat_ids` to restrict command handling to selected chat IDs.
- Telegram poller now supports `dict` response payloads with `text`/`message` and optional `image_paths`.

## [0.1.0] - 2026-04-16

### Added

- **Telegram poller bot**: `start_telegram_poller()` for automatic background polling with command dispatch
  - `TelegramCommandSpec` for defining commands with handlers
  - `TelegramPollerConfig` for configurable polling behavior (timeout, retries, offset persistence)
  - Automatic offset persistence to file for safe restarts
  - Network retry logic with configurable backoff
  - Support for multiple poller instances via `instance_key`

- **Discord slash bot**: `start_discord_bot()` for background bot management
  - `SlashCommandSpec` for defining slash commands with handlers
  - `DiscordBotConfig` for configurable bot behavior
  - Configurable intents, DM permissions, guild restrictions
  - Tunable response chunking and image limits
  - Support for multiple bot instances via `instance_key`

- **Telegram utilities**: Send messages, poll updates, parse commands, format text
  - `send_telegram_message()`: Send text/images with automatic chunking
  - `fetch_telegram_updates()`: Long polling with offset tracking
  - `parse_telegram_command()`: Parse `/command arg1 arg2` style messages
  - `extract_update_text()`: Extract text from Telegram update objects
  - Text formatting helpers for chat-friendly output

- **Discord utilities**: Webhook sender and environment-based channel routing
  - `send_discord_message()`: Send to webhook with chunking and file upload
  - `send_to_discord_env_channel()`: Route to Discord via env var (with strict mode)

- **Examples**: Complete working examples for both Telegram poller and Discord slash bot

### Notes

- Extracted from production automation code and generalized for multi-purpose ChatOps use
- Transport layer (HTTP) reused from `awesome-notify-bridge` to minimize dependencies
- All hardcoded values eliminated in favor of configuration objects
- Python 3.9+ compatible with proper type hints

[0.1.0]: https://github.com/trunghvbk-afataw/chatops/releases/tag/v0.1.0
[0.1.1]: https://github.com/trunghvbk-afataw/chatops/releases/tag/v0.1.1
