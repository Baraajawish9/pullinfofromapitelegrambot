# Public Telegram Bot Template

This repository contains a simple public Telegram bot template written in Python.
It is meant to be edited and connected to any API you want.

The private/original bot file is not included in the public version because it may
contain real tokens, private endpoints, or project-specific information.

## How The Bot Works

The bot uses `python-telegram-bot` to handle Telegram messages and `requests` to
communicate with an external API.

Basic flow:

1. The user sends `/start`.
2. The bot asks for a username.
3. The bot asks for a password.
4. The bot sends the login data to your API.
5. If login succeeds, the bot stores the returned access token in the user's
   temporary session data.
6. The bot loads a basic profile from the API.
7. The bot shows a simple menu with options like `Profile`, `Items`, `Refresh`,
   and `Logout`.

Each Telegram user has their own session data, so one user's token is not shared
with another user.

## Files

- `bot.py` - the generic bot code.
- `requirements.txt` - Python dependencies.
- `.gitignore` - prevents private files, tokens, local test files, and generated
  files from being committed.

## Requirements

- Python 3.10 or newer.
- A Telegram bot token from BotFather.
- An API with login/profile endpoints, or your own custom endpoints.

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables.

   Windows PowerShell:

   ```powershell
   $env:TELEGRAM_BOT_TOKEN="your-telegram-bot-token"
   $env:API_BASE_URL="https://your-api.example.com/api"
   ```

   Windows Command Prompt:

   ```bat
   set TELEGRAM_BOT_TOKEN=your-telegram-bot-token
   set API_BASE_URL=https://your-api.example.com/api
   ```

   macOS/Linux:

   ```bash
   export TELEGRAM_BOT_TOKEN="your-telegram-bot-token"
   export API_BASE_URL="https://your-api.example.com/api"
   ```

3. Run the bot:

   ```bash
   python public_bot_template.py
   ```

## API Endpoints Used By Default

The template expects these example endpoints:

- `POST /login`
- `GET /profile`
- `GET /items`

The login response should return one of these fields:

```json
{
  "token": "example-access-token"
}
```

or:

```json
{
  "access_token": "example-access-token"
}
```

You can rename the endpoints, request fields, and response fields inside
`public_bot_template.py` to match your API.

## Where To Customize

Common changes:

- Change `API_BASE_URL` to your own API URL.
- Update the login payload inside `get_password`.
- Update `show_profile` to display the fields your API returns.
- Update `show_items` to display your own list data.
- Add new menu buttons in `show_profile`.
- Handle new menu actions in `handle_menu_selection`.

## Security Notes

- Do not write your Telegram bot token directly in the code.
- Do not commit `.env` files or files that contain API tokens.
- Use environment variables for private values.
- If a token is accidentally pushed to GitHub, revoke it and create a new one.

## Dependencies

This project uses:

- `python-telegram-bot`
- `requests`

Install them with:

```bash
pip install -r requirements.txt
```
