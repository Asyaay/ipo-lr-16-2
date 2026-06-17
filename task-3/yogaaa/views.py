import random
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import Category, Manufacturer, Product, Cart, CartItem


def get_or_create_test_cart():
    user, _ = User.objects.get_or_create(username='test_user_asya') #находим или регистрируем тестового пользователя
    cart, _ = Cart.objects.get_or_create(user=user) #находим или создаем его личную корзину
    return cart


def fill_database():
    countries = ['Индия', 'Беларусь', 'США', 'Германия', 'Таиланд']
    manufacturers = []
    for i in range(1, 6):
        m, _ = Manufacturer.objects.get_or_create(
            name=f"Бренд Йоги {i}",
            defaults={'country': random.choice(countries), 'description': 'Описание производителя'}
        )
        manufacturers.append(m) #заполняем производителей товаров по заданию

    category_names = [
        'Коврики', 'Благовония', 'Одежда', 'Подушки', 'Блоки', 
        'Поющие чаши', 'Книги', 'Чаи', 'Масла', 'Аксессуары'
    ]
    categories = []
    for name in category_names:
        c, _ = Category.objects.get_or_create(name=name, defaults={'description': 'Описание категории товаров'})
        categories.append(c) #заполняем категории товаров по заданию

    for i in range(1, 35):
        category = categories[(i - 1) % len(categories)]
        manufacturer = random.choice(manufacturers)
        Product.objects.get_or_create(
            name=f"Йога товар №{i}",
            defaults={
                'description': 'Высококачественный предмет для эффективных занятий в студии',
                'price': random.randint(15, 120),
                'stock': random.randint(5, 25),
                'category': category,
                'manufacturer': manufacturer
            }
        ) #заполняем список всех товаров по заданию

    for i in range(1, 6):
        username = f"user_{i}"
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_password(f"password_{i}")
            user.save()
        cart, _ = Cart.objects.get_or_create(user=user)
        CartItem.objects.filter(cart=cart).delete()
        all_products = list(Product.objects.all())
        random_products = random.sample(all_products, 2)
        for prod in random_products:
            CartItem.objects.create(
                cart=cart,
                product=prod,
                quantity=random.randint(1, 2)
            ) #заполняем пользователей и корзины по заданию


def yoga(request):
    fill_database() #запускаем автоматическое заполнение базы данных по заданию
    categories = Category.objects.all() #получаем категории товаров из базы данных
    manufacturers = Manufacturer.objects.all() #получаем производителей товаров из базы данных
    products = Product.objects.all() #получаем все товары из базы данных
    carts = Cart.objects.all() #получаем все корзины из базы данных
    
    return render(request, 'index.html', {
        'categories': categories,
        'manufacturers': manufacturers,
        'products': products,
        'carts': carts,
        'error_message': None,
        'success_message': None
    })


def about(request):
    return render(request, 'about.html')


def info(request):
    return render(request, 'info.html')