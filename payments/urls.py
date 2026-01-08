from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Квартиры
    path('apartments/', views.apartment_list, name='apartment_list'),
    path('apartments/add/', views.apartment_create, name='apartment_create'),
    path('apartments/<int:pk>/edit/', views.apartment_edit, name='apartment_edit'),
    path('apartments/<int:pk>/delete/', views.apartment_delete, name='apartment_delete'),
    
    # Платежи
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/add/', views.payment_create, name='payment_create'),
    path('payments/<int:pk>/edit/', views.payment_edit, name='payment_edit'),
    path('payments/<int:pk>/delete/', views.payment_delete, name='payment_delete'),

    # Экспорт
    path('payments/export/csv/', views.payment_export_csv, name='payment_export_csv'),

    # Аналитика
    path('analytics/', views.analytics, name='analytics'),
]