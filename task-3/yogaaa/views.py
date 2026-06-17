import io
import openpyxl
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError, PermissionDenied
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth.decorators import login_required #импортируем декоратор ограничения доступа по заданию
from django.core.mail import EmailMessage #импортируем класс для отправки писем с вложениями
from django.contrib.auth import login, authenticate, logout #импортируем встроенные методы аутентификации для задания 2
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm #импортируем стандартные формы django
from rest_framework import viewsets, generics, permissions as drf_permissions
from rest_framework.response import Response
from .models import Category, Manufacturer, Product, Cart, CartItem, Order, OrderItem, Profile
from .serializers import (
    CategorySerializer, ManufacturerSerializer, ProductSerializer, 
    CartSerializer, CartItemSerializer, ProfileSerializer, OrderSerializer
)
from django.core.paginator import Paginator #импортируем встроенный модуль пагинации страниц django

def get_or_create_test_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user) #находим или создаем личную корзину конкретного авторизованного пользователя студии йоги
    return cart

def yoga(request):
    error_message = None #инициализируем пустую переменную для ошибок на главной странице витрины
    success_message = None #инициализируем пустую переменную для успешных уведомлений на главной витрине
    action = request.POST.get('action') #получаем тип действия из отправленной формы витрины
    
    if request.method == 'POST':
        # Проверяем роли: только менеджер йоги или администратор могут добавлять контент (Задание 1)
        if action in ['add_category', 'add_manufacturer', 'add_product']:
            if not request.user.is_authenticated or request.user.profile.role not in ['MANAGER', 'ADMIN']:
                raise PermissionDenied("У вас нет прав для выполнения этого действия.")

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
    
    return render(request, 'shop/index.html', {
        'categories': categories,
        'manufacturers': manufacturers,
        'products': products,
        'carts': carts,
        'error_message': error_message,
        'success_message': success_message
    }) #открываем главную страницу в подпапке по странице структуры наследования
def product_list(request):
    products = Product.objects.all().order_by('id') #получаем все товары для йоги с обязательной сортировкой для пагинатора
    query = request.GET.get('q') #получаем строку поиска товара для йоги от пользователя из запроса
    category_id = request.GET.get('category') #получаем фильтр по категории йога-товаров из запроса
    manufacturer_id = request.GET.get('manufacturer') #получаем фильтр по производителю бренда из запроса
    
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query)) #выполняем поиск через Q-объекты по заданию
        
    if category_id:
        products = products.filter(category_id=category_id) #выполняем фильтрацию по йога-категориям по заданию
        
    if manufacturer_id:
        products = products.filter(manufacturer_id=manufacturer_id) #выполняем фильтрацию по производителям брендам по заданию
        
    paginator = Paginator(products, 9) #инициализируем разбивку каталога товаров строго по 9 позиций на страницу
    page_number = request.GET.get('page') #считываем текущий номер страницы из параметров get запроса
    page_obj = paginator.get_page(page_number) #формируем выборку объектов для отображения на текущей странице
    
    categories = Category.objects.all() #получаем все категории йога-товаров из базы данных
    manufacturers = Manufacturer.objects.all() #получаем всех производителей йога-товаров из базы данных
    
    return render(request, 'shop/catalog.html', {
        'page_obj': page_obj,
        'categories': categories,
        'manufacturers': manufacturers
    }) #открываем обновленную страницу каталога по измененному тз

def product_detail(request, pk):
    product = get_or_create_test_cart(request.user) #дополнительная техническая привязка корзины для отображения в шаблонах родителя
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
    return redirect('product_list') ##перенаправляем пользователя на просмотр обновленного каталога товаров

@login_required #ограничиваем доступ к изменению количества товара только для авторизованных пользователей по заданию
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
    return render(request, 'shop/about.html') #открываем страницу информации об авторе проекта студии йоги

def info(request):
    return render(request, 'shop/info.html') #открываем страницу общей информации о магазине товаров для йоги

