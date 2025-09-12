from django.core.validators import MinValueValidator
from django.db import models
from datetime import timedelta
from django.utils import timezone
from enum import Enum


class Chat(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)
    username = models.CharField(blank=False, null=False)


class Interval(Enum):
    YESTERDAY = "yesterday"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class OperationType(models.TextChoices):
    INCOME = "income", "Income"
    EXPENSE = "expense", "Expense"


class Operation(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    operation_type = models.CharField(
        max_length=10, choices=OperationType.choices, default=None
    )
    note = models.CharField(max_length=255, null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def get_transactions_by_interval(cls, chat_id: int, interval: Interval):
        now = timezone.now()

        match interval:
            case Interval.DAY:
                start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                end = now
            case Interval.YESTERDAY:
                start = (now - timedelta(days=1)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                end = (now - timedelta(days=1)).replace(
                    hour=23, minute=59, second=59, microsecond=999999
                )
            case Interval.WEEK:
                start = (now - timedelta(days=now.weekday())).replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                end = now
            case Interval.MONTH:
                start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                end = now
            case Interval.YEAR:
                start = now.replace(
                    month=1, day=1, hour=0, minute=0, second=0, microsecond=0
                )
                end = now
            case _:
                raise ValueError("Unknown interval")

        operations = cls.objects.filter(
            chat_id=chat_id, created_at__gte=start, created_at__lte=end
        )
        return operations

    @classmethod
    def get_sum_by_type(cls, chat_id: int, operation_type) -> float:
        if operation_type not in OperationType:
            raise ValueError("Invalid operation type")
        
        operations = cls.objects.filter(
            chat_id=chat_id, operation_type=operation_type
        )
        total_amount = operations.aggregate(total=models.Sum("amount"))["total"] or 0
        return total_amount

    @classmethod
    def get_balance(cls, chat_id: int):
        total_expense = cls.get_sum_by_type(chat_id, OperationType.EXPENSE)
        total_income = cls.get_sum_by_type(chat_id, OperationType.INCOME)
        return total_income - total_expense

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
