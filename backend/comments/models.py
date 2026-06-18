from django.db import models
from datetime import timedelta

from django.conf import settings
from django.utils import timezone


class Comment(models.Model):
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='replies',
        on_delete=models.CASCADE,
        verbose_name='Parent comment'
    )
    username = models.CharField(
        max_length=100,
        verbose_name='User name'
    )
    email = models.EmailField(verbose_name='E-mail')
    homepage = models.URLField(
        blank=True,
        null=True,
        verbose_name='Home page'
    )
    text = models.TextField(verbose_name='Comment text')
    image = models.ImageField(
        upload_to='images/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name='Image'
    )
    attachment = models.FileField(
        upload_to='files/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name='File'
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP address'
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name='Browser User-Agent'
    )

    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Created at'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['parent']),
        ]

    def __str__(self):
        return f'{self.username} - {self.created_at:%Y-%m-%d %H:%M}'

    @property
    def is_root(self):
        return self.parent_id is None

    def get_replies_count(self):
        return self.replies.count()


class CaptchaChallenge(models.Model):
    key = models.CharField(max_length=64, unique=True, verbose_name='Key')
    answer = models.CharField(max_length=10, verbose_name='Answer')
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False, verbose_name='Used')

    class Meta:
        verbose_name = 'CAPTCHA'
        verbose_name_plural = 'CAPTCHAs'

    def __str__(self):
        return f'CAPTCHA {self.key} ({"used" if self.used else "active"})'

    @property
    def is_expired(self):
        return self.created_at < timezone.now() - timedelta(seconds=settings.CAPTCHA_TIMEOUT)