@login_required #ограничиваем доступ к оформлению заказа только для авторизованных пользователей по заданию
def checkout_view(request):
    cart = get_or_create_test_cart(request.user) #получаем корзину текущего пользователя для оформления заказа
    cart_items = cart.items.all() #считываем содержимое корзины для переноса в заказ

    if request.method == 'POST':
        order = Order.objects.create(user=request.user, total_cost=cart.total_cost) #создаем запись нового заказа в базе данных

        wb = openpyxl.Workbook() #инициализируем генерацию товарного чека в формате Excel
        ws = wb.active #активируем рабочий лист электронной таблицы для записи данных
        ws.title = f"Чек заказа {order.id}" #задаем имя вкладки для создаваемого Excel файла

        ws.append([f"Чек по заказу № {order.id}"]) #записываем уникальный номер чека в файл Excel
        ws.append([f"Покупатель: {request.user.username}"]) #записываем имя текущего клиента в файл Excel
        ws.append([]) #вставляем пустую строку для соблюдения структуры документа в таблице
        ws.append(["Товар", "Цена (BYN)", "Количество", "Стоимость"]) #задаем заголовки колонок чека в Excel

        for item in cart_items:
            OrderItem.objects.create(
                order=order, product=item.product, price=item.product.price, quantity=item.quantity
            ) #переносим каждую позицию товара из корзины в состав оформленного заказа
            ws.append([item.product.name, item.product.price, item.quantity, item.element_cost]) #добавляем строку с данными товара в Excel

        ws.append([]) #вставляем пустую строку перед выводом итоговых данных
        ws.append(["ИТОГО К ОПЛАТЕ:", "", "", order.total_cost]) #записываем финальную сумму к оплате в Excel

        wb.save(f"receipt_order_{order.id}.xlsx") #физически сохраняем адекватный читаемый файл Excel на компьютер для проверки

        excel_file = io.BytesIO() #создаем байтовый поток в оперативной памяти для виртуального файла
        wb.save(excel_file) #сохраняем сгенерированную Excel таблицу в созданный байтовый поток
        excel_file.seek(0) #сбрасываем указатель потока в начало для последующего чтения данных

        user_email = request.user.email if request.user.email else "customer@proyoga.by" #определяем электронный адрес покупателя
        
        email = EmailMessage(
            f"Ваш чек по заказу №{order.id} - ProYoga",
            "Благодарим за покупку в магазине ProYoga! Ваш чек во вложении.",
            "noreply@proyoga.by",
            [user_email]
        ) #формируем отправку уведомления по электронной почте покупателю

        email.attach(f"receipt_order_{order.id}.xlsx", excel_file.read(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet") #прикрепляем сгенерированный Excel файл к письму
        
        try:
            email.send(fail_silently=True) #отправляем сформированное письмо с вложенным файлом покупателю
        except Exception:
            pass #игнорируем ошибки отправки если локальный почтовый сервер не настроен

        cart.items.all().delete() #выполняем очистку содержимого корзины после успешного заказа
        
        return render(request, 'shop/index.html', {'success_message': f"Заказ №{order.id} успешно оформлен! Чек отправлен на почту."})

    return render(request, 'shop/checkout.html')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile = user.profile
            profile.full_name = request.POST.get('full_name', '')
            profile.phone = request.POST.get('phone', '')
            profile.address = request.POST.get('address', '')
            profile.role = 'CUSTOMER'
            profile.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'shop/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'shop/login.html', {'form': form})

def logout_view(request):
    logout(request)
    request.session.flush()
    response = redirect('home')
    response.delete_cookie('sessionid')
    return response
class UserProfileView(generics.RetrieveUpdateAPIView):
    # Эндпоинт GET и PATCH /api/me/ (Задание 3, пункты 1 и 2)
    serializer_class = ProfileSerializer
    permission_classes = [drf_permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile

class OrderViewSet(viewsets.ModelViewSet):
    # Эндпоинт /api/orders/ с ролевым разграничением (Задание 3, пункт 4)
    serializer_class = OrderSerializer
    permission_classes = [drf_permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user.profile, 'role', '') == 'ADMIN':
            return Order.objects.all()
        return Order.objects.filter(user=user)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ManufacturerViewSet(viewsets.ModelViewSet):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer

class ProductViewSet(viewsets.ModelViewSet):
    # Настройка кастомных прав для API каталога товаров (Задание 3, пункт 3)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    # Объявляем класс прав доступа прямо здесь, исключая внешний файл
    class DjangoIsAdminOrReadOnly(drf_permissions.BasePermission):
        def has_permission(self, request, view):
            # Разрешаем безопасные GET, HEAD, OPTIONS запросы абсолютно всем
            if request.method in drf_permissions.SAFE_METHODS:
                return True
            # Разрешаем изменение данных только для ADMIN
            return (
                request.user and 
                request.user.is_authenticated and 
                getattr(request.user.profile, 'role', '') == 'ADMIN'
            )
            
    # Подключаем созданный локально класс ограничений
    permission_classes = [DjangoIsAdminOrReadOnly]

class CartViewSet(viewsets.ModelViewSet):
    # API представление для просмотра созданных корзин пользователей
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

class CartItemViewSet(viewsets.ModelViewSet):
    # API представление для просмотра элементов внутри корзин
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer