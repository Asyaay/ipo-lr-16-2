from django.urls import path
from . import views

urlpatterns = [
    path('', views.yoga, name='home'), #главная витрина студии йоги со всеми списками
    path('about/', views.about, name='about'), #страница об авторе проекта
    path('info/', views.info, name='info'), #страница о магазине товаров для йоги
    
    path('catalog/', views.product_list, name='product_list'), #страница каталога товаров для йоги
    path('catalog/<int:pk>/', views.product_detail, name='product_detail'), #страница детальной карточки йога-товара по id
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'), #маршрут для добавления товара в корзину студии
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'), #маршрут для обновления количества товара в корзине
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'), #маршрут для удаления товара из корзины студии
    path('cart/', views.cart_view, name='cart_view'), #просмотр корзины покупателя йога-товаров
    
    path('checkout/', views.checkout_view, name='checkout_view'), #НОВАЯ страница оформления заказа по заданию 1 лабораторной 19
]