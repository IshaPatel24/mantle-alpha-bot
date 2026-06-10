import logging
from web3 import Web3
from signals import AlphaSignal
import json
import time

log = logging.getLogger(__name__)

# ABI for the SignalLogger contract
SIGNAL_LOGGER_ABI = json.loads('''[
  {
    "inputs": [
      {"internalType": "string", "name": "signalType", "type": "string"},
      {"internalType": "string", "name": "severity", "type": "string"},
      {"internalType": "uint256", "name": "valueUSD", "type": "uint256"},
      {"internalType": "uint256", "name": "confidence", "type": "uint256"},
      {"internalType": "string", "name": "txHash", "type": "string"}
    ],
    "name": "logSignal",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "anonymous": false,
    "inputs": [
      {"indexed": true, "internalType": "uint256", "name": "id", "type": "uint256"},
      {"indexed": false, "internalType": "string", "name": "signalType", "type": "string"},
      {"indexed": false, "internalType": "string", "name": "severity", "type": "string"},
      {"indexed": false, "internalType": "uint256", "name": "timestamp", "type": "uint256"}
    ],
    "name": "SignalLogged",
    "type": "event"
  }
]''')

class ChainLogger:
    def __init__(self, rpc_url: str, private_key: str, contract_address: str):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.enabled = bool(private_key and contract_address)

        if self.enabled:
            self.account = self.w3.eth.account.from_key(private_key)
            self.contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(contract_address),
                abi=SIGNAL_LOGGER_ABI
            )
            log.info(f"Chain logger ready — wallet: {self.account.address[:12]}...")
        else:
            log.warning("Chain logger disabled — set WALLET_PRIVATE_KEY and SIGNAL_LOGGER_CONTRACT")

    async def log_signal(self, signal: AlphaSignal):
        if not self.enabled:
            log.info(f"[DRY RUN] Would log signal: {signal.signal_type} | {signal.severity}")
            return

        try:
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            txn = self.contract.functions.logSignal(
                signal.signal_type,
                signal.severity,
                int(signal.value_usd),
                int(signal.confidence * 100),
                signal.tx_hash
            ).build_transaction({
                "chainId": 5000,  # Mantle mainnet
                "gas": 200_000,
                "gasPrice": self.w3.eth.gas_price,
                "nonce": nonce
            })
            signed = self.w3.eth.account.sign_transaction(txn, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
            log.info(f"Signal logged on-chain: {tx_hash.hex()}")
            return tx_hash.hex()
        except Exception as e:
            log.error(f"Chain log failed: {e}")
            return None
