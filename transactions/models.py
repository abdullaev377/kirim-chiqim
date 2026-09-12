from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Currency(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    code = models.CharField(max_length=3, unique=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return self.code


class FinanceAccount(models.Model):

    PAYMENT_TYPES = (
        ("cash", "Naqd pul"),
        ("card", "Karta"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='finance_accounts')

    name = models.CharField(max_length=100)

    account_type = models.CharField(
        max_length=20,
        choices=PAYMENT_TYPES
    )

    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name='accounts')

    balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['user', 'name'], name='unique_account_name_per_user'),
        ]
        indexes = [models.Index(fields=['user', 'currency'])]


class Category(models.Model):

    CATEGORY_TYPES = (
        ("income", "Kirim"),
        ("expense", "Chiqim"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="categories"
    )

    name = models.CharField(max_length=100)

    category_type = models.CharField(
        max_length=10,
        choices=CATEGORY_TYPES
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['category_type', 'name']
        constraints = [
            models.UniqueConstraint(fields=['user', 'name'], name='unique_category_name_per_user'),
        ]
        indexes = [models.Index(fields=['user', 'category_type'])]


class Transaction(models.Model):

    TRANSACTION_TYPES = (
        ("income", "Kirim"),
        ("expense", "Chiqim"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')

    account = models.ForeignKey(
        FinanceAccount,
        on_delete=models.PROTECT,
        related_name='transactions',
    )

    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='transactions')

    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name='transactions',
    )

    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPES
    )

    title = models.CharField(max_length=200, default='')

    amount = models.DecimalField(max_digits=15, decimal_places=2)

    date = models.DateField()

    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', '-date']),
            models.Index(fields=['user', 'transaction_type']),
            models.Index(fields=['account', '-date']),
        ]

    def __str__(self):
        return f"{self.category} - {self.amount}"