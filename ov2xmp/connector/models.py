from django.db import models
from api.enums import ChargePointStatus
from chargepoint.models import Chargepoint


# Create your models here.
class Connector(models.Model):
    uuid = models.UUIDField(primary_key=True)
    connectorid = models.IntegerField()
    availability_status = models.IntegerField(choices=ChargePointStatus.choices)
    chargepoint = models.ForeignKey(Chargepoint, on_delete=models.CASCADE)
