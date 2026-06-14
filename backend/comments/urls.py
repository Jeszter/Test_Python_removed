from django.urls import path
from .views import (
    CommentListCreateView,
    CommentDetailView,
    CommentPreviewView,
    CaptchaGenerateView,
    CaptchaValidateView,
)

urlpatterns = [
    path('comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
    path('comments/preview/', CommentPreviewView.as_view(), name='comment-preview'),
    path('captcha/', CaptchaGenerateView.as_view(), name='captcha-generate'),
    path('captcha/validate/', CaptchaValidateView.as_view(), name='captcha-validate'),
]
