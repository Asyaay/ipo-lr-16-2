from django.urls import path
from . import views

urlpatterns = [
    path('', views.yoga, name='home'), #главная страница с формами и витриной
    path('about/', views.about, name='about'), #страница об авторе
    path('info/', views.info, name='info'), #страница о магазине
    
    path('catalog/', views.catalog_view, name='catalog_view'), #страница каталога товаров
    path('catalog/<int:pk>/', views.product_detail, name='product_detail'), #страница детальной информации о товаре
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'), #добавление товара в корзину по заданию
    path('cart/update/<int:item_id>/', views.cart_update, name='cart_update'), #обновление количества в корзине по заданию
    path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove'), #удаление товара из корзины по заданию
    path('cart/', views.cart_view, name='cart_view'), #просмотр корзины пользователя по заданию
]