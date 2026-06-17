import os
from django.core.wsgi import get_wsgi_application

# Указываем правильное имя папки для продакшн-сервера Gunicorn
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yoga.settings')

application = get_wsgi_application()