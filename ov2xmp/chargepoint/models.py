from django.db import models
from ocpp.v16 import enums as enums_v16


# Create your models here.
class Chargepoint(models.Model):
    chargepoint_id = models.CharField(max_length=255, primary_key=True)
    chargepoint_serial_number = models.CharField(max_length=25, null=True)
    chargepoint_model = models.CharField(max_length=20, null=True)
    chargepoint_vendor = models.CharField(max_length=20, null=True)
    ip_address = models.CharField(max_length=15, null=True)
    connected = models.BooleanField(default=True, null=False)
    availability_status = models.CharField(choices=[(i, i.value) for i in enums_v16.AvailabilityType], default=enums_v16.AvailabilityType.operative, max_length=11)
    chargepoint_status = models.CharField(choices=[(enums_v16.ChargePointStatus.available, enums_v16.ChargePointStatus.available.value), 
                                                   (enums_v16.ChargePointStatus.unavailable, enums_v16.ChargePointStatus.unavailable.value),
                                                   (enums_v16.ChargePointStatus.faulted, enums_v16.ChargePointStatus.faulted.value)], default=enums_v16.ChargePointStatus.available, max_length=11)
    ocpp_version = models.CharField(max_length=5)
    last_heartbeat = models.DateTimeField(null=True)
