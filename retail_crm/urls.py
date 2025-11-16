
# FILE 4: retail_crm/urls.py - COMPLETE CODE
# ============================================

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('crm.urls')),
]

# Serve media files in both development and production
# Note: For production, consider using cloud storage (AWS S3, Cloudinary, etc.)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)