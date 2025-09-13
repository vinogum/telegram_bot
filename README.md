# Finance Telegram Bot

This is a **Django-based Telegram bot** for personal finance management.
It allows users to track their income and expenses, get reports, and check their balance directly from a Telegram chat.

---

## 🚀 Features

* **Add Transactions**: Record income and expenses with notes.

  ```bash
  /income <amount> <note>
  /expense <amount> <note>
  ```

* **Check Balance**: See your current total balance.

  ```bash
  /balance
  ```

* **Get Reports**: View transactions for specific periods.

  ```bash
  /report <interval>   # e.g., day, week, month, year, yesterday
  ```

* **Update and Delete**: Modify or remove existing transactions.

  ```bash
  /update <id> <(+/-)new_amount>
  /delete <id>
  ```

* **Help and Start**: Get information on how to use the bot.

  ```bash
  /start
  /help
  ```

---

## ⚙️ Setup and Installation

### Prerequisites

* Python 3.x
* Django
* A Telegram Bot Token
* An [ngrok](https://ngrok.com/) account for local development

### Local Development

1. **Clone the repository**

   ```bash
   git clone <your-repository-url>
   cd finance-telegram-bot
   ```

2. **Create a virtual environment and install dependencies**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   Create a `.env` file in the `telegram_bot/` directory and add:

   ```env
   SECRET_KEY=your-django-secret-key
   TELEGRAM_BOT_TOKEN=your-telegram-bot-token
   ```

4. **Run database migrations**

   ```bash
   python manage.py makemigrations botapp
   python manage.py migrate
   ```

5. **Start ngrok and update settings**

   ```bash
   ngrok http 8000
   ```

   Copy the `https` URL from ngrok and update `NGROK_URL` in `telegram_bot/settings.py`.

6. **Set the Telegram webhook**

   ```bash
   python telegram_bot/set_webhook.py
   ```

7. **Run the Django server**

   ```bash
   python manage.py runserver
   ```

✅ Your bot should now be active and ready to receive commands on Telegram.

---

## 📂 Project Structure

```plaintext
finance-telegram-bot/
│
├── telegram_bot/          # Main Django project directory
│   ├── settings.py        # Django settings + NGROK_URL
│   ├── urls.py            # Maps webhook URL to TelegramWebhookView
│   ├── telegram_bot.py    # Initializes Telegram Bot instance
│   ├── set_webhook.py     # Script to set webhook
│   └── del_webhook.py     # Script to delete webhook
│
├── botapp/                # Django app for bot logic
│   ├── commands.py        # Logic for each bot command
│   ├── models.py          # Database models (Chat, Operation)
│   ├── parsers.py         # Parsing and validation of command args
│   └── views.py           # Telegram webhook handler
│
└── requirements.txt
```
