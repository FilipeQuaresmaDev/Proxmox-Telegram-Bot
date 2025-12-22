import os

BOT_TOKEN = os.getenv("BOT_TELEGRAM_TOKEN", "")  #Token do BOT do telegram

AUTHORIZED_USERS = list(
    map(int, os.getenv("TELEGRAM_ID", "").split(","))
)  # seu Telegram ID
