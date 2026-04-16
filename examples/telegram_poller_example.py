"""Example: Telegram bot with chatops_bridge."""

import time
from chatops_bridge.telegram_poller import TelegramCommandSpec, TelegramPollerConfig, start_telegram_poller


def handle_status(args: list[str]) -> str:
    """Handle /status command."""
    return "Bot status: OK\nUptime: 24h\nTrades: 5 completed, 2 pending"


def handle_trade(args: list[str]) -> str:
    """Handle /trade command."""
    amount = float(args[0]) if args else 100.0
    return f"Executing trade with amount: {amount}"


def handle_info(args: list[str]) -> str:
    """Handle /info command."""
    return "Info: This is a Telegram bot powered by chatops-bridge"


def main():
    """Main example."""
    # Define commands with handlers
    commands = [
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
        TelegramCommandSpec(
            name="info",
            description="Show info",
            handler=handle_info,
        ),
    ]

    # Configure polling behavior
    config = TelegramPollerConfig(
        poll_timeout_seconds=30,
        max_retries=3,
        offset_file="/tmp/telegram_offset.txt",  # Persist offset across restarts
        allowed_updates=["message"],
    )

    # Example logger
    def my_logger(msg: str):
        print(f"[TG] {msg}")

    # Start polling thread (provide token via TELEGRAM_BOT_TOKEN env var)
    import os
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Please set TELEGRAM_BOT_TOKEN env var")
        return

    thread = start_telegram_poller(
        token=token,
        commands=commands,
        config=config,
        logger=my_logger,
    )

    print(f"Telegram poller started: {thread.name}")

    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")


if __name__ == "__main__":
    main()
