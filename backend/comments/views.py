from rest_framework import generics, status, filters, serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Comment
from .serializers import CommentSerializer, CommentCreateSerializer
from .utils import generate_captcha_image, sanitize_html


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

        response_serializer = CommentSerializer(comment, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class CommentDetailView(generics.RetrieveAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class CaptchaView(APIView):
    def get(self, request):
        captcha = generate_captcha_image()
        return Response(captcha)


class CommentPreviewView(APIView):
    class InputSerializer(serializers.Serializer):
        text = serializers.CharField(required=True, allow_blank=False)

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response({
            'text': sanitize_html(serializer.validated_data['text'])
        })