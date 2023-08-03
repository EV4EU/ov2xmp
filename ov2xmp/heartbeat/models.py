from django.db import models
from chargepoint.models import Chargepoint
from uuid import uuid4


# Create your models here.
class Heartbeat(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    timestamp = models.DateTimeField()
    chargepoint = models.ForeignKey(Chargepoint, on_delete=models.CASCADE)