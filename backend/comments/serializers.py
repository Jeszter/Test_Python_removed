import re
from django.conf import settings
from rest_framework import serializers
from .models import Comment, CaptchaChallenge
from .utils import sanitize_html, validate_html_tags


class RecursiveReplySerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = CommentSerializer(value, context=self.context)
        return serializer.data


class CommentSerializer(serializers.ModelSerializer):
    replies = RecursiveReplySerializer(many=True, read_only=True)
    replies_count = serializers.SerializerMethodField()
    parent_text = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'parent', 'username', 'email', 'homepage',
            'text', 'image', 'attachment', 'ip_address',
            'created_at', 'replies', 'replies_count', 'parent_text'
        ]
        read_only_fields = ['id', 'created_at', 'ip_address', 'replies', 'replies_count', 'parent_text']
        extra_kwargs = {
            'email': {'write_only': False},
        }

    def get_replies_count(self, obj):
        return obj.replies.count()

    def get_parent_text(self, obj):
        if not obj.parent_id:
            return ''
        return sanitize_html(obj.parent.text)


class CommentCreateSerializer(serializers.ModelSerializer):
    captcha_key = serializers.CharField(write_only=True)
    captcha_value = serializers.CharField(write_only=True)

    class Meta:
        model = Comment
        fields = [
            'id', 'parent', 'username', 'email', 'homepage',
            'text', 'image', 'attachment',
            'captcha_key', 'captcha_value',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def validate_username(self, value):
        if not re.match(r'^[a-zA-Z0-9]+$', value):
            raise serializers.ValidationError(
                'User name must contain only Latin letters and digits.'
            )
        return value

    def validate_text(self, value):
        if not validate_html_tags(value):
            raise serializers.ValidationError(
                'Text contains invalid or unclosed HTML tags. '
                f'Allowed tags: {", ".join(settings.ALLOWED_HTML_TAGS)}'
            )
        return sanitize_html(value)

    def validate_image(self, value):
        if value:
            ext = value.name.rsplit('.', 1)[-1].lower()
            if ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
                raise serializers.ValidationError(
                    f'Allowed formats: {", ".join(settings.ALLOWED_IMAGE_EXTENSIONS).upper()}'
                )
        return value

    def validate_attachment(self, value):
        if value:
            ext = value.name.rsplit('.', 1)[-1].lower()
            if ext not in settings.ALLOWED_FILE_EXTENSIONS:
                raise serializers.ValidationError('Allowed file format: TXT')
            if value.size > settings.MAX_FILE_SIZE_KB * 1024:
                raise serializers.ValidationError(
                    f'File must not exceed {settings.MAX_FILE_SIZE_KB} KB'
                )
        return value

    def validate(self, attrs):
        captcha_key = attrs.pop('captcha_key', '')
        captcha_value = attrs.pop('captcha_value', '')

        try:
            challenge = CaptchaChallenge.objects.get(key=captcha_key, used=False)
        except CaptchaChallenge.DoesNotExist:
            raise serializers.ValidationError({'captcha_value': 'CAPTCHA is expired or not found. Refresh it.'})

        if challenge.is_expired:
            challenge.delete()
            raise serializers.ValidationError({'captcha_value': 'CAPTCHA is expired. Refresh it.'})

        if challenge.answer.upper() != captcha_value.upper():
            raise serializers.ValidationError({'captcha_value': 'Invalid CAPTCHA value.'})

        challenge.used = True
        challenge.save(update_fields=['used'])

        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        if request:
            validated_data['ip_address'] = self._get_client_ip(request)
            validated_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
        return super().create(validated_data)

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')


class CaptchaResponseSerializer(serializers.Serializer):
    key = serializers.CharField()
    image_url = serializers.CharField()
