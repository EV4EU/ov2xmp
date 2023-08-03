from django.db import models
from uuid import uuid4
from transaction.models import Transaction


# Create your models here.
class Sampledvalue(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    value = models.CharField(max_length=50)
    context = models.CharField(max_length=50, null=True, default=None)
    format = models.CharField(max_length=50, null=True, default=None)
    measurand = models.CharField(max_length=50, null=True, default=None)
    phase = models.CharField(max_length=50, null=True, default=None)
    location = models.CharField(max_length=50, null=True, default=None)
    unit = models.CharField(max_length=50, null=True, default=None)

