from django.urls import path
from . import views

urlpatterns = [
    path('', views.yoga, name='home'), #главная страница со всеми списками товаров
    path('about/', views.about, name='about'), #страница об авторе
    path('info/', views.info, name='info'), #страница о магазине
]