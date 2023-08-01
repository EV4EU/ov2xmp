from django.db import models
from chargepoint.models import Chargepoint


# Create your models here.
class Heartbeat(models.Model):
    timestamp = models.DateTimeField()
    chargepoint = models.ForeignKey(Chargepoint, on_delete=models.CASCADE)