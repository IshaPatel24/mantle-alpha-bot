import logging
import aiohttp
from signals import AlphaSignal

log = logging.getLogger(__name__)

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"

class TelegramAlert:
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.url = TELEGRAM_API.format(token=token)

    async def send(self, signal: AlphaSignal):
        if not self.token or not self.chat_id:
            log.warning("Telegram not configured, skipping alert")
            return
        try:
            payload = {
                "chat_id": self.chat_id,
                "text": signal.to_message(),
                "parse_mode": "Markdown",
                "disable_web_page_preview": True
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url, json=payload) as resp:
                    if resp.status == 200:
                        log.info(f"Telegram alert sent: {signal.signal_type}")
                    else:
                        log.error(f"Telegram error {resp.status}: {await resp.text()}")
        except Exception as e:
            log.error(f"Telegram send failed: {e}")

    async def send_startup(self):
        try:
            msg = (
                "🤖 *MantleAlpha Bot Started*\n\n"
                "Monitoring Mantle Network for:\n"
                "• 🐋 Whale movements (>50K MNT)\n"
                "• 📈 Volume anomalies (Z-score >2.5)\n"
                "• 💡 Smart money wallet activity\n\n"
                "_Every signal is logged on-chain for full auditability._"
            )
            payload = {
                "chat_id": self.chat_id,
                "text": msg,
                "parse_mode": "Markdown"
            }
            async with aiohttp.ClientSession() as session:
                await session.post(self.url, json=payload)
        except Exception as e:
            log.error(f"Telegram startup message failed: {e}")
