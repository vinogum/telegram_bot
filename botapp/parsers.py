from botapp.constants import MINUS_SIGN, PLUS_SIGN
from botapp.models import Operation, OperationType, Interval
from botapp.exceptions import ParsingError


def get_interval(interval: Interval):
    try:
        interval = Interval(interval)
    except Exception:
        raise ParsingError("There is no such interval. Please check /help")
    return interval


def parse_amount(amount) -> float:
    try:
        amount = float(amount)
        return abs(amount)
    except ValueError:
        raise ParsingError("Invalid amount")


def parse_id(id) -> int:
    try:
        id = int(id)
        if id < 0:
            raise ParsingError("The ID can't be less than 0")
        return id
    except ValueError:
        raise ParsingError("Invalid ID")


def parse_note(note: list) -> str:
    return " ".join(note)


class ParserUtils:
    """The properties can be used even without validation `.is_valid()`."""

    @property
    def chat_id(self):
        if not hasattr(self, "update"):
            raise ParsingError("Hasn't attribute `update`")
        return self.update.effective_chat.id

    @property
    def username(self):
        if not hasattr(self, "update"):
            raise ParsingError("Hasn't attribute `update`")
        return self.update.effective_user.username


class Parser:
    def __init__(self, update, context):
        self.__context = context
        self.__update = update
        self.__is_valid = False
        self.__error = None
        self.__validated_data = None

    @property
    def context(self):
        return self.__context

    @property
    def update(self):
        return self.__update

    @property
    def error(self):
        return self.__error

    @property
    def validated_data(self):
        """
        Check `.is_valid()` before accessing `.validated_data`,
        or it will raise an exception.
        """
        if not self.__is_valid:
            raise ParsingError("Call `.is_valid()` first")
        return self.__validated_data

    def is_valid(self):
        """Used to understand if data was successfully parsed."""
        try:
            self.__validated_data = self.parse_data()
        except ParsingError as e:
            self.__error = str(e)
            return False

        self.__is_valid = True
        return True

    def parse_data(self):
        """There must be custom logic here."""
        raise NotImplementedError()

    def is_args(self):
        return bool(self.context.args)


class IncomeAndExpenseParser(Parser, ParserUtils):
    def parse_data(self):
        command_args = self.context.args
        amount = parse_amount(command_args[0])
        note = parse_note(command_args[1:]) if len(command_args) > 1 else ""
        return {"amount": amount, "note": note}


class DeleteParser(Parser, ParserUtils):
    def parse_data(self):
        command_args = self.context.args
        if not self.is_args():
            raise ParsingError("One argument is required")

        operation_id = parse_id(command_args[0])
        return {"operation_id": operation_id}


class UpdateParser(Parser, ParserUtils):
    def parse_data(self):
        command_args = self.context.args
        if len(command_args) < 2:
            raise ParsingError("Two arguments are required")

        operation_id = parse_id(command_args[0])

        amount, note, operation_type = None, None, None
        startswith_plus = command_args[1].startswith(PLUS_SIGN)
        startswith_minus = command_args[1].startswith(MINUS_SIGN)

        # If there is only amount or amount with note
        if startswith_plus or startswith_minus:
            operation_type = (
                OperationType.INCOME if startswith_plus else OperationType.EXPENSE
            )
            amount = parse_amount(command_args[1])

            if len(command_args) >= 3:
                note = parse_note(command_args[2:])

        # if there is only note
        else:
            note = parse_note(command_args[1:])

        return {
            "operation_id": operation_id,
            "amount": amount,
            "note": note,
            "operation_type": operation_type,
        }


class ReportParser(Parser, ParserUtils):
    def parse_data(self):
        command_args = self.context.args
        if len(command_args) != 1:
            raise ParsingError("One argument is required")

        chat_id = self.chat_id
        interval = get_interval(command_args[0])
        operations = Operation.get_transactions_by_interval(chat_id, interval)
        if not operations:
            raise ParsingError("No transactions")

        return {"operations": operations}
