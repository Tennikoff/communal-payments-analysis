from django.db import migrations


def create_initial_services(apps, schema_editor):
    ServiceType = apps.get_model('payments', 'ServiceType')
    
    services = [
        {'name': 'Электроэнергия', 'unit': 'кВт·ч', 'norm_per_person': 70, 'description': 'Оплата за электричество'},
        {'name': 'Холодная вода', 'unit': 'м³', 'norm_per_person': 5, 'description': 'Холодное водоснабжение'},
        {'name': 'Горячая вода', 'unit': 'м³', 'norm_per_person': 3.5, 'description': 'Горячее водоснабжение'},
        {'name': 'Газ', 'unit': 'м³', 'norm_per_person': 10, 'description': 'Газоснабжение'},
        {'name': 'Отопление', 'unit': 'Гкал', 'norm_per_person': 0.02, 'description': 'Центральное отопление'},
    ]
    
    for service_data in services:
        ServiceType.objects.get_or_create(
            name=service_data['name'],
            defaults=service_data
        )


def reverse_initial_services(apps, schema_editor):
    ServiceType = apps.get_model('payments', 'ServiceType')
    ServiceType.objects.filter(name__in=[
        'Электроэнергия', 'Холодная вода', 'Горячая вода', 'Газ', 'Отопление'
    ]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_userservicenorm'),
    ]

    operations = [
        migrations.RunPython(create_initial_services, reverse_initial_services),
    ]