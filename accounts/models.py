from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from shared.models import BaseModel
from datetime import timedelta
from django.utils import timezone
from config.settings import EMAIL_EXPIRATION_TIME, PHONE_EXPIRATION_TIME
import random
from rest_framework_simplejwt.tokens import RefreshToken


NEW, CODE_VERIFY, DONE, PHOTO_DONE = ('new', 'code_verify', 'done', 'photo_done')
ORDINARY_USER, SELLER, MANAGER = ('ordinary_user', 'seller', 'manager')
VIA_EMAIL, VIA_PHONE = ('via_email', 'via_phone')


class CustomUser(AbstractUser, BaseModel):
    AUTH_STATUS = (
        (NEW, NEW),
        (CODE_VERIFY, CODE_VERIFY),
        (DONE, DONE),
        (PHOTO_DONE, PHOTO_DONE),
    )
    USER_ROLE = (
        (ORDINARY_USER, ORDINARY_USER),
        (SELLER, SELLER),
        (MANAGER, MANAGER)
    )
    AUTH_TYPE = (
        (VIA_EMAIL, VIA_EMAIL), 
        (VIA_PHONE, VIA_PHONE)
    )
    auth_status = models.CharField(max_length=11, choices=AUTH_STATUS, default=NEW)
    user_role = models.CharField(max_length=13, choices=USER_ROLE, default=ORDINARY_USER)
    auth_type = models.CharField(max_length=9, choices=AUTH_TYPE)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=13, unique=True, null=True, blank=True)
    photo = models.ImageField(upload_to='user_photo/', default='user_photo/default.jpg', null=True, blank=True)
    
    def __str__(self):
        return self.username
    
    def generate_code(self, verify_type):  
        code = str(random.randint(1000, 9999))
        CodeVerify.objects.create(
            user=self,
            code=code,
            verify_type=verify_type
        )
        return code
    
    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }
    
    def username_check(self):
        if not self.username:
            temp_username = str(self.id).split('-')[-1]
            while CustomUser.objects.filter(username=temp_username).exists():
                temp_username += str(random.randint(1, 9))
                
            self.username = temp_username
                
    def pass_check(self):
        if not self.password:
            temp_password = str(self.id).split('-')[-1]
            self.password = temp_password
    
    def pass_hashing(self):
        if not self.password.startswith('pbkdf2_sha256'):
            self.set_password(self.password)
            
    def email_check(self):
        if self.email:
            temp_email = self.email.lower()
            self.email = temp_email
    
    def clean(self):
        self.username_check()
        self.email_check()
        self.pass_check()
        self.pass_hashing()
        
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    
    
    
class CodeVerify(BaseModel):
    VERIFY_TYPE = (
        (VIA_EMAIL, VIA_EMAIL),
        (VIA_PHONE, VIA_PHONE)
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='codes')
    expire_time = models.DateTimeField() #20:32 20:34   20:32  20:35
    code = models.CharField(max_length=4)
    is_used = models.BooleanField(default=False)
    verify_type = models.CharField(max_length=9, choices=VERIFY_TYPE)
    
    def __str__(self):
        return f"User:{self.user.username} | code:{self.code}"
    
    def save(self, *args, **kwargs):
        if self.verify_type == VIA_EMAIL:
            self.expire_time = timezone.now() + timedelta(minutes=EMAIL_EXPIRATION_TIME)
        else:
            self.expire_time = timezone.now() + timedelta(minutes=PHONE_EXPIRATION_TIME)

        super().save(*args, **kwargs)
    