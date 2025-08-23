from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from botapp.telegram_bot import bot
from telegram import Update
from telegram.ext import Dispatcher
from botapp.command_handlers import FinanceBot


@method_decorator(csrf_exempt, name="dispatch")
class TelegramWebhookView(APIView):
    def post(self, request, *args, **kwargs):
        update = Update.de_json(request.data, bot)

        dispatcher = Dispatcher(bot, update_queue=None, workers=0, use_context=True)
        try:
            tgbot = FinanceBot(dispatcher, allowed_commands={"help", "income", "expense", "balance"})
        except Exception as e:
            update.message.reply_text(str(e))
            return Response(status=status.HTTP_200_OK)

        tgbot.dispatcher.process_update(update)

        return Response(status=status.HTTP_200_OK)
