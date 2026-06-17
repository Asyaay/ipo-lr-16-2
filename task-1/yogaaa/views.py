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
                
        except ValidationError as e:
            if 'price' in e.message_dict:
                error_message = e.message_dict['price'][0]
            elif 'stock' in e.message_dict:
                error_message = e.message_dict['stock'][0]
            else:
                error_message = "Ошибка валидации данных!"
        except ValueError:
            error_message = "Введите корректные числовые значения!"

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


def catalog_view(request):
    products = Product.objects.all() #получаем все товары для каталога из базы данных
    return render(request, 'catalog.html', {'products': products}) #открываем страницу каталога товаров


def product_detail(request, pk):
    product = Product.objects.get(id=pk) #находим один конкретный товар по его идентификатору id
    return render(request, 'product_detail.html', {'product': product}) #открываем страницу детальной информации о товаре


def cart_view(request):
    cart = get_or_create_test_cart() #получаем текущую корзину покупателя
    return render(request, 'cart.html', {'cart': cart}) #открываем страницу просмотра корзины пользователя


def cart_add(request, product_id):
    cart = get_or_create_test_cart() #получаем текущую корзину покупателя
    product = Product.objects.get(id=product_id) #находим покупаемый товар по идентификатору
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': 0})
    try:
        cart_item.quantity += 1
        cart_item.full_clean()
        cart_item.save()
    except ValidationError:
        pass
    return redirect('cart_view') #перенаправляем пользователя на просмотр корзины


def cart_update(request, item_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart_item = CartItem.objects.get(id=item_id) #находим элемент корзины по его идентификатору
        try:
            cart_item.quantity = quantity
            cart_item.full_clean()
            cart_item.save()
        except ValidationError:
            pass
    return redirect('cart_view') #перенаправляем обратно на просмотр корзины


def cart_remove(request, item_id):
    cart_item = CartItem.objects.get(id=item_id) #находим нужный элемент корзины для удаления
    cart_item.delete() #удаляем товар из корзины пользователя
    return redirect('cart_view') #перенаправляем обратно на просмотр корзины


def about(request):
    return render(request, 'about.html')


def info(request):
    return render(request, 'info.html')