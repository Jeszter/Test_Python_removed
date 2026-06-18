from celery import shared_task
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


@shared_task
def notify_new_comment(comment_id: int):
    from .models import Comment
    from .serializers import CommentSerializer

    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return

    serializer = CommentSerializer(comment)
    data = serializer.data

    if data.get('created_at'):
        data['created_at'] = str(data['created_at'])

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'comments',
        {
            'type': 'new_comment',
            'comment': data,
        }
    )


@shared_task
def cleanup_expired_captchas():
    from django.utils import timezone
    from datetime import timedelta
    from django.conf import settings
    from .models import CaptchaChallenge

    cutoff = timezone.now() - timedelta(seconds=settings.CAPTCHA_TIMEOUT)
    deleted_count, _ = CaptchaChallenge.objects.filter(
        created_at__lt=cutoff
    ).delete()
    return f'Deleted {deleted_count} expired CAPTCHA records'
