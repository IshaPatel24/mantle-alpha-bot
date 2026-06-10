import logging
import aiohttp
from signals import AlphaSignal
import time

log = logging.getLogger(__name__)

SEVERITY_COLORS = {
    "LOW": 0xFFD700,
    "MEDIUM": 0xFF8C00,
    "HIGH": 0xFF4500,
    "CRITICAL": 0xFF0000
}

class DiscordAlert:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    async def send(self, signal: AlphaSignal):
        if not self.webhook_url:
            log.warning("Discord not configured, skipping alert")
            return
        try:
            embed = {
                "title": f"⚡ {signal.title}",
                "description": signal.description,
                "color": SEVERITY_COLORS.get(signal.severity, 0x00D4AA),
                "fields": [
                    {"name": "Signal Type", "value": signal.signal_type, "inline": True},
                    {"name": "Severity", "value": signal.severity, "inline": True},
                    {"name": "Confidence", "value": f"{signal.confidence * 100:.0f}%", "inline": True},
                    {"name": "Value", "value": f"{signal.value_usd:,.0f} MNT", "inline": True},
                    {"name": "Token", "value": signal.token, "inline": True},
                    {"name": "Tx Hash", "value": f"`{signal.tx_hash[:20]}...`", "inline": True},
                    {"name": "From", "value": f"`{signal.from_addr[:12]}...`", "inline": True},
                    {"name": "To", "value": f"`{signal.to_addr[:12]}...`", "inline": True},
                ],
                "footer": {"text": "MantleAlpha — On-Chain Intelligence Bot"},
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(signal.timestamp))
            }
            payload = {
                "username": "MantleAlpha",
                "avatar_url": "https://mantle.xyz/favicon.ico",
                "embeds": [embed]
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as resp:
                    if resp.status in (200, 204):
                        log.info(f"Discord alert sent: {signal.signal_type}")
                    else:
                        log.error(f"Discord error {resp.status}: {await resp.text()}")
        except Exception as e:
            log.error(f"Discord send failed: {e}")
