import random
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import Category, Manufacturer, Product, Cart, CartItem


def get_or_create_test_cart():
    user, _ = User.objects.get_or_create(username='test_user_asya') #находим или регистрируем тестового пользователя
    cart, _ = Cart.objects.get_or_create(user=user) #находим или создаем его личную корзину
    return cart


def yoga(request):
    error_message = None
    success_message = None
    action = request.POST.get('action')
    cart = get_or_create_test_cart() #получаем корзину пользователя

    if request.method == 'POST':
        try:
            if action == 'add_category':
                name = request.POST.get('cat_name')
                desc = request.POST.get('cat_desc')
                category = Category(name=name, description=desc)
                category.full_clean()
                category.save()
                success_message = f"Категория '{name}' успешно создана!"

            elif action == 'add_manufacturer':
                name = request.POST.get('man_name')
                country = request.POST.get('man_country')
                desc = request.POST.get('man_desc')
                manufacturer = Manufacturer(name=name, country=country, description=desc)
                manufacturer.full_clean()
                manufacturer.save()
                success_message = f"Производитель '{name}' успешно создан!"

            elif action == 'add_product':
                name = request.POST.get('prod_name')
                desc = request.POST.get('prod_desc')
                price = request.POST.get('prod_price')
                stock = request.POST.get('prod_stock')
                cat_id = request.POST.get('prod_category')
                man_id = request.POST.get('prod_manufacturer')

                price_val = float(price) if price else 0.0
                stock_val = int(stock) if stock else 0

                product = Product(
                    name=name, description=desc, price=price_val, stock=stock_val,
                    category_id=cat_id, manufacturer_id=man_id
                )
                product.full_clean()
                product.save()
                success_message = f"Товар '{name}' успешно создан!"

            elif action == 'add_to_cart':
                product_id = request.POST.get('product_id')
                quantity = int(request.POST.get('quantity', 1))
                product = Product.objects.get(id=product_id)
                
                cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': 0})
                cart_item.quantity += quantity
                cart_item.full_clean() #запускаем встроенную валидацию остатков на складе по заданию
                cart_item.save()
                success_message = f"Товар '{product.name}' успешно добавлен в корзину!"

            elif action == 'remove_from_cart':
                item_id = request.POST.get('item_id')
                cart_item = CartItem.objects.get(id=item_id)
                cart_item.delete() #удаляем элемент из корзины по заданию
                success_message = "Товар успешно убран из корзины!"
                
        except ValidationError as e:
            if 'price' in e.message_dict:
                error_message = e.message_dict['price']
            elif 'stock' in e.message_dict:
                error_message = e.message_dict['stock']
            elif 'quantity' in e.message_dict:
                error_message = e.message_dict['quantity'] #перехватываем ошибку превышения склада
            else:
                error_message = "Ошибка валидации данных!"
        except ValueError:
            error_message = "Введите корректные числа!"

    categories = Category.objects.all() #получаем категории товаров из базы данных
    manufacturers = Manufacturer.objects.all() #получаем производителей товаров из базы данных
    products = Product.objects.all() #получаем все товары из базы данных
    carts = Cart.objects.all() #получаем все корзины из базы данных
    
    return render(request, 'index.html', {
        'categories': categories,
        'manufacturers': manufacturers,
        'products': products,
        'carts': carts,
        'error_message': error_message,
        'success_message': success_message
    })


def about(request):
    return render(request, 'about.html')


def info(request):
    return render(request, 'info.html')