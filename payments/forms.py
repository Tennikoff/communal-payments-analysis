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