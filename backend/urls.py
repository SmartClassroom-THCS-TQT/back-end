
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/managements/', include('managements.urls')),
    path('api/rooms/', include('rooms_managements.urls')),
    path('api/educational-resources/', include('educational_resources.urls')),
    # path('api/posts/', include('posts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)