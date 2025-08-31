from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from botapp.telegram_bot import bot
from telegram import Update
from telegram.ext import Dispatcher
from botapp.command_handlers import CommandRegistrar
from botapp.utils import reply_text

ALLOWED_COMMANDS = [
    "help",
    "income",
    "expense",
    "balance",
    "report",
    "start",
    "delete",
    "update",
]


@method_decorator(csrf_exempt, name="dispatch")
class TelegramWebhookView(APIView):
    def post(self, request, *args, **kwargs):
        update = Update.de_json(request.data, bot)
        dispatcher = Dispatcher(bot, update_queue=None, workers=0, use_context=True)

        try:
            registrar = CommandRegistrar(dispatcher, allowed_commands=ALLOWED_COMMANDS)
        except Exception as e:
            reply_text(f"Command Registration Error: {e}")
            return Response(status=status.HTTP_200_OK)
        registrar.dispatcher.process_update(update)

        return Response(status=status.HTTP_200_OK)
