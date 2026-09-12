from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import DONE, VIA_EMAIL, CustomUser

from .models import Category, Currency, FinanceAccount, Transaction


class TransactionApiTests(APITestCase):
	def setUp(self):
		self.currency = Currency.objects.create(name='US Dollar', code='USD')
		self.user = CustomUser.objects.create_user(
			username='alice', email='alice@example.com', password='StrongPass123',
			auth_type=VIA_EMAIL, auth_status=DONE,
		)
		self.other_user = CustomUser.objects.create_user(
			username='bob', email='bob@example.com', password='StrongPass123',
			auth_type=VIA_EMAIL, auth_status=DONE,
		)
		self.account = FinanceAccount.objects.create(
			user=self.user, name='Main', account_type='card', currency=self.currency,
		)
		self.other_account = FinanceAccount.objects.create(
			user=self.other_user, name='Other Main', account_type='card', currency=self.currency,
		)
		self.category = Category.objects.create(user=self.user, name='Salary', category_type='income')
		self.other_category = Category.objects.create(user=self.other_user, name='Other Salary', category_type='income')
		self.client.force_authenticate(self.user)

	def transaction_payload(self, **overrides):
		payload = {
			'account': self.account.name,
			'category': self.category.name,
			'currency': self.currency.code,
			'transaction_type': 'income',
			'title': 'Salary',
			'amount': '500.00',
			'date': '2026-09-01',
			'description': 'Monthly salary',
		}
		payload.update(overrides)
		return payload

	def test_transaction_crud_updates_balance(self):
		response = self.client.post('/api/transactions/', self.transaction_payload())
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.account.refresh_from_db()
		self.assertEqual(self.account.balance, Decimal('500.00'))

		transaction = Transaction.objects.get()
		response = self.client.patch(
			f'/api/transactions/{transaction.pk}/',
			{'amount': '200.00', 'transaction_type': 'expense', 'category': 'Salary'},
		)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

		expense_category = Category.objects.create(user=self.user, name='Rent', category_type='expense')
		response = self.client.patch(
			f'/api/transactions/{transaction.pk}/',
			{'amount': '200.00', 'transaction_type': 'expense', 'category': expense_category.name},
		)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.account.refresh_from_db()
		self.assertEqual(self.account.balance, Decimal('-200.00'))

		response = self.client.delete(f'/api/transactions/{transaction.pk}/')
		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
		self.account.refresh_from_db()
		self.assertEqual(self.account.balance, Decimal('0.00'))

	def test_foreign_objects_are_rejected_and_list_is_isolated(self):
		response = self.client.post(self.base_url, self.transaction_payload(
			account=self.other_account.name, category=self.other_category.name,
		))
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

		Transaction.objects.create(
			user=self.other_user, account=self.other_account, category=self.other_category,
			currency=self.currency, transaction_type='income', title='Private',
			amount=Decimal('10.00'), date='2026-09-01',
		)
		response = self.client.get(self.base_url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data, [])

	def test_filters_search_and_amount(self):
		Transaction.objects.create(
			user=self.user, account=self.account, category=self.category, currency=self.currency,
			transaction_type='income', title='Salary', description='Payroll',
			amount=Decimal('500.00'), date='2026-09-01',
		)
		response = self.client.get(self.base_url + '?search=payroll&amount_min=400')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 1)

	def test_foreign_transaction_cannot_be_updated_or_deleted(self):
		foreign_transaction = Transaction.objects.create(
			user=self.other_user, account=self.other_account, category=self.other_category,
			currency=self.currency, transaction_type='income', title='Private',
			amount=Decimal('10.00'), date='2026-09-01',
		)
		response = self.client.patch(
			f'/api/transactions/{foreign_transaction.pk}/',
			{'title': 'Changed'}, format='json'
		)
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		response = self.client.delete(f'/api/transactions/{foreign_transaction.pk}/')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertTrue(Transaction.objects.filter(pk=foreign_transaction.pk).exists())

	def test_stats_returns_transaction_count(self):
		Transaction.objects.create(
			user=self.user, account=self.account, category=self.category, currency=self.currency,
			transaction_type='income', title='Salary', amount=Decimal('500.00'), date='2026-09-01',
		)
		response = self.client.get('/api/transactions/stats/')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['transaction_count'], 1)

	@property
	def base_url(self):
		return '/api/transactions/'
