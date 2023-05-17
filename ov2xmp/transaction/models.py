from django.db import models

# Create your models here.
class Transaction(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    start_transaction_timestamp = models.DateTimeField()
    stop_transaction_timestamp = models.DateTimeField(null=True)
    wh_meter_start = models.IntegerField()
    wh_meter_stop = models.IntegerField(null=True)
    id_tag = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    reason_stopped = models.CharField(max_length=50, null=True)
    #reservation_id =