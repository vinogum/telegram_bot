from telegram.ext import CommandHandler, Dispatcher
from botapp.models import Operation, Chat
from django.utils import timezone


class CommandRegistrar:
    def __init__(self, dispatcher: Dispatcher, allowed_commands=None):
        if allowed_commands is None: raise TypeError()
        self.allowed_commands = allowed_commands
        self._dispatcher = dispatcher
        handlers = self.validate_commands(allowed_commands)
        self.register_commands(handlers)

    @property
    def dispatcher(self):
        return self._dispatcher

    def validate_commands(self, allowed_commands):
        handlers = {}
        for command_name in allowed_commands:
            handler = getattr(self, command_name, None)
            if not handler: raise AttributeError()
            handlers[command_name] = handler
        return handlers

    def register_commands(self, handlers):
        for command_name, handler in handlers.items():
            self.dispatcher.add_handler(CommandHandler(command_name, handler))


class FinanceBot(CommandRegistrar):
    @staticmethod
    def start(update, context):
        update.message.reply_text(
            "Hello! I am a financial bot.\n"
            "I can help you:\n"
            "   - keep track of your income and expenses,\n"
            "   - view your balance,\n"
            "   - receive reports for the day, week, month, or year,\n"
            "   - delete or update entries as needed,\n"
            "   - view statistics for a selected period.\n\n"
            "See the commands using /help."
        )


    @staticmethod
    def _handle_income_or_expense(update, context, operation_type):
        chat_id = update.effective_chat.id
        sign = "+" if operation_type == Operation.INCOME else "-"

        # If we have no arguments, then we give the income or expense amount
        if len(context.args) == 0:
            total_sum = Operation.get_sum_by_type(chat_id, operation_type)
            update.message.reply_text(
                f"Total {operation_type}: {sign}{total_sum:.2f}"
            )
            return

        # First argument is amount
        try:
            amount = float(context.args[0])
            if amount < 0.01:
                update.message.reply_text("Amount must be a positive number")
                return
        except ValueError:
            update.message.reply_text("Amount must be a number")
            return

        # Other arguments are note
        note = " ".join(context.args[1:]) if len(context.args) > 1 else ""

        chat, _ = Chat.objects.get_or_create(
            chat_id=chat_id, username=update.effective_user.username
        )

        try:
            Operation.objects.create(
                chat=chat, amount=amount, operation_type=operation_type, note=note
            )
        except Exception:
            update.message.reply_text("Something went wrong. Please check /help")
            return

        update.message.reply_text(
            f"{operation_type.capitalize()} added: {sign}{amount:.2f}"
        )

    @classmethod
    def income(cls, update, context):
        cls._handle_income_or_expense(update, context, Operation.INCOME)

    @classmethod
    def expense(cls, update, context):
        cls._handle_income_or_expense(update, context, Operation.EXPENSE)

    @staticmethod
    def balance(update, context):
        balance = Operation.get_balance(chat_id=update.effective_chat.id)
        update.message.reply_text(f"Total balance: {balance:.2f}")

    @staticmethod
    def delete(update, context):
        if len(context.args) != 1:
            update.message.reply_text("One argument is required. Please check /help")
            return
        
        try:
            transaction_id = int(context.args[0])
        except Exception:
            update.message.reply_text("Argument must be a number")
            return
        
        chat_id = update.effective_chat.id
        transaction = Operation.objects.filter(id=transaction_id, chat_id=chat_id).first()
        if not transaction:
            update.message.reply_text("You have no such transaction")
            return
        
        transaction.delete()
        update.message.reply_text(f"Transaction {transaction_id} successfully deleted")

    @staticmethod
    def update(update, context):
        chat_id = update.effective_chat.id

        if len(context.args) < 1:
            update.message.reply_text("Transaction ID is required. Please check /help")
            return

        try:
            transaction_id = int(context.args[0])
            transaction = Operation.objects.filter(id=transaction_id, chat_id=chat_id).first()
            if not transaction:
                update.message.reply_text("Transaction not found")
                return

            amount = None
            note = None
            operation_type = None

            if len(context.args) > 1:
                if context.args[1].startswith("+") or context.args[1].startswith("-"):
                    amount = float(context.args[1])
                    operation_type = Operation.INCOME if amount > 0 else Operation.EXPENSE
                    if len(context.args) > 2:
                        note = " ".join(context.args[2:])
                else:
                    note = " ".join(context.args[1:])

            if amount and note:
                transaction.amount = abs(amount)
                transaction.note = note
                transaction.operation_type = operation_type
            elif amount:
                transaction.amount = abs(amount)
            else:
                transaction.note = note

            transaction.save()
            update.message.reply_text(f"Transaction {transaction_id} updated successfully")

        except Exception as e:
            update.message.reply_text(f"Error: {str(e)}")

    @staticmethod
    def help(update, context):
        update.message.reply_text(
            "/help – show a list of all commands.\n"
            "/income – show total income or add new income:\n"
            "   - /income <amount> – add income of <amount>\n"
            "   - /income <amount> [note] – add income of <amount> with a note\n"
            "/expense – show total expenses or add new expense:\n"
            "   - /expense <amount> – add expense of <amount>\n"
            "   - /expense <amount> [note] – add an expense of <amount> with a note\n"
            "/balance – show the total balance (income – expenses).\n"
            "/report – show transactions for a period:\n"
            "   - /report day – for the day\n"
            "   - /report week – for the week\n"
            "   - /report month – for the month\n"
            "   - /report year – for the year\n"
            "/delete <id> – delete transaction by ID:\n"
            "/update <id> <(+/-)amount> [note] - change existing transaction\n"
            "   - /update 11 -500 – change only amount\n"
            "   - /update 11 новые продукты – change only note\n"
            "   - /update 11 +500 зарплата – change amount and note\n"
        )

    def report(self, update, context):
        chat_id = update.effective_chat.id
        if len(context.args) != 1:
            update.message.reply_text("One argument is required. Please check /help")
            return
        
        try:
            interval = str(context.args[0])
            operations = Operation.get_transactions_by_interval(chat_id, interval)
        except Exception:
            update.message.reply_text("Invalid interval")
            return

        if not operations:
            update.message.reply_text("No transactions")
            return

        lines = []
        for t in operations:
            sign = "+" if t.operation_type == Operation.INCOME else "-"
            lines.append(
                f"ID: {t.id}\n"
                f"Amount: {sign}{t.amount:.2f}\n"
                f"Note: {t.note or '-'}\n"
                f"Date: {timezone.localtime(t.created_at).strftime('%d.%m.%Y %H:%M')}\n"
            )

        response = "\n".join(lines)
        update.message.reply_text(response)
