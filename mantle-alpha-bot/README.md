# MantleAlpha — On-Chain Intelligence Bot

> AI-powered on-chain anomaly detection and alpha signal delivery for Mantle Network.

Built for the **Turing Test Hackathon 2026** — AI Alpha & Data Track

## What It Does

MantleAlpha monitors Mantle Network in real time, detects smart money movements and on-chain anomalies, and delivers actionable alpha signals to traders via Telegram and Discord — with every signal permanently logged on Mantle for full auditability.

## Features
- Real-time Mantle block/tx streaming via RPC
- Z-score anomaly detection for volume spikes
- Whale wallet tracking (configurable threshold)
- Smart money wallet alerts
- Telegram + Discord instant push notifications
- On-chain signal logging via SignalLogger.sol
- Verifiable prediction auditability

## Architecture
```
Mantle RPC → MantleMonitor → SignalEngine → TelegramAlert
                                          → DiscordAlert
                                          → ChainLogger (SignalLogger.sol)
```

## Quick Start
```bash
git clone https://github.com/YOUR_USERNAME/mantle-alpha-bot
cd mantle-alpha-bot
pip install -r requirements.txt
cp .env.example .env   # fill in your keys
cd src && python main.py
```

## Signal Types
| Signal | Trigger | Severity |
|--------|---------|----------|
| WHALE_ALERT | Transfer > 50,000 MNT | HIGH |
| VOLUME_SPIKE | Z-score > 2.5 | HIGH |
| SMART_MONEY | Known alpha wallet | CRITICAL |

## Smart Contract
`SignalLogger.sol` logs every signal on Mantle with type, severity, confidence score, source tx, and timestamp.

## Tech Stack
Python 3.11 · Web3.py · aiohttp · Solidity 0.8.20 · Mantle Network (Chain ID 5000)

## License
MIT
