# Public Telegram Bot Template

This is a generic Telegram bot template that logs in to an API, stores a per-user session token, and shows a simple menu.

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables:

   ```bash
   set TELEGRAM_BOT_TOKEN=your-telegram-bot-token
   set API_BASE_URL=https://your-api.example.com/api
   ```

3. Run the public template:

   ```bash
   python public_bot_template.py
   ```

Update the endpoint paths and response fields in `public_bot_template.py` to match your own API.
