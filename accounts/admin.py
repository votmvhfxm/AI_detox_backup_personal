# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """
    ✅ 관리자 화면에서 User 확인용
    - User 모델에 실제로 존재하는 필드만 list_display에 넣어야 함
    """
    list_display = ("id", "username", "email", "provider", "provider_uid", "created_at", "is_staff", "is_active")
    search_fields = ("username", "email", "provider")
    ordering = ("-id",)

    fieldsets = DjangoUserAdmin.fieldsets + (
        ("추가 정보", {"fields": ("provider", "provider_uid", "avatar_url", "created_at")}),
    )
    readonly_fields = ("created_at",)
