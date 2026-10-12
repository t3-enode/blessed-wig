from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('wigs.urls', namespace='wigs')),
]

# Serve media and static files in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom Admin Site Branding for your Blessed
admin.site.site_header = "Blessed Wigs â€¢ Luxury Management Suite"
admin.site.site_title = "Blessed Wigs Admin"
admin.site.index_title = "Blessed Luxury Wig Store & Orders Hub"

