"""
URL configuration for tolstoy_coffee project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
"""
Главный URL-конфигуратор проекта Толстой Coffee.
Объединяет маршруты всех приложений.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path, include

urlpatterns = [
    path('django-admin/', admin.site.urls),
   
    path('accounts/', include('accounts.urls')),

    path('training/', include('training.urls')),

    path('testing/', include('testing.urls')),

    path('dashboard/', include('dashboard.urls')),

    path('api/', include('api.urls')),

    path('', lambda request: redirect('accounts:login')),
]

# Раздача медиа-файлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]