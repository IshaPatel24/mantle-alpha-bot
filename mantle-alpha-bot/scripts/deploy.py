"""
Deploy SignalLogger.sol to Mantle Network
Usage: python deploy.py
"""
from web3 import Web3
from solcx import compile_standard, install_solc
import json
import os
from dotenv import load_dotenv

load_dotenv()

MANTLE_RPC = os.getenv("MANTLE_RPC_URL", "https://rpc.mantle.xyz")
PRIVATE_KEY = os.getenv("WALLET_PRIVATE_KEY")
CHAIN_ID = 5000  # Mantle mainnet (5003 for testnet)

def deploy():
    print("Installing solc...")
    install_solc("0.8.20")

    with open("../contracts/SignalLogger.sol", "r") as f:
        source = f.read()

    compiled = compile_standard({
        "language": "Solidity",
        "sources": {"SignalLogger.sol": {"content": source}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        }
    }, solc_version="0.8.20")

    contract_data = compiled["contracts"]["SignalLogger.sol"]["SignalLogger"]
    abi = contract_data["abi"]
    bytecode = contract_data["evm"]["bytecode"]["object"]

    with open("signal_logger_abi.json", "w") as f:
        json.dump(abi, f, indent=2)
    print("ABI saved to signal_logger_abi.json")

    w3 = Web3(Web3.HTTPProvider(MANTLE_RPC))
    account = w3.eth.account.from_key(PRIVATE_KEY)
    print(f"Deploying from: {account.address}")
    print(f"Balance: {w3.from_wei(w3.eth.get_balance(account.address), 'ether')} MNT")

    Contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    nonce = w3.eth.get_transaction_count(account.address)

    txn = Contract.constructor().build_transaction({
        "chainId": CHAIN_ID,
        "gas": 1_000_000,
        "gasPrice": w3.eth.gas_price,
        "nonce": nonce
    })

    signed = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    print(f"Tx sent: {tx_hash.hex()}")

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"\n✅ Contract deployed at: {receipt.contractAddress}")
    print(f"Add this to your .env: SIGNAL_LOGGER_CONTRACT={receipt.contractAddress}")

    with open("deployment.json", "w") as f:
        json.dump({"contract_address": receipt.contractAddress, "tx_hash": tx_hash.hex()}, f, indent=2)

if __name__ == "__main__":
    deploy()
