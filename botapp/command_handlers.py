from telegram.ext import CommandHandler, Dispatcher
from botapp import commands


class CommandRegistrar:
    def __init__(self, dispatcher: Dispatcher, allowed_commands=None):
        if allowed_commands is None:
            raise TypeError()
        self.allowed_commands = allowed_commands
        self._dispatcher = dispatcher
        handlers = self.validate_commands(allowed_commands)
        self.register_commands(handlers)

    @property
    def dispatcher(self):
        return self._dispatcher

    def validate_commands(self, allowed_commands):
        """Function returns handlers (dict) where key is command name and handler is address to function"""
        handlers = {}
        for command_name in allowed_commands:
            # The commands variable is a module that contains all functions
            handler = getattr(commands, command_name, None)
            if not handler:
                raise AttributeError()
            handlers[command_name] = handler
        return handlers

    def register_commands(self, handlers):
        for command_name, handler in handlers.items():
            self.dispatcher.add_handler(CommandHandler(command_name, handler))
