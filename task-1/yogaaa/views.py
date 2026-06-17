from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth.decorators import login_required #импортируем декоратор ограничения доступа по заданию
from .models import Category, Manufacturer, Product, Cart, CartItem


def get_or_create_test_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user) #находим или создаем личную корзину конкретного авторизованного пользователя студии йоги
    return cart


def yoga(request):
    error_message = None #инициализируем пустую переменную для ошибок на главной странице витрины
    success_message = None #инициализируем пустую переменную для успешных уведомлений на главной витрине
    action = request.POST.get('action') #получаем тип действия из отправленной формы витрины

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
                error_message = e.message_dict['price']
            elif 'stock' in e.message_dict:
                error_message = e.message_dict['stock']
            else:
                error_message = "Ошибка валидации данных!"
        except ValueError:
            error_message = "Введите корректные числовые значения!"

    categories = Category.objects.all() #получаем категории товаров для йоги из базы данных
    manufacturers = Manufacturer.objects.all() #получаем производителей товаров для выпадающих списков
    products = Product.objects.all() #получаем все товары витрины йоги из базы данных
    carts = Cart.objects.all() #получаем все корзины пользователей из базы данных
    
    return render(request, 'index.html', {
        'categories': categories,
        'manufacturers': manufacturers,
        'products': products,
        'carts': carts,
        'error_message': error_message,
        'success_message': success_message
    })


def product_list(request):
    products = Product.objects.all() #получаем базовый набор всех товаров для йоги из базы данных
    query = request.GET.get('q') #получаем строку поиска товара для йоги от пользователя из запроса
    category_id = request.GET.get('category') #получаем фильтр по категории йога-товаров из запроса
    manufacturer_id = request.GET.get('manufacturer') #получаем фильтр по производителю бренда из запроса

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query)) #выполняем поиск через Q-объекты по заданию

    if category_id:
        products = products.filter(category_id=category_id) #выполняем фильтрацию по йога-категориям по заданию

    if manufacturer_id:
        products = products.filter(manufacturer_id=manufacturer_id) #выполняем фильтрацию по производителям брендов по заданию

    categories = Category.objects.all() #получаем все категории йога-товаров из базы данных
    manufacturers = Manufacturer.objects.all() #получаем всех производителей йога-товаров из базы данных
    return render(request, 'shop/product_list.html', {
        'products': products,
        'categories': categories,
        'manufacturers': manufacturers
    }) #открываем страницу списка товаров каталога студии йоги в папке shop


def product_detail(request, pk):
    product = get_object_or_404(Product, id=pk) #отображение информации о йога-товаре с обработкой ошибки 404 по заданию
    return render(request, 'shop/product_detail.html', {'product': product}) #открываем страницу детальной информации о товаре для йоги в папке shop


@login_required #ограничиваем доступ к добавлению в корзину только для авторизованных пользователей по заданию
def add_to_cart(request, product_id):
    cart = get_or_create_test_cart(request.user) #получаем личную корзину текущего вошедшего пользователя студии йоги
    product = get_object_or_404(Product, id=product_id) #находим покупаемый товар для йоги или возвращаем ошибку 404
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': 0}) #находим элемент
    
    try:
        cart_item.quantity += 1 #увеличиваем количество товара для йоги в корзине на одну штуку
        cart_item.full_clean() #проверяем валидность данных в модели элемента корзины студии йоги
        cart_item.save() #сохраняем изменения элемента корзины в базу данных
    except ValidationError:
        pass
    return redirect('cart_view') #перенаправляем пользователя на просмотр корзины покупателя


@login_required #ограничиваем доступ к изменению количества только для авторизованных пользователей по заданию
def update_cart(request, item_id):
    error_message = None #инициализируем пустую переменную для сообщения об ошибке корзины йоги
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1)) #получаем новое количество товара из формы
        cart_item = get_object_or_404(CartItem, id=item_id) #находим элемент корзины или возвращаем ошибку 404
        try:
            cart_item.quantity = quantity #обновляем поле количества в модели по заданию
            cart_item.full_clean() #запускаем валидацию количества против остатка товара на складе студии
            cart_item.save() #сохраняем обновленный элемент корзины студии йоги в базу данных
            return redirect('cart_view') #перенаправляем обратно на просмотр корзины йога-товаров
        except ValidationError as e:
            if 'quantity' in e.message_dict:
                error_message = e.message_dict['quantity'] #перехватываем точный текст ошибки остатков со склада йоги
            else:
                error_message = "Ошибка валидации количества!" #записываем общую ошибку валидации количества

    cart = get_or_create_test_cart(request.user) #получаем текущую корзину студии йоги со всеми элементами
    return render(request, 'shop/cart.html', {'cart': cart, 'error_message': error_message}) #открываем страницу корзины в папке shop с ошибкой


@login_required #ограничиваем доступ к удалению из корзины только для авторизованных пользователей по заданию
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id) #находим элемент корзины йоги по его уникальному номеру id
    cart_item.delete() #выполняем удаление объекта элемента из базы данных по заданию
    return redirect('cart_view') #перенаправляем пользователя обратно на просмотр корзины студии йоги


@login_required #ограничиваем доступ к просмотру корзины только для авторизованных пользователей по заданию
def cart_view(request):
    cart = get_or_create_test_cart(request.user) #получаем корзину со всеми элементами для отображения по заданию
    return render(request, 'shop/cart.html', {'cart': cart}) #отображение всех элементов корзины с общей стоимостью в папке shop


def about(request):
    return render(request, 'about.html') #открываем страницу информации об авторе проекта студии йоги


def info(request):
    return render(request, 'info.html') #открываем страницу общей информации о магазине товаров для йоги


def checkout_view(request):
    return render(request, 'shop/checkout.html') #НОВАЯ функция отображения страницы оформления заказа для йоги по заданию 1 лабы 19
