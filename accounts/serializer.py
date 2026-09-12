from django.db import transaction
from rest_framework import serializers
from .models import CustomUser, VIA_EMAIL, VIA_PHONE, CODE_VERIFY, NEW, DONE, PHOTO_DONE
from shared.utils import check_email_or_phone
from rest_framework.exceptions import ValidationError
from rest_framework import status
from django.db.models import Q
from django.contrib.auth import authenticate
from django.conf import settings

class SignUpSerializer(serializers.ModelSerializer):
    email_or_phone_number = serializers.CharField(required=True, write_only=True, trim_whitespace=True)
    
    class Meta:
        model = CustomUser
        fields = ['id', 'auth_status', 'auth_type', 'email_or_phone_number']
        read_only_fields = ['id', 'auth_status', 'auth_type']
        
    @transaction.atomic
    def create(self, validated_data):
        user_input = validated_data.get('email') or validated_data.get('phone_number')
        existing_user = CustomUser.objects.filter(
            Q(email=user_input) | Q(phone_number=user_input)
        ).first()
        if existing_user:
            existing_user.delete()

        user = CustomUser.objects.create(**validated_data)
        code = user.generate_code(user.auth_type)
        print(f'---------------{user.auth_type.upper()} CODE: {code} ------------------------')
        return user
        
            
        
    
    def validate(self, data):
        user_input = data['email_or_phone_number'].lower()
        existing_user = CustomUser.objects.filter(
            Q(email=user_input) | Q(phone_number=user_input)
        ).first()
        if existing_user and existing_user.auth_status not in [NEW, CODE_VERIFY]:
            raise ValidationError({
                'msg': 'Bu email yoki telefon raqamdan oldin royxatdan otilgan',
                'status': status.HTTP_400_BAD_REQUEST,
            })
        return self.auth_validate({'email_or_phone_number': user_input})
        
    @staticmethod
    def auth_validate(data):
        user_input = str(data.get('email_or_phone_number')).lower()
        user_auth_type = check_email_or_phone(user_input)
        if user_auth_type == 'email':
            data = {
                'email':user_input,
                'auth_type':VIA_EMAIL
            }
        elif user_auth_type == 'phone':
            data = {
                'phone_number':user_input,
                'auth_type':VIA_PHONE
            }
        else:
            raise ValidationError(
                { 'msg': 'Siz xato email yoki telefon raqam kiritdingiz',
                'status': status.HTTP_400_BAD_REQUEST}
                )
        return data
    
    def to_representation(self, instance):
        data =  super(SignUpSerializer, self).to_representation(instance)
        data.update(instance.token())
        if settings.DEBUG:
            active_code = instance.codes.filter(is_used=False).order_by('-created_at').first()
            if active_code:
                data['verification_code'] = active_code.code
        return data
        
    


class ChangeInfoSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True, write_only=True)
    last_name = serializers.CharField(required=True, write_only=True)
    username = serializers.CharField(required=True, write_only=True)
    email = serializers.EmailField(required=False, write_only=True)
    phone_number = serializers.CharField(required=False, write_only=True)
    password = serializers.CharField(required=True, write_only=True)
    conf_password = serializers.CharField(required=True, write_only=True)
    
    
    def validate(self, data):
        password = data.get('password')
        conf_password = data.get('conf_password')
        if password and conf_password and password != conf_password:
            raise ValidationError(
                { 'msg': 'parollar mos emas',
                'status': status.HTTP_400_BAD_REQUEST}
                )
            
        return data
    
    
    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name')
        instance.last_name = validated_data.get('last_name')
        instance.username = validated_data.get('username')
        if validated_data.get('email'):
            instance.email = validated_data.get('email')
        if validated_data.get('phone_number'):
            instance.phone_number = validated_data.get('phone_number')
        instance.set_password(validated_data.get('password'))
        
        
        if instance.auth_status == NEW:
            raise ValidationError(
                { 'msg': 'Siz hali ozingizni tasdiqlamagansiz',
                'status': status.HTTP_400_BAD_REQUEST}
                )
        
        instance.auth_status = DONE
        
        instance.save()
        
        return instance
    
    
    def to_representation(self, instance):
        return {
            "msg": 'Malumotlar yangilandi',
            'status': status.HTTP_200_OK,
            'token': instance.token()
        }
    
    
    
class ChangePhotoSerializer(serializers.Serializer):
    photo = serializers.ImageField()
    
    
    
    def update(self, instance, validated_data):
        photo = validated_data.get('photo', None)
        if photo:
            instance.photo = validated_data.get('photo')
       
    
        instance.auth_status = PHOTO_DONE
        
        instance.save()
        
        return instance
    
    
    def to_representation(self, instance):
        return {
            "msg": 'Rasm yangilandi',
            'status': status.HTTP_200_OK,
            'token': instance.token()
        }
    
    
    
from django.contrib.auth import authenticate
from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError


class VerifyCodeSerializer(serializers.Serializer):
    code = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        user = self.instance
        if not user:
            raise ValidationError({
                'msg': 'Foydalanuvchi topilmadi',
                'status': status.HTTP_400_BAD_REQUEST,
            })

        submitted_code = str(attrs.get('code', '')).strip()
        active_code = user.codes.filter(
            is_used=False,
            code=submitted_code,
            expire_time__gte=timezone.now(),
        ).first()

        if active_code is None:
            raise ValidationError({
                'msg': 'Kod xato yoki yaroqsiz',
                'status': status.HTTP_400_BAD_REQUEST,
            })

        attrs['code_instance'] = active_code
        return attrs

    def update(self, instance, validated_data):
        code_instance = validated_data.get('code_instance')
        if code_instance is None:
            raise ValidationError({
                'msg': 'Kod xato yoki yaroqsiz',
                'status': status.HTTP_400_BAD_REQUEST,
            })

        code_instance.is_used = True
        code_instance.save()

        instance.auth_status = CODE_VERIFY
        instance.save()
        return instance

    def to_representation(self, instance):
        return {
            'msg': 'code verified',
            'status': status.HTTP_200_OK,
            'token': instance.token(),
        }


class LoginSerializer(serializers.Serializer):
    user_input = serializers.CharField(required=True, write_only=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        user_input = str(attrs.get("user_input", "")).strip()
        password = attrs.get("password")

        user = CustomUser.objects.filter(
            Q(username=user_input) |
            Q(email=user_input.lower()) |
            Q(phone_number=user_input)
        ).first()

        if not user:
            raise ValidationError({
                "msg": "Login yoki parol xato",
                "status": status.HTTP_400_BAD_REQUEST
            })

        if user.auth_status in [NEW, CODE_VERIFY]:
            raise ValidationError({
                "msg": "Siz hali to'liq ro'yxatdan o'tmagansiz",
                "status": status.HTTP_400_BAD_REQUEST
            })

        authenticated_user = authenticate(
            username=user.username,
            password=password
        )

        if not authenticated_user:
            raise ValidationError({
                "msg": "Login yoki parol xato",
                "status": status.HTTP_400_BAD_REQUEST
            })

        attrs["user"] = authenticated_user
        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email',
            'phone_number', 'photo', 'auth_status', 'auth_type',
        ]
        read_only_fields = ['id', 'auth_status', 'auth_type']
    

