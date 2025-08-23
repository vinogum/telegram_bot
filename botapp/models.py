from django.core.validators import MinValueValidator
from django.db import models


class Chat(models.Model):
    chat_id = models.PositiveBigIntegerField(primary_key=True)
    username = models.CharField(blank=False, null=False)


class Operation(models.Model):
    INCOME = "income"
    EXPENSE = "expense"

    OPERATION_TYPES = [
        (INCOME, "Income"),
        (EXPENSE, "Expense"),
    ]

    chat = models.ForeignKey(Chat, on_delete=models.DO_NOTHING)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    operation_type = models.CharField(
        max_length=10, choices=OPERATION_TYPES, default=None
    )
    note = models.CharField(max_length=255, null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def get_sum_by_type(cls, chat_id: int, operation_type: str) -> float:
        if operation_type not in [cls.INCOME, cls.EXPENSE]:
            raise ValueError("Invalid operation type")
        operations_qs = cls.objects.filter(chat_id=chat_id, operation_type=operation_type)
        total_amount = operations_qs.aggregate(total=models.Sum("amount"))["total"] or 0
        return total_amount

    @classmethod
    def get_balance(cls, chat_id):
        total_expense = cls.get_sum_by_type(chat_id, cls.EXPENSE)
        total_income = cls.get_sum_by_type(chat_id, cls.INCOME)
        return total_income - total_expense
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
