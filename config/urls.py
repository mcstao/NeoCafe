from django.contrib import admin
from django.urls import path, include
from .yasg import urlpatterns as yasg_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', include('rest_framework.urls')),
    path('', include('branches.urls')),
]

urlpatterns += yasg_urls