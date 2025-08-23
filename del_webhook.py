from telegram_bot.settings import BOT_TOKEN
import requests


response = requests.post(
    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteWebhook"
)

print(response.json())
