from botapp.constants import ALLOWED_COMMANDS, COMMANDS_MODULE
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from botapp.command_handlers import CommandRegistrar
from rest_framework.response import Response
from rest_framework.views import APIView
from telegram.ext import Dispatcher
from botapp.utils import reply_text
from rest_framework import status
from telegram import Update
from botapp.telegram_bot import bot


@method_decorator(csrf_exempt, name="dispatch")
class TelegramWebhookView(APIView):
    def post(self, request, *args, **kwargs):
        update = Update.de_json(request.data, bot)
        dispatcher = Dispatcher(
            bot, update_queue=None, workers=0, use_context=True
        )

        registrar = CommandRegistrar(ALLOWED_COMMANDS, COMMANDS_MODULE)
        if not registrar.is_valid():
            reply_text(update, registrar.error)
            return Response(status=status.HTTP_200_OK)
        
        registrar.register_commands(dispatcher)
        dispatcher.process_update(update)
        return Response(status=status.HTTP_200_OK)
