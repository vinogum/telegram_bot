from telegram.ext import CommandHandler, Dispatcher
from botapp.models import Operation, Chat


class CommandRegistrar:
    def __init__(self, dispatcher: Dispatcher, allowed_commands=None):
        if allowed_commands is None:
            raise Exception("The allowed_commands field cannot be empty!")
        self.allowed_commands = allowed_commands
        self._dispatcher = dispatcher
        handlers = self.validate_commands(allowed_commands)
        self.register_commands(handlers)

    @property
    def dispatcher(self):
        return self._dispatcher

    def validate_commands(self, allowed_commands):
        handlers = {}
        for name in allowed_commands:
            method = getattr(self, name, None)
            if method is None:
                raise Exception(f"No such method: {name}")
            handlers[name] = method
        return handlers

    def register_commands(self, handlers):
        for name, handler in handlers.items():
            self.dispatcher.add_handler(CommandHandler(name, handler))


class FinanceBot(CommandRegistrar):
    @staticmethod
    def _handle_income_or_expense(update, context, operation_type):
        chat_id = update.effective_chat.id
        sign = "+" if operation_type == Operation.INCOME else "-"

        # If we have no arguments, then we give the income or expense amount
        if len(context.args) == 0:
            total_sum = Operation.get_sum_by_type(chat_id, operation_type)
            update.message.reply_text(
                f"Total {operation_type.capitalize()}: {sign}{total_sum}"
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
            f"{operation_type.capitalize()} was added: {sign}{amount}"
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
        update.message.reply_text(f"Current balance: {balance}")

    def help(self, update, context):
        commands = [f"/{cmd}" for cmd in self.allowed_commands]
        response = "\n".join(commands)
        update.message.reply_text("Command list:\n" + response)
