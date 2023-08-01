from django.db import models
from ocpp.v16 import enums as enums_v16
from django.utils.translation import gettext_lazy
from location.models import Location


class OcppProtocols(models.TextChoices):
    ocpp16 = "ocpp16", gettext_lazy("ocpp1.6")
    ocpp201 = "ocpp201", gettext_lazy("ocpp2.0.1")


# Create your models here.
class Chargepoint(models.Model):

    chargepoint_id = models.CharField(max_length=255, primary_key=True)
    chargepoint_model = models.CharField(max_length=20, blank=True)
    chargepoint_vendor = models.CharField(max_length=20, blank=True)
    chargebox_serial_number = models.CharField(max_length=20, blank=True, null=True)
    chargepoint_serial_number = models.CharField(max_length=25, blank=True, null=True)
    firmware_version = models.CharField(max_length=50, blank=True, null=True)

    ip_address = models.CharField(max_length=15)
    websocket_port = models.IntegerField()

    connected = models.BooleanField(default=True)
    chargepoint_status = models.CharField(choices=[(enums_v16.ChargePointStatus.available.value, enums_v16.ChargePointStatus.available.value), 
                                                   (enums_v16.ChargePointStatus.unavailable.value, enums_v16.ChargePointStatus.unavailable.value),
                                                   (enums_v16.ChargePointStatus.faulted.value, enums_v16.ChargePointStatus.faulted.value)], default=enums_v16.ChargePointStatus.available.value, max_length=11)
    
    ocpp_version = models.CharField(max_length=9, choices=OcppProtocols.choices)
    last_heartbeat = models.DateTimeField(null=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, default=None)
