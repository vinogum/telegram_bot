from botapp.models import Operation, Chat
from django.utils import timezone
from botapp.utils import *


def start(update, context):
    update.message.reply_text(START_TEXT)


def handle_income_or_expense(update, context, operation_type):
    chat_id = get_chat_id(update)
    username = update.effective_user.username
    sign = "+" if operation_type == Operation.INCOME else "-"

    # If we have no arguments, then we give the income or expense amount
    if not context.args:
        total_sum = Operation.get_sum_by_type(chat_id, operation_type)
        reply_text(update, f"Total {operation_type}: {sign}{total_sum:.2f}")
        return

    # First argument is amount
    amount = parse_amount(context.args[0])
    if not amount:
        reply_text(update, "Incorrect amount")
        return

    # Other arguments are note
    note = " ".join(context.args[1:]) if len(context.args) > 1 else ""
    chat, _ = Chat.objects.get_or_create(chat_id=chat_id, username=username)

    Operation.objects.create(
        chat=chat, amount=amount, operation_type=operation_type, note=note
    )
    reply_text(update, f"{operation_type.capitalize()} added: {sign}{amount:.2f}")


def income(update, context):
    handle_income_or_expense(update, context, Operation.INCOME)


def expense(update, context):
    handle_income_or_expense(update, context, Operation.EXPENSE)


def balance(update, context):
    chat_id = get_chat_id(update)
    balance = Operation.get_balance(chat_id=chat_id)
    reply_text(update, f"Total balance: {balance:.2f}")


def delete(update, context):
    if len(context.args) != 1:
        reply_text(
            update, "One argument (ID) is required to delete. Please check /help"
        )
        return

    id = parse_id(context.args[0])
    if not id:
        reply_text(update, "Invalid ID")
        return

    chat_id = get_chat_id(update)
    transaction = Operation.objects.filter(id=id, chat_id=chat_id).first()
    if not transaction:
        reply_text(update, "You have no such transaction")
        return

    transaction.delete()
    reply_text(update, f"Transaction {id} successfully deleted")


def update(update, context):
    chat_id = get_chat_id(update)

    if len(context.args) < 2:
        reply_text(update, "Two arguments are required. Please check /help")
        return

    transaction_id = parse_id(context.args[0])
    if not transaction_id:
        reply_text(update, "Invalid ID")
        return

    transaction = Operation.objects.filter(id=transaction_id, chat_id=chat_id).first()
    if not transaction:
        reply_text(update, "Transaction not found")
        return

    amount = None
    note = None
    operation_type = None

    if context.args[1].startswith("+") or context.args[1].startswith("-"):
        amount = parse_amount(context.args[1])
        if not amount:
            reply_text(update, "Invalid amount")
            return

        operation_type = Operation.INCOME if amount > 0 else Operation.EXPENSE
        if len(context.args) >= 3:
            note = " ".join(context.args[2:])
    else:
        note = " ".join(context.args[1:])

    if amount and note:
        transaction.amount = amount
        transaction.note = note
        transaction.operation_type = operation_type
    elif amount:
        transaction.amount = amount
        transaction.operation_type = operation_type
    else:
        transaction.note = note

    transaction.save()
    reply_text(update, f"Transaction {transaction_id} updated successfully")


def help(update, context):
    reply_text(update, HELP_TEXT)


def report(update, context):
    chat_id = get_chat_id(update)
    if len(context.args) != 1:
        reply_text(update, "One argument is required. Please check /help")
        return

    try:
        interval = str(context.args[0])
        operations = Operation.get_transactions_by_interval(chat_id, interval)
    except Exception:
        reply_text(update, "Invalid interval")
        return
    if not operations:
        reply_text(update, "No transactions")
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
    reply_text(update, response)
