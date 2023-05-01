from django.db import models
from api.enums import ChargePointStatus


# Create your models here.
class Chargepoint(models.Model):
    chargepoint_url_identity = models.CharField(max_length=255, primary_key=True)
    chargepoint_serial_number = models.CharField(max_length=25)
    chargepoint_model = models.CharField(max_length=20, null=True)
    chargepoint_vendor = models.CharField(max_length=20, null=True)
    ip_address = models.CharField(max_length=15, null=True)
    availability_status = models.IntegerField(choices=ChargePointStatus.choices, null=True)
    ocpp_version = models.CharField(max_length=5)

