import asyncio
import logging
from web3 import Web3
from dataclasses import dataclass
from typing import AsyncGenerator
import time

log = logging.getLogger(__name__)

WHALE_THRESHOLD_MNT = 50_000  # Flag transfers > 50k MNT
POLL_INTERVAL = 3  # seconds

@dataclass
class ChainEvent:
    event_type: str       # "transfer", "swap", "liquidity", "whale"
    tx_hash: str
    from_addr: str
    to_addr: str
    value_usd: float
    token: str
    block_number: int
    timestamp: int
    raw: dict

class MantleMonitor:
    def __init__(self, rpc_url: str):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        if not self.w3.is_connected():
            raise ConnectionError(f"Cannot connect to Mantle RPC: {rpc_url}")
        log.info(f"Connected to Mantle — block #{self.w3.eth.block_number}")
        self.last_block = self.w3.eth.block_number - 1

    async def stream_events(self) -> AsyncGenerator[ChainEvent, None]:
        while True:
            try:
                current_block = self.w3.eth.block_number
                if current_block > self.last_block:
                    for block_num in range(self.last_block + 1, current_block + 1):
                        block = self.w3.eth.get_block(block_num, full_transactions=True)
                        for tx in block.transactions:
                            event = self._parse_tx(tx, block)
                            if event:
                                yield event
                    self.last_block = current_block
                await asyncio.sleep(POLL_INTERVAL)
            except Exception as e:
                log.error(f"Monitor error: {e}")
                await asyncio.sleep(5)

    def _parse_tx(self, tx, block) -> ChainEvent | None:
        try:
            value_eth = self.w3.from_wei(tx.value, "ether")
            if float(value_eth) < 1:
                return None

            event_type = "whale" if float(value_eth) >= WHALE_THRESHOLD_MNT else "transfer"

            return ChainEvent(
                event_type=event_type,
                tx_hash=tx.hash.hex(),
                from_addr=tx["from"],
                to_addr=tx.get("to", "contract_creation") or "contract_creation",
                value_usd=float(value_eth),
                token="MNT",
                block_number=block.number,
                timestamp=block.timestamp,
                raw=dict(tx)
            )
        except Exception:
            return None

    def get_latest_block(self) -> int:
        return self.w3.eth.block_number
