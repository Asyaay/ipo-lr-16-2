from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    # Доступные роли пользователей в системе для разделения прав доступа (Вариант 2 из задания)
    ROLE_CHOICES = [
        ('CUSTOMER', 'Клиент студии'),
        ('TRAINER', 'Инструктор по йоге'),
        ('MANAGER', 'Менеджер студии'),
        ('ADMIN', 'Администратор системы'),
    ]

    # Связь "Один-к-Одному" со встроенной моделью пользователя Django (Пункт 2 задания)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Текстовое поле для хранения выбранной роли из списка ROLE_CHOICES (Вариант 2 из задания)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CUSTOMER')
    
    # Дополнительные обязательные поля профиля для хранения персональных данных (Пункт 3 задания)
    full_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Category(models.Model):
    # Категория или направление занятий (например, Хатха-йога, Аэройога)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Manufacturer(models.Model):
    # Студия или зал, где проводятся тренировки
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    # Конкретная услуга, абонемент или тренировка по йоге
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=1)  # Доступное количество мест в группе

    def __str__(self):
        return self.name
class Cart(models.Model):
    # Личная корзина выбранных абонементов пользователя
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_cost(self):
        # Подсчет общей стоимости всех услуг в корзине (используется при создании Order)
        return sum(item.element_cost for item in self.items.all())

    def __str__(self):
        return f"Корзина {self.user.username}"

class CartItem(models.Model):
    # Выбранная услуга внутри корзины
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def element_cost(self):
        # Автоматический расчет стоимости позиции в корзине (используется во views.py)
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

class Order(models.Model):
    # Модель для хранения общей информации о заказе абонементов по йоге
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Заказ №{self.id} - {self.user.username}"

class OrderItem(models.Model):
    # Используем строку 'Order' вместо ссылки на класс, чтобы убрать ошибку валидации синтаксиса
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def element_cost(self):
        # Автоматический расчет стоимости позиции для генерации чека в Excel
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product.name} для заказа №{self.order.id}"

# Автоматическое создание объекта профиля при регистрации нового пользователя
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# Автоматическое сохранение данных профиля при изменении объекта пользователя
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
