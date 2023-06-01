# Generated by Django 4.1.7 on 2023-05-16 12:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='idTag',
            fields=[
                ('idToken', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('expiry_date', models.DateTimeField(default=None, null=True)),
                ('revoked', models.BooleanField(default=False)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]