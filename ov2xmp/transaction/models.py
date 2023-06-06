from django.db import models
from idtag.models import IdTag


class TransactionStatus(models.TextChoices):
    started = "Started"
    finished = "Finished"
    unauthorized = "Unauthorized"

    
# Create your models here.
class Transaction(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    start_transaction_timestamp = models.DateTimeField()
    stop_transaction_timestamp = models.DateTimeField(null=True)
    wh_meter_start = models.IntegerField()
    wh_meter_stop = models.IntegerField(null=True)
    id_tag = models.ForeignKey(IdTag, on_delete=models.SET_NULL, null=True, default=None)
    reason_stopped = models.CharField(max_length=50, null=True)
    status = models.CharField(max_length=15, choices=TransactionStatus.choices, default=TransactionStatus.started)