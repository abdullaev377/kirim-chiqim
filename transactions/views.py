from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from django.db.models import Count, Sum
from decimal import Decimal


from .models import (
    Currency,
    FinanceAccount,
    Category,
    Transaction
)

from .serializer import (
    CurrencySerializer,
    FinanceAccountSerializer,
    CategorySerializer,
    TransactionSerializer
)

from .filters import TransactionFilter
from shared.permissions import IsVerifiedUser


class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = [IsAuthenticated]


class FinanceAccountViewSet(viewsets.ModelViewSet):

    serializer_class = FinanceAccountSerializer
    permission_classes = [IsVerifiedUser]

    def get_queryset(self):
        return FinanceAccount.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CategoryViewSet(viewsets.ModelViewSet):

    serializer_class = CategorySerializer
    permission_classes = [IsVerifiedUser]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TransactionViewSet(viewsets.ModelViewSet):

    serializer_class = TransactionSerializer
    permission_classes = [IsVerifiedUser]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TransactionFilter
    search_fields = ['title', 'description', 'category__name']
    ordering_fields = ['date', 'amount', 'created_at', 'transaction_type']

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).select_related(
            'account', 'category', 'currency'
        )

    def perform_create(self, serializer):
        with transaction.atomic():
            account = FinanceAccount.objects.select_for_update().get(
                pk=serializer.validated_data['account'].pk,
                user=self.request.user,
            )
            instance = serializer.save(user=self.request.user)
            account.balance += self._balance_delta(instance)
            account.save(update_fields=['balance'])

    def perform_update(self, serializer):
        with transaction.atomic():
            current = Transaction.objects.select_for_update().get(pk=self.get_object().pk)
            old_account = FinanceAccount.objects.select_for_update().get(pk=current.account_id)
            old_account.balance -= self._balance_delta(current)
            old_account.save(update_fields=['balance'])
            instance = serializer.save(user=self.request.user)
            new_account = FinanceAccount.objects.select_for_update().get(
                pk=instance.account_id,
                user=self.request.user,
            )
            new_account.balance += self._balance_delta(instance)
            new_account.save(update_fields=['balance'])

    def perform_destroy(self, instance):
        with transaction.atomic():
            account = FinanceAccount.objects.select_for_update().get(pk=instance.account_id)
            account.balance -= self._balance_delta(instance)
            account.save(update_fields=['balance'])
            instance.delete()

    @staticmethod
    def _balance_delta(instance):
        amount = Decimal(instance.amount)
        return amount if instance.transaction_type == 'income' else -amount

    
    @action(detail=False, methods=["get"])
    def stats(self, request):
        qs = TransactionFilter(
            data=request.query_params,
            queryset=self.get_queryset(),
            request=request,
        ).qs

        income = qs.filter(
            transaction_type="income"
        ).aggregate(total=Sum("amount"))["total"] or 0

        expense = qs.filter(
            transaction_type="expense"
        ).aggregate(total=Sum("amount"))["total"] or 0

        by_category = list(
            qs.values('category__name')
            .annotate(total=Sum('amount'), transaction_count=Count('id'))
            .order_by('-total')
        )

        return Response({
            "income": income,
            "expense": expense,
            "balance": income - expense,
            "transaction_count": qs.count(),
            "by_category": [
                {
                    'category': item['category__name'],
                    'total': item['total'],
                    'transaction_count': item['transaction_count'],
                }
                for item in by_category
            ],
        })