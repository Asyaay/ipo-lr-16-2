from django.urls import path #импортируем
from . import views #импортируем

urlpatterns = [
    path('', views.yoga, name='home'), #добавляем путь
    path('', views.yoga, name='yoga'), #добавляем путь
    path('about/', views.about, name='about'), #добавляем путь
    path('info/', views.info, name='info'), #добавляем путь
]