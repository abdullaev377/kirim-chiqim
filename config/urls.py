from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.http import Http404, HttpResponse
from django.views.static import serve as serve_static

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Kirim-Chiqim API",
        default_version='v1',
        description="Income & Expense Tracking API",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


def frontend_index(request, *args, **kwargs):
    """Serve the built React app's index.html for any non-API route.

    This makes client-side routes (e.g. /transactions, /accounts) work on a
    direct visit or page refresh instead of returning a 404.
    """
    index_path = settings.FRONTEND_DIST / 'index.html'
    if not index_path.exists():
        raise Http404(
            "Frontend build not found. Run `npm run build` inside the "
            "frontend/ folder (this happens automatically on Railway)."
        )
    return HttpResponse(index_path.read_text(encoding='utf-8'), content_type='text/html')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('accounts.urls')),
    path('api/', include('transactions.urls')),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0)),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0)),

    # Served unconditionally (not just in DEBUG) so uploaded profile photos
    # are reachable in production too. Fine for a small/demo project; for a
    # larger app move media to external storage (S3, R2, etc.).
    re_path(r'^media/(?P<path>.*)$', serve_static, {'document_root': settings.MEDIA_ROOT}),
]

# SPA fallback: any path that isn't one of the API/admin/docs/static routes
# above renders the React app, which then handles routing on the client.
urlpatterns += [
    re_path(r'^(?!admin/|api/|auth/|swagger/|redoc/|static/|media/).*$', frontend_index),
]