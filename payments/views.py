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


import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Важно! Использовать backend без GUI
import matplotlib.pyplot as plt
from django.db.models import Sum, Avg, Count
from decimal import Decimal
import io
import urllib, base64


@login_required
def analytics(request):
    """Страница аналитики с графиками"""
    # Получаем квартиры пользователя
    user_apartments = Apartment.objects.filter(user=request.user)
    
    if not user_apartments.exists():
        messages.warning(request, 'Добавьте квартиру для просмотра аналитики!')
        return redirect('apartment_create')
    
    # Получаем платежи
    payments = PaymentRecord.objects.filter(apartment__in=user_apartments).order_by('date')
    
    if not payments.exists():
        messages.warning(request, 'Добавьте платежи для просмотра аналитики!')
        return redirect('payment_create')
    
    # Преобразуем в DataFrame
    df = pd.DataFrame(list(payments.values(
        'date', 'service_type__name', 'consumption', 'total_amount', 'is_overpayment'
    )))
    
    # Переименовываем колонки
    df.columns = ['date', 'service', 'consumption', 'amount', 'is_overpayment']
    
    # ВАЖНО: Преобразуем date в datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Преобразуем Decimal в float для расчётов
    df['amount'] = df['amount'].astype(float)
    df['consumption'] = df['consumption'].astype(float)
    
    # === СТАТИСТИКА ===
    total_spent = df['amount'].sum()
    avg_monthly = df.groupby(df['date'].dt.to_period('M'))['amount'].sum().mean()
    overpayments_count = df['is_overpayment'].sum()
    overpayments_amount = df[df['is_overpayment'] == True]['amount'].sum()
    
    # === ГРАФИК 1: Расходы по месяцам ===
    monthly_data = df.groupby(df['date'].dt.to_period('M'))['amount'].sum()
    
    plt.figure(figsize=(10, 5))
    ax = monthly_data.plot(kind='bar', color='#667eea')
    plt.title('Расходы по месяцам', fontsize=14)
    plt.xlabel('Месяц')
    plt.ylabel('Сумма (руб)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Сохраняем в base64
    buffer1 = io.BytesIO()
    plt.savefig(buffer1, format='png', dpi=100)
    buffer1.seek(0)
    chart1 = base64.b64encode(buffer1.getvalue()).decode()
    buffer1.close()
    plt.close()
    
    # === ГРАФИК 2: Расходы по типам услуг ===
    service_data = df.groupby('service')['amount'].sum().sort_values(ascending=False)
    
    plt.figure(figsize=(8, 8))
    colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe']
    plt.pie(service_data.values, labels=service_data.index, autopct='%1.1f%%', 
            colors=colors[:len(service_data)], startangle=90)
    plt.title('Структура расходов по услугам', fontsize=14)
    plt.tight_layout()
    
    buffer2 = io.BytesIO()
    plt.savefig(buffer2, format='png', dpi=100)
    buffer2.seek(0)
    chart2 = base64.b64encode(buffer2.getvalue()).decode()
    buffer2.close()
    plt.close()
    
    # === ПРОГНОЗ (скользящее среднее последних 3 месяцев) ===
    recent_months = monthly_data.tail(3)
    forecast = recent_months.mean() if len(recent_months) > 0 else 0
    
    # === СРАВНЕНИЕ С НОРМАТИВАМИ ===
    apartment = user_apartments.first()
    services_stats = []
    
    for service in ServiceType.objects.all():
        service_payments = payments.filter(service_type=service)
        if service_payments.exists():
            avg_consumption = service_payments.aggregate(Avg('consumption'))['consumption__avg']
            norm = float(service.norm_per_person) * apartment.residents_count
            diff_percent = ((float(avg_consumption) - norm) / norm * 100) if norm > 0 else 0
            
            services_stats.append({
                'name': service.name,
                'avg': round(float(avg_consumption), 2),
                'norm': round(norm, 2),
                'diff': round(diff_percent, 1)
            })
    
    context = {
        'total_spent': round(total_spent, 2),
        'avg_monthly': round(avg_monthly, 2),
        'overpayments_count': int(overpayments_count),
        'overpayments_amount': round(overpayments_amount, 2),
        'forecast': round(forecast, 2),
        'chart1': chart1,
        'chart2': chart2,
        'services_stats': services_stats,
    }
    
    return render(request, 'payments/analytics.html', context)