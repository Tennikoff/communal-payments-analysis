from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

from .models import Apartment, PaymentRecord


class ApartmentForm(forms.ModelForm):
    class Meta:
        model = Apartment
        fields = ['address', 'area', 'residents_count']
        widgets = {
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Город, улица, дом, квартира'}),
            'area': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Например: 45.5'}),
            'residents_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }
        labels = {
            'address': 'Адрес',
            'area': 'Площадь (м²)',
            'residents_count': 'Количество проживающих',
        }

class PaymentRecordForm(forms.ModelForm):
    class Meta:
        model = PaymentRecord
        fields = ['apartment', 'service_type', 'date', 'consumption', 'tariff']
        widgets = {
            'apartment': forms.Select(attrs={'class': 'form-select'}),
            'service_type': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'consumption': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Потребление'}),
            'tariff': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Тариф за единицу'}),
        }
        labels = {
            'apartment': 'Квартира',
            'service_type': 'Тип услуги',
            'date': 'Дата платежа',
            'consumption': 'Потребление',
            'tariff': 'Тариф (руб/ед)',
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Показываем только квартиры текущего пользователя
        self.fields['apartment'].queryset = Apartment.objects.filter(user=user)
