# Generated by Django 4.2.1 on 2023-06-03 09:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reservation', '0002_remove_reservation_chargepoint'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reservation',
            name='status',
        ),
    ]
