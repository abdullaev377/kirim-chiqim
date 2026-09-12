from django.urls import path, include
from rest_framework.routers import DefaultRouter


from .views import (
    CurrencyViewSet,
    FinanceAccountViewSet,
    CategoryViewSet,
    TransactionViewSet
)


router = DefaultRouter()


router.register(
    "currencies",
    CurrencyViewSet
)


router.register(
    "accounts",
    FinanceAccountViewSet,
    basename="accounts"
)


router.register(
    "categories",
    CategoryViewSet,
    basename="categories"
)


router.register(
    "transactions",
    TransactionViewSet,
    basename="transactions"
)



urlpatterns = [
    path(
        "",
        include(router.urls)
    )
]