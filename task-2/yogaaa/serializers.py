from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Manufacturer, Product, Cart, CartItem, Order, OrderItem, Profile

class ProfileSerializer(serializers.ModelSerializer):
    # Сериализатор для интеграции данных учетной записи и расширенного профиля пользователя
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

class Meta:
    model = Profile
    fields = ['id', 'username', 'email', 'role', 'full_name', 'phone', 'address']
    read_only_fields = ['id', 'role'] # Защита поля роли от несанкционированного изменения через API

class ProductSerializer(serializers.ModelSerializer):
    # Сериализатор для представления позиций каталога товаров и услуг йоги
    class Meta:
        model = Product
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    # Сериализатор для отображения конкретных позиций внутри оформленного заказа
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    # Комплексный сериализатор заказа, включающий связанные вложенные элементы
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'total_cost', 'created_at', 'items']

from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    # Кастомный класс авторизации: безопасные методы открыты для всех, изменение — только для ADMIN
    def has_permission(self, request, view):
        # Предоставление беспрепятственного доступа для методов GET, HEAD, OPTIONS
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Проверка авторизации и наличия административной роли для методов POST, PUT, DELETE
        return (
            request.user and 
            request.user.is_authenticated and 
            getattr(request.user.profile, 'role', '') == 'ADMIN'
        )