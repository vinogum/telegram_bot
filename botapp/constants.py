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

MINUS_SIGN = "-"
PLUS_SIGN = "+"

ALLOWED_COMMANDS = (
    "help",
    "income",
    "expense",
    "balance",
    "report",
    "start",
    "delete",
    "update",
)

# This module contains all Telegram commands

COMMANDS_MODULE = "botapp.commands"
