import mimetypes

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.http import FileResponse
from django.utils._os import safe_join
from django.views.static import serve


def serve_media(request, path):
    full_path = safe_join(settings.MEDIA_ROOT, path)

    if path.lower().endswith('.txt'):
        response = FileResponse(
            open(full_path, 'rb'),
            content_type='text/plain; charset=utf-8'
        )
        response['Content-Disposition'] = 'inline'
        return response

    content_type, encoding = mimetypes.guess_type(full_path)
    return serve(
        request,
        path,
        document_root=settings.MEDIA_ROOT,
        content_type=content_type,
    )


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('comments.urls')),
    re_path(r'^media/(?P<path>.*)$', serve_media),
]