from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from decimal import Decimal
from .models import Apartment, PaymentRecord, ServiceType
from .forms import RegisterForm, ApartmentForm, PaymentRecordForm


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


@login_required
def payment_list(request):
    """Список платежей пользователя"""
    # Получаем все квартиры пользователя
    user_apartments = Apartment.objects.filter(user=request.user)
    # Получаем платежи по этим квартирам
    payments = PaymentRecord.objects.filter(apartment__in=user_apartments).order_by('-date')
    
    return render(request, 'payments/payment_list.html', {'payments': payments})


@login_required
def payment_create(request):
    """Добавление нового платежа"""
    # Проверяем, есть ли у пользователя квартиры
    if not Apartment.objects.filter(user=request.user).exists():
        messages.warning(request, 'Сначала добавьте квартиру!')
        return redirect('apartment_create')
    
    if request.method == 'POST':
        form = PaymentRecordForm(request.user, request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            
            # Рассчитываем сумму платежа
            payment.total_amount = payment.consumption * payment.tariff
            
            # Проверяем на переплату
            apartment = payment.apartment
            service = payment.service_type
            norm = service.norm_per_person * apartment.residents_count
            
            # Если потребление превышает норму на 10% — это переплата
            if payment.consumption > norm * Decimal('1.1'):
                payment.is_overpayment = True
            
            payment.save()
            messages.success(request, f'Платёж на сумму {payment.total_amount} руб. добавлен!')
            return redirect('payment_list')
    else:
        form = PaymentRecordForm(request.user)
    
    return render(request, 'payments/payment_form.html', {'form': form, 'title': 'Добавить платёж'})


@login_required
def payment_edit(request, pk):
    """Редактирование платежа"""
    payment = get_object_or_404(PaymentRecord, pk=pk, apartment__user=request.user)
    
    if request.method == 'POST':
        form = PaymentRecordForm(request.user, request.POST, instance=payment)
        if form.is_valid():
            payment = form.save(commit=False)
            
            # Пересчитываем сумму
            payment.total_amount = payment.consumption * payment.tariff
            
            # Пересчитываем переплату
            apartment = payment.apartment
            service = payment.service_type
            norm = service.norm_per_person * apartment.residents_count
            payment.is_overpayment = payment.consumption > norm * Decimal('1.1')
            
            payment.save()
            messages.success(request, 'Платёж обновлён!')
            return redirect('payment_list')
    else:
        form = PaymentRecordForm(request.user, instance=payment)
    
    return render(request, 'payments/payment_form.html', {'form': form, 'title': 'Редактировать платёж'})


@login_required
def payment_delete(request, pk):
    """Удаление платежа"""
    payment = get_object_or_404(PaymentRecord, pk=pk, apartment__user=request.user)
    
    if request.method == 'POST':
        payment.delete()
        messages.success(request, 'Платёж удалён!')
        return redirect('payment_list')
    
    return render(request, 'payments/payment_confirm_delete.html', {'payment': payment})
