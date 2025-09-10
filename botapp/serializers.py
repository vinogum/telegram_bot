from rest_framework import serializers
from botapp.models import Operation


class UpdateValidator(serializers.ModelSerializer):
    class Meta:
        model = Operation
        fields = ("amount", "note", "operation_type")
        extra_kwargs = {"amount": {"required": False}, "note": {"required": False}}
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
