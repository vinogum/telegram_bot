from botapp.parsers import IncomeAndExpenseParser, DeleteParser, UpdateParser, ReportParser
from botapp.models import Operation, Chat
from django.utils import timezone
from botapp import constants
from botapp.utils import *


def handle_income_or_expense(update, context, operation_type):
    parser = IncomeAndExpenseParser(update, context)

    chat_id = get_chat_id(update)
    sign = get_sign_by_type(operation_type)

    # If we have no arguments, then we give the income or expense amount
    if not parser.is_args():
        total_sum = Operation.get_sum_by_type(chat_id, operation_type)
        reply_text(update, f"Total {operation_type}: {sign}{total_sum:.2f}")
        return
    
    # Else, we parse command arguments to perform other command
    if not parser.is_valid():
        reply_text(update, parser.error)
        return
    
    amount = parser.validated_data["amount"]
    note = parser.validated_data["note"]
    username = get_username(update)

    
    chat, _ = Chat.objects.get_or_create(id=chat_id, username=username)

    Operation.objects.create(
        chat=chat, amount=amount, operation_type=operation_type, note=note
    )
    reply_text(update, f"{operation_type.capitalize()} added: {sign}{amount:.2f}")


def delete(update, context):
    chat_id = get_chat_id(update)
    parser = DeleteParser(update, context)
    print(parser.error)

    if not parser.is_valid():
        reply_text(update, parser.error)
        return

    operation_id = parser.validated_data["operation_id"]
    operation = Operation.objects.filter(id=operation_id, chat_id=chat_id).first()
    if not operation:
        reply_text(update, "You have no such transaction")
        return

    operation.delete()
    reply_text(update, f"Transaction {operation_id} successfully deleted")


def update(update, context):
    chat_id = get_chat_id(update)
    parser = UpdateParser(update, context)

    if not parser.is_valid():
        reply_text(update, parser.error)
        return
    
    operation_id = parser.validated_data["operation_id"]

    operation = Operation.objects.filter(id=operation_id, chat_id=chat_id).first()
    if not operation:
        reply_text(update, "Transaction not found")
        return
    
    for attr, value in parser.validated_data.items():
        if value:
            setattr(operation, attr, value)

    operation.save()
    reply_text(update, f"Transaction {operation_id} updated successfully")


def report(update, context):
    parser = ReportParser(update, context)
    if not parser.is_valid():
        reply_text(update, parser.error)

    operations = parser.validated_data["operations"]

    lines = []
    for t in operations:
        sign = PLUS_SIGN if t.operation_type == Operation.INCOME else MINUS_SIGN
        lines.append(
            f"ID: {t.id}\n"
            f"Amount: {sign}{t.amount:.2f}\n"
            f"Note: {t.note or '-'}\n"
            f"Date: {timezone.localtime(t.created_at).strftime('%d.%m.%Y %H:%M')}\n"
        )
    report = "\n".join(lines)
    reply_text(update, report)


def help(update, context):
    reply_text(update, constants.HELP_TEXT)


def income(update, context):
    handle_income_or_expense(update, context, Operation.INCOME)


def expense(update, context):
    handle_income_or_expense(update, context, Operation.EXPENSE)


def balance(update, context):
    chat_id = get_chat_id(update)
    balance = Operation.get_balance(chat_id=chat_id)
    reply_text(update, f"Total balance: {balance:.2f}")


def start(update, context):
    reply_text(update, constants.START_TEXT)
