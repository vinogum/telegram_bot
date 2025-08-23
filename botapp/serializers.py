from rest_framework import serializers
import re


class TelegramMessageSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        message = data.get("message", {})
        chat = message.get("chat", {})
        from_user = message.get("from", {})

        return {
            "chat_id": chat.get("id"),
            "username": from_user.get("username") or chat.get("username") or "",
            "text": message.get("text"),
        }

    def validate(self, data):
        text = data["text"]

        simple_cmd_pattern = r"^/[a-zA-Z]{3,}$"
        args_cmd_pattern = r"^/[a-zA-Z]{3,}\s+\d+(\.\d+)?(?:\s+.+)?$"

        if not (
            re.fullmatch(simple_cmd_pattern, text)
            or re.fullmatch(args_cmd_pattern, text)
        ):
            raise serializers.ValidationError("Invalid command format")

        if re.fullmatch(args_cmd_pattern, text):
            parts = text.split(maxsplit=2)
            data["cmd_name"] = parts[0].lstrip("/")
            data["amount"] = float(parts[1])
            data["note"] = parts[2] if len(parts) > 2 else ""
            data["action"] = "add"
        else:
            data["cmd_name"] = text.lstrip("/")
            data["action"] = "query"

        return data
