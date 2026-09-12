from rest_framework import serializers

from .models import (
    Currency,
    FinanceAccount,
    Category,
    Transaction
)



class CurrencySerializer(serializers.ModelSerializer):

    class Meta:
        model = Currency

        fields = [
            "id",
            "name",
            "code"
        ]



class FinanceAccountSerializer(serializers.ModelSerializer):

    balance = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )

    currency = serializers.SlugRelatedField(
        slug_field="code",
        queryset=Currency.objects.all()
    )


    class Meta:
        model = FinanceAccount

        fields = [
            "id",
            "name",
            "account_type",
            "currency",
            "balance"
        ]
        read_only_fields = ["id", "balance"]

    def validate(self, attrs):
        if self.instance and 'balance' in attrs and attrs['balance'] != self.instance.balance:
            raise serializers.ValidationError({'balance': 'Balance is managed by transactions.'})
        return attrs



class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category

        fields = [
            "id",
            "name",
            "category_type"
        ]



class TransactionSerializer(serializers.ModelSerializer):

    account = serializers.SlugRelatedField(
        slug_field='name',
        queryset=FinanceAccount.objects.all()
    )

    category = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Category.objects.all()
    )

    currency = serializers.SlugRelatedField(
        slug_field='code',
        queryset=Currency.objects.all()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            self.fields['account'].queryset = FinanceAccount.objects.filter(user=request.user)
            self.fields['category'].queryset = Category.objects.filter(user=request.user)
            self.fields['currency'].queryset = Currency.objects.all()

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Amount must be greater than zero.')
        return value

    def validate(self, attrs):
        account = attrs.get('account', getattr(self.instance, 'account', None))
        currency = attrs.get('currency', getattr(self.instance, 'currency', None))
        transaction_type = attrs.get('transaction_type', getattr(self.instance, 'transaction_type', None))
        category = attrs.get('category', getattr(self.instance, 'category', None))
        if account and currency and account.currency_id != currency.id:
            raise serializers.ValidationError({'currency': 'Currency must match the account currency.'})
        if category and transaction_type and category.category_type != transaction_type:
            raise serializers.ValidationError({'category': 'Category type must match transaction type.'})
        return attrs

    class Meta:
        model = Transaction
        fields = [
            'id',
            'account',
            'category',
            'currency',
            'transaction_type',
            'title',
            'amount',
            'date',
            'description',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']