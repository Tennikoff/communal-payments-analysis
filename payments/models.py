from django.db import models
from django.contrib.auth.models import User


class ServiceType(models.Model):
    """Тип коммунальной услуги (электричество, вода, газ и т.д.)"""
    name = models.CharField(max_length=100, verbose_name='Название услуги')
    unit = models.CharField(max_length=20, verbose_name='Единица измерения')
    norm_per_person = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='Норматив на человека'
    )
    description = models.TextField(blank=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'Тип услуги'
        verbose_name_plural = 'Типы услуг'

    def __str__(self):
        return f"{self.name} ({self.unit})"


class Apartment(models.Model):
    """Квартира пользователя"""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name='Владелец'
    )
    address = models.CharField(max_length=255, verbose_name='Адрес')
    area = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        verbose_name='Площадь (м²)'
    )
    residents_count = models.PositiveIntegerField(
        default=1, 
        verbose_name='Количество проживающих'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Квартира'
        verbose_name_plural = 'Квартиры'

    def __str__(self):
        return f"{self.address} ({self.user.username})"


class Tariff(models.Model):
    """История тарифов по услугам"""
    service_type = models.ForeignKey(
        ServiceType, 
        on_delete=models.CASCADE, 
        verbose_name='Тип услуги'
    )
    region = models.CharField(max_length=100, verbose_name='Регион')
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='Цена за единицу'
    )
    valid_from = models.DateField(verbose_name='Действует с')
    valid_to = models.DateField(
        null=True, 
        blank=True, 
        verbose_name='Действует до'
    )

    class Meta:
        verbose_name = 'Тариф'
        verbose_name_plural = 'Тарифы'

    def __str__(self):
        return f"{self.service_type.name} - {self.region}: {self.price} руб."


class PaymentRecord(models.Model):
    """Запись о платеже"""
    apartment = models.ForeignKey(
        Apartment, 
        on_delete=models.CASCADE, 
        verbose_name='Квартира'
    )
    service_type = models.ForeignKey(
        ServiceType, 
        on_delete=models.CASCADE, 
        verbose_name='Тип услуги'
    )
    date = models.DateField(verbose_name='Дата платежа')
    consumption = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='Потребление'
    )
    tariff = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='Тариф'
    )
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='Сумма платежа'
    )
    is_overpayment = models.BooleanField(
        default=False, 
        verbose_name='Переплата'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    class Meta:
        verbose_name = 'Платёж'
        verbose_name_plural = 'Платежи'
        ordering = ['-date']

    def __str__(self):
        return f"{self.apartment.address} - {self.service_type.name}: {self.total_amount} руб."


class UserServiceNorm(models.Model):
    """Персональные нормативы пользователя"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    service_type = models.ForeignKey(
        ServiceType,
        on_delete=models.CASCADE,
        verbose_name='Тип услуги'
    )
    norm_per_person = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Норматив на человека'
    )

    class Meta:
        verbose_name = 'Пользовательский норматив'
        verbose_name_plural = 'Пользовательские нормативы'
        unique_together = ['user', 'service_type']

    def __str__(self):
        return f"{self.user.username} - {self.service_type.name}: {self.norm_per_person}"