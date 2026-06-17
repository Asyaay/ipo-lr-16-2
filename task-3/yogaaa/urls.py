from django.urls import path
from . import views

urlpatterns = [
    path('', views.yoga, name='home'), #главная витрина
    path('about/', views.about, name='about'), #страница об авторе
    path('info/', views.info, name='info'), #страница о магазине
    
    path('catalog/', views.product_list, name='product_list'), #новое имя функции по твоему техническому заданию
    path('catalog/<int:pk>/', views.product_detail, name='product_detail'), #детальная страница товара
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'), #новое имя функции по твоему техническому заданию
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'), #новое имя функции по твоему техническому заданию
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'), #новое имя функции по твоему техническому заданию
    path('cart/', views.cart_view, name='cart_view'), #просмотр корзины покупателя
]