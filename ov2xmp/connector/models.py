from django.db import models
from chargepoint.models import Chargepoint


# Create your models here.
class Connector(models.Model):
    uuid = models.UUIDField(primary_key=True)
    connectorid = models.IntegerField()
    availability_status = models.CharField(max_length=20)
    chargepoint = models.ForeignKey(Chargepoint, on_delete=models.CASCADE)
