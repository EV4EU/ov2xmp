# Generated by Django 4.1.7 on 2023-05-02 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chargepoint', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chargepoint',
            name='chargepoint_serial_number',
            field=models.CharField(max_length=25, null=True),
        ),
    ]
