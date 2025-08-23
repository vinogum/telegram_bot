from telegram_bot.settings import WEBHOOK_URL
from botapp.telegram_bot import bot


bot.set_webhook(url=WEBHOOK_URL)
info = bot.get_webhook_info()
print(f"Webhook set: {info.url}")
