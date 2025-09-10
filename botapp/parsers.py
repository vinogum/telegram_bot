from botapp.constants import MINUS_SIGN, PLUS_SIGN
from botapp.models import Operation
from botapp.utils import get_chat_id


def parse_amount(amount) -> float:
    try:
        amount = float(amount)
        if amount < 0.01:
            raise ValueError()
        return amount
    except ValueError:
        raise ValueError("Invalid amount")


def parse_id(id) -> int:
    try:
        id = int(id)
        if id < 0:
            raise ValueError()
        return id
    except ValueError:
        raise ValueError("Invalid ID")


def parse_note(note):
    return " ".join(note)


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
        if not self.__is_valid:
            raise Exception("Call `.is_valid()` first")
        return self.__validated_data

    def is_valid(self):
        try:
            self.__validated_data = self.parse_data()
        except Exception as e:
            self.__error = str(e)
            return False
        
        self.__is_valid = True
        return True

    def parse_data(self):
        """There must be custom logic here."""
        raise NotImplementedError()
    
    def is_args(self):
        return bool(self.context.args)


class IncomeAndExpenseParser(Parser):
    def parse_data(self):
        command_args = self.context.args
        amount = parse_amount(command_args[0])
        note = parse_note(command_args[1:]) if len(command_args) > 1 else ""
        return {"amount": amount, "note": note}
    

class DeleteParser(Parser):
    def parse_data(self):
        command_args = self.context.args
        if not self.is_args():
            raise Exception("One argument is required")
        
        operation_id = parse_id(command_args[0])
        return {"operation_id": operation_id}
    

class UpdateParser(Parser):
    def parse_data(self):
        command_args = self.context.args
        if len(command_args) < 2:
            raise Exception("Two arguments are required")

        operation_id = parse_id(command_args[0])

        amount, note, operation_type = None, None, None
        startswith_plus = command_args[1].startswith(PLUS_SIGN)
        startswith_minus = command_args[1].startswith(MINUS_SIGN)

        # If there is only amount or amount with note
        if startswith_plus or startswith_minus:
            amount = parse_amount(command_args[1])
            operation_type = Operation.INCOME if startswith_plus else Operation.EXPENSE

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
    

class ReportParser(Parser):
    def parse_data(self):
        command_args = self.context.args
        if len(command_args) != 1:
            raise Exception("One argument is required")
        
        chat_id = get_chat_id(self.update)
        interval = str(command_args[0])
        operations = Operation.get_transactions_by_interval(chat_id, interval)
 
        if not operations:
            raise Exception("No transactions")
        return {"operations": operations}
