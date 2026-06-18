import uuid
import base64
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta

from rest_framework import generics, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Comment, CaptchaChallenge
from .serializers import CommentSerializer, CommentCreateSerializer
from .utils import generate_captcha_text, generate_captcha_image
from .tasks import notify_new_comment


class CommentListCreateView(generics.ListCreateAPIView):
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['username', 'email', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Comment.objects.filter(parent__isnull=True).prefetch_related(
            'replies__replies__replies'
        )

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CommentCreateSerializer
        return CommentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()

        try:
            notify_new_comment.delay(comment.id)
        except Exception:
            pass

        response_serializer = CommentSerializer(comment, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class CommentDetailView(generics.RetrieveAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class CommentPreviewView(APIView):
    def post(self, request):
        from .utils import sanitize_html, validate_html_tags
        text = request.data.get('text', '')
        if not validate_html_tags(text):
            return Response(
                {'error': 'Invalid HTML tags in text.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response({'preview': sanitize_html(text)})


class CaptchaGenerateView(APIView):
    def get(self, request):
        CaptchaChallenge.objects.filter(
            created_at__lt=timezone.now() - timedelta(seconds=settings.CAPTCHA_TIMEOUT),
            used=False
        ).delete()

        text = generate_captcha_text(settings.CAPTCHA_LENGTH)
        key = str(uuid.uuid4())

        CaptchaChallenge.objects.create(key=key, answer=text)

        image_bytes = generate_captcha_image(text)
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')

        return Response({
            'key': key,
            'image': f'data:image/png;base64,{image_b64}'
        })


class CaptchaValidateView(APIView):
    def post(self, request):
        key = request.data.get('key', '')
        value = request.data.get('value', '')
        try:
            challenge = CaptchaChallenge.objects.get(key=key, used=False)
            valid = not challenge.is_expired and challenge.answer.upper() == value.upper()
        except CaptchaChallenge.DoesNotExist:
            valid = False
        return Response({'valid': valid})
