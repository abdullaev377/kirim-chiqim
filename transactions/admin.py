from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum

from .models import Category, Currency, FinanceAccount, Transaction


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['code', 'name']
    ordering = ['code']


@admin.register(FinanceAccount)
class FinanceAccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'account_type', 'currency', 'balance']
    list_filter = ['account_type', 'currency']
    search_fields = ['name', 'user__username', 'user__email']
    readonly_fields = ['balance']
    ordering = ['user__username', 'name']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'category_type']
    list_filter = ['category_type']
    search_fields = ['name', 'user__username', 'user__email']
    ordering = ['user__username', 'category_type', 'name']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):

    list_display = [
        'id',
        'title',
        'user',
        'account',
        'formatted_amount',
        'transaction_type_display',
        'category',
        'date',
        'created_at',
    ]

    list_filter = [
        'transaction_type',
        'category',
        'date',
        'created_at',
    ]

    search_fields = [
        'title',
        'description',
        'category__name',
        'account__name',
        'user__username',
    ]

    readonly_fields = [
        'created_at',
            'updated_at',
    ]

    fieldsets = (
        ('Transaction Information', {
            'fields': (
                'amount',
                'title',
                'transaction_type',
                'description',
            )
        }),
        ('Details', {
            'fields': (
                'category',
                'date',
                'account',
                'currency',
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )

    date_hierarchy = 'date'
    ordering = ['-created_at']

    # =========================
    # DISPLAY TYPE
    # =========================
    def transaction_type_display(self, obj):
        if obj.transaction_type == "income":
            color = 'green'
            label = 'Kirim (Income)'
        else:
            color = 'red'
            label = 'Chiqim (Expense)'

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            label
        )

    transaction_type_display.short_description = 'Type'

    # =========================
    # AMOUNT DISPLAY (LIST)
    # =========================
    def formatted_amount(self, obj):
        symbol = '+' if obj.transaction_type == "income" else '−'
        return f"{symbol} {obj.amount:,.2f}"

    formatted_amount.short_description = 'Amount'

    # =========================
    # AMOUNT DISPLAY (DETAIL)
    # =========================
    def formatted_amount_display(self, obj):
        if obj.transaction_type == "income":
            color = 'green'
            symbol = '+'
        else:
            color = 'red'
            symbol = '−'

        return format_html(
            '<span style="color: {}; font-weight: bold; font-size: 1.2em;">{} {}</span>',
            color,
            symbol,
            f"{obj.amount:,.2f}"
        )

    formatted_amount_display.short_description = 'Formatted Amount'

    # =========================
    # SUMMARY DASHBOARD
    # =========================
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        queryset = self.get_queryset(request)

        income_total = queryset.filter(
            transaction_type="income"
        ).aggregate(total=Sum('amount'))['total'] or 0

        expense_total = queryset.filter(
            transaction_type="expense"
        ).aggregate(total=Sum('amount'))['total'] or 0

        extra_context['summary_stats'] = {
            'total_income': income_total,
            'total_expense': expense_total,
            'balance': income_total - expense_total,
            'total_transactions': queryset.count(),
        }

        return super().changelist_view(request, extra_context)

    # =========================
    # CUSTOM CSS
    # =========================
    class Media:
        css = {
            'all': ('admin/css/transaction_admin.css',)
        }