import pytz
from django.db import models
from django.contrib.auth.models import User
# pip install django-timezone-field
from timezone_field import TimeZoneField


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.png', upload_to='profile_pics')
    timezone = TimeZoneField(default='Europe/Athens')

    def __str__(self):
        return f'{self.user.username} Profile'
