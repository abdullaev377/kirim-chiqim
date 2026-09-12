from django.test import TestCase

from .models import CODE_VERIFY, CustomUser, VIA_EMAIL
from .serializer import SignUpSerializer, VerifyCodeSerializer


class AuthSerializerTests(TestCase):
    def test_signup_serializer_creates_user_and_code_for_email(self):
        payload = {'email_or_phone_number': 'Demo@Example.com'}

        serializer = SignUpSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        user = serializer.save()
        self.assertEqual(user.email, 'demo@example.com')
        self.assertEqual(user.auth_type, VIA_EMAIL)
        self.assertTrue(user.codes.exists())

    def test_verify_code_serializer_marks_user_as_verified(self):
        user = CustomUser.objects.create_user(
            username='demo-user',
            email='demo@example.com',
            password='StrongPass123',
            auth_type=VIA_EMAIL,
        )
        code = user.generate_code(VIA_EMAIL)

        serializer = VerifyCodeSerializer(instance=user, data={'code': code})
        self.assertTrue(serializer.is_valid(), serializer.errors)

        verified_user = serializer.save()
        self.assertEqual(verified_user.auth_status, CODE_VERIFY)
        self.assertTrue(verified_user.codes.filter(code=code, is_used=True).exists())
