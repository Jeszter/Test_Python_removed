from django.contrib import admin
from .models import Comment, CaptchaChallenge


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email', 'parent', 'created_at', 'ip_address']
    list_filter = ['created_at']
    search_fields = ['username', 'email', 'text', 'ip_address']
    ordering = ['-created_at']
    readonly_fields = ['ip_address', 'user_agent', 'created_at']


@admin.register(CaptchaChallenge)
class CaptchaChallengeAdmin(admin.ModelAdmin):
    list_display = ['key', 'answer', 'created_at', 'used']
    list_filter = ['used']
