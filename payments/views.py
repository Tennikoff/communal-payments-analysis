from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Apartment, PaymentRecord, ServiceType
from .forms import RegisterForm, ApartmentForm


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


@login_required
def apartment_list(request):
    """Список квартир пользователя"""
    apartments = Apartment.objects.filter(user=request.user)
    return render(request, 'payments/apartment_list.html', {'apartments': apartments})


@login_required
def apartment_create(request):
    """Добавление новой квартиры"""
    if request.method == 'POST':
        form = ApartmentForm(request.POST)
        if form.is_valid():
            apartment = form.save(commit=False)
            apartment.user = request.user
            apartment.save()
            messages.success(request, 'Квартира успешно добавлена!')
            return redirect('apartment_list')
    else:
        form = ApartmentForm()
    return render(request, 'payments/apartment_form.html', {'form': form, 'title': 'Добавить квартиру'})


@login_required
def apartment_edit(request, pk):
    """Редактирование квартиры"""
    apartment = get_object_or_404(Apartment, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ApartmentForm(request.POST, instance=apartment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Квартира успешно обновлена!')
            return redirect('apartment_list')
    else:
        form = ApartmentForm(instance=apartment)
    return render(request, 'payments/apartment_form.html', {'form': form, 'title': 'Редактировать квартиру'})


@login_required
def apartment_delete(request, pk):
    """Удаление квартиры"""
    apartment = get_object_or_404(Apartment, pk=pk, user=request.user)
    if request.method == 'POST':
        apartment.delete()
        messages.success(request, 'Квартира удалена!')
        return redirect('apartment_list')
    return render(request, 'payments/apartment_confirm_delete.html', {'apartment': apartment})