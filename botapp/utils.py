from botapp.constants import MINUS_SIGN, PLUS_SIGN
from botapp.models import Operation


def reply_text(update, text):
    update.message.reply_text(text)
    

def get_sign_by_type(operation_type):
    return PLUS_SIGN if operation_type == Operation.INCOME else MINUS_SIGN


def get_chat_id(update):
    return update.effective_chat.id
    

def get_username(update):
    return update.effective_user.username
    

def reply_text(update, text):
    return update.message.reply_text(text)
