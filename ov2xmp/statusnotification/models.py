from django.db import models
from connector.models import Connector
from ocpp.v16 import enums as enums_v16 #ChargePointErrorCode


# Create your models here.
class Statusnotification(models.Model):
    connector = models.ForeignKey(Connector, on_delete=models.CASCADE)
    error_code = models.CharField(choices=[(i.value, i.value) for i in enums_v16.ChargePointErrorCode], max_length=50)
    info = models.CharField(max_length=50, blank=True, null=True, default='')
    status = models.CharField(choices=[(i.value, i.value) for i in enums_v16.ChargePointStatus], max_length=50)
    timestamp = models.DateTimeField(blank=True, null=True, default=None)
    vendor_id = models.CharField(max_length=255, blank=True, null=True, default='')
    vendor_error_code = models.CharField(max_length=50, blank=True, null=True, default='')
