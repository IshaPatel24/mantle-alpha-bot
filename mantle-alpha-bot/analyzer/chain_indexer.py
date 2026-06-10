"""
MantleAlpha — Chain Indexer
Indexes live Mantle blockchain data: transactions, token transfers, DeFi events
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Optional
from web3 import Web3
from web3.middleware import geth_poa_middleware
from config.settings import Settings

logger = logging.getLogger(__name__)


@dataclass
class TransferEvent:
    tx_hash: str
    block_number: int
    token: str
    from_addr: str
    to_addr: str
    value_usd: float
    timestamp: int


@dataclass
class DeFiEvent:
    protocol: str
    event_type: str   # swap, add_liquidity, remove_liquidity
    token_in: str
    token_out: str
    amount_usd: float
    wallet: str
    tx_hash: str
    block_number: int


class ChainIndexer:
    """Real-time Mantle blockchain indexer"""

    # Known whale threshold in USD
    WHALE_THRESHOLD_USD = 100_000

    # ERC20 Transfer event signature
    TRANSFER_TOPIC = Web3.keccak(text="Transfer(address,address,uint256)").hex()

    # Uniswap V3 Swap event signature
    SWAP_TOPIC = Web3.keccak(text="Swap(address,address,int256,int256,uint160,uint128,int24)").hex()

    def __init__(self, settings: Settings):
        self.settings = settings
        self.w3 = Web3(Web3.HTTPProvider(settings.MANTLE_RPC_URL))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.callbacks = []

        # Known Mantle DeFi contracts
        self.watched_protocols = {
            settings.MERCHANT_MOE_ROUTER: "MerchantMoe",
            settings.AGNI_FINANCE_ROUTER: "AgniFinance",
            settings.FLUXION_ROUTER: "Fluxion",
        }

        # Known token addresses on Mantle
        self.tokens = {
            settings.METH_ADDRESS: ("mETH", 18),
            settings.USDY_ADDRESS: ("USDY", 18),
            settings.WMNT_ADDRESS: ("wMNT", 18),
        }

    async def start(self, on_event_callback):
        """Start indexing — calls callback with detected events"""
        self.callbacks.append(on_event_callback)
        logger.info("Chain indexer started on Mantle RPC: %s", self.settings.MANTLE_RPC_URL)

        last_block = self.w3.eth.block_number
        logger.info("Starting from block %d", last_block)

        while True:
            try:
                current_block = self.w3.eth.block_number
                if current_block > last_block:
                    for block_num in range(last_block + 1, current_block + 1):
                        await self._process_block(block_num)
                    last_block = current_block
                await asyncio.sleep(2)  # Mantle ~2s block time
            except Exception as e:
                logger.error("Indexer error: %s", e)
                await asyncio.sleep(5)

    async def _process_block(self, block_number: int):
        """Process all transactions in a block"""
        try:
            block = self.w3.eth.get_block(block_number, full_transactions=True)
            logger.debug("Processing block %d (%d txs)", block_number, len(block.transactions))

            for tx in block.transactions:
                await self._process_transaction(tx, block.timestamp)

        except Exception as e:
            logger.error("Error processing block %d: %s", block_number, e)

    async def _process_transaction(self, tx, timestamp: int):
        """Analyze a single transaction for significant events"""
        try:
            receipt = self.w3.eth.get_transaction_receipt(tx.hash)
            if not receipt or receipt.status == 0:
                return

            for log in receipt.logs:
                # Detect large ERC20 transfers
                if (len(log.topics) == 3 and
                        log.topics[0].hex() == self.TRANSFER_TOPIC):
                    await self._handle_transfer(log, tx, timestamp)

                # Detect DEX swaps
                if (len(log.topics) >= 2 and
                        log.topics[0].hex() == self.SWAP_TOPIC):
                    await self._handle_swap(log, tx, timestamp)

        except Exception as e:
            logger.debug("TX processing error: %s", e)

    async def _handle_transfer(self, log, tx, timestamp: int):
        """Handle ERC20 transfer — check if whale-sized"""
        token_addr = log.address.lower()
        if token_addr not in self.tokens:
            return

        token_name, decimals = self.tokens[token_addr]

        try:
            value = int(log.data.hex(), 16) / (10 ** decimals)
            value_usd = await self._estimate_usd(token_name, value)

            if value_usd >= self.WHALE_THRESHOLD_USD:
                from_addr = "0x" + log.topics[1].hex()[-40:]
                to_addr = "0x" + log.topics[2].hex()[-40:]

                event = TransferEvent(
                    tx_hash=tx.hash.hex(),
                    block_number=tx.blockNumber,
                    token=token_name,
                    from_addr=from_addr,
                    to_addr=to_addr,
                    value_usd=value_usd,
                    timestamp=timestamp,
                )
                logger.info("Whale transfer detected: $%.0f %s", value_usd, token_name)
                await self._emit_event("whale_transfer", event)

        except Exception as e:
            logger.debug("Transfer parse error: %s", e)

    async def _handle_swap(self, log, tx, timestamp: int):
        """Handle DEX swap event"""
        protocol = self.watched_protocols.get(log.address.lower(), "Unknown DEX")

        event = DeFiEvent(
            protocol=protocol,
            event_type="swap",
            token_in="unknown",
            token_out="unknown",
            amount_usd=0,
            wallet=tx.get("from", ""),
            tx_hash=tx.hash.hex(),
            block_number=tx.blockNumber,
        )
        await self._emit_event("defi_swap", event)

    async def _estimate_usd(self, token: str, amount: float) -> float:
        """Rough USD estimate — replace with oracle in production"""
        prices = {
            "mETH": 3800.0,
            "USDY": 1.0,
            "wMNT": 0.85,
        }
        return amount * prices.get(token, 1.0)

    async def _emit_event(self, event_type: str, event):
        """Emit event to all registered callbacks"""
        for cb in self.callbacks:
            try:
                await cb(event_type, event)
            except Exception as e:
                logger.error("Callback error: %s", e)

    def get_latest_block(self) -> int:
        return self.w3.eth.block_number

    def get_wallet_history(self, address: str, block_count: int = 1000):
        """Get recent transaction history for a wallet"""
        current = self.w3.eth.block_number
        txs = []
        for tx in self.w3.eth.get_block(current, full_transactions=True).transactions:
            if tx.get("from", "").lower() == address.lower():
                txs.append(tx)
        return txs
