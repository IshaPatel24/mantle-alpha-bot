import logging
from dataclasses import dataclass
from collections import deque
from typing import List
import statistics
import time

log = logging.getLogger(__name__)

@dataclass
class AlphaSignal:
    signal_type: str       # "WHALE_ALERT", "VOLUME_SPIKE", "ANOMALY", "SMART_MONEY"
    severity: str          # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    title: str
    description: str
    tx_hash: str
    value_usd: float
    confidence: float      # 0.0 - 1.0
    timestamp: int
    token: str
    from_addr: str
    to_addr: str

    def to_message(self) -> str:
        severity_emoji = {"LOW": "🟡", "MEDIUM": "🟠", "HIGH": "🔴", "CRITICAL": "🚨"}
        emoji = severity_emoji.get(self.severity, "⚡")
        return (
            f"{emoji} *MantleAlpha Signal*\n\n"
            f"*{self.title}*\n"
            f"{self.description}\n\n"
            f"💰 Value: `{self.value_usd:,.0f} MNT`\n"
            f"🎯 Confidence: `{self.confidence * 100:.0f}%`\n"
            f"📊 Type: `{self.signal_type}`\n"
            f"🔗 Tx: `{self.tx_hash[:16]}...`\n"
            f"🕐 Time: `{time.strftime('%H:%M:%S UTC', time.gmtime(self.timestamp))}`"
        )

class SignalEngine:
    def __init__(self):
        self.volume_window = deque(maxlen=100)
        self.known_smart_wallets = self._load_smart_wallets()
        self.signal_count = 0

    def analyze(self, event) -> List[AlphaSignal]:
        signals = []
        self.volume_window.append(event.value_usd)

        # Rule 1: Whale alert
        if event.value_usd >= 50_000:
            signals.append(AlphaSignal(
                signal_type="WHALE_ALERT",
                severity="HIGH" if event.value_usd >= 100_000 else "MEDIUM",
                title="Whale Movement Detected",
                description=f"Large transfer of {event.value_usd:,.0f} MNT detected on Mantle.",
                tx_hash=event.tx_hash,
                value_usd=event.value_usd,
                confidence=0.92,
                timestamp=event.timestamp,
                token=event.token,
                from_addr=event.from_addr,
                to_addr=event.to_addr
            ))

        # Rule 2: Volume spike anomaly
        if len(self.volume_window) >= 10:
            avg = statistics.mean(self.volume_window)
            stdev = statistics.stdev(self.volume_window) if len(self.volume_window) > 1 else 0
            z_score = (event.value_usd - avg) / stdev if stdev > 0 else 0
            if z_score > 2.5:
                signals.append(AlphaSignal(
                    signal_type="VOLUME_SPIKE",
                    severity="HIGH",
                    title="Volume Anomaly Detected",
                    description=f"Transaction {z_score:.1f}x above average volume. Possible accumulation or dump.",
                    tx_hash=event.tx_hash,
                    value_usd=event.value_usd,
                    confidence=min(0.6 + (z_score * 0.05), 0.95),
                    timestamp=event.timestamp,
                    token=event.token,
                    from_addr=event.from_addr,
                    to_addr=event.to_addr
                ))

        # Rule 3: Smart money wallet detection
        if event.from_addr.lower() in self.known_smart_wallets:
            signals.append(AlphaSignal(
                signal_type="SMART_MONEY",
                severity="CRITICAL",
                title="Smart Money Moving",
                description=f"Known alpha wallet is moving {event.value_usd:,.0f} MNT. Follow the smart money.",
                tx_hash=event.tx_hash,
                value_usd=event.value_usd,
                confidence=0.88,
                timestamp=event.timestamp,
                token=event.token,
                from_addr=event.from_addr,
                to_addr=event.to_addr
            ))

        self.signal_count += len(signals)
        return signals

    def _load_smart_wallets(self) -> set:
        # Seed with known Mantle ecosystem wallets (add more as discovered)
        return {
            "0x0000000000000000000000000000000000000000",  # placeholder
        }

    def get_stats(self) -> dict:
        return {
            "signals_generated": self.signal_count,
            "avg_volume": statistics.mean(self.volume_window) if self.volume_window else 0,
            "window_size": len(self.volume_window)
        }
