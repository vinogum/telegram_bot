START_TEXT = (
    "Hello! 😀 I am a financial bot.\n"
    "I can help you:\n"
    "   - keep track of your income and expenses,\n"
    "   - view your balance,\n"
    "   - receive reports for the day, week, month, or year,\n"
    "   - delete or update entries as needed,\n"
    "   - view statistics for a selected period.\n\n"
    "See the commands using /help."
)

HELP_TEXT = (
    "/help - Show a list of all commands\n" 
    "/income - Show total income or add new income\n" 
    "/income <amount> - Add income of <amount>\n"
    "/income <amount> [note] - Add income of <amount> with a note\n"
    "/expense - Show total expenses or add new expense\n"
    "/expense <amount> - Add expense of <amount>\n"
    "/expense <amount> [note] - Add an expense of <amount> with a note\n"
    "/balance - Show the total balance (income – expenses)\n"
    "/report - Show transactions for a period\n"
    "/report day - For the day\n"
    "/report week - For the week\n"
    "/report month - For the month\n"
    "/report year - For the year\n"
    "/delete <id> - Delete transaction by ID\n"
    "/update <id> <±amount> [note] - Change existing transaction\n"
)


def reply_text(update, text):
    update.message.reply_text(text)


def parse_amount(amount) -> float | None:
    try:
        amount = float(amount)
        if amount < 0.01:
            return None
        return amount
    except ValueError:
        return None


def parse_id(id) -> int | None:
    try:
        id = int(id)
        if id < 0:
            return None
        return id
    except ValueError:
        return None


def get_chat_id(update):
    return update.effective_chat.id
