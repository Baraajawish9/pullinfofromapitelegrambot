import logging
import os
from typing import Any

import requests
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL", "https://example.com/api").rstrip("/")

USERNAME, PASSWORD, MAIN_MENU = range(3)


def normalize_number(text: str) -> str:
    arabic_indic_digits = "٠١٢٣٤٥٦٧٨٩"
    western_digits = "0123456789"
    return text.translate(str.maketrans(arabic_indic_digits, western_digits))


def api_post(path: str, payload: dict[str, Any], token: str | None = None) -> requests.Response:
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    return requests.post(
        f"{API_BASE_URL}/{path.lstrip('/')}",
        json=payload,
        headers=headers,
        timeout=15,
    )


def api_get(path: str, token: str) -> Any:
    response = requests.get(
        f"{API_BASE_URL}/{path.lstrip('/')}",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text("Please enter your username:")
    return USERNAME


async def get_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    username = update.message.text.strip()
    context.user_data["username"] = username
    await update.message.reply_text("Now enter your password:")
    return PASSWORD


async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    username = context.user_data.get("username")
    password = normalize_number(update.message.text.strip())

    try:
        response = api_post("login", {"username": username, "password": password})
    except requests.RequestException as exc:
        logger.warning("Login request failed: %s", exc)
        await update.message.reply_text("Login service is unavailable. Try again later.")
        return ConversationHandler.END

    if response.status_code != 200:
        await update.message.reply_text("Login failed. Please enter your password again:")
        return PASSWORD

    data = response.json()
    access_token = data.get("token") or data.get("access_token")
    if not access_token:
        await update.message.reply_text("Login succeeded, but no access token was returned.")
        return ConversationHandler.END

    context.user_data["token"] = access_token
    await show_profile(update, context)
    return MAIN_MENU


async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    token = context.user_data.get("token")
    if not token:
        await update.message.reply_text("Your session expired. Use /start to log in again.")
        return

    try:
        profile = api_get("profile", token)
    except requests.RequestException as exc:
        logger.warning("Profile request failed: %s", exc)
        await update.message.reply_text("Could not load your profile.")
        return

    name = profile.get("name", "User")
    points = profile.get("points", "N/A")
    await update.message.reply_text(f"Welcome, {name}!\nPoints: {points}")

    keyboard = [["Profile", "Items"], ["Refresh", "Logout"]]
    await update.message.reply_text(
        "Choose an option:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=False,
        ),
    )


async def handle_menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    token = context.user_data.get("token")

    if not token:
        await update.message.reply_text(
            "Your session expired. Use /start to log in again.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END

    if text == "Profile" or text == "Refresh":
        await show_profile(update, context)
    elif text == "Items":
        await show_items(update, context)
    elif text == "Logout":
        return await logout(update, context)
    else:
        await update.message.reply_text("Unknown option. Please choose from the menu.")

    return MAIN_MENU


async def show_items(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    token = context.user_data["token"]

    try:
        items = api_get("items", token)
    except requests.RequestException as exc:
        logger.warning("Items request failed: %s", exc)
        await update.message.reply_text("Could not load items.")
        return

    if not items:
        await update.message.reply_text("No items found.")
        return

    if isinstance(items, dict):
        items = items.get("items", [])

    lines = []
    for item in items[:10]:
        title = item.get("title") or item.get("name") or "Untitled"
        value = item.get("value", "")
        lines.append(f"- {title}: {value}" if value else f"- {title}")

    await update.message.reply_text("\n".join(lines) if lines else "No items found.")


async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "You have been logged out. Use /start to log in again.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await logout(update, context)


def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("Set TELEGRAM_BOT_TOKEN before starting the bot.")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    conversation = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_username)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
            MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_selection)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CommandHandler("logout", logout),
        ],
        per_user=True,
    )

    app.add_handler(conversation)
    app.add_handler(CommandHandler("logout", logout))
    app.run_polling()


if __name__ == "__main__":
    main()
