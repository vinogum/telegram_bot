from botapp.models import Operation, Chat, OperationType
from botapp.utils import get_operation_sign, reply_text
from botapp.constants import HELP_TEXT, START_TEXT
from django.utils import timezone
from botapp import parsers


def handle_income_or_expense(update, context, operation_type):
    parser = parsers.IncomeAndExpenseParser(update, context)
    sign = get_operation_sign(operation_type)

    # If we have no arguments, then we give the income or expense amount
    if not parser.is_args():
        total_sum = Operation.get_sum_by_type(parser.chat_id, operation_type)
        reply_text(update, f"Total {operation_type.value}: {sign}{total_sum:.2f}")
        return

    # Else, we parse command arguments to perform other command
    if not parser.is_valid():
        reply_text(update, parser.error)
        return

    amount = parser.validated_data["amount"]
    note = parser.validated_data["note"]
    username = parser.username

    chat, _ = Chat.objects.get_or_create(id=parser.chat_id, username=username)

    Operation.objects.create(
        chat=chat, amount=amount, operation_type=operation_type, note=note
    )
    reply_text(update, f"{operation_type.value.capitalize()} added: {sign}{amount:.2f}")


def delete(update, context):
    parser = parsers.DeleteParser(update, context)

    if not parser.is_valid():
        reply_text(update, parser.error)
        return

    operation_id = parser.validated_data["operation_id"]
    operation = Operation.objects.filter(
        id=operation_id, chat_id=parser.chat_id
    ).first()
    if not operation:
        reply_text(update, "You have no such transaction")
        return

    operation.delete()
    reply_text(update, f"Transaction {operation_id} successfully deleted")


def update(update, context):
    parser = parsers.UpdateParser(update, context)

    if not parser.is_valid():
        reply_text(update, parser.error)
        return

    operation_id = parser.validated_data["operation_id"]

    operation = Operation.objects.filter(
        id=operation_id, chat_id=parser.chat_id
    ).first()
    if not operation:
        reply_text(update, "Transaction not found")
        return

    for attr, value in parser.validated_data.items():
        if value:
            setattr(operation, attr, value)

    operation.save()
    reply_text(update, f"Transaction {operation_id} updated successfully")


def report(update, context):
    parser = parsers.ReportParser(update, context)
    if not parser.is_valid():
        reply_text(update, parser.error)
        return

    operations = parser.validated_data["operations"]

    lines = []
    for t in operations:
        sign = get_operation_sign(t.operation_type)
        lines.append(
            f"ID: {t.id}\n"
            f"Amount: {sign}{t.amount:.2f}\n"
            f"Note: {t.note or '-'}\n"
            f"Date: {timezone.localtime(t.created_at).strftime('%d.%m.%Y %H:%M')}\n"
        )
    report = "\n".join(lines)
    reply_text(update, report)


def balance(update, context):
    chat_id = update.effective_chat.id
    balance = Operation.get_balance(chat_id=chat_id)
    reply_text(update, f"Total balance: {balance:.2f}")


def help(update, context):
    reply_text(update, HELP_TEXT)


def income(update, context):
    handle_income_or_expense(update, context, OperationType.INCOME)


def expense(update, context):
    handle_income_or_expense(update, context, OperationType.EXPENSE)


def start(update, context):
    reply_text(update, START_TEXT)
