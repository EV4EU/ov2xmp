from django.db import models

# Create your models here.
class Location(models.Model):
    uuid = models.UUIDField(primary_key=True)
    country = models.CharField(max_length=20)
    postal_code = models.CharField(max_length=20)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=20)
    name = models.CharField(max_length=20)