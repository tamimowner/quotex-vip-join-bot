# Quotex VIP Join Bot

Telegram bot that verifies Quotex deposits via Partner Postback and issues **one-time unique invite links** to a private VIP group.

## Features

- Language selection (English / বাংলা) on `/start`
- Affiliate link with `click_id` = Telegram user ID
- Quotex Partner Postback receiver (GET/POST)
- Automatic verification on deposit (`sumdep`)
- Creates **member_limit=1** invite link only for the verified user
- Auto-revokes the link after the user joins
- Account status (trader_id, country, total deposit, etc.)
- PostgreSQL database
- Railway ready

## Flow

1. User starts bot → chooses language
2. Clicks "Premium Channel Join Process"
3. Bot gives affiliate registration link (click_id = their Telegram ID)
4. User registers + deposits on Quotex under your partner link
5. Quotex sends Postback → bot matches by click_id → marks verified
6. Bot creates unique invite link (member_limit=1) for that user only
7. User joins → link is revoked automatically
8. User can check Account Status anytime

## Setup

### 1. Create Bot
- Talk to @BotFather → create bot → copy token

### 2. Create VIP Group
- Create a private Telegram group/channel
- Add the bot as **Administrator** with permission to invite users / manage invite links
- Get the group ID (use @userinfobot or similar)

### 3. Quotex Partner Postback
In Quotex Partner panel set:

**URL:** `https://your-railway-app.up.railway.app/postback`

**Method:** GET or POST

**Example format:**
```
https://your-domain/postback?status={status}&eid={event_id}&cid={click_id}&sid={site_id}&lid={lid}&uid={trader_id}&country={country}&sumdep={sumdep}&sumwithdraw={sumwithdraw}
```

### 4. Environment Variables
Copy `.env.example` → `.env` and fill values.

### 5. Deploy on Railway
- New Project → Deploy from GitHub repo
- Add PostgreSQL plugin
- Set all environment variables
- Deploy

## Commands

- `/start` – Start & language select
- `/status` – Account status
- `/admin` – Admin panel (only for ADMIN_IDS)

## Tech Stack

- Python 3.11+
- aiogram 3
- FastAPI (postback endpoint)
- SQLAlchemy + asyncpg
- PostgreSQL
- Railway
