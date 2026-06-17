from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from yogaaa import views

router = DefaultRouter()
router.register(r'api/categories', views.CategoryViewSet)
router.register(r'api/manufacturers', views.ManufacturerViewSet)
router.register(r'api/products', views.ProductViewSet)
router.register(r'api/carts', views.CartViewSet)
router.register(r'api/cart-items', views.CartItemViewSet)
router.register(r'api/orders', views.OrderViewSet) # регистрация роута заказов (Задание 3, пункт 4)

urlpatterns = [
    path('', views.yoga, name='home'),
    path('about/', views.about, name='about'),
    path('info/', views.info, name='info'),
    path('catalog/', views.product_list, name='product_list'),
    path('catalog/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/', views.cart_view, name='cart_view'),
    path('checkout/', views.checkout_view, name='checkout_view'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Новый эндпоинт профиля текущего пользователя (Задание 3, пункты 1 и 2)
    path('api/me/', views.UserProfileView.as_view(), name='user-profile-api'),
    
    path('', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)