from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from decimal import Decimal
from .models import Apartment, PaymentRecord, ServiceType, UserServiceNorm
from .forms import RegisterForm, ApartmentForm, PaymentRecordForm, UserServiceNormForm
from django.db.models import Sum, Count, Avg
from django.http import JsonResponse

def home(request):
    """Главная страница с расширенной статистикой"""
    from django.db.models import Sum, Avg
    
    stats = {
        'users_count': User.objects.count(),
        'apartments_count': Apartment.objects.count(),
        'payments_count': PaymentRecord.objects.count(),
    }
    
    # Общая сумма всех платежей
    total_sum = PaymentRecord.objects.aggregate(Sum('total_amount'))['total_amount__sum']
    total_sum_value = float(total_sum) if total_sum else 0
    
    # Форматирование суммы (округление до целого)
    if total_sum_value >= 1000:
        stats['total_sum_display'] = f"{int(total_sum_value / 1000)}тыс ₽"
    else:
        stats['total_sum_display'] = f"{int(total_sum_value)} ₽"
    
    stats['total_sum'] = int(total_sum_value)
    
    # Количество выявленных переплат
    stats['overpayments_count'] = PaymentRecord.objects.filter(is_overpayment=True).count()
    
    # Средний платёж (округляем до целого)
    avg_payment = PaymentRecord.objects.aggregate(Avg('total_amount'))['total_amount__avg']
    stats['avg_payment'] = int(round(float(avg_payment))) if avg_payment else 0
    
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
    """Список квартир пользователя со статистикой"""
    apartments = Apartment.objects.filter(user=request.user)
    
    # Добавляем статистику для каждой квартиры
    apartments_with_stats = []
    for apartment in apartments:
        payments = PaymentRecord.objects.filter(apartment=apartment)
        total_spent = payments.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        payments_count = payments.count()
        overpayments_count = payments.filter(is_overpayment=True).count()
        
        apartments_with_stats.append({
            'apartment': apartment,
            'total_spent': round(float(total_spent), 2),
            'payments_count': payments_count,
            'overpayments_count': overpayments_count,
        })
    
    return render(request, 'payments/apartment_list.html', {'apartments': apartments_with_stats})


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
    """Список платежей пользователя с фильтрацией и статистикой"""
    user_apartments = Apartment.objects.filter(user=request.user)
    payments = PaymentRecord.objects.filter(apartment__in=user_apartments)
    
    # Фильтрация по типу услуги
    service_filter = request.GET.get('service')
    if service_filter:
        payments = payments.filter(service_type_id=service_filter)
    
    # Фильтрация по переплате
    overpayment_filter = request.GET.get('overpayment')
    if overpayment_filter == 'yes':
        payments = payments.filter(is_overpayment=True)
    elif overpayment_filter == 'no':
        payments = payments.filter(is_overpayment=False)
    
    # Сортировка
    sort = request.GET.get('sort', '-date')
    payments = payments.order_by(sort)
    
    # Получаем типы услуг для фильтра
    services = ServiceType.objects.all()
    
    # Статистика с агрегацией
    total_amount = payments.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    overpayments_count = payments.filter(is_overpayment=True).count()
    avg_payment = payments.aggregate(Avg('total_amount'))['total_amount__avg'] or 0
    
    context = {
        'payments': payments,
        'services': services,
        'total_amount': round(float(total_amount), 2),
        'avg_payment': round(float(avg_payment), 2),
        'overpayments_count': overpayments_count,
        'current_service': service_filter,
        'current_overpayment': overpayment_filter,
        'current_sort': sort,
    }
    
    return render(request, 'payments/payment_list.html', context)


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
    user_apartments = Apartment.objects.filter(user=request.user)
    
    if not user_apartments.exists():
        messages.warning(request, 'Добавьте квартиру для просмотра аналитики!')
        return redirect('apartment_create')
    
    payments = PaymentRecord.objects.filter(apartment__in=user_apartments).order_by('date')
    
    if not payments.exists():
        messages.warning(request, 'Добавьте платежи для просмотра аналитики!')
        return redirect('payment_create')
    
    # Получаем пользовательские нормативы
    user_norms = {
        un.service_type_id: un.norm_per_person 
        for un in UserServiceNorm.objects.filter(user=request.user)
    }
    
    # Преобразуем в DataFrame
    df = pd.DataFrame(list(payments.values(
        'date', 'service_type__name', 'consumption', 'total_amount', 'is_overpayment'
    )))
    
    df.columns = ['date', 'service', 'consumption', 'amount', 'is_overpayment']
    df['date'] = pd.to_datetime(df['date'])
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
    ax = monthly_data.plot(kind='bar', color='#1e3a5f')
    plt.title('Расходы по месяцам', fontsize=14, fontweight='bold')
    plt.xlabel('Месяц')
    plt.ylabel('Сумма (руб)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    buffer1 = io.BytesIO()
    plt.savefig(buffer1, format='png', dpi=100)
    buffer1.seek(0)
    chart1 = base64.b64encode(buffer1.getvalue()).decode()
    buffer1.close()
    plt.close()
    
    # === ГРАФИК 2: Расходы по типам услуг ===
    service_data = df.groupby('service')['amount'].sum().sort_values(ascending=False)
    
    plt.figure(figsize=(8, 8))
    colors = ['#1e3a5f', '#17a2b8', '#28a745', '#ffc107', '#dc3545']
    plt.pie(service_data.values, labels=service_data.index, autopct='%1.1f%%', 
            colors=colors[:len(service_data)], startangle=90)
    plt.title('Структура расходов по услугам', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    buffer2 = io.BytesIO()
    plt.savefig(buffer2, format='png', dpi=100)
    buffer2.seek(0)
    chart2 = base64.b64encode(buffer2.getvalue()).decode()
    buffer2.close()
    plt.close()
    
    # === ПРОГНОЗ ===
    recent_months = monthly_data.tail(3)
    forecast = recent_months.mean() if len(recent_months) > 0 else 0
    
    # === СРАВНЕНИЕ С НОРМАТИВАМИ ===
    apartment = user_apartments.first()
    services_stats = []
    
    for service in ServiceType.objects.all():
        service_payments = payments.filter(service_type=service)
        if service_payments.exists():
            avg_consumption = service_payments.aggregate(Avg('consumption'))['consumption__avg']
            
            # Используем пользовательский норматив, если есть
            if service.id in user_norms:
                norm_value = float(user_norms[service.id])
                is_custom = True
            else:
                norm_value = float(service.norm_per_person)
                is_custom = False
            
            norm = norm_value * apartment.residents_count
            diff_percent = ((float(avg_consumption) - norm) / norm * 100) if norm > 0 else 0
            
            services_stats.append({
                'id': service.id,
                'name': service.name,
                'unit': service.unit,
                'avg': round(float(avg_consumption), 2),
                'norm': round(norm, 2),
                'norm_per_person': round(norm_value, 2),
                'default_norm': float(service.norm_per_person),
                'is_custom': is_custom,
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
        'residents_count': apartment.residents_count,
    }
    
    return render(request, 'payments/analytics.html', context)


import csv
from django.http import HttpResponse


@login_required
def payment_export_csv(request):
    """Экспорт платежей в CSV"""
    user_apartments = Apartment.objects.filter(user=request.user)
    payments = PaymentRecord.objects.filter(apartment__in=user_apartments).order_by('-date')
    
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="payments.csv"'
    response.write('\ufeff')  # BOM для корректного отображения в Excel
    
    writer = csv.writer(response)
    writer.writerow(['Дата', 'Квартира', 'Услуга', 'Потребление', 'Единица', 'Тариф', 'Сумма', 'Переплата'])
    
    for payment in payments:
        writer.writerow([
            payment.date.strftime('%d.%m.%Y'),
            payment.apartment.address,
            payment.service_type.name,
            float(payment.consumption),
            payment.service_type.unit,
            float(payment.tariff),
            float(payment.total_amount),
            'Да' if payment.is_overpayment else 'Нет'
        ])
    
    return response


@login_required
def update_user_norm(request):
    """Обновление пользовательского норматива через AJAX"""
    if request.method == 'POST':
        service_id = request.POST.get('service_id')
        norm_value = request.POST.get('norm_value')
        
        try:
            service = ServiceType.objects.get(id=service_id)
            norm_value = Decimal(norm_value)
            
            # Создаём или обновляем норматив
            user_norm, created = UserServiceNorm.objects.update_or_create(
                user=request.user,
                service_type=service,
                defaults={'norm_per_person': norm_value}
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Норматив для "{service.name}" обновлён'
            })
        except (ServiceType.DoesNotExist, ValueError) as e:
            return JsonResponse({
                'success': False,
                'message': 'Ошибка при обновлении норматива'
            })
    
    return JsonResponse({'success': False, 'message': 'Неверный метод запроса'})


@login_required
def reset_user_norm(request):
    """Сброс пользовательского норматива к стандартному"""
    if request.method == 'POST':
        service_id = request.POST.get('service_id')
        
        try:
            UserServiceNorm.objects.filter(
                user=request.user,
                service_type_id=service_id
            ).delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Норматив сброшен к стандартному'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Ошибка при сбросе норматива'
            })
    
    return JsonResponse({'success': False, 'message': 'Неверный метод запроса'})