from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Apartment, PaymentRecord
from .forms import RegisterForm


def home(request):
    """Главная страница"""
    stats = {
        'users_count': User.objects.count(),
        'apartments_count': Apartment.objects.count(),
        'payments_count': PaymentRecord.objects.count(),
    }
    return render(request, 'home.html', {'stats': stats})


def register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешна! Добро пожаловать!')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})
