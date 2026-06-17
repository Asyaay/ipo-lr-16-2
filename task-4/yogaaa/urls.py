from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from yogaaa import views

router = DefaultRouter() #инициализируем стандартный маршрутизатор для построения адресов api
router.register(r'api/categories', views.CategoryViewSet) #регистрируем конечную точку api для категорий
router.register(r'api/manufacturers', views.ManufacturerViewSet) #регистрируем конечную точку api для залов
router.register(r'api/products', views.ProductViewSet) #регистрируем конечную точку api для товарных позиций
router.register(r'api/carts', views.CartViewSet) #регистрируем конечную точку api для корзин пользователей
router.register(r'api/cart-items', views.CartItemViewSet) #регистрируем конечную точку api для элементов корзины

# Добавляем аргумент basename для корректной работы динамического get_queryset (Задание 3, пункт 4)
router.register(r'api/orders', views.OrderViewSet, basename='orders') 
urlpatterns = [
    path('', views.yoga, name='home'), #главная витрина студии йоги со всеми списками
    path('about/', views.about, name='about'), #страница об авторе проекта
    path('info/', views.info, name='info'), #страница о магазине товаров для йоги
    path('catalog/', views.product_list, name='product_list'), #страница каталога товаров для йоги
    path('catalog/<int:pk>/', views.product_detail, name='product_detail'), #страница детальной карточки йога-товара
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'), #маршрут для добавления товара в корзину
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'), #маршрут для обновления количества товара
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'), #маршрут для удаления товара
    path('cart/', views.cart_view, name='cart_view'), #просмотр корзины покупателя йога-товаров
    path('checkout/', views.checkout_view, name='checkout_view'), #страница оформления заказа товаров для йоги
    path('register/', views.register_view, name='register'), #маршрут страницы регистрации нового пользователя и профиля
    path('login/', views.login_view, name='login'), #маршрут страницы аутентификации и выдачи куки-токена
    path('logout/', views.logout_view, name='logout'), #маршрут для логаута и очистки сессии/кукис
    
        # URL-маршрут для визуальной страницы Личного кабинета (Задание 4)
    path('profile/', views.profile_page_view, name='profile_page'),

    
    # Новый эндпоинт профиля текущего пользователя (Задание 3, пункты 1 и 2)
    path('api/me/', views.UserProfileView.as_view(), name='user-profile-api'),
    
    path('', include(router.urls)), #интегрируем автоматически сгенерированные маршруты api в общий список адресов
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) #обслуживание медиа файлов в режиме разработки