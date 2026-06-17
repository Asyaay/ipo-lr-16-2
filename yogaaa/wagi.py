import os
from django.core.wsgi import get_wsgi_application

# Жестко задаем модуль настроек для продакшна продакшн-сервера
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yogaaa.settings')

application = get_wsgi_application()