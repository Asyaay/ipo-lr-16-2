from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    # Кастомное право доступа для каталога товаров (Задание 3, пункт 3)
    def has_permission(self, request, view):
        # GET, HEAD, OPTIONS запросы (чтение) доступны абсолютно всем
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # POST, PUT, PATCH, DELETE доступны только если пользователь авторизован и имеет роль ADMIN
        return (
            request.user and 
            request.user.is_authenticated and 
            getattr(request.user.profile, 'role', '') == 'ADMIN'
        )