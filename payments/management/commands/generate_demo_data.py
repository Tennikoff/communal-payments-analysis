from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from payments.models import Apartment, ServiceType, PaymentRecord
from datetime import date, timedelta
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Генерация демо-данных для презентации проекта'

    def handle(self, *args, **options):
        self.stdout.write('Начинаем генерацию демо-данных...\n')

        # 1. Создаём или получаем демо-пользователя
        demo_user, created = User.objects.get_or_create(
            username='demo',
            defaults={
                'email': 'demo@example.com',
                'first_name': 'Демо',
                'last_name': 'Пользователь',
            }
        )
        if created:
            demo_user.set_password('demo123456')
            demo_user.save()
            self.stdout.write(self.style.SUCCESS(' Создан пользователь: demo / demo123456'))
        else:
            self.stdout.write('Пользователь demo уже существует')

        # 2. Создаём типы услуг (если ещё нет)
        services_data = [
            {'name': 'Электроэнергия', 'unit': 'кВт·ч', 'norm_per_person': 70, 'description': 'Оплата за электричество'},
            {'name': 'Холодная вода', 'unit': 'м³', 'norm_per_person': 5, 'description': 'Холодное водоснабжение'},
            {'name': 'Горячая вода', 'unit': 'м³', 'norm_per_person': 3.5, 'description': 'Горячее водоснабжение'},
            {'name': 'Газ', 'unit': 'м³', 'norm_per_person': 10, 'description': 'Газоснабжение'},
            {'name': 'Отопление', 'unit': 'Гкал', 'norm_per_person': 0.02, 'description': 'Центральное отопление'},
        ]

        services = []
        for s_data in services_data:
            service, created = ServiceType.objects.get_or_create(
                name=s_data['name'],
                defaults={
                    'unit': s_data['unit'],
                    'norm_per_person': Decimal(str(s_data['norm_per_person'])),
                    'description': s_data['description'],
                }
            )
            services.append(service)
            if created:
                self.stdout.write(f' Создана услуга: {service.name}')

        # 3. Создаём квартиры для демо-пользователя
        apartments_data = [
            {'address': 'г. Москва, ул. Пушкина, д. 10, кв. 25', 'area': 54.5, 'residents_count': 3},
            {'address': 'г. Москва, ул. Белинского, д. 52, кв. 12', 'area': 38.0, 'residents_count': 2},
            {'address': 'МО, г. Химки, ул. Победы, д. 8, кв. 101', 'area': 72.3, 'residents_count': 4},
        ]

        apartments = []
        for a_data in apartments_data:
            apartment, created = Apartment.objects.get_or_create(
                user=demo_user,
                address=a_data['address'],
                defaults={
                    'area': Decimal(str(a_data['area'])),
                    'residents_count': a_data['residents_count'],
                }
            )
            apartments.append(apartment)
            if created:
                self.stdout.write(f' Создана квартира: {apartment.address[:30]}...')

        # 4. Генерируем платежи за последние 12 месяцев
        self.stdout.write('\n Генерируем платежи...\n')
        
        # Тарифы для каждой услуги
        tariffs = {
            'Электроэнергия': Decimal('5.47'),
            'Холодная вода': Decimal('42.30'),
            'Горячая вода': Decimal('198.50'),
            'Газ': Decimal('7.20'),
            'Отопление': Decimal('2800.00'),
        }

        payments_created = 0
        today = date.today()

        for apartment in apartments:
            for month_offset in range(12):
                # Дата платежа — первое число каждого месяца
                payment_date = date(
                    today.year if today.month - month_offset > 0 else today.year - 1,
                    (today.month - month_offset - 1) % 12 + 1,
                    15
                )

                for service in services:
                    # Пропускаем отопление летом
                    if service.name == 'Отопление' and payment_date.month in [5, 6, 7, 8, 9]:
                        continue

                    # Базовое потребление на основе норматива
                    base_consumption = float(service.norm_per_person) * apartment.residents_count
                    
                    # Добавляем случайное отклонение (-20% до +40%)
                    variation = random.uniform(0.8, 1.4)
                    consumption = Decimal(str(round(base_consumption * variation, 2)))

                    # Иногда делаем явную переплату (15% случаев)
                    if random.random() < 0.15:
                        consumption = consumption * Decimal('1.5')

                    tariff = tariffs.get(service.name, Decimal('10.00'))
                    total_amount = consumption * tariff

                    # Проверяем на переплату
                    norm = service.norm_per_person * apartment.residents_count
                    is_overpayment = consumption > norm * Decimal('1.1')

                    # Проверяем, не существует ли уже такой платёж
                    exists = PaymentRecord.objects.filter(
                        apartment=apartment,
                        service_type=service,
                        date=payment_date
                    ).exists()

                    if not exists:
                        PaymentRecord.objects.create(
                            apartment=apartment,
                            service_type=service,
                            date=payment_date,
                            consumption=consumption,
                            tariff=tariff,
                            total_amount=round(total_amount, 2),
                            is_overpayment=is_overpayment,
                        )
                        payments_created += 1

        self.stdout.write(self.style.SUCCESS(f'\n Создано {payments_created} платежей!'))
        self.stdout.write(self.style.SUCCESS('\n Демо-данные успешно созданы!'))
        self.stdout.write(self.style.WARNING('\n Данные для входа: demo / demo123456'))