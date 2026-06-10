import asyncio
import logging
from monitor import MantleMonitor
from signals import SignalEngine
from telegram_bot import TelegramAlert
from discord_bot import DiscordAlert
from chain_logger import ChainLogger
from dotenv import load_dotenv
import os

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

async def main():
    log.info("MantleAlpha bot starting...")

    monitor = MantleMonitor(rpc_url=os.getenv("MANTLE_RPC_URL"))
    engine = SignalEngine()
    telegram = TelegramAlert(
        token=os.getenv("TELEGRAM_BOT_TOKEN"),
        chat_id=os.getenv("TELEGRAM_CHAT_ID")
    )
    discord = DiscordAlert(webhook_url=os.getenv("DISCORD_WEBHOOK_URL"))
    logger = ChainLogger(
        rpc_url=os.getenv("MANTLE_RPC_URL"),
        private_key=os.getenv("WALLET_PRIVATE_KEY"),
        contract_address=os.getenv("SIGNAL_LOGGER_CONTRACT")
    )

    log.info("All components initialized. Monitoring Mantle...")

    async for event in monitor.stream_events():
        signals = engine.analyze(event)
        for signal in signals:
            log.info(f"Signal detected: {signal}")
            await telegram.send(signal)
            await discord.send(signal)
            await logger.log_signal(signal)

if __name__ == "__main__":
    asyncio.run(main())
