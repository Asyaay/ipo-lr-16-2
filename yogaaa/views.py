from django.shortcuts import render #импортируем

def yoga(request): #создаем функцию
    return render(request, 'index.html') #оформляем страницу
def about(request): #создаем функцию
    return render(request, 'about.html') #оформляем страницу
def info(request): #создаем функцию
    return render(request, 'info.html') #оформляем страницу