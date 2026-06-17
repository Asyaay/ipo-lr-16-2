from django.contrib import admin
from django.urls import path, include
urlpatterns = [
    path('admin/', admin.site.urls),#маршрут для админки
    path('', include('yogaaa.urls')),#маршрут для приложения
]