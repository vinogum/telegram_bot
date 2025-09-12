from botapp.exceptions import CommandRegistrarError
from telegram.ext import CommandHandler
import importlib


class CommandRegistrar:
    def __init__(self, allowed_commands: list, commands_module_path: str):
        self._allowed_commands = allowed_commands
        self._commands_module_path = commands_module_path
        self._error = None
        self._is_valid = False
        self._handlers = None

    @property
    def handlers(self):
        if not self._is_valid:
            raise CommandRegistrarError("Commands not validated yet")
        return self._handlers

    @property
    def error(self):
        return self._error

    def is_valid(self) -> bool:
        try:
            self.validate()
            self._is_valid = True
            self._error = None
        except CommandRegistrarError as e:
            self._error = str(e)
            self._is_valid = False
        return self._is_valid

    def get_commands_module(self):
        try:
            return importlib.import_module(self._commands_module_path)
        except ModuleNotFoundError:
            raise CommandRegistrarError(f"No such commands module: {self._commands_module_path}")

    def validate(self):
        commands_module = self.get_commands_module()
        handlers = {}
        for command_name in self._allowed_commands:
            if not hasattr(commands_module, command_name):
                raise CommandRegistrarError(f"No such command: {command_name}")
            handlers[command_name] = getattr(commands_module, command_name)
        self._handlers = handlers

    def register_commands(self, dispatcher):
        for command_name, handler in self.handlers.items():
            dispatcher.add_handler(CommandHandler(command_name, handler))
