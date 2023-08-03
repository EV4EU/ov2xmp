from django.db import models
from chargepoint.models import Chargepoint
from ocpp.v16 import enums as enums_v16
from uuid import uuid4


# Create your models here.
class Connector(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    connectorid = models.IntegerField()
    availability_status = models.CharField(choices=[(i.value, i.value) for i in enums_v16.AvailabilityType], default=enums_v16.AvailabilityType.operative.value, max_length=11)
    connector_status = models.CharField(choices=[(i.value, i.value) for i in enums_v16.ChargePointStatus], default=enums_v16.ChargePointStatus.available.value, max_length=13)
    chargepoint = models.ForeignKey(Chargepoint, on_delete=models.CASCADE)

    def __str__(self):
        return "Connector " + str(self.connectorid) + " of " + self.chargepoint.chargepoint_id