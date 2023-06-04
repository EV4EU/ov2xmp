from django.db import models
from connector.models import Connector
from chargepoint.models import Chargepoint


# Create your models here.
class Reservation(models.Model):
    uuid = models.UUIDField(primary_key=True)
    connector = models.ForeignKey(Connector, on_delete=models.CASCADE)
    reservation_id = models.IntegerField()
    expiry_date = models.DateTimeField()
