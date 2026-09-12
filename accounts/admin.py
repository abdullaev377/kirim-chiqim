from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CodeVerify, CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
	list_display = ['username', 'email', 'phone_number', 'auth_status', 'user_role', 'is_active']
	list_filter = ['auth_status', 'user_role', 'is_active', 'is_staff']
	search_fields = ['username', 'email', 'phone_number']
	ordering = ['username']
	readonly_fields = ['last_login', 'date_joined', 'created_at', 'updated_at']


@admin.register(CodeVerify)
class CodeVerifyAdmin(admin.ModelAdmin):
	list_display = ['user', 'verify_type', 'is_used', 'expire_time', 'created_at']
	list_filter = ['verify_type', 'is_used']
	search_fields = ['user__username', 'user__email']
	readonly_fields = ['created_at', 'updated_at']



