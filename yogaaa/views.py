import io
import openpyxl
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError, PermissionDenied
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from rest_framework import viewsets, generics, permissions as drf_permissions
from rest_framework.response import Response
from .models import Category, Manufacturer, Product, Cart, CartItem, Order, OrderItem, Profile
from .serializers import (
    CategorySerializer, ManufacturerSerializer, ProductSerializer, 
    CartSerializer, CartItemSerializer, ProfileSerializer, OrderSerializer
)
from django.core.paginator import Paginator

def get_or_create_test_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart

def yoga(request):
    error_message = None
    success_message = None
    action = request.POST.get('action')
    
    if request.method == 'POST':
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

    categories = Category.objects.all()
    manufacturers = Manufacturer.objects.all()
    products = Product.objects.all()
    carts = Cart.objects.all()
    
    return render(request, 'shop/index.html', {
        'categories': categories,
        'manufacturers': manufacturers,
        'products': products,
        'carts': carts,
        'error_message': error_message,
        'success_message': success_message
    })
def product_list(request):
    products = Product.objects.all().order_by('id')
    query = request.GET.get('q')
    category_id = request.GET.get('category')
    manufacturer_id = request.GET.get('manufacturer')
    
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
        
    if category_id:
        products = products.filter(category_id=category_id)
        
    if manufacturer_id:
        products = products.filter(manufacturer_id=manufacturer_id)
        
    paginator = Paginator(products, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    manufacturers = Manufacturer.objects.all()
    
    return render(request, 'shop/catalog.html', {
        'page_obj': page_obj,
        'categories': categories,
        'manufacturers': manufacturers
    })

def product_detail(request, pk):
    product = get_or_create_test_cart(request.user)
    product = get_object_or_404(Product, id=pk)
    return render(request, 'shop/product_detail.html', {'product': product})
@login_required
def add_to_cart(request, product_id):
    cart = get_or_create_test_cart(request.user)
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': 0})
    
    try:
        cart_item.quantity += 1
        cart_item.full_clean()
        cart_item.save()
    except ValidationError:
        pass
    return redirect('product_list')

@login_required
def update_cart(request, item_id):
    error_message = None
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart_item = get_object_or_404(CartItem, id=item_id)
        try:
            cart_item.quantity = quantity
            cart_item.full_clean()
            cart_item.save()
            return redirect('cart_view')
        except ValidationError as e:
            if 'quantity' in e.message_dict:
                error_message = e.message_dict['quantity']
            else:
                error_message = "Ошибка валидации количества!"
                
    cart = get_or_create_test_cart(request.user)
    return render(request, 'shop/cart.html', {'cart': cart, 'error_message': error_message})

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    return redirect('cart_view')

@login_required
def cart_view(request):
    cart = get_or_create_test_cart(request.user)
    return render(request, 'shop/cart.html', {'cart': cart})
def about(request):
    return render(request, 'shop/about.html')

def info(request):
    return render(request, 'shop/info.html')

@login_required
def checkout_view(request):
    cart = get_or_create_test_cart(request.user)
    cart_items = cart.items.all()

    if request.method == 'POST':
        order = Order.objects.create(user=request.user, total_cost=cart.total_cost)
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = f"Чек заказа {order.id}"
        ws.append([f"Чек по заказу № {order.id}"])
        ws.append([f"Покупатель: {request.user.username}"])
        ws.append([])
        ws.append(["Товар", "Цена (BYN)", "Количество", "Стоимость"])

        for item in cart_items:
            OrderItem.objects.create(order=order, product=item.product, price=item.product.price, quantity=item.quantity)
            ws.append([item.product.name, item.product.price, item.quantity, item.element_cost])

        ws.append([])
        ws.append(["ИТОГО К ОПЛАТЕ:", "", "", order.total_cost])
        wb.save(f"receipt_order_{order.id}.xlsx")

        excel_file = io.BytesIO()
        wb.save(excel_file)
        excel_file.seek(0)

        user_email = request.user.email if request.user.email else "customer@proyoga.by"
        email = EmailMessage(f"Ваш чек №{order.id}", "Благодарим за покупку!", "noreply@proyoga.by", [user_email])
        email.attach(f"receipt_order_{order.id}.xlsx", excel_file.read(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        try: email.send(fail_silently=True)
        except Exception: pass

        cart.items.all().delete()
        return render(request, 'shop/index.html', {'success_message': f"Заказ №{order.id} оформлен!"})
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
            profile.save()
            login(request, user)
            return redirect('home')
    else: form = UserCreationForm()
    return render(request, 'shop/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else: form = AuthenticationForm()
    return render(request, 'shop/login.html', {'form': form})

def logout_view(request):
    logout(request)
    request.session.flush()
    response = redirect('home')
    response.delete_cookie('sessionid')
    return response

def profile_page_view(request):
    return render(request, 'shop/profile.html')

@login_required
def settings_page_view(request):
    # Логика смены email в настройках безопасности (Индивидуальное задание, пункт 3)
    success_msg = None
    if request.method == 'POST':
        new_email = request.POST.get('email')
        if new_email:
            request.user.email = new_email
            request.user.save()
            success_msg = "✨ Email безопасности успешно обновлен!"
    return render(request, 'shop/settings.html', {'success_message': success_msg})
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [drf_permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile

    def perform_update(self, serializer):
        # Принудительно сохраняем измененные специфичные поля (Пункт 1)
        serializer.save()

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [drf_permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user.profile, 'role', '') == 'ADMIN': return Order.objects.all()
        return Order.objects.filter(user=user)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ManufacturerViewSet(viewsets.ModelViewSet):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    class DjangoIsAdminOrReadOnly(drf_permissions.BasePermission):
        def has_permission(self, request, view):
            if request.method in drf_permissions.SAFE_METHODS: return True
            return (request.user and request.user.is_authenticated and getattr(request.user.profile, 'role', '') == 'ADMIN')
    permission_classes = [DjangoIsAdminOrReadOnly]

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer