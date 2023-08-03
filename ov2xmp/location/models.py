from django.db import models
from django_countries.fields import CountryField
from uuid import uuid4


# Create your models here.
class Location(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    country = CountryField()
    postal_code = models.CharField(max_length=20)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=20)
    name = models.CharField(max_length=20)