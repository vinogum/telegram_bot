from botapp.constants import MINUS_SIGN, PLUS_SIGN
from botapp.models import OperationType


def get_operation_sign(operation_type: OperationType) -> str:
    return PLUS_SIGN if operation_type == OperationType.INCOME else MINUS_SIGN


def reply_text(update, text):
    return update.message.reply_text(text)
