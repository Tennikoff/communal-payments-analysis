# 💡 КоммуналПро - Система анализа коммунальных платежей

Веб-сервис для жильцов многоквартирных домов, позволяющий отслеживать коммунальные платежи, выявлять переплаты и прогнозировать расходы.

**Демо-версия:** [https://Tennikoff.pythonanywhere.com](https://Tennikoff.pythonanywhere.com)

**📝 Тестовый аккаунт:** логин `demo` / пароль `demo123456`

---

## 🎯 Возможности

- ✅ Учёт нескольких квартир
- ✅ Ведение истории платежей по услугам (электричество, вода, газ, отопление)
- ✅ Автоматическое выявление переплат (сравнение с нормативами)
- ✅ Графики динамики расходов (Matplotlib)
- ✅ Прогноз расходов на следующий месяц
- ✅ Сравнение потребления с нормативами

---

## 🛠 Технологии

- **Backend:** Python 3.14, Django 6.0
- **Database:** SQLite (dev)
- **Data Analysis:** Pandas, Matplotlib, NumPy
- **Frontend:** Bootstrap 5, HTML5, CSS3, JavaScript
- **Deploy:** PythonAnywhere

---

## 📊 Скриншоты

### Главная страница
![Главная страница](screenshots/home.png)

### Аналитика расходов
![Аналитика](screenshots/analytics.png)

### Список платежей
![Платежи](screenshots/payments.png)

---

## 🚀 Как запустить проект локально


1. **Клонируйте репозиторий**
    ```bash
    git clone https://github.com/Tennikoff/communal-payments-analysis.git
    cd communal-payments-analysis
    ```
2. **Создайте виртуальное окружение**
    ```bash
    python -m venv venv
    venv\Scripts\activate  # Windows
    source venv/bin/activate  # Linux/Mac
    ```
3. **Установите зависимости**
    ```bash
    pip install -r requirements.txt
    ```
4. **Выполните миграции**
    ```bash
    python manage.py migrate
    ```
5. **Выберите один из вариантов запуска:**  
    
    **Вариант А: Быстрый старт с демо-данными (рекомендуется для проверки)**  

    Описание: Создаёт демо-аккаунт с 3 квартирами и ~150 платежами за 12 месяцев для наглядной демонстрации всех возможностей сервиса: 
    ```bash
    python manage.py generate_demo_data
    ```
    Данные для входа:  
    Логин: demo/Пароль: demo123456

    **Вариант Б: Чистый старт (для работы с нуля)**  
    
    Описание: Создаёт только администратора, данные добавляете сами:
    ```bash
    python manage.py createsuperuser
    ```
    Введите логин, email (опционально) и пароль.

6. **Запустите сервер**
    ```bash
    python manage.py runserver
    ```
7. **Откройте в браузере**
    ```bash
    http://127.0.0.1:8000/
    ```
---

## 📁 Структура проекта

```text
communal-payments-analysis/
├── config/                     # Настройки Django
│   ├── settings.py             # Конфигурация проекта
│   ├── urls.py                 # Главные URL маршруты
│   └── wsgi.py                 # WSGI для деплоя
├── payments/                   # Основное приложение
│   ├── management/
│   │   └── commands/
│   │       └── generate_demo_data.py  # Команда генерации тестовых данных
│   ├── migrations/             # Миграции БД
│   ├── models.py               # Модели данных
│   ├── views.py                # Логика представлений
│   ├── forms.py                # Формы Django
│   ├── admin.py                # Настройки админ-панели
│   └── urls.py                 # URL маршруты приложения
├── templates/                  # HTML шаблоны
│   ├── base.html               # Базовый шаблон
│   ├── home.html               # Главная страница
│   ├── payments/               # Шаблоны платежей
│   └── registration/           # Шаблоны авторизации
├── screenshots/                # Скриншоты для README
├── requirements.txt            # Зависимости Python
├── TZ.md                       # Техническое задание
└── README.md                   # Документация
```

---


## 👤 Автор
```text
Имя: [Егор]
GitHub: Tennikoff
```