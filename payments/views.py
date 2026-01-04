from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Apartment, PaymentRecord


def home(request):
    """Главная страница"""
    stats = {
        'users_count': User.objects.count(),
        'apartments_count': Apartment.objects.count(),
        'payments_count': PaymentRecord.objects.count(),
    }
    return render(request, 'home.html', {'stats': stats})
