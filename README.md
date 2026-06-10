MantleAlpha — On-Chain Intelligence Bot

> AI-powered on-chain anomaly detection and alpha signal delivery for Mantle Network traders.

Built for the [Turing Test Hackathon 2026](https://dorahacks.io/hackathon/mantleturingtesthackathon2026/detail)** — AI Alpha & Data Track | Prize Pool: $100K

---

 What Is MantleAlpha?

Retail and institutional traders on Mantle lack real-time, verifiable on-chain intelligence. MantleAlpha** is an AI agent that tracks smart money flows, detects on-chain anomalies, and delivers actionable alpha signals via Telegram and Discord — with every prediction logged permanently on Mantle for full transparency and auditability.

---

Features

- Real-time monitoring** — Streams live Mantle blockchain data block by block
- Whale tracking** — Flags large transfers above configurable thresholds
- Anomaly detection** — Z-score based volume spike detection vs rolling average
- Smart money alerts** — Tracks known alpha wallet activity
- Telegram alerts** — Instant push notifications with confidence scores
- Discord alerts** — Rich embeds with severity colours and full signal detail
- On-chain logging** — Every signal is permanently recorded via `SignalLogger.sol`
- Verifiable auditability** — Predictions logged on Mantle for full transparency

---

Architecture

```
Mantle RPC (rpc.mantle.xyz)
        │
        ▼
 MantleMonitor
 (real-time block & tx streaming)
        │
        ▼
 SignalEngine
 (whale detection · Z-score anomaly · smart money)
        │
        ├──► TelegramAlert  →  Telegram Channel/Group
        ├──► DiscordAlert   →  Discord Server
        └──► ChainLogger    →  SignalLogger.sol (Mantle Network)
```

---

Project Structure

```
mantle-alpha-bot/
├── src/
│   ├── main.py            # Entry point — wires all components
│   ├── monitor.py         # Mantle RPC block/tx streaming
│   ├── signals.py         # AI signal engine & anomaly detection
│   ├── telegram_bot.py    # Telegram push alert delivery
│   ├── discord_bot.py     # Discord webhook rich embeds
│   └── chain_logger.py    # On-chain signal logging via Web3
├── contracts/
│   └── SignalLogger.sol   # Solidity contract — permanent signal log
├── scripts/
│   └── deploy.py          # One-command Mantle contract deployment
├── requirements.txt
├── .env.example
└── README.md
```

---

Quick Start

 1. Clone & Install

```bash
git clone https://github.com/YOUR_USERNAME/mantle-alpha-bot
cd mantle-alpha-bot
pip install -r requirements.txt
```

2. Configure Environment

```bash
cp .env.example .env
# Open .env and fill in your keys (see Configuration section below)
```

3. Deploy Smart Contract (Recommended)

```bash
cd scripts
python deploy.py
# Copy the printed contract address to .env → SIGNAL_LOGGER_CONTRACT
```

4. Run the Bot

```bash
cd src
python main.py
```

---

 Configuration

Copy `.env.example` to `.env` and fill in:

| Variable | Description |
|---|---|
| `MANTLE_RPC_URL` | Mantle RPC — `https://rpc.mantle.xyz` |
| `WALLET_PRIVATE_KEY` | Wallet for on-chain signal logging |
| `SIGNAL_LOGGER_CONTRACT` | Deployed SignalLogger contract address |
| `TELEGRAM_BOT_TOKEN` | From [@BotFather](https://t.me/BotFather) on Telegram |
| `TELEGRAM_CHAT_ID` | Your channel or group chat ID |
| `DISCORD_WEBHOOK_URL` | Discord Server → Integrations → Webhooks |
| `WHALE_THRESHOLD_MNT` | Min MNT to trigger whale alert (default: 50000) |

---

Signal Types

| Signal | Trigger | Severity | Confidence |
|--------|---------|----------|------------|
| `WHALE_ALERT` | Transfer > 50,000 MNT | HIGH / CRITICAL | ~92% |
| `VOLUME_SPIKE` | Z-score > 2.5 vs rolling avg | HIGH | ~75–95% |
| `SMART_MONEY` | Known alpha wallet activity | CRITICAL | ~88% |

---

 Smart Contract — SignalLogger.sol

Deployed on **Mantle Network (Chain ID: 5000)**

Every AI-generated signal is logged on-chain with:
- Signal type and severity
- USD value of detected transaction
- Confidence score (0–100%)
- Source transaction hash
- Logger wallet address
- Block timestamp
- Verification status (updated when outcome confirmed)

This creates a permanent, immutable, verifiable record** of all predictions — the first of its kind in Web3.

---

Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11+ |
| Blockchain | Mantle Network (Chain ID 5000) |
| Web3 | Web3.py 6.x |
| Smart Contract | Solidity 0.8.20 |
| Async | asyncio + aiohttp |
| Alerts | Telegram Bot API + Discord Webhooks |
| Deployment | py-solc-x |

---

Hackathon

- Event: Turing Test Hackathon 2026
- Track: AI Alpha & Data (Sponsored by Mirana Ventures)
- Phase: Phase 2 — AI Awakening (May 1 – June 15, 2026)
- Prize Pool:** $100,000 USD

---
