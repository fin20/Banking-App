from django.db import migrations


def create_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name='Admins')
    Group.objects.get_or_create(name='Customers')


def reverse_func(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name='Admins').delete()
    Group.objects.filter(name='Customers').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('register', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_groups, reverse_func),
    ]

