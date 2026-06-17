from django.contrib import admin
from .models import Category, Manufacturer, Product, Cart, CartItem #импортируем все наши модели из файла по заданию

admin.site.register(Category) #регистрируем категории товаров в админ-панели Django
admin.site.register(Manufacturer) #регистрируем производителей товаров в админ-панели Django
admin.site.register(Product) #регистрируем товары йоги в админ-панели Django
admin.site.register(Cart) #регистрируем корзины пользователей в админ-панели Django
admin.site.register(CartItem) #регистрируем элементы корзин в админ-панели Django